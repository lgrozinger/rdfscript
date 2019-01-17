import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.core as core


class ParserTriplesTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_parser_three_names(self):
        forms = self.parser.parse('name > name > name')
        expected = core.Three(core.Name('name'),
                              core.Name('name'),
                              core.Name('name'))
        actually = forms[0]

        self.assertEqual(expected, actually)

    def test_parser_three_name_name_value(self):
        forms = self.parser.parse('name > name > true')
        expected = core.Three(core.Name('name'),
                              core.Name('name'),
                              core.Value(True))
        actually = forms[0]

        self.assertEqual(expected, actually)

    def test_parser_three_uri_uri_uri(self):
        forms = self.parser.parse('<name> > <name> > <name>')
        uri = core.Name(core.Uri('name'))
        expected = core.Three(uri, uri, uri)
        actually = forms[0]

        self.assertEqual(expected, actually)

    def test_parser_two_name_name(self):
        forms = self.parser.parse('name > name')
        expected = core.Two(core.Name('name'),
                            core.Name('name'))
        actually = forms[0]

        self.assertEqual(expected, actually)

    def test_parser_three_two(self):
        forms = self.parser.parse('name > name > name name > name')
        name = core.Name('name')

        expected = [core.Three(name, name, name), core.Two(name, name)]
        actually = forms

        self.assertEqual(expected, actually)

    def test_parser_two_three(self):
        forms = self.parser.parse('name > name name > name > name')
        name = core.Name('name')

        expected = [core.Two(name, name), core.Three(name, name, name)]
        actually = forms

        self.assertEqual(expected, actually)
