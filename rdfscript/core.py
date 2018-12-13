import rdflib
import re

from .error import PrefixError

class Node(object):
    """Language object superclass."""
    def __init__(self, location):
        """
        location is a Location object representing this language
        object's position in the source code.
        """
        self._location = location

    @property
    def location(self):
        return self._location

    @property
    def line(self):
        return self._location.position.line

    @property
    def col(self):
        return self._location.position.col

    @property
    def position(self):
        return self._location.position

    @property
    def file(self):
        return self._location.filename

class Name(Node):

    def __init__(self, *names, location=None):

        Node.__init__(self, location)
        self._names = list(names)

    def __eq__(self, other):
        return (isinstance(other, Name) and
                self.names == other.names)

    def __repr__(self):
        return format("[NAME: %s]" % (self.names))

    @property
    def names(self):
        return self._names

    # def prefixify(self, prefix):
    #     if not self._prefix:
    #         self._prefix = prefix

    def evaluate(self, context):
        uri = Uri('')
        for name in self.names:
            if isinstance(name, Self):
                uri.extend(context.self_uri, delimiter='')
            elif isinstance(name, Uri):
                uri.extend(name, delimiter='')
            elif isinstance(name, str):
                uri.extend(Uri(name), delimiter='')

            uri = context.lookup(uri) or uri

        return uri

class Uri(Node):
    """Language object for a URI."""

    def __init__(self, uri, location=None):
        """
        uri can be one of:
          - string
          - rdflib.URIRef object
          - Uri object

        uri is converted to a string
        """
        Node.__init__(self, location)
        if isinstance(uri, rdflib.URIRef):
            self._uri = uri.toPython()
        elif isinstance(uri, Uri):
            self._uri = uri.uri
        else:
            self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, Uri) and
                self.uri == other.uri)

    def __repr__(self):
        return format("[URI: %s]" % self._uri)

    def __hash__(self):
        return self.uri.__hash__()

    @property
    def uri(self):
        return self._uri

    def extend(self, other, delimiter='#'):
        self._uri = self.uri + delimiter + other.uri

    def split(self):
        return re.split('#|/|:', self.uri)

    def evaluate(self, context):
        return self

class Value(Node):
    """Language object for an RDF literal."""

    def __init__(self, python_literal, location=None):

        Node.__init__(self, location)
        self._python_val = python_literal

    def __eq__(self, other):
        return (isinstance(other, Value) and
                self.value == other.value)

    def __repr__(self):
        return format("[VALUE: %s]" % self.value)

    def __hash__(self):
        return self._python_val.__hash__()

    @property
    def value(self):
        return self._python_val

    def evaluate(self, context):
        return self.value

class Self(Node):

    def __init__(self, location=None):
        Node.__init__(self, location)

    def __eq__(self, other):
        return isinstance(other, Self)

    def __repr__(self):
        return format("[SELF]")

    def evaluate(self, context):
        return context.self_uri
