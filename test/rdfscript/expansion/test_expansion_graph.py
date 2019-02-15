import unittest
import rdflib

import rdfscript.rdfscriptparser as parser
import rdfscript.utils as utils
import rdfscript.expansions as expansions
import rdfscript.graph as graphs
import rdfscript.runtime as runtime
import rdfscript.core as core
import rdfscript.evaluate as evaluate


class ExpansionGraphTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        None

    # don't do this...
    # expansions in the first case should just be add triples to
    # graph, templates are where to add complexity

    # expand template === get template's triples, sub args for
    # params, add triples to the graph.
    @unittest.skip("See above comment.")
    def test_get_context_creates_resource(self):
        template = core.Name('T')
        expansion = expansions.Expansion(name, template, [], [])

        graphs.object_context(expansion, self.rt)
        expected = core.Uri(self.rt._root.uri + 'e')
        actually = self.rt.binding(name)

        self.assertEqual(expected, actually)

    def test_template_triples_on_simple_template(self):
        template = self.parser.parse('T() = ' +
                                     '(<http://s> > <http://p> > true)')[0]

        evaluate.evaluate(template, self.rt)
        s = core.Uri('http://s')
        p = core.Uri('http://p')
        o = core.Value(True)

        expected = [(s, p, o)]
        actually = graphs.template_triples(template.name, self.rt)
        self.assertEqual(expected, actually)

    def test_template_triples_crossed_wires_template(self):
        template = self.parser.parse('T() = ' +
                                     '(<http://s> > <http://p> > true' +
                                     ' <http://p> > <http://s> > false)')[0]

        evaluate.evaluate(template, self.rt)
        s = core.Uri('http://s')
        p = core.Uri('http://p')

        expected = [(s, p, core.Value(True)), (p, s, core.Value(False))]
        actually = graphs.triples(self.rt.context(template.name)._graph)
        self.assertEqual(set(expected), set(actually))

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
