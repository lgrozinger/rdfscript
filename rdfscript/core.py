import rdflib
import re

from .error import PrefixError

class Node(object):
    """Language object."""
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
        return ((isinstance(other, Name) and
                 self.names == other.names) or
                (isinstance(other, Self) and
                 self.names == [Self()]))

    def __repr__(self):
        return format("[NAME: %s]" % (self.names))

    @property
    def names(self):
        return self._names

    def evaluate(self, context):
        uri = Uri(context.default_prefix, location=self.location)
        for n in range(0, len(self.names)):
            if isinstance(self.names[n], Self):
                current_self = context.current_self
                if isinstance(current_self, Uri):
                    if n > 0:
                        uri.extend(context.current_self, delimiter='')
                    else:
                        uri = Uri(current_self, location=self.location)
                elif isinstance(current_self, Name):
                    rest = current_self.names + self.names[n + 1:]
                    if n > 0:
                        return Name(uri, *rest, location=self.location)
                    else:
                        return Name(*rest, location= self.location)
            elif isinstance(self.names[n], Uri):
                if n > 0:
                    uri.extend(self.names[n], delimiter='')
                else:
                    uri = Uri(self.names[n])
            elif isinstance(self.names[n], str):
                uri.extend(Uri(self.names[n]), delimiter='')

            lookup = context.lookup(uri)
            if lookup is not None:
                if isinstance(lookup, Uri):
                    uri = Uri(lookup, location=self.location)
                else:
                    uri = lookup

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
                type(self.value) == type(other.value) and
                self.value == other.value)

    def __repr__(self):
        return format("[VALUE: %s]" % self.value)

    def __hash__(self):
        return self._python_val.__hash__()

    @property
    def value(self):
        return self._python_val

    def evaluate(self, context):
        return self

class Self(Node):

    def __init__(self, location=None):
        Node.__init__(self, location)

    def __eq__(self, other):
        return (isinstance(other, Self) or
                (isinstance(other, Name) and
                 other.names == [Self()]))

    def __repr__(self):
        return format("[SELF]")

    def evaluate(self, context):
        return context.current_self

class Assignment(Node):

    def __init__(self, name, value, location=None):

        Node.__init__(self, location)
        self._name  = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __repr__(self):
        return format("[ASSIGN: %s = %s]" %
                      (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def evaluate(self, context):
        uri = self.name.evaluate(context)
        if not isinstance(uri, Uri):
            raise UnexpectedType(Uri, type(uri), self.location)

        value = self.value.evaluate(context)

        context.assign(uri, value)
        return value
