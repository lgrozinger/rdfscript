import unittest

import rdfscript.core as core
import rdfscript.env as env


class TestTwos(unittest.TestCase):

    def setUp(self):
        self.env = env.Env()

    def tearDown(self):
        pass

    def test_equal_not_equal_perm(self):

        a = core.Name('a')
        b = core.Name('b')

        t1 = core.Two(a, b)
        t2 = core.Two(b, a)

        self.assertFalse(t1 == t2)

    def test_equal_not_equal(self):
        a = core.Name('a')
        b = core.Name('b')
        c = core.Name('c')

        t1 = core.Two(a, b)
        t2 = core.Two(a, c)

        self.assertFalse(t1 == t2)

    def test_equal(self):
        a = core.Name('a')
        b = core.Name('b')

        t1 = core.Two(a, b)
        t2 = core.Two(a, b)

        self.assertTrue(t1 == t2)

    def test_get_property_value(self):
        value = core.Value(42)
        predicate = core.Uri('http://predicate/')
        owner = core.Uri('http://owner/')
        self.env.add_triples([(owner, predicate, value)])

        expected = value
        actually = core.Two(owner, predicate).evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_get_property_value_no_value(self):
        value = core.Value(42)
        predicate = core.Uri('http://predicate/')
        owner = core.Uri('http://owner/')
        self.env.add_triples([(owner, predicate, value)])

        not_owner = core.Uri('http://not-owner/')
        expected = None
        actually = core.Two(not_owner, predicate).evaluate(self.env)
        self.assertEqual(expected, actually)

    def test_get_property_value_lots(self):
        predicate = core.Uri('http://predicate/')
        owner = core.Uri('http://owner/')
        triples = [(owner, predicate, core.Value(i)) for i in range(0, 50)]
        self.env.add_triples(triples)

        expected = [o for (s, p, o) in triples]
        actually = core.Two(owner, predicate).evaluate(self.env)
        self.assertEqual(set(expected), set(actually))
