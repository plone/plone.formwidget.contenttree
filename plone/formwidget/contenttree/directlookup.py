import plone.formwidget.contenttree.widget
from Products.Five.browser import BrowserView
from zope.interface import implementsOnly, implementer
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.interface import implements, Interface
from zope.component import adapts

from ZTUtils import make_query

import z3c.form.interfaces

try:
    from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
except ImportError:
    # Plone trunk
    from plone.app.layout.navigation.sitemap import SitemapNavtreeStrategy
from Products.CMFPlone import utils

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.formwidget.contenttree.interfaces  import IContentTreeWidget

from Products.CMFCore.utils import getToolByName

class Fetch(BrowserView):

    fragment_template = ViewPageTemplateFile('fragment.pt')

    def brain_to_token(self,brain):
        # Using an attribute as a token, fetch that
        if getattr(self,'token_attribute',None):
            return getattr(brain,getattr(self, 'token_attribute'))
        # Fall back to fetching path
        if not(hasattr(self,'portal_path')):
            portal_tool = getToolByName(self.context, "portal_url")
            self.portal_path = portal_tool.getPortalPath()
        return brain.getPath()[len(self.portal_path):]

    def __call__(self):

        catalog = getToolByName(self.context, 'portal_catalog')
        self.token_attribute = self.request.form.get('token_attribute', None)

        mode = self.request.form.get('mode', 'autocomplete')
        if mode == 'contenttree':
            navtree_query = self.request.form.get('navtree_query', {})
            navtree_query['path'] = {'depth': 1, 'query': self.request.form.get('href', '')}
            if 'is_default_page' not in navtree_query:
                navtree_query['is_default_page'] = False

            strategy = NavtreeStrategy(self.context,navtree_query)
            children = []
            for brain in catalog(navtree_query):
                newNode = {'item'          : brain,
                           'depth'         : -1, # not needed here
                           'currentItem'   : False,
                           'currentParent' : False,
                           'children'      : []}
                if strategy.nodeFilter(newNode):
                    newNode = strategy.decoratorFactory(newNode)
                    children.append(newNode)

            return self.fragment_template(children=children, level=int(self.request.form.get('rel', 0)))

        elif mode == 'autocomplete':
            if not(self.request.form.has_key('q')): return ''
            limit = int(self.request.form.get('limit', 50))
            brains = catalog(
                SearchableText=self.request.form.get('q'),
                sort_on='sortable_title',
                sort_order='ascending',
                sort_limit=limit
            )[:limit]
            rv = ''
            for brain in brains:
                token = self.brain_to_token(brain)
                rv += "%s|%s\n" % (token, brain.Title or token)
            return rv
        else:
            raise ValueError("Invalid mode "+mode)

class ContentTreeWidget(plone.formwidget.contenttree.widget.ContentTreeWidget):
    """ContentTree widget that allows single selection.
    """
    def autocomplete_url(self):
        return "%s?%s" % (
            self.request.getURL().replace('@@edit','@@contenttree-fetch'), #TODO: Yuck
            make_query(
            mode='autocomplete',
            token_attribute= self.token_attribute if self.token_attribute else '',
            navtree_query=self.source.navigation_tree_query,
            selectable_filter={}, # TODO
        ))

    def contenttree_url(self):
        return "%s?%s" % (
            self.request.getURL().replace('@@edit','@@contenttree-fetch'), #TODO: Yuck
            make_query(
            mode='contenttree',
            token_attribute= self.token_attribute if self.token_attribute else '',
            navtree_query=self.source.navigation_tree_query,
            selectable_filter={}, # TODO
        ))

class MultiContentTreeWidget(plone.formwidget.contenttree.widget.MultiContentTreeWidget):
    """ContentTree widget that allows multiple selection
    """
    def autocomplete_url(self):
        # TODO: C&P / refactor
        return "%s/@@contenttree-query" % self.request.getURL()

    def contenttree_url(self):
        # TODO: C&P / refactor
        return "%s/@@contenttree-fetch" % self.request.getURL()

@implementer(z3c.form.interfaces.IFieldWidget)
def ContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentTreeWidget(request))
    
    
@implementer(z3c.form.interfaces.IFieldWidget)
def MultiContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, MultiContentTreeWidget(request))
        

class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the content tree widget
    """
    implements(INavtreeStrategy)
    adapts(Interface, IContentTreeWidget)

    def __init__(self, context, navigation_tree_query):
        super(NavtreeStrategy, self).__init__(context, None)

        # set rootPath to the query path if the source query is not a navtree query
        # in this case we want the widget to only show elements below the query path
        if 'path' in navigation_tree_query:
            queryPath = navigation_tree_query['path']
            if 'navtree' not in queryPath or not queryPath['navtree']:
                self.rootPath = queryPath['query']

        self.showAllParents = False # override from base class
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
        new_node['selectable'] = True #TODO: Alter interface, could save the parameters to rebuild the CustomFilter?
        #new_node['selectable'] = self.widget.bound_source.isBrainSelectable(
        #    new_node['item'])

        # turn all strings to unicode to render non ascii characters
        # in the recursion template
        for key, value in new_node.items():
            if isinstance(value, str):
                new_node[key] = unicode(value, self.site_encoding)

        return new_node
