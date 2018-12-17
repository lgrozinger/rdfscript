import unittest

from rdfscript.core import Value
from rdfscript.template import (Parameter,
                                Argument)

class TestArgumentClass(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_marshal_true(self):

        p = Parameter('z', 0)
        a = Argument(Value(1), 0)

        self.assertEqual(a.marshal(p), Value(1))

    def test_marshal_false(self):

        p = Parameter('z', 0)
        a = Argument(Value(1), 1)

        self.assertEqual(a.marshal(p), p)

    def test_marshal_not_parameter(self):

        p = Value("string")
        a = Argument(Value(1), 0)

        self.assertEqual(a.marshal(p), p)
