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
                            Self)

from rdfscript.template import (Template,
                                Parameter,
                                Property,
                                Expansion,
                                Argument)

from rdfscript.evaluate import evaluate

class TemplatingTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()
        self.maxDiff = None

        self.templateA = Template(Name(None, 'A', None),
                                  [Name(None, 'x', None),
                                   Name(None, 'y', None)],
                                  [Property(Name(None, 'x', None),
                                            Value(42, None),
                                            None),
                                   Property(Uri('http://example.eg/predicate', None),
                                            Name(None, 'y', None),
                                            None)],
                                  None,
                                  None)

        self.templateB = Template(Name(None, 'B', None),
                                  [],
                                  [Property(Name(None, 'x', None),
                                                      Name('p', 'y', None),
                                                      None),
                                             Property(Name(None, 'z', None),
                                                      Value("STRING", None),
                                                      None)],
                                  Expansion(Name(None, 'B', None),
                                            Name(None, 'A', None),
                                            [Name(None, 'x', None),
                                             Value("VALUE", None)],
                                            [],
                                            None),
                                  None)

        self.templateC = Template(Name(None, 'C', None),
                                  [Name(None, 'x', None)],
                                  [Property(Name(None, 'x', None),
                                                      Name('p', 'y', None),
                                                      None),
                                             Property(Name(None, 'z', None),
                                                      Value("STRING", None),
                                                      None)],
                                  Expansion(Name(None, 'C', None),
                                            Name(None, 'A', None),
                                            [Name(None, 'x', None),
                                             Value("VALUE", None)],
                                            [],
                                            None),
                                  None)

    def tearDown(self):
        None

    def test_parameterise_expansion(self):

        template = Template(Name(None, 'A', None),
                            [Name(None, 'a', None),
                             Name(None, 'b', None),
                             Name(None, 'c', None)],
                            [Property(Name(None, 'a', None),
                                      Value(1, None),
                                      None),
                             Property(Name(None, 'x', None),
                                      Name(None, 'b', None),
                                      None),
                             Property(Name(None, 'c', None),
                                      Name(None, 'a', None),
                                      None)],
                            None,
                            None)

        expansion = Expansion(Name(None, 'E', None),
                              Name(None, 'T', None),
                              [Name(None, 'x', None),
                               Name(None, 'y', None),
                               Name(None, 'z', None)],
                              [Property(Name(None, 'y', None),
                                      Value(1, None),
                                      None),
                               Property(Name(None, 'x', None),
                                        Name(None, 'b', None),
                                        None),
                               Property(Name(None, 'z', None),
                                        Name(None, 'a', None),
                                        None)],
                              None)

        expansion.parameterise([Parameter('x', 0, None), Parameter('a', 1, None)])

        parameterised = Expansion(Name(None, 'E', None),
                                  Name(None, 'T', None),
                                  [Parameter('x', 0, None),
                                   Name(None, 'y', None),
                                   Name(None, 'z', None)],
                                  [Property(Name(None, 'y', None),
                                            Value(1, None),
                                            None),
                                   Property(Parameter('x', 0, None),
                                            Name(None, 'b', None),
                                            None),
                                   Property(Name(None, 'z', None),
                                            Parameter('a', 1, None),
                                            None)],
                                  None)

        self.assertEqual(expansion, parameterised)


    def test_template_as_triples(self):

        template_triples = [(Name(None, 'A', None).as_uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (Name(None, 'A', None).as_uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Parameter('y', 0, None))]

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.assertEqual(self.templateA.as_triples(self.env), template_triples)

    def test_derived_template_as_triples(self):

        self.env.bind_prefix('p', rdflib.URIRef('http://eg.test/'))
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.templateC.parameterise()
        self.templateC.de_name(self.env)

        self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)
        self.env.assign_template(self.env.resolve_name(None, 'C'), self.templateC)

        template_triples = [(Name(None, 'C', None).as_uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (Name(None, 'C', None).as_uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Value("VALUE", None)),
                            (Name(None, 'C', None).as_uri(self.env),
                             Parameter('x', 0, None),
                             Name('p', 'y', None).as_uri(self.env)),
                            (Name(None, 'C', None).as_uri(self.env),
                             Name(None, 'z', None).as_uri(self.env),
                             Value("STRING", None))]

        self.assertEqual(self.env.lookup_template(self.env.resolve_name(None, 'C')).as_triples(self.env), template_triples)

    def test_expansion_as_triples(self):

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)

        expansion = Expansion(Name(None, 'E', None),
                              Name(None, 'A', None),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [],
                              None)

        expansion.de_name(self.env)

        expansion_triples = [(Name(None, 'E', None).as_uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value(True, None))]

        self.assertEqual(expansion.as_triples(self.env), expansion_triples)

    def test_double_expansion_as_triples(self):

        self.env.bind_prefix('p', rdflib.URIRef('http://eg.test/'))
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.templateC.parameterise()
        self.templateC.de_name(self.env)

        self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)
        self.env.assign_template(self.env.resolve_name(None, 'C'), self.templateC)

        expansion = Expansion(Name(None, 'E', None),
                              Name(None, 'C', None),
                              [Uri('http://uri.org/x', None)],
                              [],
                              None)
        
        expansion.de_name(self.env)

        expansion_triples = [(Name(None, 'E', None).as_uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value("VALUE", None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://uri.org/x', None),
                              Name('p', 'y', None).as_uri(self.env)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Name(None, 'z', None).as_uri(self.env),
                              Value("STRING", None))]

        self.assertEqual(expansion_triples, expansion.as_triples(self.env))

    def test_default_prefixed_template(self):

        self.env.bind_prefix('eg', rdflib.URIRef('http://eg.org/'))
        self.env.set_default_prefix('eg')

        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)

        template_triples = [(Name('eg', 'A', None).as_uri(self.env),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (Name('eg', 'A', None).as_uri(self.env),
                             Uri('http://example.eg/predicate', None),
                             Parameter('y', 0, None))]

        self.assertEqual(template_triples,
                         self.env.lookup_template(self.env.resolve_name('eg', 'A')).as_triples(self.env))

    def test_default_prefixed_template_expansion(self):
            self.env.bind_prefix('eg', rdflib.URIRef('http://eg.org/'))
            self.env.set_default_prefix('eg')

            self.templateA.parameterise()
            self.templateA.de_name(self.env)
            self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)

            expansion = Expansion(Name(None, 'E', None),
                                  Name('eg', 'A', None),
                                  [Uri('http://uri.org/x', None),
                                   Value(True, None)],
                                  [],
                                  None)

            expansion.de_name(self.env)
            expansion_triples = [(Name(None, 'E', None).as_uri(self.env),
                                  Uri('http://uri.org/x', None),
                                  Value(42, None)),
                                 (Name(None, 'E', None).as_uri(self.env),
                                  Uri('http://example.eg/predicate', None),
                                  Value(True, None))]

            self.assertEqual(expansion_triples, expansion.as_triples(self.env))

    def test_self_in_expansion(self):
        self.templateA.parameterise()
        self.templateA.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(None, 'A'), self.templateA)

        expansion = Expansion(Name(None, 'E', None),
                              Name(None, 'A', None),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [Property(Uri('http://me.org/myself', None),
                                        Self(None),
                                        None)],
                              None)

        expansion_triples = [(Name(None, 'E', None).as_uri(self.env),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Value(True, None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://me.org/myself', None),
                              Name(None, 'E', None).as_uri(self.env))]

        expansion.de_name(self.env)
        self.assertEqual(expansion_triples, expansion.replace_self(expansion.as_triples(self.env)))

    def test_self_in_template(self):
        templateA = Template(Name(None, 'A', None),
                                  [],
                                  [],
                                  Expansion(Name(None, 'A', None),
                                            Name(None, 'B', None),
                                            [],
                                            [Property(Name(None, 'x', None),
                                                      Value(42, None),
                                                      None),
                                             Property(Uri('http://example.eg/predicate', None),
                                                      Self(None),
                                                      None)],
                                            None),
                             None)

        templateB = Template(Name(None, 'B', None),
                                  [],
                                  [Property(Name(None, 'x', None),
                                            Self(None),
                                            None)],
                                  None,
                                  None)
        templateA.parameterise()
        templateB.parameterise()
        templateA.de_name(self.env)
        templateB.de_name(self.env)
        self.env.assign_template(self.env.resolve_name(None, 'A'), templateA)
        self.env.assign_template(self.env.resolve_name(None, 'B'), templateB)

        expansion = Expansion(Name(None, 'E', None),
                              Name(None, 'A', None),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [Property(Uri('http://me.org/myself', None),
                                        Self(None),
                                        None)],
                              None)

        expansion.de_name(self.env)

        expansion_triples = [(Name(None, 'E', None).as_uri(self.env),
                              Name(None, 'x', None).as_uri(self.env),
                              Name(None, 'E', None).as_uri(self.env)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Name(None, 'x', None).as_uri(self.env),
                              Value(42, None)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://example.eg/predicate', None),
                              Name(None, 'E', None).as_uri(self.env)),
                             (Name(None, 'E', None).as_uri(self.env),
                              Uri('http://me.org/myself', None),
                              Name(None, 'E', None).as_uri(self.env))]

        self.assertEqual(expansion_triples, expansion.replace_self(expansion.as_triples(self.env)))
