import rdflib

from rdfscript.toplevel import ScriptObject, Assignment, InstanceExp
from rdfscript.identifier import LocalName

class Template:

    def __init__(self, base, identifier, param_names, body, linenum):
        super().__init__(linenum)
        self.params = dict([(name, rdflib.BNode())
                            for name
                            in param_names])

        self.identifier = identifier
        self.body = body

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.identifier == other.identifier and
                self.param_names == other.param_names and
                self.body == other.body)

    def __repr__(self):
        return format("CONSTRUCTORDEF: (%s, with args: %s)" %
                      (self.identifier, self.param_names))

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

