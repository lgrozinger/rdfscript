import rdfscript.error as error
import rdfscript.core as core

class UsingPragma(core.Node):

    def __init__(self, prefix, location=None):
        core.Node.__init__(self, location)
        self._prefix = prefix

    def __eq__(self, other):
        return (isinstance(other, UsingPragma) and
                self.prefix == other.prefix)

    def __str__(self):
        return format("using %s" % self.prefix)

    def __repr__(self):
        return format("USING DIRECTIVE: %s" % self.prefix)

    @property
    def prefix(self):
        return self._prefix


class PrefixPragma(core.Node):

    def __init__(self, prefix, uri, location=None):
        core.Node.__init__(self, location)
        self._prefix = prefix
        self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, PrefixPragma) and
                self.prefix == other.prefix and
                self.uri == other.uri)

    def __str__(self):
        return format("@prefix %s = %s" % (self.prefix, self.uri))

    def __repr__(self):
        return format("PREFIX DIRECTIVE: (%s, %s)" % (self.prefix, self.uri))

    @property
    def prefix(self):
        return self._prefix

    @property
    def uri(self):
        return self._uri


class DefaultPrefixPragma(core.Node):

    def __init__(self, prefix, location=None):
        core.Node.__init__(self, location)
        self._prefix = prefix

    def __eq__(self, other):
        return (isinstance(other, DefaultPrefixPragma) and
                self.prefix == other.prefix)

    def __str__(self):
        return format("@prefix %s" % self.prefix)

    def __repr__(self):
        return format("DEFAULTPREFIX DIRECTIVE: (%s)" % self.prefix)

    @property
    def prefix(self):
        return self._prefix


class ImportPragma(core.Node):

    def __init__(self, target, location=None):
        core.Node.__init__(self, location)
        self._target = target

    def __eq__(self, other):
        return (isinstance(other, ImportPragma) and
                self.target == other.target)

    def __str__(self):
        return format("@import %s" % self.target)

    def __repr__(self):
        return format("[IMPORT DIRECTIVE: %s]" % self.target)

    @property
    def target(self):
        return self._target


class ExtensionPragma(core.Node):

    def __init__(self, name, args, location=None):
        core.Node.__init__(self, location)
        self._name = name
        self._args = args

    def __eq__(self, other):
        return (isinstance(other, ExtensionPragma) and
                self.name == other.name and
                self.args == other.args)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return format("@extension %s(%s)" % (self.name, self.args))

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    def substitute_params(self, parameters):
        for parameter in parameters:
            self._args = [parameter
                          if parameter.is_substitute(arg)
                          else arg
                          for arg in self.args]

    def run(self, context, triples):
        self.evaluate(context)
        return context.run_extension_on_triples(self, triples)

    def as_python_object(self, context):

        self.evaluate(context)
        ext_class = context.get_extension(self.name)

        return ext_class(*self.args)
