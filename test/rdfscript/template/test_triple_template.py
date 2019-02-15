import unittest

import rdfscript.rdfscriptparser as parser
import rdfscript.evaluate as evaluate
import rdfscript.runtime as runtime
import rdfscript.core as core


class TestTripleTemplate(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        pass

    def test_triple_template_graphed(self):
        form = self.parser.parse('Triple(a, b, c) = (a > b > c)')[0]
        evaluate.evaluate(form, self.rt)

    def test_triple_template_expand(self):
        forms = self.parser.parse('Triple(a, b, c) = (a > b > c)' +
                                  'Triple(<http://subject>, <http://predicate>, "object")')
        for form in forms:
            evaluate.evaluate(form, self.rt)

        triples = self.rt._g.root_context.triples
        expected = (core.Uri('http://subject'),
                    core.Uri('http://predicate'),
                    core.Value("object"))

        self.assertTrue(expected in triples)
