import unittest

import rdfscript.core as core
import rdfscript.utils as utils
import rdfscript.runtime as runtime
import rdfscript.evaluate as evaluate
import rdfscript.rdfscriptparser as parser


class TestTwos(unittest.TestCase):

    def setUp(self):
        self.rt = runtime.Runtime()
        self.parser = parser.RDFScriptParser()

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
        three = self.parser.parse('<http://pred/> > <http://owner/> > 42')[0]
        evaluate.evaluate(three, self.rt)

        expected = core.Value(42)
        actually = evaluate.evaluate(core.Two(three.one, three.two), self.rt)
        self.assertEqual(expected, actually)

    def test_get_property_value_no_value(self):
        three = self.parser.parse('<http://pred/> > <http://owner/> > 42')[0]
        evaluate.evaluate(three, self.rt)

        not_owner = core.Uri('http://not-owner/')
        expected = None
        actually = evaluate.evaluate(core.Two(not_owner, three.two), self.rt)
        self.assertEqual(expected, actually)

    @unittest.skip("Lists not implemented")
    def test_get_property_value_lots(self):
        predicate = core.Uri('http://predicate/')
        owner = core.Uri('http://owner/')
        triples = [(owner, predicate, core.Value(i)) for i in range(0, 50)]
        self.rt._g.graph.add(utils.to_rdf_triples(triples))

        expected = [o for (s, p, o) in triples]
        actually = evaluate.evaluate(core.Two(owner, predicate), self.rt)
        self.assertEqual(set(expected), set(actually))
