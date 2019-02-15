import unittest
import rdflib

import rdfscript.rdfscriptparser as parser
import rdfscript.utils as utils
import rdfscript.templates as templates
import rdfscript.graph as graph
import rdfscript.runtime as runtime
import rdfscript.core as core


class TemplateGraphTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        None

    def test_set_rdf_type_to_template(self):
        name = core.Name('T')
        template = templates.Template(name, [], [])

        graph.set_template_type(template, self.rt)
        context = self.rt.context(template.name)

        expected = core.lang_uri(template)
        actually = context.get(utils.from_rdf(rdflib.RDF.type))
        self.assertEqual(expected, actually)

    def test_get_context_creates_leveled_resource(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        graph.set_template_type(template, self.rt)
        expected = core.Uri(self.rt._root.uri + 'nsT')
        actually = self.rt.binding(name)

        self.assertEqual(expected, actually)

    def test_get_context_returns_correct_context_leveled(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        graph.set_template_type(template, self.rt)
        context = self.rt.context(template.name)
        expected = rdflib.URIRef(self.rt._root.uri + 'nsT')
        actually = utils.to_rdf(context.root)

        self.assertEqual(expected, actually)

    def test_set_rdf_type_to_leveled_template(self):
        name = core.Name('ns', 'T')
        template = templates.Template(name, [], [])

        graph.set_template_type(template, self.rt)
        context = self.rt.context(template.name)

        expected = core.lang_uri(template)
        actually = context.get(utils.from_rdf(rdflib.RDF.type))
        self.assertEqual(expected, actually)

    def test_hang_params_one_param(self):
        name = core.Name('T')
        param = core.Name('p')
        template = templates.Template(name, [param], [])

        graph.set_template_type(template, self.rt)
        graph.hang_params(template, self.rt)
        context = self.rt.context(template.name)

        expected = utils.contextualise_uri(core.Uri('p'), context)
        actually = context.get(core.params_uri(1))
        self.assertEqual(expected, actually)

    def test_hang_params_no_params(self):
        name = core.Name('T')
        template = templates.Template(name, [], [])

        graph.set_template_type(template, self.rt)
        graph.hang_params(template, self.rt)
        context = self.rt.context(template.name)

        expected = None
        actually = context.get(core.params_uri(1))
        self.assertEqual(expected, actually)

    def test_hang_params_two_params(self):
        name = core.Name('T')
        params = [core.Name('p'), core.Name('q')]
        template = templates.Template(name, params, [])

        graph.set_template_type(template, self.rt)
        graph.hang_params(template, self.rt)
        context = self.rt.context(template.name)

        expected = utils.contextualise_uri(core.Uri('p'), context)
        actually = context.get(core.params_uri(1))
        self.assertEqual(expected, actually)

        expected = utils.contextualise_uri(core.Uri('q'), context)
        actually = context.get(core.params_uri(2))
        self.assertEqual(expected, actually)
