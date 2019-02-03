import unittest
import pdb

import rdfscript.rdfscriptparser as parser
import rdfscript.runtime as runtime
import rdfscript.evaluate as evaluate
import rdfscript.core as core


class TestEvaluateUsing(unittest.TestCase):

    def setUp(self):
        self.parser = parser.RDFScriptParser()
        self.rt = runtime.Runtime()

    def tearDown(self):
        pass

    def test_using(self):
        forms = self.parser.parse('@prefix NS = <http://ns/>' +
                                  'NS.variable = 1234' +
                                  'using NS')

        for form in forms:
            evaluate.evaluate(form, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('variable'))
        self.assertEqual(expected, actually)

    def test_using_multiple_namespaces(self):
        forms = self.parser.parse('@prefix NS1 = <http://ns1/> ' +
                                  'NS1.variable1 = 1234 ' +
                                  'using NS1 ' +
                                  '@prefix NS2 = <http://ns2/>' +
                                  'NS2.variable2 = 5678' +
                                  'using NS2')

        for form in forms:
            evaluate.evaluate(form, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('variable1'))
        self.assertEqual(expected, actually)

        expected = core.Value(5678)
        actually = self.rt.binding(core.Name('variable2'))
        self.assertEqual(expected, actually)

    def test_using_with_default_prefix(self):
        forms = self.parser.parse('@prefix NS = <http://ns/> ' +
                                  'NS.variable = 1234 ' +
                                  '@prefix PRE = <http://pre/> ' +
                                  '@prefix PRE ' +
                                  'using NS')

        for form in forms:
            evaluate.evaluate(form, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('variable'))
        self.assertEqual(expected, actually)

    def test_using_with_default_prefix_has_ns(self):
        forms = self.parser.parse('@prefix NS = <http://ns/> ' +
                                  'NS.variable = 1234 ' +
                                  '@prefix PRE = <http://pre/> ' +
                                  '@prefix PRE ' +
                                  'using NS')

        for form in forms:
            evaluate.evaluate(form, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('PRE', 'variable'))
        self.assertEqual(expected, actually)

    def test_using_with_change_prefix_shadows_ns(self):
        forms = self.parser.parse('@prefix NS = <http://ns/> ' +
                                  'NS.variable = 1234 ' +
                                  '@prefix PRE = <http://pre/> ' +
                                  '@prefix PRE ' +
                                  'using NS ' +
                                  '@prefix POST = <http://post/> ' +
                                  '@prefix POST ')

        for form in forms:
            evaluate.evaluate(form, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('PRE', 'variable'))
        self.assertEqual(expected, actually)
        self.assertFalse(self.rt.bound_p(core.Name('variable')))
