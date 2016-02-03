# -*- coding: utf-8 -*-
from plone.formwidget.contenttree.interfaces import IContentTreeWidgetPreview
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements


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


class FilePreviewAdapter(DefaultPreviewAdapter):

    def size(self):
        return self.context.getObjSize()


class ImagePreviewAdapter(FilePreviewAdapter):

    template = ViewPageTemplateFile('image.pt')

    def image(self):
        # XXX: Get primary field on dexterity:
        # from plone.rfc822.interfaces import IPrimaryFieldInfo
        # field = IPrimaryFieldInfo(self.context).field
        #
        scaling = getMultiAdapter(
            (self.context, self.request), name='images')
        return scaling.scale('image', 'mini').tag()
