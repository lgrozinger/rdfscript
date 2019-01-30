import unittest

import rdfscript.runtime as runtime
import rdfscript.core as core


class TestRuntime(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_prefix(self):
        rt = runtime.Runtime()
        expected = None
        actually = rt.prefix

        self.assertEqual(expected, actually)

    def test_empty_namespace_on_init(self):
        rt = runtime.Runtime()
        expected = []
        actually = rt._g.root_context.get_all()

        self.assertEqual(expected, actually)
        actually = rt._g.root_context.get_all_triples()
        self.assertEqual(expected, actually)

    def test_bind(self):
        rt = runtime.Runtime()
        name = core.Name('v')
        value = core.Value(12345)
        rt.bind(value, name)

        expected = value
        actually = rt._resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_bind_levels(self):
        rt = runtime.Runtime()
        name = core.Name('v', 'u')
        value = core.Value(12345)
        rt.bind(value, name)

        expected = value
        actually = rt._resolver.resolve(name)
        self.assertEqual(expected, actually)

    def test_bound_p_true(self):
        rt = runtime.Runtime()
        name = core.Name('v')
        value = core.Value(12345)
        rt.bind(value, name)

        self.assertTrue(rt.bound_p(name))

    def test_bound_p_true_levels(self):
        rt = runtime.Runtime()
        name = core.Name('v', 'u')
        value = core.Value(12345)
        rt.bind(value, name)

        self.assertTrue(rt.bound_p(name))

    def test_bound_p_false(self):
        rt = runtime.Runtime()
        v = core.Name('v')
        u = core.Name('u')
        value = core.Value(12345)
        rt.bind(value, v)

        self.assertFalse(rt.bound_p(u))

    def test_bound_p_false_levels(self):
        rt = runtime.Runtime()
        u = core.Name('v', 'u')
        w = core.Name('v', 'w')
        value = core.Value(12345)
        rt.bind(value, u)

        self.assertFalse(rt.bound_p(w))

    def test_bound_p_intermediate_value(self):
        rt = runtime.Runtime()
        v = core.Name('v')
        w = core.Name('v', 'w')
        value = core.Value(12345)
        rt.bind(value, v)

        self.assertFalse(rt.bound_p(w))

    def test_add_prefix(self):
        rt = runtime.Runtime()
        name = core.Name('Prefix')
        uri = core.Uri('http://prefix/')

        rt.add_prefix(name, uri)
        expected = uri
        actually = rt._g.prefix_to_uri(name)
        self.assertEqual(expected, actually)

    def test_set_prefix(self):
        rt = runtime.Runtime()
        name = core.Name('Prefix')
        uri = core.Uri('http://prefix/')

        rt.add_prefix(name, uri)
        rt.prefix = name
        expected = name
        actually = rt.prefix
        self.assertEqual(expected, actually)
