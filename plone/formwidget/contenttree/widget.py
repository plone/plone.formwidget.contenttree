from zope.interface import implements, implementer
from zope.component import getMultiAdapter

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.util

from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from plone.formwidget.autocomplete.widget import AutocompleteMultiSelectionWidget

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.formwidget.contenttree.interfaces import IContentTreeWidget
from plone.formwidget.contenttree import MessageFactory as _

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from AccessControl import getSecurityManager
from Acquisition import Explicit

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class Fetch(BrowserView):
    
    fragment_template = ViewPageTemplateFile('fragment.pt')
    recurse_template = ViewPageTemplateFile('input_recurse.pt')
    
    def validate_access(self):
        content = self.context.form.context
        view_name = self.context.form.__name__
        view_instance = getMultiAdapter((content, self.request), name=view_name).__of__(content)
        
        # May raise Unauthorized
        getSecurityManager().validate(content, content, view_name, view_instance)
        
    def __call__(self):
        
        # We want to check that the user was indeed allowed to access the
        # form for this widget. We can only this now, since security isn't
        # applied yet during traversal.
        self.validate_access()
        
        widget = self.context
        context = widget.context
        source = widget.bound_source
        
        portal_url = getMultiAdapter((self.context, self.request), name=u'plone_portal_state').portal_url()
        directory = portal_url + self.request.form.get('href', None)
        level = self.request.form.get('rel', 0)
        
        navtree_query = source.navigation_tree_query.copy()
        navtree_query['path'] = {'depth': 1, 'query': directory}
        
        if 'is_default_page' not in navtree_query:
            navtree_query['is_default_page'] = False
            
        strategy = getMultiAdapter((context, widget), INavtreeStrategy)
        catalog = getToolByName(context, 'portal_catalog')
        
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

        return self.fragment_template(children=children, level=int(level))
    
class ContentTreeBase(Explicit):
    implements(IContentTreeWidget)
    
    # XXX: Due to the way the rendering of the QuerySourceRadioWidget works,
    # if we call this 'template' or use a <z3c:widgetTemplate /> directive,
    # we'll get infinite recursion when trying to render the radio buttons.

    widget_template = ViewPageTemplateFile('input.pt')
    recurse_template = ViewPageTemplateFile('input_recurse.pt')
    
    # Parameters passed to the JavaScript function
    folderEvent = 'click'
    selectEvent = 'click'
    expandSpeed = 200
    collapseSpeed = 200
    multiFolder = True
    multi_select = False

    # Overrides for autocomplete widget
    formatItem = 'function(row, idx, count, value) { return row[1] + " (" + row[0] + ")"; }'

    def render_tree(self):
        context = self.context
        source = self.bound_source
        
        strategy = getMultiAdapter((context, self), INavtreeStrategy)
        data = buildFolderTree(context,
                               obj=context,
                               query=source.navigation_tree_query,
                               strategy=strategy)

        return self.recurse_template(children=data.get('children', []), level=1)

    def render(self):
        return self.widget_template(self)

    def js_extra(self):

        form_url = self.request.getURL()
        form_name = self.form.__name__
        widget_name = self.name.split('.')[-1]

        url = "%s/@@%s/++widget++%s/@@contenttree-fetch" % (form_url, form_name, widget_name)

        return """\
                $('#%(id)s-widgets-query').after(
                    $(document.createElement('input'))
                        .attr({
                            'type': 'button',
                            'value': 'Browse...'
                        })
                        .addClass('searchButton')
                        .click(function () {
                            $('#%(id)s-contenttree-window').showDialog();
                        })
                );
                $('#%(id)s-contenttree-window').find('.contentTreeAdd').click(function () {
                    $(this).contentTreeAdd('%(id)s', '%(name)s', '%(klass)s', '%(title)s', %(multiSelect)s);
                });
                $('#%(id)s-contenttree-window').find('.contentTreeCancel').click(function () {
                    $(this).contentTreeCancel();
                });
                $('#%(id)s-widgets-query').after(" ");
                $('#%(id)s-contenttree').contentTree(
                    {
                        script: '%(url)s',
                        folderEvent: '%(folderEvent)s',
                        selectEvent: '%(selectEvent)s',
                        expandSpeed: %(expandSpeed)d,
                        collapseSpeed: %(collapseSpeed)s,
                        multiFolder: %(multiFolder)s,
                        multiSelect: %(multiSelect)s,
                    },
                    function(event, selected, data, title) {
                        // alert(event + ', ' + selected + ', ' + data + ', ' + title);
                    }
                );
        """ % dict(url=url,
                   id=self.name.replace('.', '-'),
                   folderEvent=self.folderEvent,
                   selectEvent=self.selectEvent,
                   expandSpeed=self.expandSpeed,
                   collapseSpeed=self.collapseSpeed,
                   multiFolder=str(self.multiFolder).lower(),
                   multiSelect=str(self.multi_select).lower(),
                   name=self.name,
                   klass=self.klass,
                   title=self.title)

class ContentTreeWidget(ContentTreeBase, AutocompleteSelectionWidget):
    """ContentTree widget that allows single selection.
    """

class MultiContentTreeWidget(ContentTreeBase, AutocompleteMultiSelectionWidget):
    """ContentTree widget that allows multiple selection
    """

    multi_select = True

@implementer(z3c.form.interfaces.IFieldWidget)
def ContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ContentTreeWidget(request))

@implementer(z3c.form.interfaces.IFieldWidget)
def MultiContentTreeFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, MultiContentTreeWidget(request))