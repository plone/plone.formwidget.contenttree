# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import helpers
from plone.app.testing import layers
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig

import doctest


class ContentTreeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.formwidget.contenttree
        xmlconfig.file('testing.zcml',
                       plone.formwidget.contenttree,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        helpers.applyProfile(portal, 'plone.formwidget.contenttree:default')

        portal.acl_users.userFolderAddUser('admin', 'secret', ['Manager'], [])

        login(portal, 'admin')
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        setRoles(portal, TEST_USER_ID, ['Manager'])


CONTENTTREE_FIXTURE = ContentTreeLayer()
CONTENTTREE_INTEGRATION_TESTING = layers.IntegrationTesting(
    bases=(CONTENTTREE_FIXTURE,),
    name="plone.formwidget.contenttree:Integration")
CONTENTTREE_FUNCTIONAL_TESTING = layers.FunctionalTesting(
    bases=(CONTENTTREE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="plone.formwidget.contenttree:Functional")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
