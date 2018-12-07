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
                            LocalName,
                            Prefix)
from rdfscript.evaluate import evaluate

class RuntimeIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_localname_unbound(self):
        forms = self.parser.parse("UnboundSymbol")

        env = Env()
        uri = env.resolve_name(Name(None, LocalName('UnboundSymbol', None), None))

        self.assertEqual(evaluate(forms[0], env), uri)

    def test_self(self):
        forms = self.parser.parse("self")

        env = Env()
        expected_value = env.default_prefix.uri(env)

        self.assertEqual(evaluate(forms[0], env), expected_value)

    def test_localname_bound(self):

        script = ("X=\"value\"\n" +
                  "X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value", None)

        self.assertEqual(evaluate(forms[0], env), expected_value)
        self.assertEqual(evaluate(forms[1], env), expected_value)

    def test_qname_symbol_symbol_unbound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.UnboundSymbol")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol', None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), uri)

    def test_qname_symbol_uri_unbound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.<UnboundSymbol>")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol', None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), uri)

    def test_qname_uri_uri_unbound(self):

        script = ("<http://eg.org/>.<UnboundSymbol>")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol', None)

        self.assertEqual(evaluate(forms[0], env), uri)

    def test_qname_uri_symbol_unbound(self):

        script = ("<http://eg.org/>.UnboundSymbol")
        forms = self.parser.parse(script)

        env = Env()
        uri = Uri('http://eg.org/UnboundSymbol', None)

        self.assertEqual(evaluate(forms[0], env), uri)

    def test_qname_symbol_symbol_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "p.X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value", None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), Value('value', None))
        self.assertEqual(evaluate(forms[2], env), Value('value', None))

    def test_qname_symbol_uri_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "p.<X>")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value", None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), Value('value', None))
        self.assertEqual(evaluate(forms[2], env), Value('value', None))

    def test_qname_uri_uri_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "<http://eg.org/>.<X>")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value", None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), Value('value', None))
        self.assertEqual(evaluate(forms[2], env), Value('value', None))

    def test_qname_uri_symbol_bound(self):

        script = ("@prefix p <http://eg.org/>\n" +
                  "p.X=\"value\"\n" +
                  "<http://eg.org/>.X")
        forms = self.parser.parse(script)

        env = Env()
        expected_value = Value("value", None)

        self.assertEqual(evaluate(forms[0], env), Prefix('p', None))
        self.assertEqual(evaluate(forms[1], env), Value('value', None))
        self.assertEqual(evaluate(forms[2], env), Value('value', None))

