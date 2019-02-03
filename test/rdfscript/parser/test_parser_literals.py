import unittest
import ply

import rdfscript.rdfscriptparser as parser
import rdfscript.core as core


class ParserLiteralTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ply.yacc.yacc(module=parser, start='literal')
        cls.parser.filename = None

        cls.rdfscriptparser = parser.RDFScriptParser()
        cls.rdfscriptparser.parser = cls.parser

    def setUp(self):
        pass

    def tearDown(self):
        None

    def test_parser_literal_boolean(self):
        forms = self.parser.parse('true')
        self.assertEqual(forms, core.Value(True))
        
        forms = self.parser.parse('false')
        self.assertEqual(forms, core.Value(False))

    def test_parser_literal_double(self):
        forms = self.parser.parse('0.12345')

        self.assertEqual(forms, core.Value(0.12345))

    def test_parser_literal_integer(self):
        forms = self.parser.parse('12345')

        self.assertEqual(forms, core.Value(12345))

    def test_parser_literal_negative_integer(self):
        forms = self.parser.parse('-12345')

        self.assertEqual(forms, core.Value(-12345))

    def test_parser_literal_string(self):
        script = '"string with whitespace"'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Value("string with whitespace"))
