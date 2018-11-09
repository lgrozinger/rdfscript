import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex
import rdflib

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.env import Env

from rdfscript.toplevel import TripleObject
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class RuntimeIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser, debug=False)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_resolve_localname(self):

        script = "UnboundSymbol"
        forms = self.parser.parse(script, lexer=self.reader)

        env = Env()

        uri = rdflib.URIRef('file://rdfscript.env/UnboundSymbol')

        self.assertEqual(forms, [LocalName('UnboundSymbol', 1)])
        self.assertEqual(forms[0].resolve(env), uri)

    def test_evaluate_localname_not_bound(self):

        script = "UnboundSymbol"
        forms  = self.parser.parse(script, lexer=self.reader)

        env = Env()

        self.assertEqual(env.interpret(forms), None)


    def test_evaluate_localname_bound(self):

        script = (f"X=\"value\"\n"
                  f"X")

        forms = self.parser.parse(script, lexer=self.reader)

        env = Env()

        expected_value = rdflib.term.Literal("value")

        self.assertEqual(env.interpret(forms), expected_value)

    def test_resolve_qname(self):

        script = (f"@prefix p <http://eg.org/>\n"
                  f"p.UnboundSymbol")

        forms = self.parser.parse(script, lexer=self.reader)

        env = Env()

        uri = rdflib.URIRef('http://eg.org/UnboundSymbol')

        env.interpret(forms)

        self.assertEqual(forms[1].resolve(env), uri)

    def test_evaluate_qname_not_bound(self):

        script = (f"@prefix p <http://eg.org/>\n"
                  f"p.UnboundSymbol")

        forms  = self.parser.parse(script, lexer=self.reader)

        env = Env()

        self.assertEqual(env.interpret(forms), None)


    def test_evaluate_qname_bound(self):

        script = (f"@prefix p <http://eg.org/>\n"
                  f"p.X=\"value\"\n"
                  f"p.X")

        forms = self.parser.parse(script, lexer=self.reader)

        env = Env()

        expected_value = rdflib.term.Literal("value")

        self.assertEqual(env.interpret(forms), expected_value)

