from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone')

from plone.formwidget.contenttree.widget import ContentTreeFieldWidget
from plone.formwidget.contenttree.widget import MultiContentTreeFieldWidget

from plone.formwidget.contenttree.source import PathSourceBinder,\
    ObjPathSourceBinder, UUIDSourceBinder

# Some binder instances for use with plone.supermodel schemas
path_src_binder = PathSourceBinder()
obj_path_src_binder = ObjPathSourceBinder()
uuid_src_binder = UUIDSourceBinder()
