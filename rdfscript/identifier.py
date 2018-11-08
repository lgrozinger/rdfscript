import rdflib

from urllib.parse import quote as urlencode

from rdfscript.toplevel import ScriptObject

class Identifier(ScriptObject):
    def __init__(self, line_num):
        super().__init__(line_num)

class URI(Identifier):

    def __init__(self, quoted_uri, line_num):
        super().__init__(line_num)

        self.uri = quoted_uri

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.uri == other.uri)

    def __repr__(self):
        return format("URI: %s" % self.uri)

    def evaluate(self, env):
        return rdflib.URIRef(self.uri)

## as in RDF/XML LocalName
## evaluates to rdflib.URIRef('name')
class LocalName(Identifier):
    def __init__(self, name, line_num):
        super().__init__(line_num)
        self.name = name

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.name == other.name)

    def __repr__(self):
        return format("(LOCALNAME: %s)" % self.name)

    def resolve(self, env):

        uri = env.resolve_name(self.name)
        uri.n3()

        return uri

    def evaluate(self, env):

        ## here is lookup
        uri = self.resolve(env)

        return env.lookup(uri)


## as in RDF/XML QName
## evaluates to a rdflib.URIRef
class QName(Identifier):
    def __init__(self, prefix, localname, line_num):
        super().__init__(line_num)

        self.prefix    = prefix
        self.localname = localname

        ## have to hold off on getting a URIRef, since the full name
        ## might depend on env at the exact time of evaluation

    def __eq__(self, other):
        return (type(self) == type(other)         and
                self.prefix == other.prefix       and
                self.localname == other.localname)

    def __repr__(self):
        return format("QNAME: %s : %s" % (self.prefix, self.localname))

    def resolve(self, env):

        uri = env.resolve_name(self.localname, prefix=self.prefix)
        uri.n3()

        return uri

    def evaluate(self, env):

        uri = self.resolve(env)

        return env.lookup(uri)
