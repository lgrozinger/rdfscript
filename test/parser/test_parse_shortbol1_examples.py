import unittest
import logging
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader

from rdfscript.toplevel import TripleObject, ConstructorDef
from rdfscript.identifier import URI, QName, LocalName
from rdfscript.literal import Literal

class ParseShortBOL1ExamplesTest(unittest.TestCase):

    def setUp(self):
        self.parser = yacc.yacc(module=parser)
        self.reader = leex.lex(module=reader)
        self.reader.at_line_start = True
        self.reader.indent_stack = [0]
        self.log = logging.getLogger()

    def tearDown(self):
        None

    ## these tests only test success or failure of the parser, not
    ## that the AST is correct
    def test_parse_genomic_sbol_file(self):
        with open("test/parser/example-files/genomic.sbol", 'r') as in_file:
            data = in_file.read()

        forms  = self.parser.parse(data, lexer=self.reader, debug=self.log)

        formTypes = [type(form) for form in forms]

        self.assertTrue(None not in forms)

        self.assertEqual(formTypes,
                         [type(ConstructorDef('', [], 0))] * 37)

if __name__ == '__main__':
    unittest.main()
