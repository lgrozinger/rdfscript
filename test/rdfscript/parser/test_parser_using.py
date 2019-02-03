import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.pragma as pragmas
import rdfscript.core as core


class TestParserUsing(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        None

    def test_using(self):
        forms = self.parser.parse('using prefix')

        expected = [pragmas.UsingPragma(core.Name('prefix'))]
        actually = forms
        self.assertEqual(expected, actually)
