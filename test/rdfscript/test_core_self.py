import unittest

from rdfscript.core import Self, Uri
from rdfscript.env import Env


class TestCoreSelf(unittest.TestCase):

    def test_self_evaluate(self):

        env = Env()
        self.assertEqual(Uri(env._rdf._g.identifier.toPython()), Self().evaluate(env))
