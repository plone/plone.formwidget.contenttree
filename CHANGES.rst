Changelog
=========

1.2.0 (2020-01-27)
------------------

New features:

- Added Python 3 compatibility.  [cekk]


1.1.0 (2018-03-07)
------------------

New features:

- Add uninstall profile.
  [thet]


1.0.16 (2018-01-17)
-------------------

Fixes:

- If the widget is loaded without a content filter to limit the content listing,
  skip retrieving all index data for the brain from the catalog in
  isBrainSelectable. This considerably speeds up listing folders with many items
  that have large (SearchableText) indexes.
  [fredvd, mauritsvanrees]


1.0.15 (2016-08-08)
-------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


1.0.14 (2016-05-15)
-------------------

Fixes:

- Slice search results in `PathSource` object to limit the search results correctly.
  http://docs.plone.org/develop/plone/searching_and_indexing/query.html#sorting-and-limiting-the-number-of-results
  [elioschmutz]

1.0.13 (2016-02-09)
-------------------

New:

- Translations moved to plone.app.locales in plone domain.
  [staeff]


1.0.12 (2015-12-01)
-------------------

- Remove unnecessary test setup.
  [timo]

- Fix HTML entities in browse button title
  [gaudenz]

- Implement __len__ for PathSource
  [gaudenz]

- Add missing test dependency declaration.
  [MatthewWilkes]


1.0.11 (2015-02-09)
-------------------

- Add support for providing defaults to contenttrees. This wasn't reliable
  previously as only defaults that were found by the initial query were
  rendered. Now SourceBinders take an optional default or defaultFactory
  argument, in the same format as schema.Choice.
  [MatthewWilkes]

1.0.10 (2015-01-16)
-------------------

- Render CSS as link, no css-import. This allows cooking with other
  link rendered css and gives better asynchronous download behavior.
  [thet]

- Add support for navigating into objects with spaces in their ids
  [MatthewWilkes]

1.0.9 (2014-10-25)
------------------

* Implement ``renderForValue`` on ``ContentTreeBase`` in order to make
  single valued relation fields work.
  [rnixx]

1.0.8 (2014-10-21)
------------------

* Work around bizarro Diazo encoding bug
  [gyst]

1.0.7 (2013-06-30)
------------------

* Add in some default binder instances, mostly for use with supermodel XML
  schemas.
  [lentinj]

* Switch to ``plone.app.testing``
  [saily]

* Add js and css registration tests
  [saily]

* Added check in tree generation if it allready exists (reopening the contenttree window).
  [phgross]

* Do not exclude content types which are not allowed in navigation [ebrehault]

* Ignore missing values, content objects can go away or the content of a source may change.
  [gaudenz]

1.0.6 (2012-09-28)
------------------

* Tweak CSS to use outline instead of border.
  [elro]

* Avoid theming ajax response.
  [elro]

* Ensure context is a content item of some sort.
  [elro]

* Import getSite from zope.component to avoid dependency on zope.app.component.
  [hvelarde]

* Import ViewPageTemplateFile from zope.browserpage to avoid dependency on
  zope.app.pagetemplate.
  [hvelarde]

* Added french translation.
  [phgross]

* Trigger change handler when used with datagrid
  [kingel]

* Use an ajax fetch for the initial call
  [kingel]

* Fix url in display templates, so that it uses absolute urls.
  [phgross]

* pep8
  [joka]

* Fix term title genration to use the brain id if there is not brain title
  [joka]

* Added Italian translation.
  [gborelli]

* Added Finnish (fi) translation.
  [dokai]

* By default filter out nodes that are not selectable and not folderish.
  This can be overridden on the widget by setting show_all_nodes to True.
  [maurits]

* Added Dutch translation.
  [maurits]

1.0.5 (2012-02-20)
------------------

* Added Spanish translation
  [hvelarde]

1.0.4 (2011-10-04)
------------------

* fix _getBrainByValue to check if value is traversable
  first so we can provide the correct token.
  [vangheem]

1.0.3 (2011-09-24)
------------------

