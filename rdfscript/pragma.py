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