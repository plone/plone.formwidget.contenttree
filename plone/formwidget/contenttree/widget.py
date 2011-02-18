import json
from AccessControl import getSecurityManager
from Acquisition import Explicit
from Acquisition.interfaces import IAcquirer
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implementsOnly, implementer
from zope.component import getMultiAdapter
from zope.i18n import translate

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.util

from z3c.formwidget.query.widget import QuerySourceRadioWidget
from z3c.formwidget.query.widget import QuerySourceCheckboxWidget

from zope.app.component.hooks import getSite

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.formwidget.contenttree.interfaces import IContentTreeWidget


class Fetch(BrowserView):

    def validate_access(self):

        content = self.context.form.context

        # If the object is not wrapped in an acquisition chain
        # we cannot check any permission.
        if not IAcquirer.providedBy(content):
            return
        
        url = self.request.getURL()
        view_name = url[len(content.absolute_url()):].split('/')[1]
        
        # May raise Unauthorized

        # If the view is 'edit', then traversal prefers the view and
        # restrictedTraverse prefers the edit() method present on most CMF
        # content. Sigh...
        if not view_name.startswith('@@') and not view_name.startswith('++'):
            view_name = '@@' + view_name

        view_instance = content.restrictedTraverse(view_name)
        getSecurityManager().validate(content, content, view_name, view_instance)

    def buildJSON(self, children):
        data = []
        for node in children:
            icon = node['item_icon']
            try:
                icon = icon.url
            except:
                pass
            data.append(
                {'title': node['Title'],
                 'tooltip': node['Description'],
                 'icon': icon,
                 'isFolder': node['show_children'],
                 'isLazy': True,
                 'key': node['path']})

        return json.dumps(data)        

    def __call__(self):
        # We want to check that the user was indeed allowed to access the
        # form for this widget. We can only this now, since security isn't
        # applied yet during traversal.
        self.validate_access()

        widget = self.context
        context = widget.context

        # Update the widget before accessing the source.
        # The source was only bound without security applied
        # during traversal before.
        widget.update()
        source = widget.bound_source

        directory = self.request.form.get('key', None)
        content = context
        if not IAcquirer.providedBy(content):
            content = getSite()
        strategy = getMultiAdapter((content, widget), INavtreeStrategy)
        
        if directory is None:
            data = buildFolderTree(
                content,
                obj=content,
                query=source.navigation_tree_query,
                strategy=strategy)

            return self.buildJSON(data.get('children', []))

        navtree_query = source.navigation_tree_query.copy()
        print navtree_query
        navtree_query['path'] = {'depth': 1, 'query': directory}

        if 'is_default_page' not in navtree_query:
            navtree_query['is_default_page'] = False

        catalog = getToolByName(content, 'portal_catalog')

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

        return self.buildJSON(children)

    def search(self):
        print self.request.form
        self.validate_access()

        widget = self.context
        context = widget.context

        widget.update()
        source = widget.bound_source

        search = self.request.form.get('search', None)
        if search is None:
            return self.buildJSON([])

        content = context
        if not IAcquirer.providedBy(content):
            content = getSite()
        strategy = getMultiAdapter((content, widget), INavtreeStrategy)
        
        navtree_query = source.navigation_tree_query.copy()
        query = {'portal_type': navtree_query['portal_type'],
                 'SearchableText': search}

        catalog = getToolByName(content, 'portal_catalog')

        children = []
        for brain in catalog(query):
            newNode = {'item'          : brain,
                       'depth'         : -1, # not needed here
                       'currentItem'   : False,
                       'currentParent' : False,
                       'children'      : []}
            if strategy.nodeFilter(newNode):
                newNode = strategy.decoratorFactory(newNode)
                children.append(newNode)

        return self.buildJSON(children)


class ContentTreeBase(Explicit):
    implementsOnly(IContentTreeWidget)

    # XXX: Due to the way the rendering of the QuerySourceRadioWidget works,
    # if we call this 'template' or use a <z3c:widgetTemplate /> directive,
    # we'll get infinite recursion when trying to render the radio buttons.

    input_template = ViewPageTemplateFile('input.pt')
    hidden_template = ViewPageTemplateFile('hidden.pt')
    display_template = None # set by subclass

    # Parameters passed to the JavaScript function
    folderEvent = 'click'
    selectEvent = 'click'
    expandSpeed = 200
    collapseSpeed = 200
    multiFolder = True
    multi_select = False

    def update(self):
        super(ContentTreeBase, self).update()
        self.portal_path = getToolByName(getSite(), 'portal_url').getPortalPath()

    def getAjaxUrl(self):
        form_url = self.request.getURL()
        form_prefix = self.form.prefix + self.__parent__.prefix
        widget_name = self.name[len(form_prefix):]
        return "%s/++widget++%s/@@contenttree" % (form_url, widget_name,)

    def render(self):
        if self.mode == z3c.form.interfaces.DISPLAY_MODE:
            return self.display_template(self)
        elif self.mode == z3c.form.interfaces.HIDDEN_MODE:
            return self.hidden_template(self)
        else:
            return self.input_template(self)


class ContentTreeWidget(ContentTreeBase, QuerySourceRadioWidget):
    """ ContentTree widget that allows single selection. """

    klass = u"contenttree-widget"
    display_template = ViewPageTemplateFile('display_single.pt')


class MultiContentTreeWidget(ContentTreeBase, QuerySourceCheckboxWidget):
    """ContentTree widget that allows multiple selection """

    klass = u"contenttree-widget"
    multi_select = True
    display_template = ViewPageTemplateFile('display_multiple.pt')


@implementer(z3c.form.interfaces.IFieldWidget)
def ContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentTreeWidget(request))


@implementer(z3c.form.interfaces.IFieldWidget)
def MultiContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, MultiContentTreeWidget(request))
