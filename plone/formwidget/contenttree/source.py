import logging

import Missing
from zope.interface import implementer
from zope.component import getMultiAdapter

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm

from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.vocabularies.catalog import parse_query

from Products.CMFCore.utils import getToolByName
from Products.ZCTextIndex.ParseTree import ParseError

from plone.formwidget.contenttree.interfaces import IContentSource
from plone.formwidget.contenttree.interfaces import IContentFilter
from plone.formwidget.contenttree.utils import closest_content

from OFS.interfaces import ITraversable

logger = logging.getLogger(__name__)


@implementer(IContentFilter)
class CustomFilter(object):
    """A filter that can be used to test simple values in brain metadata and
    indexes.

    Limitations:

    - Will probably only work on FieldIndex, KeywordIndex and PathIndex indexes
    """

    def __init__(self, **kw):
        self.criteria = {}
        for key, value in kw.items():
            if (not isinstance(value, (list, tuple, set, frozenset))
                    and not key == 'path'):
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


@implementer(IContentSource)
class PathSource(object):

    def __init__(self, context, selectable_filter, navigation_tree_query=None, default=None, defaultFactory=None):
        self.context = context

        nav_root = getNavigationRootObject(context, None)
        query_builder = getMultiAdapter((nav_root, self),
                                        INavigationQueryBuilder)
        query = query_builder()

        if navigation_tree_query is None:
            navigation_tree_query = {}

        # Copy path from selectable_filter into the navigation_tree_query
        # normally it does not make sense to show elements that wouldn't be
        # selectable anyway and are unneeded to navigate to selectable items
        if ('path' not in navigation_tree_query
                and 'path' in selectable_filter.criteria):
            navigation_tree_query['path'] = selectable_filter.criteria['path']

        query.update(navigation_tree_query)

        self.navigation_tree_query = query
        self.selectable_filter = selectable_filter

        self.catalog = getToolByName(context, "portal_catalog")

        portal_tool = getToolByName(context, "portal_url")
        self.portal_path = portal_tool.getPortalPath()

        self._default_terms = []
        if default is not None:
            term = self.getTerm(default)
            self._default_terms = [term]
        elif defaultFactory is not None:
            term = self.getTerm(defaultFactory(context))
            self._default_terms = [term]


    # Tokenised vocabulary API

    def __iter__(self):
        return iter(self._default_terms)

    def __len__(self):
        return len(self._default_terms)

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
            raise LookupError('Value "%s" does not match criteria for field'
                              , str(value))
        return self.getTermByBrain(brain)

    # Query API - used to locate content, e.g. in non-JS mode

    def search(self, query, limit=20):
        catalog_query = self.selectable_filter.criteria.copy()
        catalog_query.update(parse_query(query, self.portal_path))

        if limit and 'sort_limit' not in catalog_query:
            catalog_query['sort_limit'] = limit

        try:
            for brain in self.catalog(**catalog_query)[:limit]:
                yield self.getTermByBrain(brain, real_value=False)
        except ParseError:
            pass

    def isBrainSelectable(self, brain):
        if brain is None:
            return False
        if not getattr(self.selectable_filter, 'criteria', True):
            # Short circuits expensive index retrieval for large objects.
            # Without filter criteria selectable_filter will always return true.
            # For custom implementations of CustomFilter, continue retrieving
            # indexes.
            return True
        index_data = self.catalog.getIndexDataForRID(brain.getRID())
        return self.selectable_filter(brain, index_data)

    def getTermByBrain(self, brain, real_value=True):
        value = brain.getPath()[len(self.portal_path):]
        for term in self._default_terms:
            # Short-circuit the generation of a new term, so we can return the
            # same object if this represents a default term. This is required
            # because z3c.form coerces the terms to a list when rendering
            # radio buttons
            if term.value == value:
                return term
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title or
                          brain.id)

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
        for term in self._default_terms:
            # Short-circuit the generation of a new term, so we can return the
            # same object if this represents a default term. This is required
            # because z3c.form coerces the terms to a list when rendering
            # radio buttons
            if term.value == value:
                return term
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title or
                          brain.id)


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
        for term in self._default_terms:
            # Short-circuit the generation of a new term, so we can return the
            # same object if this represents a default term. This is required
            # because z3c.form coerces the terms to a list when rendering
            # radio buttons
            if term.value == value:
                return term
        return SimpleTerm(value, token=brain.getPath(), title=brain.Title or
                          brain.id)


@implementer(IContextSourceBinder)
class PathSourceBinder(object):

    path_source = PathSource

    def __init__(self, navigation_tree_query=None, default=None, defaultFactory=None, **kw):
        self.selectable_filter = CustomFilter(**kw)
        self.navigation_tree_query = navigation_tree_query
        self.default = default
        self.defaultFactory = defaultFactory

    def __call__(self, context):
        return self.path_source(
            closest_content(context),
            selectable_filter=self.selectable_filter,
            navigation_tree_query=self.navigation_tree_query,
            default=self.default,
            defaultFactory=self.defaultFactory)

    def __contains__(self, value):
        # If used without being properly bound (looks at DataGridField), bind
        # now and pass through to the bound version
        return self(None).__contains__(value)


class ObjPathSourceBinder(PathSourceBinder):
    path_source = ObjPathSource


class UUIDSourceBinder(PathSourceBinder):
    path_source = UUIDSource
