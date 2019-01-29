import unittest

import rdflib

import rdfscript.context as context
import rdfscript.core as core


class TestContext(unittest.TestCase):

    def setUp(self):
        self.g = rdflib.ConjunctiveGraph()

    def tearDown(self):
        pass

    def test_equal(self):
        c = context.Context(self.g)
        d = context.Context(self.g)
        c.put(core.Value(1), core.Uri('v'))
        d.put(core.Value(1), core.Uri('v'))
        self.assertEqual(c, d)

    def test_not_equal(self):
        h = rdflib.ConjunctiveGraph()
        c = context.Context(self.g)
        c.put(core.Value(1), core.Uri('v'))
        d = context.Context(h)
        c.put(core.Value(2), core.Uri('v'))
        self.assertNotEqual(c, d)

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
        root = core.Uri(self.g.identifier.toPython())
        expected = [(root, core.Uri('v'), core.Value(83))]
        c = context.Context(self.g)
        c.put(core.Value(83), core.Uri('v'))
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

    def test_get_all(self):
        c = context.Context(self.g)
        c.put(core.Value(83), core.Uri('v'))
        c.put(core.Value(84), core.Uri('u'))
        c.put(core.Value(85), core.Uri('t'))

        expected = [core.Value(83), core.Value(84), core.Value(85)]
        actually = c.get_all()
        self.assertEqual(set(expected), set(actually))
