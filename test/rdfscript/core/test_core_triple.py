import unittest
import rdflib

import rdfscript.core as core
import rdfscript.env as env
import rdfscript.rdfscriptparser as parser
import rdfscript.error as error


class TripleTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_equal_not_equal_perm(self):

        a = core.Name('a')
        b = core.Name('b')
        c = core.Name('c')

        t1 = core.Three(a, b, c)
        t2 = core.Three(b, c, a)

        self.assertFalse(t1 == t2)

    def test_equal_not_equal(self):
        a = core.Name('a')
        b = core.Name('b')
        c = core.Name('c')
        d = core.Name('d')

        t1 = core.Three(a, b, c)
        t2 = core.Three(a, b, d)

        self.assertFalse(t1 == t2)

    def test_equal(self):
        a = core.Name('a')
        b = core.Name('b')
        c = core.Name('c')

        t1 = core.Three(a, b, c)
        t2 = core.Three(a, b, c)

        self.assertTrue(t1 == t2)

    def test_evaluate_3_names(self):
        context = env.Env()

        expected = (rdflib.URIRef('one'),
                    rdflib.URIRef('two'),
                    rdflib.URIRef('three'))

        graph = context._rdf._g.triples((None, None, None))
        self.assertFalse(expected in graph)

        t = self.parser.parse('one > two > three')[0]
        t.evaluate(context)
        graph = context._rdf._g.triples((None, None, None))
        self.assertTrue(expected in graph)

    def test_evaluate_name_uri_value(self):
        context = env.Env()

        expected = (rdflib.URIRef('one'),
                    rdflib.URIRef('two'),
                    rdflib.Literal(3))

        graph = context._rdf._g.triples((None, None, None))
        self.assertFalse(expected in graph)

        t = self.parser.parse('one > <two> > 3')[0]
        t.evaluate(context)
        graph = context._rdf._g.triples((None, None, None))
        self.assertTrue(expected in graph)

    def test_evaluate_value_value_value(self):
        context = env.Env()

        with self.assertRaises(error.UnexpectedType):
            t = self.parser.parse('1 > 2 > 3')[0]
            t.evaluate(context)
