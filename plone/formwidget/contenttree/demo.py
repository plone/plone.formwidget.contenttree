from zope.component import adapts
from zope.interface import Interface, implementer
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


@implementer(ITestForm)
class TestAdapter(object):
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
