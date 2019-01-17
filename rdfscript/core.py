import rdflib
import re

import rdfscript.error as error


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


class Two(Node):

    def __init__(self, one, two, location=None):
        Node.__init__(self, location)
        self._one = one
        self._two = two

    def __eq__(self, other):
        return (isinstance(other, Two) and
                self.one == other.one and
                self.two == other.two)

    @property
    def one(self):
        return self._one

    @property
    def two(self):
        return self._two


class Three(Node):

    def __init__(self, one, two, three, location=None):
        Node.__init__(self, location)
        self._one = one
        self._two = two
        self._three = three

    def __eq__(self, other):
        return (isinstance(other, Three) and
                self.one == other.one and
                self.two == other.two and
                self.three == other.three)

    @property
    def one(self):
        return self._one

    @property
    def two(self):
        return self._two

    @property
    def three(self):
        return self._three

    def evaluate(self, context):
        e_one = self.one.evaluate(context)
        e_two = self.two.evaluate(context)
        e_three = self.three.evaluate(context)

        type_assert(e_one, Uri)
        type_assert(e_two, Uri)

        context.add_triples([(e_one, e_two, e_three)])
        return e_one


class Name(Node):

    def __init__(self, *names, location=None):

        Node.__init__(self, location)
        self._names = list(names)

    def __eq__(self, other):
        return ((isinstance(other, Name) and
                 self.names == other.names) or
                (isinstance(other, Self) and
                 self.names == [Self()]))

    def __str__(self):
        return ':'.join([str(name) for name in self.names])

    def __repr__(self):
        return format("[NAME: %s]" % (self.names))

    @property
    def names(self):
        return self._names

    def is_prefixed(self, context):
        if len(self.names) > 1 and isinstance(self.names[0], str):
            try:
                return context.uri_for_prefix(self.names[0])
            except error.PrefixError:
                return False
        else:
            return False

    def evaluate(self, context):

        uri = Uri(context.uri, location=self.location)

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
                        return Name(*rest, location=self.location)
            elif isinstance(self.names[n], Uri):
                if n > 0:
                    uri.extend(self.names[n], delimiter='')
                else:
                    uri = Uri(self.names[n])
            elif isinstance(self.names[n], str):
                if n == 0 and self.is_prefixed(context):
                    uri = self.is_prefixed(context)
                else:
                    uri.extend(Uri(self.names[n]), delimiter='')

            lookup = context.lookup(uri)
            if lookup is not None:
                if isinstance(lookup, Uri):
                    uri = Uri(lookup, location=self.location)
                elif n == len(self.names) - 1:
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

    def __str__(self):
        return '<' + self.uri + '>'

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
                isinstance(other.value, type(self.value)) and
                self.value == other.value)

    def __str__(self):
        return format("%r" % self.value)

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

    def __str__(self):
        return "self"

    def __repr__(self):
        return format("[SELF]")

    def evaluate(self, context):
        return context.current_self


class Assignment(Node):

    def __init__(self, name, value, location=None):

        Node.__init__(self, location)
        self._name = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __str__(self):
        return format("%s = %s" % (self.name, self.value))

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
        Three(self.name,
              identity,
              self.value,
              location=self.location).evaluate(context)

        return self.value


def type_assert(this_is, of_type):
    if not isinstance(this_is, of_type):
        try:
            raise error.UnexpectedType(of_type, this_is, this_is.location)
        except AttributeError:
            raise error.UnexpectedType(of_type, this_is, None)
    return True


def param_number(i):
    assert isinstance(i, type(1))
    param = 'http://github.com/lgrozinger/rdfscript/lang/param/'
    return Uri(param + str(i))


identity = Uri('http://github.com/lgrozinger/rdfscript/lang/is')
