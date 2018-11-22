import rdflib

from .error import PrefixError

class Node:

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
    """Env's abstraction of a identifier node in the RDF graph."""

    def __init__(self, prefix, localname, location):

        super().__init__(location)
        self._prefix = prefix
        self._localname = localname

    def __eq__(self, other):
        return (isinstance(other, Name) and
                self.prefix == other.prefix and
                self.localname == other.localname)

    def __repr__(self):
        return format("<RDFscript NAME: <%s%s> >" % (self.prefix, self.localname))

    @property
    def prefix(self):
        return self._prefix

    @property
    def localname(self):
        return self._localname

    def as_uri(self):
        prefix = self._prefix or ''
        localname = self._localname or ''
        return Uri(prefix + localname, self.location)

class Uri(Node):
    """Env's abstraction of a URI"""

    def __init__(self, uri, location):

        super().__init__(location)
        self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, Uri) and
                self.uri == other.uri)

    def __repr__(self):
        return format("<RDFscript URI: %s>" % self._uri)

    @property
    def uri(self):
        return self._uri

    def as_uriref(self):
        return rdflib.URIRef(self._uri)

class Value(Node):
    """Env's abstraction of a literal node in the RDF graph."""

    def __init__(self, python_literal, location):

        super().__init__(location)
        self._python_val = python_literal

    def __eq__(self, other):
        return (isinstance(other, Value) and
                self.as_pythonval() == other.as_pythonval())

    def __repr__(self):
        return format("<RDFscript VALUE: %s>" % self.as_pythonval())

    def as_pythonval(self):

        return self._python_val

    def as_rdfliteral(self):

        return rdflib.Literal(self._python_val)

class Parameter:
    """Env's abstraction of a RDF BNode for a template parameter."""

    def __init__(self, parameter_name):

        self._param_name = parameter_name
        self._binding    = rdflib.BNode()

    @property
    def name(self):
        return self._param_name

    @property
    def binding(self):
        return self._binding

    def __eq__(self, other):
        return (isinstance(other, Parameter) and
                self.name == other.name)

    def __repr__(self):
        return format("<RDFscript PARAMETER: %s>" % self.name)

    def as_rdfbnode(self):
        return self._binding

    def isBound(self):
        return not isinstance(self._binding, rdflib.BNode)

    def bind(self, binding):
        self._binding = binding
