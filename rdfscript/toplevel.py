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

class Assignment(ScriptObject):

    def __init__(self, identifier, value, line_num):
        super().__init__(line_num)

        self.identifier = identifier
        self.value      = value

    def __eq__(self, other):
        return (type(self) == type(other)           and
                self.identifier == other.identifier and
                self.value == other.value)

    def __repr__(self):
        return format("ASSIGN: (%s to %s)" %
                      (self.identifier, self.value))

    def evaluate(self, env):

        assignment_predicate = env.get_assignment_uri()

        env.add_triple(self.identifier.evaluate(env),
                       assignment_predicate,
                       self.value.evaluate(env))

        return self.value.evaluate(env)
