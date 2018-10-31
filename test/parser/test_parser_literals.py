import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.literal import Literal

class ParserLiteralTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]
        
    def tearDown(self):
        None

    def test_parser_literal_boolean(self):
        script = 'true false'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal('true', 1), Literal('false', 1)])

    def test_parser_literal_double(self):
        script = '0.12345'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal(0.12345, 1)])

    def test_parser_literal_integer(self):
        script = '12345'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal(12345, 1)])

    def test_parser_literal_integer(self):
        script = '-12345'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal(-12345, 1)])

    def test_parser_literal_string(self):
        script = '"string with whitespace"'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal("string with whitespace", 1)])
