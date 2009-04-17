Introduction
============

plone.formwidget.contenttree is a z3c.form widget for use with Plone. It
uses the jQuery Autocomplete widget, and has graceful fallback for non-
Javascript browsers.

There is a single-select version (AutocompleteSelectionFieldWidget) for
Choice fields, and a multi-select one (AutocompleteMultiSelectionFieldWidget)
for collection fields (e.g. List, Tuple) with a value_type of Choice.

When using this widget, the vocabulary/source has to provide the IQuerySource
interface from z3c.formwidget.query and have a search() method.

