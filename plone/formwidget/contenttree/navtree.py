from zope.interface import implements, Interface
from zope.component import adapts

from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
    SitemapNavtreeStrategy  # pyflakes
except ImportError:
    # Plone trunk
    from plone.app.layout.navigation.sitemap import SitemapNavtreeStrategy
from Products.CMFPlone import utils

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from plone.app.layout.navigation.root import getNavigationRoot

from plone.formwidget.contenttree.interfaces  import IContentSource
from plone.formwidget.contenttree.interfaces  import IContentTreeWidget


class QueryBuilder(object):
    """Build a navtree query for a content source
    """
    implements(INavigationQueryBuilder)
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


class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the content tree widget
    """
    implements(INavtreeStrategy)
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
        # Don't filter any nodes.
        return True

    def decoratorFactory(self, node):
        new_node = super(NavtreeStrategy, self).decoratorFactory(node)

        # Allow entering children even if the type would not normally be
        # expanded in the navigation tree
        new_node['show_children'] = getattr(new_node['item'],
                                            'is_folderish',
                                            False)

        # Mark selectable nodes
        new_node['selectable'] = self.widget.bound_source.isBrainSelectable(
            new_node['item'])

        # turn all strings to unicode to render non ascii characters
        # in the recursion template
        for key, value in new_node.items():
            if isinstance(value, str):
                new_node[key] = unicode(value, self.site_encoding)

        return new_node
