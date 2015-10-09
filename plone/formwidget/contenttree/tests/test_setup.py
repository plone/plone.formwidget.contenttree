# -*- coding: utf-8 -*-
from plone.formwidget.contenttree.testing import (
    CONTENTTREE_INTEGRATION_TESTING,
)
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

import unittest2 as unittest


class ContentTreeFormWidgetTestCase(unittest.TestCase):

    layer = CONTENTTREE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_css_registered(self):
        css_registry = self.portal['portal_css']
        stylesheets_ids = css_registry.getResourceIds()
        self.assertIn(
            '++resource++plone.formwidget.contenttree/contenttree.css',
            stylesheets_ids
        )

    def test_js_registered(self):
        js_registry = self.portal['portal_javascripts']
        javascript_ids = js_registry.getResourceIds()
        self.assertIn(
            '++resource++plone.formwidget.contenttree/contenttree.js',
            javascript_ids
        )
