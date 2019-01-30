import unittest

import rdfscript.core as core
import rdfscript.graph as graph
import rdfscript.utils as utils
import rdfscript.error as error
import rdfscript.context as context


class TestEnvironmentGraph(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_graph(self):
        eg = graph.EnvironmentGraph()
        expected = eg._graph
        actually = eg.graph
        self.assertEqual(expected, actually)

    def test_get_context_empty(self):
        eg = graph.EnvironmentGraph()
        context_uri = eg.root
        expected = context.Context(eg.graph)
        actually = eg.get_context(context_uri)
        self.assertEqual(expected, actually)

    def test_get_context(self):
        eg = graph.EnvironmentGraph()
        c = eg.get_context(eg.root)
        c.put(core.Value(83), core.Uri('v'))
        expected = context.Context(eg.graph)
        actually = eg.get_context(eg.root)
        self.assertEqual(expected, actually)

    def test_bind_prefix(self):
        eg = graph.EnvironmentGraph()
        before = set(eg.graph.namespaces())
        uri = core.Uri('http://prefix/')
        p = core.Name('prefix')
        eg.bind_prefix(p, uri)

        expected = {('prefix', utils.to_rdf(uri))}.union(before)
        actually = set(eg.graph.namespaces())
        self.assertEqual(expected, actually)

    def test_get_uri_for_prefix(self):
        eg = graph.EnvironmentGraph()
        uri = core.Uri('http://prefix/')
        p = core.Name('prefix')
        eg.bind_prefix(p, uri)

        expected = uri
        actually = eg.prefix_to_uri(p)
        self.assertEqual(expected, actually)

    def test_get_uri_for_unbound_prefix(self):
        eg = graph.EnvironmentGraph()
        p = core.Name('prefix')
        with self.assertRaises(error.PrefixError):
            eg.prefix_to_uri(p)

    def test_get_prefix_for_uri(self):
        eg = graph.EnvironmentGraph()
        uri = core.Uri('http://prefix/')
        p = core.Name('prefix')
        eg.bind_prefix(p, uri)

        expected = p
        actually = eg.uri_to_prefix(uri)
        self.assertEqual(expected, actually)

    def test_get_prefix_for_unbound_uri(self):
        eg = graph.EnvironmentGraph()
        with self.assertRaises(error.PrefixError):
            eg.uri_to_prefix(core.Uri('http://prefix/'))
