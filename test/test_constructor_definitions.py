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

class RuntimeConstructorDefTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser, debug=False)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]

    def tearDown(self):
        None

    def test_constructordef_no_args(self):

        script = (f"Template =>\n"
                  f"  a = 1\n"
                  f"  b = 2")

        forms = self.parser.parse(script, lexer=self.reader)

        env = Env()

        self.assertEqual(forms, [LocalName('UnboundSymbol', 1)])
        self.assertEqual(forms[0].resolve(env), uri)
