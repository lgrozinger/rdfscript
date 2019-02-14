import rdflib
import re

import rdfscript.error as error

__lang__ = "https://github.com/lgrozinger/rdfscript/lang/"


def lang_uri(obj):
    return Uri(__lang__ + obj.__class__.__name__)


def params_uri(index):
    return Uri(__lang__ + 'param_' + str(index))


def triple_uri(onetwoorthree):
    return Uri(__lang__ + '_' + str(onetwoorthree))


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


class Two(Node):

    def __init__(self, one, two, location=None):
        Node.__init__(self, location)
        self._one = one
        self._two = two

    def __eq__(self, other):
        return (isinstance(other, Two) and
                self.one == other.one and
                self.two == other.two)

    def __repr__(self):
        return format("Two(%s, %s)" % (self.one, self.two))

    def __str__(self):
        return format("%s > %s" % (self.one, self.two))

    @property
    def one(self):
        return self._one

    @property
    def two(self):
        return self._two

    def evaluate(self, context):
        e_one = self.one.evaluate(context)
        e_two = self.two.evaluate(context)
        return context.lookup_property(e_one, e_two)


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

    def __repr__(self):
        return format("Three(%s,%s,%s)" % (self.one,
                                           self.two,
                                           self.three))

    def __str__(self):
        return format("%s > %s > %s" % (self.one, self.two, self.three))

    @property
    def one(self):
        return self._one

    @property
    def two(self):
        return self._two

    @property
    def three(self):
        return self._three

    def map(self, f):
        self._one = f(self.one)
        self._two = f(self.two)
        self._three = f(self.three)

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
        for name in names[1:]:
            type_assert(name, Uri, str, Self)

    def __eq__(self, other):
        return ((isinstance(other, Name) and
                 self.names == other.names) or
                (isinstance(other, Self) and
                 self.names == [Self()]))

    def __str__(self):
        return '.'.join([str(name) for name in self.names])

    def __repr__(self):
        return format("Name(%s)" % (self.names))

    @property
    def names(self):
        return self._names

    def concrete_p(self, context):
        return not Self() in self.names or context.concrete_self_p()

    def bound_p(self, context):

        if not self.concrete_p(context):
            return False

        roots = context.namespaces
        for root in roots:
            current = root

            for i in range(0, len(self.names)):
                name = self.names[i]
                type_assert(current, Uri)
                type_assert(name, str, Self, Uri)

                if isinstance(name, (Uri, str)):
                    concrete_name = Uri(name)
                else:
                    concrete_name = context.concrete_self_p()

                hit = context.lookup_property(current, concrete_name)

                if hit is None:
                    break
                else:
                    type_assert(hit, Uri, Value)
                    current = hit
                    if i == len(self.names) - 1:
                        return hit

        return False

    def get_prefix(self, context):
        prefix = self.names[0]

        if isinstance(prefix, Uri):
            prefix = Uri(prefix.uri)
            self.names.pop(0)
        elif isinstance(prefix, Self):
            prefix = Uri(context.current_self)
            self.names.pop(0)
        elif context.prefix is not None:
            prefix = context.uri_for_prefix(context.prefix)
        else:
            prefix = Uri(prefix)
            self.names.pop(0)

        return prefix

    def pop_prefix(self, context):
        prefix = self.names[0]

        if isinstance(prefix, Uri):
            prefix = Uri(prefix.uri)
            self.names.pop(0)
        elif isinstance(prefix, Self):
            prefix = Uri(context.current_self)
            self.names.pop(0)
        elif context.prefix is not None:
            prefix = context.uri_for_prefix(context.prefix)
        else:
            prefix = Uri(prefix)
            self.names.pop(0)

        return prefix

    def resolve(self, context):
        result = False
        names = [name for name in self.names]
        leftover_names = []
        while not result and names:
            leftover_names.insert(0, names.pop())
            result = Name(*names).bound_p(context)
            if not isinstance(result, Uri):
                result = False

        leftover_name = Name(*leftover_names)
        if not result:
            result = leftover_name.pop_prefix(context)

        for name in leftover_name.names:
            type_assert(name, Uri, str, Self)
            if isinstance(name, Self):
                name_uri = context.current_self
            else:
                name_uri = Uri(name)

            result.extend(name_uri, delimiter='')

        return result

    def evaluate(self, context):

        result = False
        if self.concrete_p(context):
            result = self.bound_p(context)
        else:
            result = self

        return result or self.resolve(context)


class Uri(Node):

    def __init__(self, uri, location=None):
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
        return format("Uri(%s)" % self._uri)

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
        return format("Value(%s)" % self.value)

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
        type_assert(name, Name)
        self._name = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __str__(self):
        return format("%s = %s" % (self.name, self.value))

    def __repr__(self):
        return format("Assignment(%s, %s)" %
                      (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


def type_assert(this_is, *of_type):
    if isinstance(this_is, of_type):
        return True
    else:
        try:
            raise error.UnexpectedType(of_type, this_is, this_is.location)
        except AttributeError:
            raise error.UnexpectedType(of_type, this_is, None)
