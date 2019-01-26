import unittest

import rdflib

import rdfscript.context as context
import rdfscript.core as core


class TestContext(unittest.TestCase):

    def setUp(self):
        self.g = rdflib.ConjunctiveGraph()

    def tearDown(self):
        pass

    def test_get_root_node(self):
        c = context.Context(self.g)
        expected = core.Uri(c._root.toPython())
        actually = c.root
        self.assertEqual(expected, actually)

    def test_get_graph_triples_empty(self):
        c = context.Context(self.g)
        expected = []
        actually = c.get_all_triples()
        self.assertEqual(expected, actually)

    def test_get_graph_triples_non_empty(self):
        expected = [(core.Uri(self.g.identifier),
                     core.Uri('v'),
                     core.Value(83))]
        c = context.Context(self.g)
        actually = c.get_all_triples()
        self.assertEqual(expected, actually)

    def test_put_into_context(self):
        c = context.Context(self.g)
        c.put(core.Value(83), core.Uri('v'))

        expected = [(c.root, core.Uri('v'), core.Value(83))]
        actually = c.get_all_triples()
        self.assertEqual(expected, actually)

    def test_put_into_context_duplicate(self):
        c = context.Context(self.g)
        c.put(core.Value(83), core.Uri('v'))
        c.put(core.Value(84), core.Uri('v'))

        expected = [(c.root, core.Uri('v'), core.Value(84))]
        actually = c.get_all_triples()
        self.assertEqual(expected, actually)

    def test_get_from_context(self):
        c = context.Context(self.g)
        c.put(core.Value(83), core.Uri('v'))

        expected = core.Value(83)
        actually = c.get(core.Uri('v'))
        self.assertEqual(expected, actually)
