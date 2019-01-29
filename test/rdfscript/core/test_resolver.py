import unittest
import pdb

import rdfscript.resource_handler as handler
import rdfscript.graph as graph
import rdfscript.core as core


class TestResolver(unittest.TestCase):

    def setUp(self):
        self.env_graph = graph.EnvironmentGraph()
        self.creator = handler.Creator(self.env_graph)

    def tearDown(self):
        pass

    def test_abs_resolve_one_level(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        name = core.Name('variable')
        self.creator.create(name, value)
        expected = value
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_two_level(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        name = core.Name('u', 'v')
        self.creator.create(name, value)
        expected = value
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_three_level(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        name = core.Name('u', 'v', 'w')
        self.creator.create(name, value)

        expected = value
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_bound_step(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        name = core.Name('u', 'v')
        self.creator.create(core.Name('u'), value)
        expected = None
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_resolve_correct_context_chosen(self):
        resolver = handler.Resolver(self.env_graph)
        value1 = core.Value(12345)
        value2 = core.Value(67890)
        name = core.Name('w', 'v')
        self.creator.create(name, value1)
        self.creator.create(core.Name('u', 'v'), value2)
        expected = value1
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)
