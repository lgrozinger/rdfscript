import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.pragma as pragmas
import rdfscript.core as core


class ParserPragmaTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix = <http://eg/>"
        forms = self.parser.parse(script)

        expected = [pragmas.PrefixPragma(core.Name('Prefix'),
                                         core.Uri('http://eg/'))]
        actually = forms
        self.assertEqual(expected, actually)

    def test_prefix_pragma_name(self):
        script = "@prefix Prefix = name"
        forms = self.parser.parse(script)

        expected = [pragmas.PrefixPragma(core.Name('Prefix'),
                                         core.Name('name'))]
        actually = forms
        self.assertEqual(expected, actually)

    def test_default_prefix_pragma(self):
        script = "@prefix Prefix"
        forms = self.parser.parse(script)

        expected = [pragmas.DefaultPrefixPragma(core.Name('Prefix'))]
        actually = forms
        self.assertEqual(expected, actually)

    def test_prefix_then_default_prefix_pragma(self):
        script = "@prefix Prefix = <http://prefix/> @prefix Prefix"
        forms = self.parser.parse(script)

        name = core.Name('Prefix')
        uri = core.Uri('http://prefix/')

        expected = [pragmas.PrefixPragma(name, uri),
                    pragmas.DefaultPrefixPragma(name)]
        actually = forms
        self.assertEqual(expected, actually)
