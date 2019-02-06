import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.evaluate as evaluate
import rdfscript.runtime as runtime


class TestTripleTemplate(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        pass

    def test_triple_template_graphed(self):
        form = self.parser.parse('Triple(a, b, c)(a > b > c)')
        evaluate.evaluate(form[0], self.rt)
