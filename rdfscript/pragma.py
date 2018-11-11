import rdflib

from .core import Node

class PrefixPragma(Node):

    def __init__(self, prefix, uri, location):
        super().__init__(location)

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

    def evaluate(self, env):

        prefixuri = self.uri.evaluate(env)
        return env.bind_prefix(self.prefix, prefixuri)

class DefaultPrefixPragma(Node):

    def __init__(self, prefix, location):
        super().__init__(location)

        self._prefix = prefix

    def __eq__(self, other):
        return (isinstance(other, DefaultPrefixPragma) and
                self.prefix == other.prefix)

    def __repr__(self):
        return format("DEFAULTPREFIX DIRECTIVE: (%s)" % self.prefix)

    @property
    def prefix(self):
        return self._prefix

    def evaluate(self, env):

        return None

class ImportPragma(Node):

    def __init__(self, target, location):
        super().__init__(location)

        self._target =  target

    def __eq__(self, other):
        return (isinstance(other, ImportPragma) and
                self.target == other.target)

    def __repr__(self):
        return format("IMPORT DIRECTIVE: %s)" % self.target)

    @property
    def target(self):
        return self._target

    def evaluate(self, env):

        return None
