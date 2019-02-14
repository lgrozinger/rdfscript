import unittest
import rdflib

import rdfscript.rdfscriptparser as parser
import rdfscript.utils as utils
import rdfscript.expansions as expansions
import rdfscript.graph as graphs
import rdfscript.runtime as runtime
import rdfscript.core as core


class ExpansionGraphTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        None

    def test_get_context_creates_resource(self):
        name = core.Name('e')
        template = core.Name('T')
        expansion = expansions.Expansion(name, template, [], [])

        graphs.object_context(expansion, self.rt)
        expected = core.Uri(self.rt._root.uri + 'e')
        actually = self.rt.binding(name)

        self.assertEqual(expected, actually)

    # def test_get_context_returns_correct_context(self):
    #     name = core.Name('T')
    #     template = templates.Template(name, [], [])

    #     context = tgraphs.template_context(template, self.rt)
    #     expected = rdflib.URIRef(self.rt._root.uri + 'T')
    #     actually = utils.to_rdf(context.root)

    #     self.assertEqual(expected, actually)

    # def test_set_rdf_type_to_template(self):
    #     name = core.Name('T')
    #     template = templates.Template(name, [], [])

    #     tgraphs.set_template_type(template, self.rt)
    #     context = tgraphs.template_context(template, self.rt)

    #     expected = core.lang_uri(template)
    #     actually = context.get(utils.from_rdf(rdflib.RDF.type))
    #     self.assertEqual(expected, actually)

    # def test_get_context_creates_leveled_resource(self):
    #     name = core.Name('ns', 'T')
    #     template = templates.Template(name, [], [])

    #     tgraphs.template_context(template, self.rt)
    #     expected = core.Uri(self.rt._root.uri + 'nsT')
    #     actually = self.rt.binding(name)

    #     self.assertEqual(expected, actually)

    # def test_get_context_returns_correct_context_leveled(self):
    #     name = core.Name('ns', 'T')
    #     template = templates.Template(name, [], [])

    #     context = tgraphs.template_context(template, self.rt)
    #     expected = rdflib.URIRef(self.rt._root.uri + 'nsT')
    #     actually = utils.to_rdf(context.root)

    #     self.assertEqual(expected, actually)

    # def test_set_rdf_type_to_leveled_template(self):
    #     name = core.Name('ns', 'T')
    #     template = templates.Template(name, [], [])

    #     tgraphs.set_template_type(template, self.rt)
    #     context = tgraphs.template_context(template, self.rt)

    #     expected = core.lang_uri(template)
    #     actually = context.get(utils.from_rdf(rdflib.RDF.type))
    #     self.assertEqual(expected, actually)

    # def test_hang_params_one_param(self):
    #     name = core.Name('T')
    #     param = core.Name('p')
    #     template = templates.Template(name, [param], [])

    #     tgraphs.set_template_type(template, self.rt)
    #     tgraphs.hang_params(template, self.rt)
    #     context = tgraphs.template_context(template, self.rt)

    #     expected = utils.contextualise_uri(core.Uri('p'), context)
    #     actually = context.get(core.params_uri(1))
    #     self.assertEqual(expected, actually)

    # def test_hang_params_no_params(self):
    #     name = core.Name('T')
    #     template = templates.Template(name, [], [])

    #     tgraphs.set_template_type(template, self.rt)
    #     tgraphs.hang_params(template, self.rt)
    #     context = tgraphs.template_context(template, self.rt)

    #     expected = None
    #     actually = context.get(core.params_uri(1))
    #     self.assertEqual(expected, actually)

    # def test_hang_params_two_params(self):
    #     name = core.Name('T')
    #     params = [core.Name('p'), core.Name('q')]
    #     template = templates.Template(name, params, [])

    #     tgraphs.set_template_type(template, self.rt)
    #     tgraphs.hang_params(template, self.rt)
    #     context = tgraphs.template_context(template, self.rt)

    #     expected = utils.contextualise_uri(core.Uri('p'), context)
    #     actually = context.get(core.params_uri(1))
    #     self.assertEqual(expected, actually)

    #     expected = utils.contextualise_uri(core.Uri('q'), context)
    #     actually = context.get(core.params_uri(2))
    #     self.assertEqual(expected, actually)