* Add zh_CN translation.
  [jianaijun]

1.0.2 (2011-07-02)
------------------

* Fix regression that broke the browsing with JQuery < 1.4.
  [davisagli]

1.0.1 (2011-05-16)
------------------

* Make placeholder terms for hidden / missing items, so that you can still see
  something in the editing interface and not accidentally remove them. Ideally
  we should say if a page is invisible or missing, but not today.
  [lentinj]

* Use javascript function from plone.formwidget.autocomplete to add new input
  boxes, make javascript as clone-safe (when making new rows in datagridfield)
  as possible
  [lentinj]

* Just use full widget name in ++widget++ URL, don't try and strip form prefix
  off. If within a subform, this is the wrong thing to do and the traverser now
  supports stripping the initial 'form.widgets'
  [lentinj]

* Workaround for sources being used without being bound first.
  [lentinj]

* Check the request for context before falling back to getSite()
  [lentinj]

* Add a UUIDSource that stores plone.uuid pointers to content.
  [lentinj]

* Use tokens as full URL of content, move all token<->value operations into the
  source. Rename methods so that actually-public methods have public names
  [lentinj]

* Alter terms so that token is the full path to an item, value is the path
  without portal_url that is stored in the DB. This means all the path parsing
  can be kept within the source.
  [lentinj]

* _filter is used outside the source, so not an internal helper function
  anymore.
  [lentinj]

1.0 (2011-04-30)
----------------

* Made compatible with Plone 4.1 by loading the permissions.zcml from
  Products.CMFCore (only when plone.app.upgrade is available, to keep
  compatibility with Plone 3, if we currently have that).
  [maurits]

* Improved CSS for selected items to make them more evident in the Sunburst
  theme.
  [davisagli]

* Add content type CSS class to items in the navtree so that icons are shown
  in Plone 4.
  [davisagli]

1.0b3 (2011-02-11)
------------------

* Use `zope.i18n.translate` instead of translation_service, since
  translation_service was removed in plone4.
  [jbaumann]


1.0b2 (2010-08-25)
------------------

* Fall back to the site to perform content-related operations if the
  context is not wrapped into an acquisition chain.
  [dukebody]

* Compute the view name as the request URL left-stripped the content
  absolute URL.
  [dukebody]

* Make it possible to restrict the field to objects below a path
  The constructor of ObjPathSource takes a path keyword argument
  with a PathIndex catalog query. This argument filters objects
  outside of this path. If the navigation_tree_query does not have
  a path argument, the path is also copied into this query.
  [gaudenzius]

* Update widget in the contenttree-fetch browser view
  The widget.update() call rebinds to source which previously
  was only bound during traversal. This avoids problems with
  sources that only work after security is applied.
  [gaudenzius]

1.0b1 - 2010-04-19
------------------

* Adjusted styles so the widget looks reasonable with Plone 4's sunburst theme.
  [davisagli]

* Fix icons in CMF 2.2.  This closes
  http://code.google.com/p/dexterity/issues/detail?id=111
  [davisagli]

* Make the widget work properly on Zope 2.12
  [optilude]

* Add a template for HIDDEN_MODE.
  [csenger]

* Convert all strings in a new navtree node into unicode using the site
  encoding to render non-ascii characters in the widget.
  [csenger]

* Added message IDs for translations and added locales directory with
  german translations.
  [jbaumann]

1.0a5 - 2009-08-02
------------------

* Don't filter children of non-queriable parent types (e.g. Large Plone
  Folders).
  [optilude]

1.0a3 - 2009-07-12
------------------

* Apply patch from Gerhard Weis to make the lightbox play nicer with CSS
  z-indexes.
  [optilude]

1.0a3 - 2009-06-29
------------------

* Fix security validator to work properly on add views and other views using
  namespace traversal (++add++...)
  [optilude]

1.0a2 - 2009-06-28
------------------

* Fix display widgets.
  [optilude]

* Import SitemapNavtreeStrategy conditionally so it doesn't break on Plone
  trunk. [davisagli]

1.0a1 - 2009-04-17
------------------

* Initial release
