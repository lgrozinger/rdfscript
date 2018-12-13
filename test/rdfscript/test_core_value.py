import unittest

from rdfscript.core import Value

class TestCoreValue(unittest.TestCase):

    def test_value_string(self):

        value = Value("string")
        self.assertEqual(value.value, "string")

    def test_value_integer(self):

        value = Value(12345)
        self.assertEqual(value.value, 12345)

    def test_value_double(self):

        value = Value(0.12345)
        self.assertEqual(value.value, 0.12345)

    def test_value_boolean(self):

        value = Value(True)
        self.assertEqual(value.value, True)

        value = Value(False)
        self.assertEqual(value.value, False)
