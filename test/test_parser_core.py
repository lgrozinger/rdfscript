import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader
import rdfscript.env    as env

from rdfscript.objects import (Literal,
                               URI,
                               QName,
                               NSPrefix,
                               LocalName,
                               Symbol)


class ParserCoreTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)

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

    def test_parser_literal_string(self):
        script = '"string with whitespace"'
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [Literal("string with whitespace", 1)])

    def test_parser_uri(self):
        script = "'http://uri.org/'"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [QName('',
                                       LocalName(URI('http://uri.org/',
                                                     1)
                                                 , 1), 1)])

    def test_parser_qname_nsprefix_localname(self):
        script = "'http://uri.org/'.'#fragment'"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [QName(NSPrefix(URI('http://uri.org/',
                                                    1),
                                                1),
                                       LocalName(URI('#fragment', 1)
                                                 , 1),
                                       1)])

        script = "'http://uri.org/'.Fragment"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [QName(NSPrefix(URI('http://uri.org/',
                                                    2)
                                                , 2),
                                       LocalName(Symbol('Fragment',
                                                        2), 2),
                                       2)])

        script = "Prefix.'#fragment'"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [QName(NSPrefix(Symbol('Prefix', 3), 3),
                                       LocalName(URI('#fragment', 3), 3),
                                       3)])

        script = "Prefix.LocalName"
        forms  = self.parser.parse(script, lexer=self.reader)

        self.assertEqual(forms, [QName(NSPrefix(Symbol('Prefix', 4), 4),
                                       LocalName(Symbol('LocalName', 4),
                                                 4),
                                       4)])



if __name__ == '__main__':
    unittest.main()
