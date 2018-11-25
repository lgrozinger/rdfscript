import rdflib
import sys
import pathlib
import logging

import rdfscript.toplevel
import rdfscript.core

from .evaluate import evaluate
from .error import RDFScriptError, FailToImport

from rdfscript.identifier import URI

from .rdfscriptparser import RDFScriptParser

from .importer import Importer

from .SBOL2Serialize import serialize_sboll2

from .extensions import ExtensionManager

class Env:
    def __init__(self,
                 repl=False,
                 filename=None,
                 serializer=None,
                 paths=[],
                 extensions=[]):

        self._symbol_table = {}
        self._template_table = {}
        self._extension_manager = ExtensionManager(extras=extensions)

        self._rdf = RuntimeGraph(serializer=serializer)

        self._default_ns = rdflib.Namespace(self._rdf.namespace)
        self._default_prefix = None

        self._logger = logging.getLogger(__name__)

        if filename:
            paths.append(pathlib.Path(filename).parent)
            self._importer = Importer(paths)
        else:
            self._importer = Importer(paths)

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

    @property
    def default_prefix(self):
        return self._default_prefix

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
            self._default_prefix = prefix
            return prefix

    def assign(self, uriref, value):

        self._symbol_table[uriref] = value

    def lookup(self, uriref):

        return self._symbol_table.get(uriref, None)

    def assign_template(self, uriref, template):

        self._template_table[uriref] = template

    def lookup_template(self, uriref):

        return self._template_table.get(uriref, None)

    def get_extension(self, name):
        return self._extension_manager.get_extension(name)

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

        self._importer.add_path(pathlib.Path(filename).parent)
        import_text = self._importer.import_file(filename)
        if not import_text:
            return False
        else:
            self.interpret(parser.parse(self._importer.import_file(filename)))

        self._importer.remove_path(pathlib.Path(filename).parent)
        return True

    def get_current_path(self):

        return [str(p) for p in self._importer.path]

class RuntimeGraph:

    def __init__(self, serializer=None):

        self._g = rdflib.Graph()
        self._serializer = serializer

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
        if self._serializer == 'rdfxml':
            return self._g.serialize(format='xml').decode("utf-8")
        elif self._serializer == 'n3':
            return self._g.serialize(format='n3').decode("utf-8")
        elif self._serializer == 'turtle':
            return self._g.serialize(format='turtle').decode("utf-8")
        elif self._serializer == 'sbolxml':
            return serialize_sboll2(self._g).decode("utf-8")
