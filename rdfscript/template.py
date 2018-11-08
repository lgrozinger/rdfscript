import rdflib

from rdfscript.toplevel import Assignment, InstanceExp
from rdfscript.identifier import LocalName

class Template:

    def __init__(self, base, identifier, param_names, body, env):

        self.triples = []
        self.params = dict([(name, rdflib.BNode())
                            for name
                            in param_names])

        self.ns = rdflib.Namespace(identifier.resolve(env))

        self.env = env

        # self.triples.append([self.param_triple(param)
        #                      for param
        #                      in self.params])

        # self.triples.append([self.body_triple(body_form)
        #                      for body_form
        #                      in body])

    def param_predicate_uri(self, name):
        return rdflib.URIRef(self.ns['parameter/' + name])

    def param_triple(self, param):
        return (rdflib.URIRef(self.ns),
                self.param_predicate_uri(self.ns, param),
                rdflib.BNode())

    def body_triple(self, form):

        if type(form) == type(Assignment(None, None, 0)):
            return self.property_triple(form)
        elif type(form) == type(InstanceExp(None, None, 0)):
            return None
        else:
            return None

    def property_triple(self, assignment):

        s = rdflib.URIRef(self.ns)
        p = None
        o = None

        # check for parameters in the assignment identifier
        if (type(assignment.identifier)==type(LocalName(None,None,0))
            and assignment.identifier.name in self.params):

            ## then the predicate points to a parameter
            p = self.params[assignment.identifier.name]
        else:
            p = assignment.identifier.evaluate(self.env)
            if not p:
                p = assignment.identifier.resolve(self.env)

        # check for parameters in the assignment value
        if (type(assignment.value)==type(LocalName(None,None,0))
            and assignment.value.name in self.params):

            ## then the object points to a parameter
            o = self.params[assignment.value.name]
        else:
            o = assignment.identifier.resolve(self.env)

        return (s, p, o)


