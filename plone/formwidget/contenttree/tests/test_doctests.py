# -*- coding: utf-8 -*-
from plone.formwidget.contenttree.testing import (
    CONTENTTREE_INTEGRATION_TESTING,
)
from plone.testing import layered

import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('../README.rst'),
                CONTENTTREE_INTEGRATION_TESTING)
    ])

    return suite
