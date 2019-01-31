import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.runtime as runtime
import rdfscript.evaluate as evaluate
import rdfscript.core as core


class TestPrefixEvaluate(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        None

    def test_prefix_pragma_uri(self):
        script = "@prefix Prefix = <http://eg/>"
        form = self.parser.parse(script)[0]
        evaluate.evaluate(form, self.rt)

        expected = core.Uri('http://eg/')
        actually = self.rt._g.prefix_to_uri(core.Name('Prefix'))
        self.assertEqual(expected, actually)

    def test_prefix_pragma_name(self):
        script = "@prefix Prefix = name"
        form = self.parser.parse(script)[0]
        self.rt.bind(core.Uri('http://eg/'), core.Name('name'))
        evaluate.evaluate(form, self.rt)

        expected = core.Uri('http://eg/')
        actually = self.rt._g.prefix_to_uri(core.Name('Prefix'))
        self.assertEqual(expected, actually)

    def test_default_prefix_pragma(self):
        script = "@prefix Prefix = <http://eg/> @prefix Prefix"
        forms = self.parser.parse(script)
        evaluate.evaluate(forms[0], self.rt)
        evaluate.evaluate(forms[1], self.rt)

        expected = core.Name('Prefix')
        actually = self.rt.prefix
        self.assertEqual(expected, actually)
