Introduction
============

``plone.formwidget.contenttree`` is a ``z3c.form`` widget for use with Plone.
It uses the jQuery Autocomplete widget, and has graceful fallback for non-
Javascript browsers.

There is a single-select version (AutocompleteSelectionFieldWidget) for
Choice fields, and a multi-select one (AutocompleteMultiSelectionFieldWidget)
for collection fields (e.g. List, Tuple) with a value_type of Choice.

When using this widget, the vocabulary/source has to provide the IQuerySource
interface from z3c.formwidget.query and have a search() method. The easiest
way to do this is generate one with one of:

* ``plone.formwidget.contenttree.PathSourceBinder(navigation_tree_query=None, **kw)``
* ``plone.formwidget.contenttree.ObjPathSourceBinder(navigation_tree_query=None, **kw)``
* ``plone.formwidget.contenttree.UUIDSourceBinder(navigation_tree_query=None, **kw)``

Where ``navigation_tree_query`` is some restrictions that should be applied to
any Catalog query. The rest of the arguments are used to form a filter
(see source.py).

``PathSourceBinder`` and ``ObjPathSourceBinder`` store the selected object's
path in the field value. This means that the link will be broken if the object
is moved. ``UUIDSourceBinder`` stores UUID references, so will handle pages
being moved.

If you do not want to filter the content tree whatsoever, there are some
pre-baked instances too:

* plone.formwidget.contenttree.path_src_binder
* plone.formwidget.contenttree.obj_path_src_binder
* plone.formwidget.contenttree.uuid_src_binder

Example Usage::

    from zope.component import adapter
    from zope.interface import Interface
    from zope.interface import implementer
    from zope import schema
    from plone.z3cform import layout
    from z3c.form import form
    from z3c.form import button
    from z3c.form import field
    from plone.formwidget.contenttree import ContentTreeFieldWidget
    from plone.formwidget.contenttree import MultiContentTreeFieldWidget
    from plone.formwidget.contenttree import PathSourceBinder


    class ITestForm(Interface):

        buddy = schema.Choice(
            title=u"Buddy object",
            description=u"Select one, please",
            source=PathSourceBinder(portal_type='Document')
        )

        friends = schema.List(
            title=u"Friend objects",
            description=u"Select as many as you want",
            value_type=schema.Choice(
                title=u"Selection",
                source=PathSourceBinder(portal_type='Document')
            )
        )


    @implementer(ITestForm)
    @adapter(Interface)
    class TestAdapter(object):

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
