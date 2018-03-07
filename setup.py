from setuptools import setup
from setuptools import find_packages


version = '1.1.0'
desc = 'AJAX selection widget for Plone'
longdesc = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='plone.formwidget.contenttree',
    version=version,
    description=desc,
    long_description=longdesc,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
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
    extras_require={
        'test': [
            'plone.app.testing',
            'unittest2'
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
