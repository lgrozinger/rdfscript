import rdflib
import sys
import pathlib
import logging

from .core import Uri, Value

from .error import (RDFScriptError,
                    FailToImport,
                    PrefixError)

from .template import Template
from .rdfscriptparser import RDFScriptParser

from .importer import Importer

from .extensions import ExtensionManager
from extensions.error import ExtensionError
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
        self._default_prefix = Uri(self._rdf._g.identifier.toPython())
        self._self = self._default_prefix
        self._prefix_set_by_user = False

        if filename:
            paths.append(pathlib.Path(filename).parent)
            self._importer = Importer(paths)
        else:
            self._importer = Importer(paths)

    def __repr__(self):
        return format("%s" % self._rdf.serialise())

    @property
    def self_uri(self):
        return self._self

    @self_uri.setter
    def self_uri(self, uri):
        self._self = uri
        
    @property
    def default_prefix(self):
        """The language object that set the default prefix."""
        return self._default_prefix

    @property
    def default_prefix_set(self):
        return self._prefix_set_by_user

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
            self._prefix_set_by_user = True
            return prefix

    def assign(self, uri, value):

        self._symbol_table[uri] = value

    def lookup(self, uri):

        return self._symbol_table.get(uri, None)

    def assign_template(self, uri, template):

        #uriref = self._rdf.to_rdf(uri)
        self._template_table[uri] = template

    def lookup_template(self, uri):

        #uriref = self._rdf.to_rdf(uri)
        return self._template_table.get(uri, None)

    def get_extension(self, name):
        return self._extension_manager.get_extension(name)

    def interpret(self, forms):
        result = None

        for form in forms:
            try:
                result = evaluate(form, self)
            except RDFScriptError as e:
                logging.error(str(e))
            except ExtensionError as e:
                logging.error(str(e))

        return result

    def eval_import(self, uri):

        filename = uri.uri
        parser = RDFScriptParser(filename=filename)

        import_text = self._importer.import_file(filename)
        if not import_text:
            return False
        else:
            self.interpret(parser.parse(import_text))

        return True

    def get_current_path(self):

        return [str(p) for p in self._importer.path]

