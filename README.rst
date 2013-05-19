.. image:: https://travis-ci.org/saily/plone.formwidget.contenttree.png
   :target: http://travis-ci.org/saily/plone.formwidget.contenttree

.. contents::

!!! THIS IS AN EXPERIMENTAL FORK - DO NOT USE FOR PRODUCTION !!!

Introduction
============

plone.formwidget.contenttree is a `z3c.form`_ widget for use with Plone. It
uses the `jQuery Autocomplete widget`_, and has graceful fallback for non-
Javascript browsers.

There is a single-select version (AutocompleteSelectionFieldWidget) for
Choice fields, and a multi-select one (AutocompleteMultiSelectionFieldWidget)
for collection fields (e.g. List, Tuple) with a value_type of Choice.

When using this widget, the vocabulary/source has to provide the IQuerySource
interface from `z3c.formwidget.query`_ and have a search() method.


New Features
============

Pictures say more than words do - so first a screenshot of current work:

.. image:: https://raw.github.com/saily/plone.formwidget.contenttree/master/docs/features-libraries-preview.png


Shared libraries
----------------

This fork tries to handle several issues we discovered (and still discovering)
while building a huge multilingual site on ``plone.app.contenttypes`` and
``plone.app.multilingual`` and Plone 4.3.

You'll have multiple content objects providing *INavigationRoot* when using
``plone.app.multilingual`` because of it's shared folder.

Idea is to implement a library like selection to switch between *Language folders*
and  *Shared folders*. You can register your own library folders by adapting
``ILibraryProvider`` interface and register in zcml as an adapter.::

    @adapter(IContentTreeWidget)
    @implementer(ILibraryProvider)
    def shared_libs(widget):
        """TODO: Refactor to allow binding on special fields"""

        catalog = getToolByName(widget.context, 'portal_catalog')
        return [{'label': item.Title, 'query': item.getPath()}
                for item in catalog(object_provides=INavigationRoot.__identifier__)]


See ``adapters/libraries.py`` for more details.


Preview pane
------------

Preview pane was refactored to support registering custom Preview adapters on
different types. I really would like to see new multiadapters for File and
Images displaying contenttype and size information.::


    class DefaultPreviewAdapter(object):
        implements(IContentTreeWidgetPreview)

        template = ViewPageTemplateFile('default.pt')

        def __init__(self, context, widget):
            self.context = context
            self.request = widget.request
            self.widget = widget

        def title(self):
            return self.context.Title()

        def description(self):
            return self.context.Description()

        def __call__(self):
            return self.template()


See ``adapters/preview.py`` for more details.


Demo
----

* Run egg-contained buildout
* Start up your instance
* Create new plone site
* Setup up some languages in ``plone.app.multilingual`` controlpanel
* Create some Demo content
* Open browser and go to http://localhost:8080/Plone/en/@@test-tree-widget


How to use it
=============

Example Usage::

    from zope.component import adapts
    from zope.interface import Interface, implements
    from zope import schema

    from plone.z3cform import layout

    from z3c.form import form, button, field

    from plone.formwidget.contenttree import ContentTreeFieldWidget
    from plone.formwidget.contenttree import MultiContentTreeFieldWidget
    from plone.formwidget.contenttree import PathSourceBinder


    class ITestForm(Interface):

        buddy = schema.Choice(title=u"Buddy object",
                              description=u"Select one, please",
                              source=PathSourceBinder(portal_type='Document'))

        friends = schema.List(
            title=u"Friend objects",
            description=u"Select as many as you want",
            value_type=schema.Choice(
                title=u"Selection",
                source=PathSourceBinder(portal_type='Document')))


    class TestAdapter(object):
        implements(ITestForm)
        adapts(Interface)

        def __init__(self, context):
            self.context = context

        def _get_buddy(self):
            return None
        def _set_buddy(self, value):
            print "setting", value
        buddy = property(_get_buddy, _set_buddy)

        def _get_friends(self):
            return []
        def _set_friends(self, value):
            print "setting", value
        friends = property(_get_friends, _set_friends)


    class TestForm(form.Form):
        fields = field.Fields(ITestForm)
        fields['buddy'].widgetFactory = ContentTreeFieldWidget
        fields['friends'].widgetFactory = MultiContentTreeFieldWidget
        # To check display mode still works, uncomment this and hit refresh.
        #mode = 'display'

        @button.buttonAndHandler(u'Ok')
        def handle_ok(self, action):
            data, errors = self.extractData()
            print data, errors

    TestView = layout.wrap_form(TestForm)


.. include:: docs/INSTALL.txt

.. include:: TODO.txt

.. _`z3c.formwidget.query`: https://pypi.python.org/pypi/z3c.formwidget.query
.. _`z3c.form`: https://pypi.python.org/pypi/z3c.form
.. _`jQuery Autocomplete widget`: https://github.com/plone/plone.formwidget.autocomplete
