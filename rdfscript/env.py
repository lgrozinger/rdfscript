import rdflib
import sys
import pathlib
import logging

import rdfscript.toplevel
import rdfscript.core

from .evaluate import evaluate
from .error import RDFScriptError

from rdfscript.identifier import URI

from .rdfscriptparser import RDFScriptParser

class Env:
    def __init__(self, repl=False, filename=None):

        self._symbol_table = {}

        self._interactive_mode = repl

        self._rdf = RuntimeGraph()

        self._default_ns = rdflib.Namespace(self._rdf.namespace)

        self._logger = logging.getLogger(__name__)

        if filename:
            self._path = pathlib.Path(filename).parent
        else:
            self._path = pathlib.Path('.')

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

    def add_triples(self, triples):
        for (s, p, o) in triples:
            self._rdf.add(s, p, o)

    def bind_prefix(self, prefix, uri):
        return self._rdf.bind_prefix(prefix, uri)

    def set_default_prefix(self, prefix):

        ns = self._rdf.ns_for_prefix(prefix)

        if not ns:
            return None
        else:
            self._default_ns = ns
            return prefix

    def assign(self, uriref, value):

        self._symbol_table[uriref] = value

    def lookup(self, uriref):

        return self._symbol_table.get(uriref, None)

    def resolve_name(self, prefix, name):

        if not prefix:
            ns = self._default_ns
        else:
            ns = self._rdf.ns_for_prefix(prefix)

        if not ns:
            return None
        else:
            return rdflib.URIRef(ns[name])

    def interpret(self, forms):
        result = None

        for form in forms:
            try:
                result = evaluate(form, self)
            except RDFScriptError as e:
                self._logger.error(str(e))

        return result

    def eval_import(self, uri):

        filename = uri.toPython()
        parser = RDFScriptParser(filename=filename)

        self.interpret(parser.parse((self._path / filename).with_suffix('.rdfsh').read_text()))

class RuntimeGraph:

    def __init__(self):

        self._g = rdflib.Graph()

    @property
    def namespace(self):
        return self._g.identifier

    def add(self, s, p, o, unique=False):
        if unique:
            self._g.set((s, p, o))
        else:
            self._g.add((s, p, o))

    def bind_prefix(self, prefix, uri):
        self._g.bind(prefix, uri)
        return prefix

    def ns_for_prefix(self, prefix):

        namespaces = self._g.namespaces()
        matching = [n for (p, n) in namespaces if p == prefix]

        if len(matching) == 1:
            return rdflib.Namespace(matching[0])
        elif len(matching) == 0:
            None

    def prefix_for_ns(self, uri):

        namespaces = self._g.namespaces()
        matching = [p for (p, n) in namespaces if n == uri]

        if len(matching) == 1:
            return matching[0]
        elif len(matching) == 0:
            None

    def serialise(self):
        return self._g.serialize(format='xml').decode("utf-8")
