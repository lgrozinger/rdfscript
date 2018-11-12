import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.toplevel import TripleObject
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class ParserIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    @unittest.skip("Explicitly coded triples are not yet implemented.")
    def test_parser_triple(self):
        script = 'Subject Predicate Object'
        forms  = self.parser.parse(script)
