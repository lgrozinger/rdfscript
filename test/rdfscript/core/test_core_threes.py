import unittest
import rdflib

import rdfscript.core as core
import rdfscript.rdfscriptparser as parser
import rdfscript.error as error
import rdfscript.evaluate as evaluate
import rdfscript.runtime as runtime


class TestThrees(unittest.TestCase):

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
        rt = runtime.Runtime()

        expected = (rdflib.URIRef('one'),
                    rdflib.URIRef('two'),
                    rdflib.URIRef('three'))

        graph = rt._g.graph.triples((None, None, None))
        self.assertFalse(expected in graph)

        t = self.parser.parse('one > two > three')[0]
        rt.bind(core.Uri('one'), core.Name('one'))
        rt.bind(core.Uri('two'), core.Name('two'))
        rt.bind(core.Uri('three'), core.Name('three'))
        evaluate.evaluate(t, rt)
        graph = rt._g.graph.triples((None, None, None))

        self.assertTrue(expected in graph)

    def test_evaluate_name_uri_value(self):
        rt = runtime.Runtime()

        expected = (rdflib.URIRef('one'),
                    rdflib.URIRef('two'),
                    rdflib.Literal(3))

        graph = rt._g.graph.triples((None, None, None))
        self.assertFalse(expected in graph)

        t = self.parser.parse('one > <two> > 3')[0]
        rt.bind(core.Uri('one'), core.Name('one'))
        evaluate.evaluate(t, rt)
        graph = rt._g.graph.triples((None, None, None))
        self.assertTrue(expected in graph)

    def test_evaluate_value_value_value(self):
        rt = runtime.Runtime()

        with self.assertRaises(error.UnexpectedType):
            t = self.parser.parse('1 > 2 > 3')[0]
            evaluate.evaluate(t, rt)
