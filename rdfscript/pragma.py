from .core import (Node,
                   Name,
                   Assignment)

from .error import FailToImport


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
        context.prefix = self.prefix
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

    def evaluate(self, context):

        uri = self.target.evaluate(context)
        old_prefix = context.prefix

        if not context.eval_import(uri):
            raise FailToImport(self.target, context.get_current_path(), self.location)
        
        context.prefix = old_prefix
        return self.target


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

    def substitute_params(self, parameters):
        for parameter in parameters:
            self._args = [parameter
                          if parameter.is_substitute(arg)
                          else arg
                          for arg in self.args]

    def evaluate(self, context):

        self._args = [arg.evaluate(context) for arg in self.args]
        return self

    def run(self, context, triples):

        self.evaluate(context)
        return context.run_extension_on_triples(self, triples)

    def as_python_object(self, context):

        self.evaluate(context)
        ext_class = context.get_extension(self.name)
        
        return ext_class(*self.args)
