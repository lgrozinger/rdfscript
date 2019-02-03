import unittest

import rdfscript.core as core
import rdfscript.evaluate as evaluate
import rdfscript.runtime as runtime
import rdfscript.error as error
import rdfscript.rdfscriptparser as parser


class TestEvaluateAssignment(unittest.TestCase):

    def setUp(self):
        self.rt = runtime.Runtime()
        self.parser = parser.RDFScriptParser()

    def tearDown(self):
        pass

    def test_assign_simple_value(self):
        assign = self.parser.parse('Variable = 1234')[0]
        evaluate.evaluate(assign, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('Variable'))
        self.assertEqual(expected, actually)

    def test_assign_simple_uri(self):
        assign = self.parser.parse('Variable = <http://uri>')[0]
        evaluate.evaluate(assign, self.rt)

        expected = core.Uri('http://uri')
        actually = self.rt.binding(core.Name('Variable'))
        self.assertEqual(expected, actually)

    def test_assign_named_value(self):
        assign = self.parser.parse('Variable = 1234')[0]
        evaluate.evaluate(assign, self.rt)
        assign = self.parser.parse('OtherVar = Variable')[0]
        evaluate.evaluate(assign, self.rt)

        expected = core.Value(1234)
        actually = self.rt.binding(core.Name('OtherVar'))
        self.assertEqual(expected, actually)

    def test_assign_to_bound_name(self):
        assign = self.parser.parse('Variable = 1234')[0]
        evaluate.evaluate(assign, self.rt)
        assign = self.parser.parse('Variable = Variable')[0]

        with self.assertRaises(error.BindingError):
            evaluate.evaluate(assign, self.rt)

    def test_assign_unbound_name(self):
        assign = self.parser.parse('Variable = Unbound')[0]

        with self.assertRaises(error.UnexpectedType):
            evaluate.evaluate(assign, self.rt)
