import rdflib
import sys
import pathlib
import logging

from .core import Uri, Value, Prefix

from .evaluate import evaluate
from .error import (RDFScriptError,
                    FailToImport,
                    PrefixError)

from .template import Template
from .rdfscriptparser import RDFScriptParser

from .importer import Importer

from .SBOL2Serialize import serialize_sboll2

from .extensions import ExtensionManager
from .rdf_data import RDFData

class Env(object):
    def __init__(self,
                 repl=False,
                 filename=None,
                 serializer=None,
                 paths=[],
                 extensions=[]):

        self._symbol_table = {}
        self._template_table = {}
        self._extension_manager = ExtensionManager(extras=extensions)

        self._rdf = RDFData(serializer=serializer)
        self._default_prefix = Prefix(Uri(self._rdf._g.identifier.toPython(), None), None)

        if filename:
            paths.append(pathlib.Path(filename).parent)
            self._importer = Importer(paths)
        else:
            self._importer = Importer(paths)

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

    @property
    def default_prefix(self):
        """The language object that set the default prefix."""
        return self._default_prefix

    def uri_for_prefix(self, prefix):
        """Return a Uri object for a Prefix object."""
        try:
            return self._rdf.uri_for_prefix(prefix.identity)
        except PrefixError:
            raise PrefixError(prefix, prefix.location)

    def add_triples(self, triples):
        """Add a triple of Uri or Value language objects to the RDF graph."""
        for (s, p, o) in triples:
            self._rdf.add(s, p, o)

    def bind_prefix(self, prefix, uri):
        self._rdf.bind_prefix(prefix.identity, uri)
        return prefix

    def set_default_prefix(self, prefix):

        ns = self._rdf.uri_for_prefix(prefix.identity)

        if not ns:
            raise PrefixError(prefix, prefix.location)
        else:
            self._default_prefix = prefix
            return prefix

    def assign(self, uri, value):

        uriref = self._rdf.to_rdf(uri)
        self._symbol_table[uriref] = value

    def lookup(self, uri):

        uriref = self._rdf.to_rdf(uri)
        return self._symbol_table.get(uriref, None)

    def assign_template(self, uri, template):

        uriref = self._rdf.to_rdf(uri)
        self._template_table[uriref] = template

    def lookup_template(self, uri):

        uriref = self._rdf.to_rdf(uri)
        return self._template_table.get(uriref, None)

    def get_extension(self, name):
        return self._extension_manager.get_extension(name)

    def resolve_name(self, name):

        prefix = name.prefix
        local  = name.localname.uri(self)

        if not prefix:
            ns = self._default_prefix.uri(self)
        else:
            ns = prefix.uri(self)

        return Uri(ns.uri + local.uri, name.location)

    def interpret(self, forms):
        result = None

        for form in forms:
            try:
                result = evaluate(form, self)
            except RDFScriptError as e:
                logging.error(str(e))

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

