import rdflib

from urllib.parse import quote as urlencode

from rdfscript.objects import ScriptObject

class Identifier(ScriptObject):
    def __init__(self, line_num):
        super().__init__(line_num)

class URI(Identifier):

    def __init__(self, quoted_uri, line_num):
        super().__init__(line_num)

        self.uri = urlencode(quoted_uri)

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.uri == other.uri)

    def __repr__(self):
        return format("URI: %s" % self.uri)

    def evaluate(self, env):
        return self.uri

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

    def evaluate(self, env):
        return rdflib.URIRef(urlencode(self.name))

## as in RDF/XML NSPrefix
## evaluates to a rdflib.Namespace
class NSPrefix(Identifier):
    def __init__(self, namespace, line_num):
        super().__init__(line_num)

        self.namespace = namespace

    def __eq__(self, other):
        return (type(self) == type(other)         and
                self.namespace == other.namespace)

    def __repr__(self):
        return format("(NSPREFIX: %s)" % self.namespace)

    def evaluate(self, env):
        return rdflib.Namespace(self.namespace.evaluate(env))

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

    def evaluate(self, env):
        ## construct the fully-qualified URI from the prefix and local
        ## parts

        ## TODO: default prefix directive (pragma)
        ## by adding check for 'None' prefix
        if not self.prefix:
            namespace = env.get_default_namespace()
        else:
            namespace = self.prefix.evaluate(env)

        localname = self.localname.evaluate(env)

        uri = rdflib.term.URIRef(namespace[localname.toPython()])
        uri.n3()

        return uri
