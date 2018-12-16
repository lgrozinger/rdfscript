import unittest

from rdfscript.env import Env
from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Self)

from rdfscript.template import (Parameter,
                                Property)

class TestPropertyClass(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_property_substitute_parameters(self):

        p = Property(Name('x'), Name('y'))
        p.substitute_params([Parameter('x', 0)])

        self.assertEqual(p.name, Parameter('x', 0))
        self.assertEqual(p.value, Name('y'))

    def test_as_triples_simple(self):

        p = Property(Name('x'), Name('y'))

        expect = [(Self(), Name('x').evaluate(self.env), Name('y').evaluate(self.env))]
        self.assertEqual(p.as_triples(self.env), expect)
