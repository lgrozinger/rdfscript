import rdflib

from .error import PrefixError

class Node(object):

    def __init__(self, location):

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

    def __init__(self, prefix_string, localname_string, location):

        Node.__init__(self, location)
        self._prefix = prefix_string
        self._localname = localname_string

    def __eq__(self, other):
        return (isinstance(other, Name) and
                self.prefix == other.prefix and
                self.localname == other.localname)

    def __repr__(self):
        return format("[NAME: %s.%s]" % (self.prefix, self.localname))

    @property
    def prefix(self):
        return self._prefix

    @property
    def localname(self):
        return self._localname

    def prefixify(self, prefix):
        if not self._prefix:
            self._prefix = prefix

    def as_uri(self, env):
        return Uri(env.resolve_name(self._prefix, self._localname).toPython(),
                   self.location)

class Uri(Node):
    """Env's abstraction of a URI"""

    def __init__(self, uri_string, location):

        Node.__init__(self, location)
        if isinstance(uri_string, rdflib.URIRef):
            self._uri = uri_string.toPython()
        else:
            self._uri = uri_string

    def __eq__(self, other):
        return (isinstance(other, Uri) and
                self.uri == other.uri)

    def __repr__(self):
        return format("[URI: %s]" % self._uri)

    @property
    def uri(self):
        return self._uri

    def as_uriref(self):
        return rdflib.URIRef(self._uri)

class Value(Node):
    """Env's abstraction of a literal node in the RDF graph."""

    def __init__(self, python_literal, location):

        Node.__init__(self, location)
        self._python_val = python_literal

    def __eq__(self, other):
        return (isinstance(other, Value) and
                self.as_pythonval() == other.as_pythonval())

    def __repr__(self):
        return format("[VALUE: %s]" % self.as_pythonval())

    def as_pythonval(self):

        return self._python_val

    def as_rdfliteral(self):

        return rdflib.Literal(self._python_val)

class Self(Node):

    def __init__(self, location):

        Node.__init__(self, location)

    def __eq__(self, other):
        return isinstance(other, Self)

    def __repr__(self):
        return format("[SELF]")
