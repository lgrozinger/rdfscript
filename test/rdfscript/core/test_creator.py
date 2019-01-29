import unittest

import rdfscript.resource_handler as handler
import rdfscript.graph as graph
import rdfscript.core as core


class TestCreator(unittest.TestCase):

    def setUp(self):
        self.env_graph = graph.EnvironmentGraph()
        self.resolver = handler.Resolver(self.env_graph)

    def tearDown(self):
        pass

    def test_create_resource(self):
        creator = handler.Creator(self.env_graph)
        name = core.Name('v')
        value = core.Value(12345)
        creator.create(name, value)
        expected = value
        actually = self.resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_create_resource_two_level(self):
        creator = handler.Creator(self.env_graph)
        name = core.Name('u', 'v')
        value = core.Value(12345)
        creator.create(name, value)
        expected = value
        actually = self.resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_create_resource_three_level(self):
        creator = handler.Creator(self.env_graph)
        name = core.Name('u', 'v', 'w')
        value = core.Value(12345)
        creator.create(name, value)
        expected = value
        actually = self.resolver.resolve(name)
        self.assertEqual(expected, actually)