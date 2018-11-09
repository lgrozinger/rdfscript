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

        env.assign(self.identifier.resolve(env),
                   self.value.evaluate(env))

        return self.value.evaluate(env)

class ConstructorDef(ScriptObject):

    def __init__(self, base, identifier, param_names, body, linenum):
        super().__init__(linenum)
        self.params = dict([(localname.name, rdflib.BNode())
                            for localname
                            in param_names])

        self.identifier = identifier
        self.body = body

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.identifier == other.identifier and
                self.params == other.params and
                self.body == other.body)

    def __repr__(self):
        return format("CONSTRUCTORDEF: (%s, with args: %s)" %
                      (self.identifier, self.params))

    def template_ns(self, env):
        return rdflib.Namespace(self.identifier.resolve(env))

    def param_uri(self, name, env):
        return rdflib.URIRef(self.template_uri(env)['parameter/' + name])

    def param_triple(self, param, env):
        return (rdflib.URIRef(self.template_ns(env)),
                self.param_uri(self.template_ns(env), param),
                self.params[param])

    def body_triple(self, form):

        if type(form) == type(Assignment(None, None, 0)):
            return self.property_triple(form, env)
        elif type(form) == type(InstanceExp(None, None, 0)):
            return None
        else:
            return None

    def property_triple(self, assignment, env):

        s = rdflib.URIRef(self.template_ns(env))
        p = None
        o = None

        # check for parameters in the assignment identifier
        if (type(assignment.identifier)==type(LocalName(None,None,0))
            and assignment.identifier.name in self.params):

            ## then the predicate points to a parameter
            p = self.params[assignment.identifier.name]
        else:
            p = assignment.identifier.evaluate(env)
            if not p:
                p = assignment.identifier.resolve(env)

        # check for parameters in the assignment value
        if (type(assignment.value)==type(LocalName(None,None,0))
            and assignment.value.name in self.params):

            ## then the object points to a parameter
            o = self.params[assignment.value.name]
        else:
            o = assignment.identifier.resolve(env)

        return (s, p, o)

    def evaluate(self, env):

        param_triples = [self.param_triple(param, env) for param in self.params]

        body_triples = [self.body_triple(form) for form in self.body]

        env.put_template(param_triples + body_triples)

        return self.template_ns(env)


class InstanceExp(ScriptObject):

    def __init__(self, identifier, constructorapp, linenum):
        super().__init__(linenum)

        self.identifier = identifier
        self.constructorapp = constructorapp

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.identifier == other.identifier and
                self.constructorapp == other.constructorapp)

    def __repr__(self):
        return format("INSTANCE: (%s : %s)" %
                      (self.identifier, self.constructorapp))

    def evaluate(self, env):
        pass


