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

class Prefix(Node):
    """Language object for the 'prefix' part of a Name."""

    def __init__(self, uri_or_string , location):

        Node.__init__(self, location)
        self._identity = uri_or_string

    def __eq__(self, other):
        return (isinstance(other, Prefix) and
                self._identity == other._identity)

    def __repr__(self):
        return format("%s" % self._identity)

    @property
    def identity(self):
        return self._identity

    def uri(self, env):
        if isinstance(self._identity, Uri):
            return self._identity
        else:
            return env.uri_for_prefix(self)

    @property
    def string(self):
        if isinstance(self._identity, Uri):
            return self._identity.uri
        else:
            return self._identity


class LocalName(Node):
    """Language object for the local part of a Name."""

    def __init__(self, uri_or_string, location):

        Node.__init__(self, location)
        self._identity = uri_or_string

    def __eq__(self, other):
        return (isinstance(other, LocalName) and
                self._identity == other._identity)

    def __repr__(self):
        return format("%s" % self._identity)

    @property
    def identity(self):
        return self._identity

    def uri(self, env):
        return Uri(self.identity, self.location)

    @property
    def string(self):
        if isinstance(self._identity, Uri):
            return self._identity.uri
        else:
            return self._identity

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

    def prefixify(self, prefix):
        if not self._prefix:
            self._prefix = prefix

    def uri(self, env):
        return env.resolve_name(self)

class Uri(Node):
    """Language object for a URI."""

    def __init__(self, uri, location=None):
        """
        uri can be one of:
          - string
          - rdflib.URIRef object
          - rdflib.Namespace object
          - Uri object

        uri is converted to a string
        """
        Node.__init__(self, location)
        if isinstance(uri, rdflib.URIRef):
            self._uri = uri.toPython()
        elif isinstance(uri, rdflib.Namespace):
            self._uri = rdflib.URIRef(uri).toPython()
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

class Value(Node):
    """Language object for an RDF literal."""

    def __init__(self, python_literal, location):

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

class Self(Node):

    def __init__(self, location=None):
        Node.__init__(self, location)

    def __eq__(self, other):
        return isinstance(other, Self)

    def __repr__(self):
        return format("[SELF]")

    def uri(self, env):
        return Name(None, self.localname, self.location).uri(env)
