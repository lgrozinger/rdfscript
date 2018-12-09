import unittest
import logging

from rdfscript.rdfscriptparser import RDFScriptParser

from rdfscript.core import (Uri,
                            Name,
                            Prefix,
                            LocalName,
                            Self)

class ParserIdentifierTest(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_parser_uri(self):
        script = "<http://uri.org/>"
        forms  = self.parser.parse(script)

        self.assertEqual(forms, [Uri('http://uri.org/', None)])

    def test_qname_symbol_symbol(self):
        script = 'Prefix.LocalName'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Name(Prefix('Prefix', None),
                                      LocalName('LocalName', None),
                                      None)])

    def test_qname_symbol_uri(self):
        script = 'Prefix.<localname>'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Name(Prefix('Prefix', None),
                                      LocalName(Uri('localname', None), None),
                                      None)])

    def test_qname_uri_uri(self):
        script = '<http://prefix/>.<localname>'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Name(Prefix(Uri('http://prefix/', None), None),
                                      LocalName(Uri('localname', None), None),
                                      None)])

    def test_qname_uri_symbol(self):
        script = '<http://prefix/>.LocalName'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Name(Prefix(Uri('http://prefix/', None), None),
                                      LocalName('LocalName', None),
                                      None)])

    def test_qname_self_symbol(self):
        script = 'self.LocalName'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Self(None, localname=LocalName('LocalName', None))])

    def test_qname_self_uri(self):
        script = 'self.<localname>'
        forms = self.parser.parse(script)
        self.assertEqual(forms, [Self(None, localname=LocalName(Uri('LocalName', None), None))])

    def test_localname(self):
        script = 'localName'
        forms = self.parser.parse(script)

        self.assertEqual(forms, [Name(None, LocalName('localName', None), None)])


if __name__ == '__main__':
    unittest.main()
