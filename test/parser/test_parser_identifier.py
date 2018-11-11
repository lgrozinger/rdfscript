import unittest
import logging

import rdfscript
from parser import RDFScriptParser

class ParserIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_parser_uri(self):
        script = "<http://uri.org/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Uri('http://uri.org/', None)])

    def test_parser_qname(self):
        script = 'Prefix.LocalName'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name('Prefix', 'LocalName', None)])

    def test_parser_localname(self):
        script = 'localName'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name(None, 'localName', None)])


if __name__ == '__main__':
    unittest.main()
