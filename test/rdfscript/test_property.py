import unittest

from rdfscript.env import Env
from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Self)

from rdfscript.template import (Parameter,
                                Property)

class TestPropertyClass(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_property_substitute_parameters(self):

        p = Property(Name('x'), Name('y'))
        p.substitute_params([Parameter('x', 0)])

        self.assertEqual(p.name, Parameter('x', 0))
        self.assertEqual(p.value, Name('y'))

    def test_as_triples_simple(self):

        p = Property(Name('x'), Name('y'))

        expect = [(Self().evaluate(self.env), Name('x').evaluate(self.env), Name('y').evaluate(self.env))]
        self.assertEqual(p.as_triples(self.env), expect)

    def test_as_triples_expansion(self):

        forms = self.parser.parse('t()(x=1) e is a t()')
        t = forms[0]
        e = forms[1]
        p = Property(Name('y'), e)

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(1)),
                  (Self().evaluate(self.env), Name('y').evaluate(self.env), Name('e').evaluate(self.env))]

        self.assertEqual(expect, p.as_triples(self.env))

    def test_as_triples_self_in_name(self):

        p = Property(Name(Self()), Value(1))

        expect = [(Name(Self()).evaluate(self.env), Uri(self.env._rdf._g.identifier.toPython()), Value(1))]

        self.assertEqual(expect, p.as_triples(self.env))

    def test_as_triples_self_in_name_with_context(self):

        p = Property(Name(Self()), Value(1))
        expect = [(Name(Self()), Name(Self()), Value(1))]

        self.env.current_self = Name(Self())
        self.assertEqual(expect, p.as_triples(self.env))

    def test_as_triples_self_prefix_in_name_with_context(self):

        p = Property(Name(Self(), 'p'), Value(1))
        expect = [(Name(Self()), Name(Self(), 'p'), Value(1))]

        self.env.current_self = Name(Self())
        self.assertEqual(expect, p.as_triples(self.env))

    def test_as_triples_self_prefix_in_name_with_resolved_context(self):

        p = Property(Name(Self(), 'p'), Value(1))
        self.env.current_self = Uri('context')
        expect = [(Uri('context'), Uri('contextp'), Value(1))]

        self.assertEqual(expect, p.as_triples(self.env))
