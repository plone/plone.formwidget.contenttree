import os
import unittest

from zope.testing import doctest
from zope.app.testing.functional import ZCMLLayer

testing_zcml_path = os.path.join(os.path.dirname(__file__), 'testing.zcml')
testing_zcml_layer = ZCMLLayer(testing_zcml_path, 'plone.formwidget.contenttree', 'testing_zcml_layer')

def test_suite():
    readme_txt = doctest.DocFileSuite('README.txt')
    readme_txt.layer = testing_zcml_layer

    return unittest.TestSuite([
        readme_txt,
        ])
