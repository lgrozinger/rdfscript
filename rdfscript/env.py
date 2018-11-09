import rdflib
import sys

import rdfscript.toplevel
from rdfscript.identifier import URI

from urllib.parse import quote as urlencode

class Env:
    def __init__(self, repl=False, filename=None):

        self.interactive_mode = repl

        self.rdf = RuntimeGraph('file://rdfscript.env/')


    def bind_prefix(self, prefix, uri):
        return self.rdf.bind_prefix(prefix, uri)

    def assign(self, identifier, value):

        self.rdf.add(identifier, self.rdf.expansion_predicate, value)

    def lookup(self, identifier):

        expansions = self.rdf.get_expansions(identifier)

        if len(expansions) > 1:
            ## this is an error condition
            raise SyntaxError("Multiple expansions found for identifier.")
        elif len(expansions) == 0:
            return None
        else:
            return expansions[0]

    def resolve_name(self, name, prefix=None):

        ns = self.rdf.ns_for_prefix(prefix)

        return rdflib.URIRef(ns[name])

    def put_template(self, template_as_triples):

        for triple in template_as_triples:
            self.rdf.add(triple)

    def interpret(self, forms):
        result = None

        for form in forms:
            result = form.evaluate(self)

        return result

    def rt_error(self, form):
        if self.interactive_mode or not form.lineno:
            print("ERROR: unexpected object %s"
                  % form)
        else:
            print("ERROR: unexpected object %s : LINENO: %d"
                  % (form, form.lineno))
        raise SyntaxError

class RuntimeGraph:

    def __init__(self, env_ns):

        self.g = rdflib.Graph()

        self.default_ns = rdflib.Namespace(env_ns)
        self.env_ns     = rdflib.Namespace(env_ns)
        self.g.bind('rdfscript', self.env_ns)

        self.expansion_predicate = self.env_ns['expandsTo']

    def add(self, s, p, o):

        self.g.add((s, p, o))

    def bind_prefix(self, prefix, uri):

        self.g.bind(prefix, uri)
        return prefix

    def ns_for_prefix(self, prefix):

        if not prefix:
            return self.default_ns
        else:
            namespaces = self.g.namespaces()
            matching = [n for (p, n) in namespaces if p == prefix]

            if len(matching) == 1:
                return rdflib.Namespace(matching[0])
            else:
                ## TODO: actually indicate an error
                return None

    def get_expansions(self, identifier):

        return [o for (s, p, o) in (self.g.triples((identifier,
                                    self.expansion_predicate,
                                    None)))]

    def serialise(self):
        return self.g.serialize(format='turtle')
