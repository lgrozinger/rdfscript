import unittest
import pdb

import rdfscript.resource_handler as handler
import rdfscript.error as error
import rdfscript.graph as graph
import rdfscript.utils as utils
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

    def test_abs_resolve_one_level_unbound(self):
        resolver = handler.Resolver(self.env_graph)
        name = core.Name('v')

        expected = None
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_two_level_unbound(self):
        resolver = handler.Resolver(self.env_graph)
        name = core.Name('u', 'v')

        expected = None
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_three_level_unbound(self):
        resolver = handler.Resolver(self.env_graph)
        name = core.Name('u', 'v', 'w')

        expected = None
        actually = resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_abs_resolve_bound_step_is_value(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        name = core.Name('u', 'v')
        self.creator.create(core.Name('u'), value)
        with self.assertRaises(error.UnexpectedType):
            resolver.resolve(name)

    def test_abs_resolve_bound_step_is_bound_uri(self):
        resolver = handler.Resolver(self.env_graph)
        value = core.Value(12345)
        v = core.Name('u', 'v')
        u = core.Name('u')
        u_uri = utils.name_to_uri(u)
        w = core.Name('w')
        uri = utils.contextualise_uri(u_uri, self.env_graph.root_context)

        self.creator.create(w, uri)
        self.creator.create(v, value)
        expected = value
        actually = resolver.resolve(core.Name('w', 'v'))
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
