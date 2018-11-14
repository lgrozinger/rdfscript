import rdflib
import sys

import rdfscript.toplevel
import rdfscript.core

from .evaluate import evaluate

from rdfscript.identifier import URI

from urllib.parse import quote as urlencode

class Env:
    def __init__(self, repl=False, filename=None):

        self._interactive_mode = repl

        self._rdf = RuntimeGraph()

        self._assign_predicate = rdflib.BNode()

        self._default_ns = rdflib.Namespace(self._rdf.internal_graph.identifier)

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

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

    def assign(self, identifier, value):

        self._rdf.add_internal(identifier, self._assign_predicate, value, unique=True)

    def lookup(self, identifier):

        expansions = [o for (s, p, o)
                      in self._rdf.get_internal_triples((identifier,
                                                         self._assign_predicate,
                                                         None))]

        if len(expansions) > 1:
            ## this is an error condition
            raise SyntaxError("Multiple expansions found for identifier.")
        elif len(expansions) == 0:
            return None
        else:
            return expansions[0]

    def resolve_name(self, prefix, name):

        if not prefix:
            ns = self._default_ns
        else:
            ns = self._rdf.ns_for_prefix(prefix)

        return rdflib.URIRef(ns[name])

    def put_template(self, template_as_triples):

        for (s, p, o) in template_as_triples:
            self._rdf.add_internal(s, p, o, unique=True)

    def get_template(self, template_uri):

        graph = self._rdf.get_internal_context(template_uri)
        return [triple for triple in graph.triples((None, None, None))]

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
    def user_graph(self):
        return self._user

    @property
    def internal_graph(self):
        return self._internal

    def add_internal(self, s, p, o, unique=False, context=None):
        if unique:
            self._g.get_context(self._internal.identifier).set((s, p, o))
        else:
            self._g.get_context(self._internal.identifier).add((s, p, o))

    def get_internal_context(self, context_uri):
        internal = self._g.get_context(self._internal.identifier)
        return rdflib.Graph(store=internal.store, identifier=context_uri, namespace_manager=internal)

    def add_user(self, s, p, o):
        self._g.get_context(self._user.identifier).add((s, p, o))

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
