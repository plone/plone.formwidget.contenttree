from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('plone.formwidget.contenttree')

from plone.formwidget.contenttree.widget import ContentTreeFieldWidget
from plone.formwidget.contenttree.widget import MultiContentTreeFieldWidget

from plone.formwidget.contenttree.source import PathSourceBinder,\
    ObjPathSourceBinder, UUIDSourceBinder

# Some binder instances for use with plone.supermodel schemas
path_src_binder = PathSourceBinder()
obj_path_src_binder = ObjPathSourceBinder()
uuid_src_binder = UUIDSourceBinder()
