import unittest

from extensions.triples import TriplePack
import rdfscript.core as core
from rdfscript.template import (Template,
                                Property,
                                Expansion)
from rdfscript.env import Env


def triple_eval(triple, env):
    (s, p, o) = triple
    s = s.evaluate(env)
    p = p.evaluate(env)
    o = o.evaluate(env)

    return (s, p, o)


class TriplePackTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

        self.v_uri = core.Uri('http://test.triplepack/#variable')
        do_assign(self.v_uri, core.Value(42), self.env)

        self.template = Template(core.Name('A'),
                                 [core.Name('x'),
                                  core.Name('y')],
                                 [Property(core.Name('x'),
                                           core.Value(42)),
                                  Property(core.Uri('http://example.eg/predicate'),
                                           core.Name('y'))])

        self.expansion = Expansion(core.Name('e'),
                                   core.Name('A'),
                                   [core.Value(1),
                                    core.Value(2)],
                                   [])
        self.template.evaluate(self.env)

        triples = self.expansion.as_triples(self.env)
        triples = [triple_eval(triple, self.env) for triple in triples]

        bindings = self.env._rdf.get(None, core.identity, None)
        symbol_table = dict()
        for (s, p, o) in bindings:
            symbol_table[s] = o

        templates = self.env._template_table

        self.pack = TriplePack(triples, symbol_table, templates)

    def testDown(self):
        None

    def test_triples_init(self):

        exp_uri = core.Name('e').evaluate(self.env)
        triples = [(exp_uri,
                    core.Value(1),
                    core.Value(42)),
                   (exp_uri,
                    core.Uri('http://example.eg/predicate'),
                    core.Value(2))]

        self.assertEqual(self.pack.triples, triples)
        self.assertEqual(self.pack.bindings, {self.v_uri: core.Value(42)})
        self.assertEqual(self.pack.templates, self.env._template_table)

    def test_triples_lookup(self):

        self.assertEqual(self.pack.lookup(self.v_uri), core.Value(42))
        self.assertEqual(self.pack.lookup(
            core.Uri('http://triplepack.org/#not')), None)

    def test_triples_lookup_template(self):

        self.assertEqual(self.pack.lookup_template(self.template.name.evaluate(self.env)),
                         self.template.as_triples(self.env))
        self.assertEqual(self.pack.lookup_template(
            core.Uri('http://triplepack.org/#not')), None)

    def test_triples_get_subjects_1(self):

        self.assertEqual(self.pack.subjects, set(
            [self.expansion.name.evaluate(self.env)]))

    def test_triples_get_subjects_2(self):
        expansion = Expansion(core.Name('f'),
                              core.Name('A'),
                              [core.Value(1),
                               core.Value(2)],
                              [])

        triples = expansion.as_triples(self.env)
        triples = [triple_eval(triple, self.env) for triple in triples]
        doublePack = TriplePack(self.pack.triples + triples,
                                self.pack.bindings,
                                self.pack.templates)

        self.assertEqual(doublePack.subjects, set([self.expansion.name.evaluate(self.env),
                                                   expansion.name.evaluate(self.env)]))

    def test_triples_get_subjects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.subjects, set())

    def test_triples_get_predicates(self):

        self.assertEqual(self.pack.predicates, set(
            [core.Value(1), core.Uri('http://example.eg/predicate')]))

    def test_triples_get_predicates_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.predicates, set())

    def test_triples_get_objects(self):

        self.assertEqual(self.pack.objects, set(
            [core.Value(2), core.Value(42)]))

    def test_triples_get_objects_empty(self):
        emptyPack = TriplePack([], {}, {})

        self.assertEqual(emptyPack.objects, set())

    def test_triples_get_triples_by_subject(self):

        expected_result = [(core.Name('e').evaluate(self.env),
                            core.Value(1),
                            core.Value(42)),
                           (core.Name('e').evaluate(self.env),
                            core.Uri('http://example.eg/predicate'),
                            core.Value(2))]

        self.assertEqual(self.pack.search((core.Name('e').evaluate(self.env), None, None)),
                         expected_result)

        self.assertEqual(self.pack.search((core.Name('f').evaluate(self.env), None, None)),
                         [])

    def test_triples_get_triples_by_predicate(self):

        self.assertEqual(self.pack.search((None, core.Value(1), None)),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1),
                           core.Value(42))])

        self.assertEqual(self.pack.search((None, core.Uri('http://example.eg/predicate'), None)),
                         [(core.Name('e').evaluate(self.env),
                           core.Uri('http://example.eg/predicate'),
                           core.Value(2))])

        self.assertEqual(self.pack.search((None, core.Value(3), None)), [])

    def test_triples_get_triples_by_object(self):

        self.assertEqual(self.pack.search((None, None, core.Value(42))),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1),
                           core.Value(42))])

        self.assertEqual(self.pack.search((None, None, core.Value(2))),
                         [(core.Name('e').evaluate(self.env),
                           core.Uri('http://example.eg/predicate'),
                           core.Value(2))])

        self.assertEqual(self.pack.search((None, None, core.Value(3))), [])

    def test_triples_get_triples_exact(self):

        self.assertEqual(self.pack.search((core.Name('e').evaluate(self.env), core.Value(1), core.Value(42))),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1),
                           core.Value(42))])

        self.assertEqual(self.pack.search(
            (core.Value(1), core.Value(2, None), core.Value(3, None))), [])

    def test_triples_get_triples_subject_predicate(self):

        self.assertEqual(self.pack.search((core.Name('e').evaluate(self.env), core.Value(1, None), None)),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1, None),
                           core.Value(42, None))])

        self.assertEqual(self.pack.search(
            (core.Name('f').evaluate(self.env), core.Value(1, None), None)), [])
        self.assertEqual(self.pack.search(
            (core.Name('e').evaluate(self.env), core.Value(2, None), None)), [])

    def test_triples_get_triples_subject_object(self):

        self.assertEqual(self.pack.search((core.Name('e').evaluate(self.env), None, core.Value(42, None))),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1, None),
                           core.Value(42, None))])

        self.assertEqual(self.pack.search(
            (core.Name('f').evaluate(self.env), None, core.Value(42, None))), [])
        self.assertEqual(self.pack.search(
            (core.Name('e').evaluate(self.env), None, core.Value(41, None))), [])

    def test_triples_get_triples_predicate_object(self):

        self.assertEqual(self.pack.search((None, core.Value(1, None), core.Value(42, None))),
                         [(core.Name('e').evaluate(self.env),
                           core.Value(1, None),
                           core.Value(42, None))])

        self.assertEqual(self.pack.search(
            (None, core.Value(2, None), core.Value(42, None))), [])
        self.assertEqual(self.pack.search(
            (None, core.Value(1, None), core.Value(41, None))), [])

    def test_triples_subject_has_property(self):

        self.assertTrue(self.pack.has(
            core.Name('e').evaluate(self.env), core.Value(1, None)))
        self.assertFalse(self.pack.has(
            core.Name('e').evaluate(self.env), core.Value(2, None)))
        self.assertFalse(self.pack.has(
            core.Name('f').evaluate(self.env), core.Value(1, None)))

    def test_triples_subject_has_unique_property(self):

        self.assertTrue(self.pack.has_unique(
            core.Name('e').evaluate(self.env), core.Value(1, None)))
        self.assertFalse(self.pack.has_unique(
            core.Name('e').evaluate(self.env), core.Value(2, None)))
        self.assertFalse(self.pack.has_unique(
            core.Name('f').evaluate(self.env), core.Value(1, None)))

        duplicatePack = TriplePack(self.pack.triples + [(core.Name('e').evaluate(self.env),
                                                         core.Value(1, None),
                                                         core.Value(42, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertFalse(duplicatePack.has_unique(
            core.Name('e').evaluate(self.env), core.Value(1, None)))

    def test_triples_get_values_for(self):

        self.assertEqual(self.pack.value(core.Name('e').evaluate(self.env), core.Value(1, None)),
                         core.Value(42, None))
        self.assertEqual(self.pack.value(
            core.Name('e').evaluate(self.env), core.Value(2, None)), None)
        self.assertEqual(self.pack.value(
            core.Name('f').evaluate(self.env), core.Value(1, None)), None)

        duplicatePack = TriplePack(self.pack.triples + [(core.Name('e').evaluate(self.env),
                                                         core.Value(1, None),
                                                         core.Value(41, None))],
                                   self.pack.bindings,
                                   self.pack.templates)

        self.assertEqual(duplicatePack.value(core.Name('e').evaluate(self.env), core.Value(1, None)),
                         [core.Value(42, None), core.Value(41, None)])

    def test_triples_add(self):

        self.assertFalse(self.pack.has(
            core.Name('e').evaluate(self.env), core.Value('fake', None)))
        self.pack.add((core.Name('e').evaluate(self.env), core.Value(
            'fake', None), core.Value('added', None)))
        self.assertTrue(self.pack.has(
            core.Name('e').evaluate(self.env), core.Value('fake', None)))
        self.assertEqual(self.pack.value(core.Name('e').evaluate(
            self.env), core.Value('fake', None)), core.Value('added', None))

    def test_triples_set(self):

        self.assertEqual(self.pack.value(core.Name('e').evaluate(
            self.env), core.Value(1, None)), core.Value(42, None))

        self.pack.set(core.Name('e').evaluate(self.env),
                      core.Value(1, None), core.Value('set', None))

        self.assertTrue(self.pack.has_unique(
            core.Name('e').evaluate(self.env), core.Value(1, None)))
        self.assertEqual(self.pack.value(core.Name('e').evaluate(
            self.env), core.Value(1, None)), core.Value('set', None))

        self.pack.set(core.Name('e').evaluate(self.env),
                      core.Value('fake', None), core.Value('set', None))
        self.assertTrue(self.pack.has(
            core.Name('e').evaluate(self.env), core.Value('fake', None)))


def do_assign(name, value, env):
    core.Assignment(name, value).evaluate(env)
