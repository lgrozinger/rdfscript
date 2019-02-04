import unittest
import rdflib

import rdfscript.rdfscriptparser as parser
import rdfscript.error as error
import rdfscript.utils as utils
import rdfscript.templates as templates
import rdfscript.runtime as runtime
import rdfscript.core as core


class TemplateGraphTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        None

    def test_get_context_creates_resource(self):
        name = core.Name('T')
        template = templates.Template(name, [], [])

        templates.template_context(template, self.rt)
        expected = core.Uri(self.rt._root.uri + 'T')
        actually = self.rt.binding(name)

        self.assertEqual(expected, actually)

    def test_get_context_returns_correct_context(self):
        name = core.Name('T')
        template = templates.Template(name, [], [])

        context = templates.template_context(template, self.rt)
        expected = rdflib.URIRef(self.rt._root.uri + 'T')
        actually = utils.to_rdf(context.root)

        self.assertEqual(expected, actually)

    def test_set_rdf_type_to_template(self):
        name = core.Name('T')
        template = templates.Template(name, [], [])

        templates.set_template_type(template, self.rt)
        context = templates.template_context(template, self.rt)

        expected = core.lang_uri(template)
        actually = context.get(utils.from_rdf(rdflib.RDF.type))
        self.assertEqual(expected, actually)

    def test_get_context_creates_leveled_resource(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        templates.template_context(template, self.rt)
        expected = core.Uri(self.rt._root.uri + 'nsT')
        actually = self.rt.binding(name)

        self.assertEqual(expected, actually)

    def test_get_context_returns_correct_context_leveled(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        context = templates.template_context(template, self.rt)
        expected = rdflib.URIRef(self.rt._root.uri + 'nsT')
        actually = utils.to_rdf(context.root)

        self.assertEqual(expected, actually)

    def test_set_rdf_type_to_leveled_template(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        templates.set_template_type(template, self.rt)
        context = templates.template_context(template, self.rt)

        expected = core.lang_uri(template)
        actually = context.get(utils.from_rdf(rdflib.RDF.type))
        self.assertEqual(expected, actually)
