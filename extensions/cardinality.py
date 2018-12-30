import rdflib
from .error import ExtensionError

class AtLeastOne:

    def __init__(self, property_uri):
        self._prop = property_uri

    def run(self, triplepack):

        subjects = triplepack.subjects
        if len(subjects) > 0:
            for subject in subjects:
                if not triplepack.has(subject, self._prop):
                    raise CardinalityError(self._prop, 'at least 1', 'none')
        else:
            raise CardinalityError(self._prop, 'at least 1', 'none')
                    
        return triplepack

class CardinalityError(ExtensionError):

    def __init__(self, predicate, expected, actual):
        ExtensionError.__init__(self)
        self._type = 'Cardinality restriction violation'
        self._predicate = predicate
        self._expected = expected
        self._actual = actual

    def __str__(self):
        return (ExtensionError.__str__(self) +
                format(" Expected %s value(s) for %s, but actually got %s\n"
                       % (self._expected, self._predicate, self._actual)))
