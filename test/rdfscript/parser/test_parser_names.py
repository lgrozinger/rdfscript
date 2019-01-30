import unittest
import ply

import rdfscript.rdfscriptparser as parser
import rdfscript.core as core


class NameParsingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ply.yacc.yacc(module=parser, start='name')
        cls.parser.filename = None

        cls.rdfscriptparser = parser.RDFScriptParser()
        cls.rdfscriptparser.parser = cls.parser

    def tearDown(self):
        None

    def test_name_local(self):
        script = 'localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name('localname'))

    def test_name_one_prefix(self):
        script = 'prefix.localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name('prefix', 'localname'))

    def test_name_several_symbols(self):
        script = 'prefix.localname.morelocal'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name('prefix', 'localname', 'morelocal'))

    @unittest.skip("Not implemented.")
    def test_name_start_uri(self):
        script = '<http://prefix/>.localname'
        forms = self.parser.parse(script)

        expected = core.Name(core.Uri('http://prefix/'), 'localname')
        self.assertEqual(forms, expected)

    @unittest.skip("Not implemented.")
    def test_name_end_uri(self):
        script = 'prefix.<localname>'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name('prefix', core.Uri('localname')))

    @unittest.skip("Not implemented.")
    def test_name_middle_uri(self):
        script = 'prefix.<localname>.morelocal'
        forms = self.parser.parse(script)

        expected = core.Name('prefix', core.Uri('localname'), 'morelocal')
        self.assertEqual(forms, expected)

    @unittest.skip("Not implemented.")
    def test_name_uri_only(self):
        script = '<http://name.eg/#test>'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name(core.Uri('http://name.eg/#test')))

    def test_name_self_prefix(self):
        script = 'self.localname'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name(core.Self(), 'localname'))

    def test_name_self_suffix(self):
        script = 'prefix.self'
        forms = self.parser.parse(script)

        self.assertEqual(forms, core.Name('prefix', core.Self()))
