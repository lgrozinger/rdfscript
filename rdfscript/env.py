import rdflib
import sys

import rdfscript.toplevel
import rdfscript.core

from .evaluate import evaluate

from rdfscript.identifier import URI

from urllib.parse import quote as urlencode

class Env:
    def __init__(self, repl=False, filename=None):

        self._symbol_table = {}

        self._interactive_mode = repl

        self._rdf = RuntimeGraph()

        self._assign_predicate = rdflib.BNode()

        self._default_ns = rdflib.Namespace(self._rdf.internal_context)

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

    def add_triples(self, triples):
        for (s, p, o) in triples:
            self._rdf.add(s, p, o, self._rdf.user_context)

    def bind_prefix(self, prefix, uri):
        return self._rdf.bind_prefix(prefix, uri)

    def set_default_prefix(self, prefix):

        ns = self._rdf.ns_for_prefix(prefix)

        if not ns:
            # error condition
            return None
        else:
            self._default_ns = ns
            return prefix

    def assign(self, uriref, value):

        self._symbol_table[uriref] = value
        # self._rdf.add(identifier,
        #               self._assign_predicate,
        #               value,
        #               self._rdf.internal_context,
        #               unique=True)

    def lookup(self, uriref):

        return self._symbol_table.get(uriref, None)
        # expansions = [o for (s, p, o)
        #               in self._rdf.get_internal_triples((identifier,
        #                                                  self._assign_predicate,
        #                                                  None))]

        # if len(expansions) > 1:
        #     ## this is an error condition
        #     raise SyntaxError("Multiple expansions found for identifier.")
        # elif len(expansions) == 0:
        #     return None
        # else:
        #     return expansions[0]

    def resolve_name(self, prefix, name):

        if not prefix:
            ns = self._default_ns
        else:
            ns = self._rdf.ns_for_prefix(prefix)

        return rdflib.URIRef(ns[name])

    # def put_template(self, template_uri, template_as_triples):

    #     for (s, p, o) in template_as_triples:
    #         self._rdf.add(s, p, o, template_uri, unique=True)

    # def get_template(self, template_uri):

    #     graph = self._rdf.get_context_graph(template_uri)
    #     return [triple for triple in graph.triples((None, None, None))]

    def interpret(self, forms):
        result = None

        for form in forms:
            result = evaluate(form, self)

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

    def __init__(self):

        self._g = rdflib.ConjunctiveGraph()

        self._user     = rdflib.ConjunctiveGraph()
        self._internal = rdflib.ConjunctiveGraph()

    @property
    def user_context(self):
        return self._user.identifier

    @property
    def internal_context(self):
        return self._internal.identifier

    def get_context_graph(self, context):
        return self._g.get_context(context)

    def add(self, s, p, o, c, unique=False):
        if unique:
            self._g.get_context(c).set((s, p, o))
        else:
            self._g.get_context(c).add((s, p, o))

    def bind_prefix(self, prefix, uri):
        self._g.bind(prefix, uri)
        return prefix

    def ns_for_prefix(self, prefix):

        namespaces = self._g.namespaces()
        matching = [n for (p, n) in namespaces if p == prefix]

        if len(matching) == 1:
            return rdflib.Namespace(matching[0])
        elif len(matching) == 0:
            raise SyntaxError("No such prefix as '%s'" % prefix)

    def get_internal_triples(self, triple):
        return self._g.get_context(self._internal.identifier).triples(triple)

    def get_user_triples(self, triple):
        return self._g.get_context(self._user.identifier).triples(triple)

    def serialise(self):
        return self._g.serialize(format='turtle')
