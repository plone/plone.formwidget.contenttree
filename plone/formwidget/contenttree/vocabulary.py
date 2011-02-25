from zope.interface import implements

from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm

class BrainTerm(object):
    """Term that can also contain a brain object"""

    implements(ITitledTokenizedTerm)

    def __init__(self, brain, token=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.  If title is provided, 
        term implements ITitledTokenizedTerm.
        """
        self.brain = brain
        self.title = brain.Title
        if token is None:
            self.token = self.value = str(brain.UID)
        else:
            self.value = token
            self.token = str(token)
