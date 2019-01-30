import unittest
import rdflib

import rdfscript.core as core
import rdfscript.context as context
import rdfscript.error as err
from rdfscript.utils import to_rdf
from rdfscript.utils import from_rdf
from rdfscript.utils import from_rdf_triples
from rdfscript.utils import to_rdf_triples
from rdfscript.utils import name_to_uri
from rdfscript.utils import contextualise_uri
from rdfscript.utils import type_assert


class TestRDFLibUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_to_rdf_uri(self):

        uri = core.Uri('http://test.org/#')

        self.assertEqual(rdflib.URIRef('http://test.org/#'), to_rdf(uri))
        self.assertEqual(rdflib.URIRef(''), to_rdf(core.Uri('')))

    def test_to_rdf_value(self):
        self.assertEqual(rdflib.Literal(42), to_rdf(core.Value(42)))
        self.assertEqual(rdflib.Literal("s"), to_rdf(core.Value("s")))
        self.assertEqual(rdflib.Literal(True), to_rdf(core.Value(True)))
        self.assertEqual(rdflib.Literal(0.123), to_rdf(core.Value(0.123)))

    def test_from_rdf_uri(self):
        u1 = 'http://namespace.eg/'
        u2 = 'http://uri.org/'
        self.assertEqual(core.Uri(u1), from_rdf(rdflib.Namespace(u1)))
        self.assertEqual(core.Uri(u2), from_rdf(rdflib.URIRef(u2)))

        bnode = rdflib.BNode()
        self.assertEqual(core.Uri(bnode.toPython()), from_rdf(bnode))

    def test_from_rdf_value(self):
        self.assertEqual(core.Value(42), from_rdf(rdflib.Literal(42)))
        self.assertEqual(core.Value(False), from_rdf(rdflib.Literal(False)))
        self.assertEqual(core.Value("s"), from_rdf(rdflib.Literal("s")))

    def test_triples_from_rdf_empty(self):
        triples = []
        expected = []
        actually = from_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_triples_from_rdf_one(self):
        triples = [(rdflib.URIRef('subject'),
                    rdflib.URIRef('predicate'),
                    rdflib.Literal("value"))]

        expected = [(core.Uri('subject'),
                     core.Uri('predicate'),
                     core.Value("value"))]
        actually = from_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_triples_from_rdf_several(self):
        triples = [(rdflib.URIRef('subject'),
                    rdflib.URIRef('predicate'),
                    rdflib.Literal("value"))] * 10

        expected = [(core.Uri('subject'),
                     core.Uri('predicate'),
                     core.Value("value"))] * 10
        actually = from_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_triples_to_rdf_empty(self):
        triples = []
        expected = []
        actually = to_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_triples_to_rdf_one(self):
        triples = [(core.Uri('subject'),
                    core.Uri('predicate'),
                    core.Value("value"))]

        expected = [(rdflib.URIRef('subject'),
                     rdflib.URIRef('predicate'),
                     rdflib.Literal("value"))]
        actually = to_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_triples_to_rdf_several(self):
        triples = [(core.Uri('subject'),
                    core.Uri('predicate'),
                    core.Value("value"))] * 10

        expected = [(rdflib.URIRef('subject'),
                     rdflib.URIRef('predicate'),
                     rdflib.Literal("value"))] * 10
        actually = to_rdf_triples(triples)
        self.assertEqual(expected, actually)

    def test_name_to_uri(self):
        name = core.Name(core.Uri('https://name/'), 'name')
        expected = core.Uri('https://name/name')
        actually = name_to_uri(name)
        self.assertEqual(expected, actually)

    def test_contextualise_uri(self):
        c = context.Context(rdflib.Graph())
        uri = core.Uri('uri')
        root = from_rdf(c._graph.identifier)
        expected = core.Uri(root.uri + 'uri')
        actually = contextualise_uri(uri, c)
        self.assertEqual(expected, actually)

    def test_type_assert_incorrect_type_single(self):

        with self.assertRaises(err.UnexpectedType):
            type_assert(core.Name(''), core.Uri)

    def test_type_assert_incorrect_type_multiple(self):

        with self.assertRaises(err.UnexpectedType):
            type_assert(core.Name(''), core.Uri, core.Self)

    def test_type_assert_correct_type_single(self):

        type_assert(core.Uri(''), core.Uri)

    def test_type_assert_correct_type_multiple(self):

        type_assert(core.Uri(''), core.Name, core.Uri)
