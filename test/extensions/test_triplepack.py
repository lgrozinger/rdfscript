import unittest
import rdflib

from extensions.triples import TriplePack
from rdfscript.core import (Uri,
                            Value)

from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env

import test.test_helper as test

class TriplePackTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = Uri('http://test.triplepack/#variable', None)
        self.env.assign(self.v_uri,
                        Value(42, None))

        self.template = Template(test.name('A'),
                                  [test.name('x'),
                                   test.name('y')],
                                  [Property(test.name('x'),
                                            Value(42, None),
                                            None),
                                   Property(Uri('http://example.eg/predicate', None),
                                            test.name('y'),
                                            None)],
                                  None,
                                  None)

        self.expansion = Expansion(test.name('e'),
                                   test.name('A'),
                                   [Value(1, None),
                                    Value(2, None)],
                                   [],
                                   None)

        self.template.parameterise()
        self.template.de_name(self.env)
        self.env.assign_template(self.template.name, self.template)

        self.expansion.de_name(self.env)
        triples = self.expansion.as_triples(self.env)
        bindings = self.env._symbol_table
        templates = self.env._template_table

        self.pack = TriplePack(triples, bindings, templates)

    def testDown(self):
        None

    def test_triples_init(self):

        exp_uri = test.name('e').uri(self.env)
        triples = [(exp_uri,
                    Value(1, None),
                    Value(42, None)),
                   (exp_uri,
                    Uri('http://example.eg/predicate', None),
                    Value(2, None))]

        self.assertEqual(self.pack.triples, triples)
        self.assertEqual(self.pack.bindings, self.env._symbol_table)
        self.assertEqual(self.pack.templates, self.env._template_table)

    def test_triples_lookup(self):

        self.assertEqual(self.pack.lookup(self.v_uri), Value(42, None))
        self.assertEqual(self.pack.lookup(Uri('http://triplepack.org/#not', None)), None)

    def test_triples_lookup_template(self):

        self.assertEqual(self.pack.lookup_template(self.template.name), self.template)
        self.assertEqual(self.pack.lookup_template(Uri('http://triplepack.org/#not', None)), None)

    def test_triples_get_subjects_1(self):

        self.assertEqual(self.pack.subjects, set([self.expansion.name]))

    def test_triples_get_subjects_2(self):
        expansion = Expansion(test.name('f'),
                                   test.name('A'),
                                   [Value(1, None),
                                    Value(2, None)],
                                   [],
                                   None)

        expansion.de_name(self.env)
        doublePack = TriplePack(self.pack.triples + expansion.as_triples(self.env),
                                self.pack.bindings,
                                self.pack.templates)

        self.assertEqual(doublePack.subjects, set([self.expansion.name, expansion.name]))

    def test_triples_get_subjects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.subjects, set())

    def test_triples_get_predicates(self):

        self.assertEqual(self.pack.predicates, set([Value(1, None), Uri('http://example.eg/predicate', None)]))

    def test_triples_get_predicates_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.predicates, set())

    def test_triples_get_objects(self):

        self.assertEqual(self.pack.objects, set([Value(2, None), Value(42, None)]))

    def test_triples_get_objects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.objects, set())

    def test_triples_get_triples_by_subject(self):

        expected_result = [(test.name('e').uri(self.env),
                            Value(1, None),
                            Value(42, None)),
                           (test.name('e').uri(self.env),
                            Uri('http://example.eg/predicate', None),
                            Value(2, None))]

        self.assertEqual(self.pack.search((test.name('e').uri(self.env), None, None)),
                         expected_result)

        self.assertEqual(self.pack.search((test.name('f').uri(self.env), None, None)),
                         [])

    def test_triples_get_triples_by_predicate(self):

        self.assertEqual(self.pack.search((None, Value(1, None), None)),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((None, Uri('http://example.eg/predicate', None), None)),
                         [(test.name('e').uri(self.env),
                           Uri('http://example.eg/predicate', None),
                           Value(2, None))])

        self.assertEqual(self.pack.search((None, Value(3, None), None)), [])

    def test_triples_get_triples_by_object(self):

        self.assertEqual(self.pack.search((None, None, Value(42, None))),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((None, None, Value(2, None))),
                         [(test.name('e').uri(self.env),
                           Uri('http://example.eg/predicate', None),
                           Value(2, None))])

        self.assertEqual(self.pack.search((None, None, Value(3, None))), [])

    def test_triples_get_triples_exact(self):

        self.assertEqual(self.pack.search((test.name('e').uri(self.env), Value(1, None), Value(42, None))),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((Value(1, None), Value(2, None), Value(3, None))), [])

    def test_triples_get_triples_subject_predicate(self):

        self.assertEqual(self.pack.search((test.name('e').uri(self.env), Value(1, None), None)),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((test.name('f').uri(self.env), Value(1, None), None)), [])
        self.assertEqual(self.pack.search((test.name('e').uri(self.env), Value(2, None), None)), [])

    def test_triples_get_triples_subject_object(self):

        self.assertEqual(self.pack.search((test.name('e').uri(self.env), None, Value(42, None))),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((test.name('f').uri(self.env), None, Value(42, None))), [])
        self.assertEqual(self.pack.search((test.name('e').uri(self.env), None, Value(41, None))), [])

    def test_triples_get_triples_predicate_object(self):

        self.assertEqual(self.pack.search((None, Value(1, None), Value(42, None))),
                         [(test.name('e').uri(self.env),
                           Value(1, None),
                           Value(42, None))])

        self.assertEqual(self.pack.search((None, Value(2, None), Value(42, None))), [])
        self.assertEqual(self.pack.search((None, Value(1, None), Value(41, None))), [])

    def test_triples_subject_has_property(self):

        self.assertTrue(self.pack.has(test.name('e').uri(self.env), Value(1, None)))
        self.assertFalse(self.pack.has(test.name('e').uri(self.env), Value(2, None)))
        self.assertFalse(self.pack.has(test.name('f').uri(self.env), Value(1, None)))

    def test_triples_subject_has_unique_property(self):

        self.assertTrue(self.pack.has_unique(test.name('e').uri(self.env), Value(1, None)))
        self.assertFalse(self.pack.has_unique(test.name('e').uri(self.env), Value(2, None)))
        self.assertFalse(self.pack.has_unique(test.name('f').uri(self.env), Value(1, None)))

        duplicatePack = TriplePack(self.pack.triples + [(test.name('e').uri(self.env),
                                                         Value(1, None),
                                                         Value(42, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertFalse(duplicatePack.has_unique(test.name('e').uri(self.env), Value(1, None)))

    def test_triples_get_values_for(self):

        self.assertEqual(self.pack.value(test.name('e').uri(self.env), Value(1, None)),
                         Value(42, None))
        self.assertEqual(self.pack.value(test.name('e').uri(self.env), Value(2, None)), None)
        self.assertEqual(self.pack.value(test.name('f').uri(self.env), Value(1, None)), None)

        duplicatePack = TriplePack(self.pack.triples + [(test.name('e').uri(self.env),
                                                         Value(1, None),
                                                         Value(41, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertEqual(duplicatePack.value(test.name('e').uri(self.env), Value(1, None)),
                         [Value(42, None), Value(41, None)])

    def test_triples_add(self):

        self.assertFalse(self.pack.has(test.name('e').uri(self.env), Value('fake', None)))
        self.pack.add((test.name('e').uri(self.env), Value('fake', None), Value('added', None)))
        self.assertTrue(self.pack.has(test.name('e').uri(self.env), Value('fake', None)))
        self.assertEqual(self.pack.value(test.name('e').uri(self.env), Value('fake', None)), Value('added', None))

    def test_triples_set(self):

        self.assertEqual(self.pack.value(test.name('e').uri(self.env), Value(1, None)), Value(42, None))

        self.pack.set(test.name('e').uri(self.env), Value(1, None), Value('set', None))

        self.assertTrue(self.pack.has_unique(test.name('e').uri(self.env), Value(1, None)))
        self.assertEqual(self.pack.value(test.name('e').uri(self.env), Value(1, None)), Value('set', None))

        self.pack.set(test.name('e').uri(self.env), Value('fake', None), Value('set', None))
        self.assertTrue(self.pack.has(test.name('e').uri(self.env), Value('fake', None)))
