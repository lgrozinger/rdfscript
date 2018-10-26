import rdflib
from urllib.parse import quote as urlencode

class ScriptObject:

    def __init__(self, line_num):
        self.line = line_num

    def __eq__(self, other):
        return self is other

## represents an RDF statement
## a TripleObject evaluates to a rdflib.URIRef, i.e. a node in the rdf
## graph
class TripleObject(ScriptObject):

    def __init__(self, s, p, o, line_num):
        super().__init__(line_num)

        self.s = s
        self.p = p
        self.o = o

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.s == other.s         and
                self.p == other.p         and
                self.o == other.o)

    def __repr__(self):
        return format("TRIPLE: (%s, %s, %s)" % (self.s, self.p, self.o))

    def evaluate(self, env):

        ## first evaluate subject, object and predicate
        subject   = self.s.evaluate(env)
        objekt    = self.o.evaluate(env)
        predicate = self.p.evaluate(env)

        ## TODO: type checking on sub, obj, pred

        env.add_triple(subject, predicate, objekt)

        return subject

class Term(ScriptObject):

    def __init__(self, line_num):
        super().__init__(line_num)

class Literal(Term):

    def __init__(self, lexical_value, line_num):
        super().__init__(line_num)
        self.value = rdflib.Literal(lexical_value)

        self.datatype = self.value.datatype

    def __eq__(self, other):
        return self.value == other.value

    def evaluate(self, env):
        return self.value

class URI(Term):

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

class Identifier(ScriptObject):
    def __init__(self, line_num):
        super().__init__(line_num)

## as in RDF/XML LocalName
## evaluates to a rdflib.URIRef
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
        ## limited check for valid URI

        ## TODO: default prefix
        self.URI = rdflib.term.URIRef(self.name.evaluate(env))
        self.URI.n3()

        return self.URI;

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

        namespace = self.prefix.evaluate(env)
        localname = self.localname.evaluate(env)

        return rdflib.term.URIRef(namespace[localname.toPython()])

class Symbol(ScriptObject):
    def __init__(self, name, line_num):
        super().__init__(line_num)

        self.name = name

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.name == other.name)

    def __repr__(self):
        return "SYMBOL: " + str(self.name)

    def evaluate(self, env):
        return env.symbol_lookup(self.name)
