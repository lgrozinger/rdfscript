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
from rdfscript.evaluate import evaluate

class RuntimeIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_env_resolve_localname(self):
        forms = self.parser.parse("UnboundSymbol")

        env = Env()

        ## going into the internals of Env
        uri = rdflib.Namespace(env._default_ns)['UnboundSymbol']

        self.assertEqual(forms, [Name(None, 'UnboundSymbol', None)])
        self.assertEqual(env.resolve_name(forms[0].prefix,
                                          forms[0].localname),
                         uri)

    def test_evaluate_localname_not_bound(self):
        forms  = self.parser.parse("UnboundSymbol")

        env = Env()

        self.assertEqual(env.interpret(forms), env.resolve_name(None, 'UnboundSymbol'))


    def test_evaluate_self(self):

        script = "self"

        forms = self.parser.parse(script)

        env = Env()

        expected_value = env._default_ns['']

        self.assertEqual(env.interpret(forms), expected_value)

    def test_evaluate_localname_bound(self):

        script = ("X=\"value\"\n" +
                  "X")

        forms = self.parser.parse(script)

        env = Env()

        expected_value = rdflib.term.Literal("value")

        self.assertEqual(env.interpret(forms), expected_value)

    def test_resolve_qname(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.UnboundSymbol")

        forms = self.parser.parse(script)

        env = Env()

        uri = rdflib.URIRef('http://eg.org/UnboundSymbol')

        env.interpret(forms)

        self.assertEqual(env.resolve_name(forms[1].prefix, forms[1].localname),
                         uri)

    def test_evaluate_qname_not_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.UnboundSymbol")

        forms  = self.parser.parse(script)

        env = Env()

        self.assertEqual(env.interpret(forms), env.resolve_name('p', 'UnboundSymbol'))


    def test_evaluate_qname_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "p.X")

        forms = self.parser.parse(script)

        env = Env()

        expected_value = rdflib.term.Literal("value")

        self.assertEqual(env.interpret(forms), expected_value)

