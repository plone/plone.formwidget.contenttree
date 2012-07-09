from zope.interface import Interface, Attribute
from zope import schema

from z3c.formwidget.query.interfaces import IQuerySource


class IContentFilter(Interface):
    """A filter that specifies what content is addable, where
    """

    criteria = Attribute("A dict with catalog search parameters")

    def __call__(self, brain, index_data):
        """Return True or False depending on whether the given brain, which
        was found from the given index data (a dict), should be included.
        """


class IContentSource(IQuerySource):
    """A source that can specify content. The generated terms should have
       tokens that are URLs to the content, since these are used to create
       links.
    """

    navigation_tree_query = Attribute(
        "A dict to pass to portal_catalog when "
        "searching for items to display. This dictates "
        "how the tree is structured, and also provides an "
        "upper bound for items allowed by the source."
    )

    selectable_filter = schema.Object(
        title=u"Filter",
        description=u"The filter will be applied to any returned search results",
        schema=IContentFilter
    )

    def isBrainSelectable(self, brain):
        """Return True iff the brain represents a page that can be selected
        in the navigation tree. Base implementation should be sufficient
        """

    def getTermByBrain(self, brain, real_value=True):
        """Given a brain, generate a Term that represents this brain
        """


class IContentTreeWidget(Interface):
    """Marker interface for the content tree widget
    """
