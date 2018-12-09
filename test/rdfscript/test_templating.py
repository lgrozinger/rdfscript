import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value,
                            Self,
                            Prefix,
                            LocalName)

from rdfscript.template import (Template,
                                Parameter,
                                Property,
                                Expansion,
                                Argument)

from rdfscript.evaluate import evaluate
import test.test_helper as test

class TemplatingTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()
        self.maxDiff = None

        self.templateA = Template(test.name('A'),
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

        self.templateB = Template(test.name('B'),
                                  [],
                                  [Property(test.name('x'),
                                                      test.name('y', p='p'),
                                                      None),
                                             Property(test.name('z'),
                                                      Value("STRING", None),
                                                      None)],
                                  Expansion(test.name('B'),
                                            test.name('A'),
                                            [test.name('x'),
                                             Value("VALUE", None)],
                                            [],
                                            None),
                                  None)

        self.templateC = Template(test.name('C'),
                                  [test.name('x')],
                                  [Property(test.name('x'),
                                                      test.name('y', p='p'),
                                                      None),
                                             Property(test.name('z'),
                                                      Value("STRING", None),
                                                      None)],
                                  Expansion(test.name('C'),
                                            test.name('A'),
                                            [test.name('x'),
                                             Value("VALUE", None)],
                                            [],
                                            None),
                                  None)

    def tearDown(self):
        None

    def test_parameterise_expansion(self):

        template = Template(test.name('A'),
                            [test.name('a'),
                             test.name('b'),
                             test.name('c')],
                            [Property(test.name('a'),
                                      Value(1, None),
                                      None),
                             Property(test.name('x'),
                                      test.name('b'),
                                      None),
                             Property(test.name('c'),
                                      test.name('a'),
                                      None)],
                            None,
                            None)

        expansion = Expansion(test.name('E'),
                              test.name('T'),
                              [test.name('x'),
                               test.name('y'),
                               test.name('z')],
                              [Property(test.name('y'),
                                      Value(1, None),
                                      None),
                               Property(test.name('x'),
                                        test.name('b'),
                                        None),
                               Property(test.name('z'),
                                        test.name('a'),
                                        None)],
                              None)

        expansion.parameterise([Parameter('x', 0, None), Parameter('a', 1, None)])

        parameterised = Expansion(test.name('E'),
                                  test.name('T'),
                                  [Parameter('x', 0, None),
                                   test.name('y'),
                                   test.name('z')],
                                  [Property(test.name('y'),
                                            Value(1, None),
                                            None),
                                   Property(Parameter('x', 0, None),
                                            test.name('b'),
                                            None),
                                   Property(test.name('z'),
                                            Parameter('a', 1, None),
                                            None)],
                                  None)

        self.assertEqual(expansion, parameterised)


    def test_template_as_triples(self):

        template_triples = [(test.name('A').uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (test.name('A').uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Parameter('y', 0, None))]

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.assertEqual(self.templateA.as_triples(self.env), template_triples)

    def test_derived_template_as_triples(self):

        self.env.bind_prefix(Prefix('p', None), Uri('http://eg.test/', None))
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.templateC.parameterise()
        self.templateC.de_name(self.env)

        self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)
        self.env.assign_template(self.env.resolve_name(test.name('C')), self.templateC)

        template_triples = [(test.name('C').uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (test.name('C').uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Value("VALUE", None)),
                            (test.name('C').uri(self.env),
                             Parameter('x', 0, None),
                             test.name('y', p='p').uri(self.env)),
                            (test.name('C').uri(self.env),
                             test.name('z').uri(self.env),
                             Value("STRING", None))]

        self.assertEqual(self.env.lookup_template(self.env.resolve_name(test.name('C'))).as_triples(self.env), template_triples)

    def test_expansion_as_triples(self):

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)

        expansion = Expansion(test.name('E'),
                              test.name('A'),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [],
                              None)

        expansion.de_name(self.env)

        expansion_triples = [(test.name('E').uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (test.name('E').uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value(True, None))]

        self.assertEqual(expansion.as_triples(self.env), expansion_triples)

    def test_double_expansion_as_triples(self):

        self.env.bind_prefix(Prefix('p', None), Uri('http://eg.test/', None))
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.templateC.parameterise()
        self.templateC.de_name(self.env)

        self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)
        self.env.assign_template(self.env.resolve_name(test.name('C')), self.templateC)

        expansion = Expansion(test.name('E'),
                              test.name('C'),
                              [Uri('http://uri.org/x', None)],
                              [],
                              None)

        expansion.de_name(self.env)

        expansion_triples = [(test.name('E').uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (test.name('E').uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value("VALUE", None)),
                             (test.name('E').uri(self.env),
                              Uri('http://uri.org/x', None),
                              test.name('y', p='p').uri(self.env)),
                             (test.name('E').uri(self.env),
                              test.name('z').uri(self.env),
                              Value("STRING", None))]

        self.assertEqual(expansion_triples, expansion.as_triples(self.env))

    def test_default_prefixed_template(self):

        self.env.bind_prefix(Prefix('eg', None), Uri('http://eg.org/', None))
        self.env.set_default_prefix(Prefix('eg', None))

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)

        template_triples = [(test.name('A', p='eg').uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (test.name('A', p='eg').uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Parameter('y', 0, None))]

        self.assertEqual(template_triples,
                         self.env.lookup_template(self.env.resolve_name(test.name('A', p='eg'))).as_triples(self.env))

    def test_default_prefixed_template_expansion(self):
            self.env.bind_prefix(Prefix('eg', None), Uri('http://eg.org/', None))
            self.env.set_default_prefix(Prefix('eg', None))

            self.templateA.parameterise()
            self.templateA.de_name(self.env)
            self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)

            expansion = Expansion(test.name('E'),
                                  test.name('A', p='eg'),
                                  [Uri('http://uri.org/x', None),
                                   Value(True, None)],
                                  [],
                                  None)

            expansion.de_name(self.env)
            expansion_triples = [(test.name('E').uri(self.env),
                                  Uri('http://uri.org/x', None),
                                  Value(42, None)),
                                 (test.name('E').uri(self.env),
                                  Uri('http://example.eg/predicate', None),
                                  Value(True, None))]

            self.assertEqual(expansion_triples, expansion.as_triples(self.env))

    def test_self_in_expansion(self):
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(test.name('A')), self.templateA)

        expansion = Expansion(test.name('E'),
                              test.name('A'),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [Property(Uri('http://me.org/myself', None),
                                        Self(None),
                                        None),
                               Property(Uri('http://me.org/child', None),
                                        Self(None, localname=LocalName('child', None)),
                                        None)],
                              None)

        expansion_triples = [(test.name('E').uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (test.name('E').uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value(True, None)),
                             (test.name('E').uri(self.env),
                              Uri('http://me.org/myself', None),
                              test.name('E').uri(self.env)),
                             (test.name('E').uri(self.env),
                              Uri('http://me.org/child', None),
                              Uri(test.name('E').uri(self.env).uri + 'child', None))]

        expansion.de_name(self.env)
        self.assertEqual(expansion_triples, expansion.replace_self(expansion.as_triples(self.env), self.env))

    def test_self_in_template(self):
        templateA = Template(test.name('A'),
                                  [],
                                  [],
                                  Expansion(test.name('A'),
                                            test.name('B'),
                                            [],
                                            [Property(test.name('x'),
                                                      Value(42, None),
                                                      None),
                                             Property(Uri('http://example.eg/predicate', None),
                                                      Self(None),
                                                      None)],
                                            None),
                             None)

        templateB = Template(test.name('B'),
                                  [],
                                  [Property(test.name('x'),
                                            Self(None),
                                            None),
                                   Property(test.name('child'),
                                            Self(None, localname=LocalName('child', None)),
                                            None)],
                                  None,
                                  None)
        templateA.parameterise()
        templateB.parameterise()
        templateA.de_name(self.env)
        templateB.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(test.name('A')), templateA)
        self.env.assign_template(self.env.resolve_name(test.name('B')), templateB)

        expansion = Expansion(test.name('E'),
                              test.name('A'),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [Property(Uri('http://me.org/myself', None),
                                        Self(None),
                                        None)],
                              None)

        expansion.de_name(self.env)

        expansion_triples = [(test.name('E').uri(self.env),
                              test.name('x').uri(self.env),
                              test.name('E').uri(self.env)),
                             (test.name('E').uri(self.env),
                              test.name('child').uri(self.env),
                              Uri(test.name('E').uri(self.env).uri + 'child', None)),
                             (test.name('E').uri(self.env),
                              test.name('x').uri(self.env),
                              Value(42, None)),
                             (test.name('E').uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              test.name('E').uri(self.env)),
                             (test.name('E').uri(self.env),
                              Uri('http://me.org/myself', None),
                              test.name('E').uri(self.env))]

        self.assertEqual(expansion_triples, expansion.replace_self(expansion.as_triples(self.env), self.env))
