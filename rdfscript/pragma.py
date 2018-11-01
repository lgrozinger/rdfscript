import rdflib

from rdfscript.toplevel import ScriptObject, Assignment

class PrefixPragma(ScriptObject):

    def __init__(self, prefix, uri, line_num):
        super().__init__(line_num)

        self.prefix = prefix
        self.uri    = uri

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.prefix == other.prefix and
                self.uri == other.uri)

    def __repr__(self):
        return format("PREFIX DIRECTIVE: (%s, %s)" % (self.prefix, self.uri))

    def evaluate(self, env):

        prefixuri = self.uri.evaluate(env)
        env.bind_prefix(self.prefix, prefixuri)

        return env.get_ns_for_prefix(self.prefix)

class DefaultPrefixPragma(ScriptObject):

    def __init__(self, prefix, line_num):
        super().__init__(line_num)

        self.prefix = prefix

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.prefix == other.prefix)

    def __repr__(self):
        return format("DEFAULTPREFIX DIRECTIVE: (%s)" % self.prefix)

    def evaluate(self, env):

        return None

class ImportPragma(ScriptObject):

    def __init__(self, target, line_num):
        super().__init__(line_num)

        self.target =  target

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.target == other.target)

    def __repr__(self):
        return format("IMPORT DIRECTIVE: %s)" % self.target)

    def evaluate(self, env):

        return None
