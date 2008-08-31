from zope.interface import Interface, implements
from zope.component import adapts
from zope import schema

from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import MultiContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder

from z3c.form import form, button, field
from plone.z3cform import layout

from Products.CMFCore.utils import getToolByName

class ITestForm(Interface):
    
    buddy = schema.Choice(title=u"Buddy object",
                          source=PathSourceBinder(portal_type='Document'))

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

class TestForm(form.Form):
    fields = field.Fields(ITestForm)
    fields['buddy'].widgetFactory = ContentTreeFieldWidget
    
    @button.buttonAndHandler(u'Ok')
    def handle_ok(self, action):
        data, errors = self.extractData()
        print data, errors

TestView = layout.wrap_form(TestForm)