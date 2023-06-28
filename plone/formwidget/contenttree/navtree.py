from Acquisition import aq_inner
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.root import getNavigationRoot
from plone.formwidget.contenttree.interfaces import IContentSource
from plone.formwidget.contenttree.interfaces import IContentTreeWidget
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from zope.component import adapts
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import implementer


try:
    from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
    SitemapNavtreeStrategy  # pyflakes
except ImportError:
    # Plone trunk
    from plone.app.layout.navigation.sitemap import SitemapNavtreeStrategy


@implementer(INavigationQueryBuilder)
class QueryBuilder(object):
    """Build a navtree query for a content source
    """
    adapts(Interface, IContentSource)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    def __call__(self):
        context = self.context

        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')

        query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if not currentPath.startswith(rootPath):
            query['path'] = {'query': rootPath, 'depth': 1}
        else:
            query['path'] = {'query': currentPath, 'navtree': 1}

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        return query


@implementer(INavtreeStrategy)
class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the content tree widget
    """
    adapts(Interface, IContentTreeWidget)

    def __init__(self, context, widget):
        super(NavtreeStrategy, self).__init__(context, None)

        self.context = context
        self.widget = widget

        # set rootPath to the query path if the source query is not a
        # navtree query in this case we want the widget to only show
        # elements below the query path
        if 'path' in widget.source.navigation_tree_query:
            queryPath = widget.source.navigation_tree_query['path']
            if 'navtree' not in queryPath or not queryPath['navtree']:
                self.rootPath = queryPath['query']

        self.showAllParents = False  # override from base class
        self.site_encoding = utils.getSiteEncoding(self.context)

    def subtreeFilter(self, node):
        # Allow entering children even if the type would not normally be
        # expanded in the navigation tree
        return True

    def showChildrenOf(self, object):
        # Allow entering children even if the type would not normally be
        # expanded in the navigation tree
        return True

    def nodeFilter(self, node):
        # Returns True when the node should not be filtered.
        if self.widget.show_all_nodes:
            return True
        # Show folderish nodes.
        if getattr(node['item'], 'is_folderish', False):
            return True
        # Show selectable nodes.
        return self.widget.bound_source.isBrainSelectable(node['item'])

    def decoratorFactory(self, node):
        """Cleanup this method's original
            - remove unused plone view, then request is not needed anymore
        """
        context = aq_inner(self.context)
        # Patch: request empty because acquisiton gone already, but we do not need it anyway
        # request = context.REQUEST

        newNode = node.copy()
        item = node['item']

        portalType = getattr(item, 'portal_type', None)
        itemUrl = item.getURL()
        if portalType is not None and portalType in self.viewActionTypes:
            itemUrl += '/view'

        useRemoteUrl = False
        getRemoteUrl = getattr(item, 'getRemoteUrl', None)
        isCreator = self.memberId == getattr(item, 'Creator', None)
        if getRemoteUrl and not isCreator:
            useRemoteUrl = True

        isFolderish = getattr(item, 'is_folderish', None)
        showChildren = False
        if isFolderish and \
                (portalType is None or portalType not in self.parentTypesNQ):
            showChildren = True

        isFolderish = getattr(item, 'is_folderish', None)

        # Patch: remove unused view
        #layout_view = getMultiAdapter((context, request), name=u'plone_layout')

        newNode['Title'] = utils.pretty_title_or_id(context, item)
        newNode['id'] = item.getId
        newNode['UID'] = item.UID
        newNode['absolute_url'] = itemUrl
        newNode['getURL'] = itemUrl
        newNode['path'] = item.getPath()
        newNode['Creator'] = getattr(item, 'Creator', None)
        newNode['creation_date'] = getattr(item, 'CreationDate', None)
        newNode['portal_type'] = portalType
        newNode['review_state'] = getattr(item, 'review_state', None)
        newNode['Description'] = getattr(item, 'Description', None)
        newNode['show_children'] = showChildren
        # Allow entering children even if the type would not normally be
        # expanded in the navigation tree
        newNode['show_children'] = getattr(item,
                                           'is_folderish',
                                           False)
        newNode['no_display'] = False  # We sort this out with the nodeFilter
        # BBB getRemoteUrl and link_remote are deprecated, remove in Plone 4
        newNode['getRemoteUrl'] = getattr(item, 'getRemoteUrl', None)
        newNode['useRemoteUrl'] = useRemoteUrl
        newNode['link_remote'] = (
            newNode['getRemoteUrl'] and newNode['Creator'] != self.memberId
        )
        # Mark selectable nodes
        newNode['selectable'] = self.widget.bound_source.isBrainSelectable(item)

        idnormalizer = queryUtility(IIDNormalizer)
        newNode['normalized_portal_type'] = idnormalizer.normalize(portalType)
        newNode['normalized_review_state'] = idnormalizer.normalize(
            newNode['review_state']
        )
        newNode['normalized_id'] = idnormalizer.normalize(newNode['id'])

        # turn all strings to unicode to render non ascii characters
        # in the recursion template
        for key, value in newNode.items():
            if isinstance(value, str):
                newNode[key] = unicode(value, self.site_encoding)

        return newNode
