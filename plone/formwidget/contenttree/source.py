import logging

from Acquisition.interfaces import IAcquirer
import Missing
from zope.interface import implements
from zope.component import getMultiAdapter

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm

from zope.app.component.hooks import getSite
try:
    from zope.globalrequest import getRequest
    getRequest  # pyflakes
except ImportError:
    # Fake it
    getRequest = object

from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.vocabularies.catalog import parse_query

from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError

from plone.formwidget.contenttree.interfaces import IContentSource
from plone.formwidget.contenttree.interfaces import IContentFilter

from OFS.interfaces import ITraversable

logger = logging.getLogger(__name__)


class CustomFilter(object):
    """A filter that can be used to test simple values in brain metadata and
    indexes.

    Limitations:

    - Will probably only work on FieldIndex, KeywordIndex and PathIndex indexes
    """
    implements(IContentFilter)

    def __init__(self, **kw):
        self.criteria = {}
        for key, value in kw.items():
            if (not isinstance(value, (list, tuple, set, frozenset)) and
                not key == 'path'):
                self.criteria[key] = [value]
            elif isinstance(value, (set, frozenset)):
                self.criteria[key] = list(value)
            else:
                self.criteria[key] = value

    def __call__(self, brain, index_data):
        for key, value in self.criteria.items():
            test_value = index_data.get(key, None)
            if test_value is not None:
                if (not isinstance(test_value, (list, tuple, set, frozenset))
                    and not key == 'path'):
                    test_value = set([test_value])
                elif isinstance(value, (list, tuple)):
                    test_value = set(test_value)
                if key == 'path':
                    if not test_value.startswith(value['query']):
                        return False
                elif not test_value.intersection(value):
                    return False
        return True


class PathSource(object):
    implements(IContentSource)

    def __init__(self, context, selectable_filter, navigation_tree_query=None):
        self.context = context

        query_builder = getMultiAdapter((context, self),
                                        INavigationQueryBuilder)
        query = query_builder()

        if navigation_tree_query is None:
            navigation_tree_query = {}

        # Copy path from selectable_filter into the navigation_tree_query
        # normally it does not make sense to show elements that wouldn't be
        # selectable anyway and are unneeded to navigate to selectable items
        if ('path' not in navigation_tree_query and
            'path' in selectable_filter.criteria):
            navigation_tree_query['path'] = selectable_filter.criteria['path']

        query.update(navigation_tree_query)

        self.navigation_tree_query = query
        self.selectable_filter = selectable_filter

        self.catalog = getToolByName(context, "portal_catalog")

        portal_tool = getToolByName(context, "portal_url")
        self.portal_path = portal_tool.getPortalPath()

    # Tokenised vocabulary API

    def __iter__(self):
        return [].__iter__()

    def __contains__(self, value):
        try:
            brain = self._getBrainByValue(value)
            # If brain was not found, assume item is still good. This seems
            # somewhat nonsensical, but:-
            #  (a) If an item is invisible to the current editor, they should
            #      be able to keep the item there.
            #  (b) If using PathSource and an item the path points to was
            #      deleted by mistake, I may want save my changes then restore
            #      this page, rather than remove the relation.
            if brain is None:
                return True
            return self.isBrainSelectable(brain)
        except (KeyError, IndexError):
            return False

    def getTermByToken(self, token):
        if token.startswith('#error-missing-'):
            value = token.partition('#error-missing-')[2]
            return self._placeholderTerm(value)
        brain = self._getBrainByToken(token)
        if not self.isBrainSelectable(brain):
            raise LookupError(token)
        return self.getTermByBrain(brain)

    def getTerm(self, value):
        brain = self._getBrainByValue(value)
        if brain is None:
            return self._placeholderTerm(value)
        if not self.isBrainSelectable(brain):
            raise LookupError(value)
        return self.getTermByBrain(brain)

    # Query API - used to locate content, e.g. in non-JS mode

    def search(self, query, limit=20):
        catalog_query = self.selectable_filter.criteria.copy()
        catalog_query.update(parse_query(query, self.portal_path))

        if limit and 'sort_limit' not in catalog_query:
            catalog_query['sort_limit'] = limit

        try:
            results = (self.getTermByBrain(brain, real_value=False)
                       for brain in self.catalog(**catalog_query))
        except ParseError:
            return []

        return results

    def isBrainSelectable(self, brain):
        if brain is None:
            return False
        index_data = self.catalog.getIndexDataForRID(brain.getRID())
        return self.selectable_filter(brain, index_data)

    def getTermByBrain(self, brain, real_value=True):
        value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)

    def tokenToPath(self, token):
        # token==path for existing sources, but may not be true in future
        return token

    # Helper functions
    def _getBrainByToken(self, token):
        rid = self.catalog.getrid(token)
        if not(rid):
            return None
        return self.catalog._catalog[rid]

    def _getBrainByValue(self, value):
        if ITraversable.providedBy(value):
            token = '/'.join(value.getPhysicalPath())
        else:
            token = self.portal_path + value
        return self._getBrainByToken(token)

    # Generate a term to persist the value, even when we can't resolve the
    # brain. These will get hidden in the display templates
    def _placeholderTerm(self, value):
        return SimpleTerm(str(value),
                          token='#error-missing-' + value,
                          title=u"Hidden or missing item '%s'" % value)


