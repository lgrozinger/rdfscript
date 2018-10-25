import unittest
import ply.yacc as yacc
import ply.lex as leex

import rdfscript.parser as parser
import rdfscript.reader as reader
import rdfscript.env    as env
import rdfscript.objects

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

if __name__ == '__main__':
    unittest.main()
