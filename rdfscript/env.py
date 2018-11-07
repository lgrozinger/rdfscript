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

        ## TODO: type checking
        self.rdf.add(identifier, self.rdf.expansion_predicate, value)

    def resolve_name(self, name, prefix=None):

        ns = self.rdf.ns_for_prefix(prefix)
        ## TODO: type checking?

        return rdflib.URIRef(ns[urlencode(name)])

    def interpret(self, forms):
        result = None

        for form in forms:
            result = form.evaluate(self)

        return result

    def rt_error(self, form):
        # TODO: better, cleaner error handling and reporting
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

        ## what if already bound?
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

    def serialise(self):
        return self.g.serialize(format='turtle')
