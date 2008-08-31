from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone import utils

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import NavtreeStrategyBase

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
        source = self.source
        
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        
        portal_url = getToolByName(context, 'portal_url')
        
        query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if not currentPath.startswith(rootPath):
            query['path'] = {'query' : rootPath, 'depth' : 1}
        else:
            query['path'] = {'query' : currentPath, 'navtree' : 1}

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
        self.showAllParents = True # override from base class
    
    def nodeFilter(self, node):
        # Don't filter any nodes here
        return True

    def decoratorFactory(self, node):    
        new_node = super(NavtreeStrategy, self).decoratorFactory(node)
        new_node['selectable'] = self.widget.bound_source._filter(new_node['item'])
        return new_node