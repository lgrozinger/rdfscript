import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.objects import TripleObject
from rdfscript.identifier import URI, QName, NSPrefix, LocalName
from rdfscript.literal import Literal

class ParserIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)

    def tearDown(self):
        None

    def test_parser_triple(self):
        script = 'Subject Predicate Object'
        forms  = self.parser.parse(script, lexer=self.reader)

        s = QName(None, LocalName('Subject', 1), 1)
        p = QName(None, LocalName('Predicate', 1), 1)
        o = QName(None, LocalName('Object', 1), 1)
        self.assertEqual(forms, [TripleObject(s, p, o, 1)])