class ObjPathSource(PathSource):

    def _getBrainByValue(self, value):
        return self._getBrainByToken('/'.join(value.getPhysicalPath()))

    def getTermByBrain(self, brain, real_value=True):
        if real_value:
            value = brain._unrestrictedGetObject()
        else:
            value = brain.getPath()[len(self.portal_path):]
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)


class UUIDSource(PathSource):
    """
    A source that stores UUIDs as values, so references don't get broken if
    content is moved.
    """

    def _getBrainByValue(self, value):
        try:
            return self.catalog(UID=value)[0]
        except (KeyError, IndexError):
            return None

    def getTermByBrain(self, brain, real_value=True):
        value = brain.UID
        if value is Missing.Value:
            # This is likely to give problems at some point.
            logger.warn("Brain in UUIDSource has missing UID value. Maybe you "
                        "need to enable plone.app.referenceablebehavior on "
                        "portal type %s?", brain.portal_type)
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title)


class PathSourceBinder(object):
    implements(IContextSourceBinder)

    path_source = PathSource

    def __init__(self, navigation_tree_query=None, **kw):
        self.selectable_filter = CustomFilter(**kw)
        self.navigation_tree_query = navigation_tree_query

    def __call__(self, context):
        return self.path_source(
            self._find_page_context(context),
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query)

    def __contains__(self, value):
        # If used without being properly bound (looks at DataGridField), bind
        # now and pass through to the bound version
        return self(None).__contains__(value)

    def _find_page_context(self, given_context=None):
        """Try to find a usable context, with increasing agression"""
        # Normally, we should be given a useful context (e.g the page)
        c = given_context
        if IAcquirer.providedBy(c):
            return c
        # Subforms (e.g. DataGridField) may not have a context set, find out
        # what page is being published
        c = getattr(getRequest(), 'PUBLISHED', None)
        if IAcquirer.providedBy(c):
            return c
        # During widget traversal nothing is being published yet, use getSite()
        c = getSite()
        if IAcquirer.providedBy(c):
            return c
        # During kss_z3cform_inline_validation, PUBLISHED and getSite() return
        # a Z3CFormValidation object. What we want is it's context.
        c = getattr(getattr(getRequest(), 'PUBLISHED', None), 'context', None)
        if IAcquirer.providedBy(c):
            return c
        raise ValueError('Cannot find suitable context to bind to source')


class ObjPathSourceBinder(PathSourceBinder):
    path_source = ObjPathSource


class UUIDSourceBinder(PathSourceBinder):
    path_source = UUIDSource
