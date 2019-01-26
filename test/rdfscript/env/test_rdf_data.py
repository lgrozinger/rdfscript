import unittest
import random
import rdflib

from rdfscript.core import Uri, Value
from rdfscript.rdf_data import RDFData


class RDFDataTest(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_init(self):

        data = RDFData()
        self.assertEqual(data._serializer, None)

        data = RDFData(serializer='turtle')
        self.assertEqual(data._serializer, 'turtle')

    def test_namespace(self):

        data = RDFData()
        self.assertEqual(data.namespace, Uri(
            data._g.identifier.toPython(), None))

    def test_add(self):

        data = RDFData()
        (s, p, o) = (Uri('http://subject.com/', None),
                     Uri('http://predicate.com/', None), Value(123, None))

        data.add(s, p, o)

        rdf_triple = (rdflib.URIRef('http://subject.com/'),
                      rdflib.URIRef('http://predicate.com/'),
                      rdflib.Literal(123))

        self.assertEqual(next(data._g.triples((None, None, None))), rdf_triple)

    def test_get(self):
        data = RDFData()
        s = Uri('http://subject.com/')
        p = Uri('http://predicate.com/')
        o = Value(123)

        data.add(s, p, o)

        expected = [(s, p, o)]
        actually = data.get(s, None, None)
        self.assertEqual(expected, actually)
        actually = data.get(None, p, None)
        self.assertEqual(expected, actually)
        actually = data.get(None, None, o)
        self.assertEqual(expected, actually)

    def test_bind_get_prefix(self):

        data = RDFData()

        prefixes = [p for (p, n) in data._g.namespaces()]
        self.assertFalse('test_prefix' in prefixes)

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        prefixes = list(data._g.namespaces())
        self.assertTrue(('test_prefix', rdflib.URIRef(
            'http://prefix.org/#')) in prefixes)

    def test_uri_for_prefix(self):

        data = RDFData()

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        self.assertEqual(data.uri_for_prefix('test_prefix'),
                         Uri('http://prefix.org/#', None))

    def test_prefix_for_uri(self):

        data = RDFData()

        data.bind_prefix('test_prefix', Uri('http://prefix.org/#', None))

        self.assertEqual(data.prefix_for_uri(
            Uri('http://prefix.org/#', None)), 'test_prefix')

    def test_get_all_triples(self):
        data = RDFData()
        s = Uri('http://subject.com/')
        p = Uri('http://predicate.com/')

        expected = [(s, p, Value(i)) for i in range(0, random.randint(0, 100))]
        for (s, p, o) in expected:
            data.add(s, p, o)

        actually = data.triples
        self.assertEqual(set(expected), set(actually))

    def test_get_all_triples_equal_to_get(self):
        data = RDFData()
        s = Uri('http://subject.com/')
        p = Uri('http://predicate.com/')

        for i in range(0, random.randint(0, 100)):
            data.add(s, p, Value(i))

        with_triples = data.triples
        with_get = data.get(None, None, None)
        self.assertEqual(set(with_triples), set(with_get))
