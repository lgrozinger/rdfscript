import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Value)
from rdfscript.templating import (Template,
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
                                  ['x', 'y'],
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
                                  None,
                                  Expansion(Name(None, 'A', None),
                                            Name(None, 'B', None),
                                            [Argument(Name(None, 'x', None), 1, None),
                                             Argument(Value("VALUE", None), 0, None)],
                                            [],
                                            None))

        self.templateC = Template(Name(None, 'C', None),
                                  ['x'],
                                  [Property(Name(None, 'x', None),
                                            Name('p', 'y', None),
                                            None),
                                   Property(Name(None, 'z', None),
                                            Value("STRING", None),
                                            None)],
                                  None,
                                  Expansion(Name(None, 'A', None),
                                            Name(None, 'C', None),
                                            [Name(None, 'x', None),
                                             Value("VALUE", None)],
                                            [],
                                            None))

    def tearDown(self):
        None

    def test_template_as_triples(self):

        template_triples = [(Name(None, 'A', None),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (Name(None, 'A', None),
                             Uri('http://example.eg/predicate', None),
                             Parameter('y', 0, None))]

        self.assertEqual(self.templateA.as_triples(self.env), template_triples)

    def test_derived_template_as_triples(self):

        self.env.assign(self.env.resolve_name(None, 'A'), self.templateA)
        self.env.assign(self.env.resolve_name(None, 'C'), self.templateB)

        template_triples = [(Name(None, 'C', None),
                             Parameter('x', 1, None),
                             Value(42, None)),
                            (Name(None, 'C', None),
                             Uri('http://example.eg/predicate', None),
                             Value("VALUE", None)),
                            (Name(None, 'C', None),
                             Parameter('x', 0, None),
                             Name('p', 'y', None)),
                            (Name(None, 'C', None),
                             Name(None, 'z', None),
                             Value("STRING", None))]

        self.assertEqual(self.templateC.as_triples(self.env), template_triples)

    def test_expansion_as_triples(self):

        self.env.assign(self.env.resolve_name(None, 'A'), self.templateA)

        expansion = Expansion(Name(None, 'A', None),
                              Name(None, 'E', None),
                              [Uri('http://uri.org/x', None),
                               Value(True, None)],
                              [],
                              None)

        expansion_triples = [(Name(None, 'E', None),
                             Uri('http://uri.org/x', None),
                             Value(42, None)),
                            (Name(None, 'E', None),
                             Uri('http://example.eg/predicate', None),
                             Value(True, None))]

        self.assertEqual(expansion.as_triples(self.env), expansion_triples)

    def test_double_expansion_as_triples(self):

        self.env.assign(self.env.resolve_name(None, 'A'), self.templateA)
        self.env.assign(self.env.resolve_name(None, 'C'), self.templateC)

        expansion = Expansion(Name(None, 'C', None),
                              Name(None, 'E', None),
                              [Uri('http://uri.org/x', None)],
                              [],
                              None)

        expansion_triples = [(Name(None, 'E', None),
                              Uri('http://uri.org/x', None),
                              Value(42, None)),
                             (Name(None, 'E', None),
                              Uri('http://example.eg/predicate', None),
                              Value("VALUE", None)),
                             (Name(None, 'E', None),
                              Uri('http://uri.org/x', None),
                              Name('p', 'y', None)),
                             (Name(None, 'E', None),
                              Name(None, 'z', None),
                              Value("STRING", None))]

        self.assertEqual(expansion_triples, expansion.as_triples(self.env))

