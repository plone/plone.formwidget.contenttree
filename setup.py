from setuptools import setup, find_packages
import os

version = '1.0.5'

setup(name='plone.formwidget.contenttree',
      version=version,
      description="AJAX selection widget for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone selection widget AJAX',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='https://github.com/plone/plone.formwidget.contenttree',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.formwidget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.formwidget.query',
          'plone.formwidget.autocomplete >= 1.2.0',
          'plone.z3cform >= 0.7.4',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
