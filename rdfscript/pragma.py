from .core import (Node,
                   Name,
                   Assignment)


class PrefixPragma(Node):

    def __init__(self, prefix, uri, location=None):
        Node.__init__(self, location)

        self._prefix = prefix
        self._uri    = uri

    def __eq__(self, other):
        return (isinstance(other, PrefixPragma) and
                self.prefix == other.prefix and
                self.uri == other.uri)

    def __repr__(self):
        return format("PREFIX DIRECTIVE: (%s, %s)" % (self.prefix, self.uri))

    @property
    def prefix(self):
        return self._prefix

    @property
    def uri(self):
        return self._uri

    def evaluate(self, context):

        Assignment(Name(self.prefix, location=self.location), self.uri).evaluate(context)
        context.bind_prefix(self.prefix, self.uri.evaluate(context))
        return Name(self.prefix, location=self.location)


class DefaultPrefixPragma(Node):

    def __init__(self, prefix, location=None):
        Node.__init__(self, location)

        self._prefix = prefix

    def __eq__(self, other):
        return (isinstance(other, DefaultPrefixPragma) and
                self.prefix == other.prefix)

    def __repr__(self):
        return format("DEFAULTPREFIX DIRECTIVE: (%s)" % self.prefix)

    @property
    def prefix(self):
        return self._prefix

    def evaluate(self, context):
        context.set_default_prefix(self.prefix)
        return Name(self.prefix, location=self.location)


class ImportPragma(Node):

    def __init__(self, target, location=None):
        Node.__init__(self, location)

        self._target =  target

    def __eq__(self, other):
        return (isinstance(other, ImportPragma) and
                self.target == other.target)

    def __repr__(self):
        return format("[IMPORT DIRECTIVE: %s]" % self.target)

    @property
    def target(self):
        return self._target


class ExtensionPragma(Node):

    def __init__(self, name, args, location=None):
        Node.__init__(self, location)
        self._name = name
        self._args = args

    def __eq__(self, other):
        return (isinstance(other, ExtensionPragma) and
                self.name == other.name and
                self.args == other.args)

    def __repr__(self):
        return format("@extension %s(%s)" % (self.name, self.args))

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    def parameterise(self, parameters):
        for param in parameters:
            if self.name == param.name:
                self._name = param

            self._args = [param if arg == param.name
                          else arg
                          for arg in self.args]

    def evaluate(self, context):

        self._args = [arg.evaluate(context) for arg in self.args]
        return self
