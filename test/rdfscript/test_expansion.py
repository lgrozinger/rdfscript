import unittest

from rdfscript.template import (Expansion)
from rdfscript.core import (Name,
                            Value,
                            Uri,
                            Self)
from rdfscript.pragma import ExtensionPragma
from rdfscript.env import Env
from rdfscript.rdfscriptparser import RDFScriptParser

from extensions.cardinality import CardinalityError

class TestExpansionClass(unittest.TestCase):

    def setUp(self):
        self.parser = RDFScriptParser()
        self.env = Env()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_as_triples(self):

        forms = self.parser.parse('t()(x=12345) e is a t()')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(12345))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_body(self):

        forms = self.parser.parse('t()(x=12345) e is a t()(y=54321)')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(12345)),
                  (Name('e').evaluate(self.env), Name('y').evaluate(self.env), Value(54321))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args(self):

        forms = self.parser.parse('t(x)(<http://predicate.com>=x) e is a t(1)')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Uri('http://predicate.com'), Value(1))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_body(self):

        forms = self.parser.parse('t(x)(<http://predicate.com>=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Uri('http://predicate.com'), Value(1)),
                  (Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self(self):

        forms = self.parser.parse('t(x)(self=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('e').evaluate(self.env), Value(1)),
                  (Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_self_as_object(self):

        forms = self.parser.parse('t()(x=self) e is a t()')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Name('e').evaluate(self.env))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_args_with_self_prefix(self):

        forms = self.parser.parse('t(x)(self.p=x) e is a t(1)(x=2)')
        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('e', 'p').evaluate(self.env), Value(1)),
                  (Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_as_triples_with_expansion_in_template(self):

        forms = self.parser.parse('s()(z=true)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))
        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('z').evaluate(self.env), Value(True)),
                  (Name('f').evaluate(self.env), Name('x').evaluate(self.env), Name('e').evaluate(self.env))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_expansion_in_template_with_self(self):

        forms = self.parser.parse('s()(z=self)' +
                                  't()(x = e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))
        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env),
                   Name('z').evaluate(self.env),
                   Name('e').evaluate(self.env)),
                  (Name('f').evaluate(self.env),
                   Name('x').evaluate(self.env),
                   Name('e').evaluate(self.env))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_context(self):

        forms = self.parser.parse('s()(z=self)' +
                                  'self.f is a s()')

        s = forms[0]
        f = forms[1]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))

        self.env.current_self = Uri('e')
        expect = [(Uri('ef'),
                   Name('z').evaluate(self.env),
                   Uri('ef'))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_unresolved_context(self):

        forms = self.parser.parse('s()(z=self)' +
                                  'self.f is a s()')

        s = forms[0]
        f = forms[1]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))

        self.env.current_self = Name(Self(), 'e')
        expect = [(Name(Self(), 'e', 'f'),
                   Name('z').evaluate(self.env),
                   Name(Self(), 'e', 'f'))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_as_triples_with_self_named_expansion_in_template(self):

        forms = self.parser.parse('s()(z=self)' +
                                  't()(x=self.e is a s())' +
                                  'f is a t()')
        s = forms[0]
        t = forms[1]
        f = forms[2]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))
        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('f', 'e').evaluate(self.env),
                   Name('z').evaluate(self.env),
                   Name('f', 'e').evaluate(self.env)),
                  (Name('f').evaluate(self.env),
                   Name('x').evaluate(self.env),
                   Name('f', 'e').evaluate(self.env))]

        self.assertEqual(expect, f.as_triples(self.env))

    def test_extensions_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t("a")')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('AtLeastOne', [Value("a")])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_multiple_argument_binding(self):

        forms = self.parser.parse('t(a, b)(@extension ext(a, b))' +
                                  'e is a t(1, 2)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(1), Value(2)])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_mixed_argument_binding(self):

        forms = self.parser.parse('t(a)(@extension ext(12345, a))' +
                                  'e is a t(1)')

        t = forms[0]
        e = forms[1]

        t.evaluate(self.env)
        ext = ExtensionPragma('ext', [Value(12345), Value(1)])
        self.assertEqual(e.get_extensions(self.env), [ext])

    def test_extensions_from_multiple_templates(self):

        forms = self.parser.parse('s(a)(@extension ext(a))' +
                                  't(a) from s("s")(@extension ext(a))' +
                                  'e is a t("t")')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)
        exts = [ExtensionPragma('ext', [Value("t")]),
                ExtensionPragma('ext', [Value("s")])]

        self.assertEqual(e.get_extensions(self.env), exts)

    def test_extensions_self_in_extension_arguments(self):

        forms = self.parser.parse('s()(@extension ext(self.name))' +
                                  't() from s()(@extension ext(self.name))' +
                                  'e is a t()')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)
        exts = [ExtensionPragma('ext', [Name(Self(), 'name')]),
                ExtensionPragma('ext', [Name(Self(), 'name')])]

        self.assertEqual(e.get_extensions(self.env), exts)
        
    def test_extensions_in_expansion(self):

        forms = self.parser.parse('s(a)(@extension ext(a))' +
                                  't(a) from s("s")(@extension ext(a))' +
                                  'e is a t("t")(@extension ext("e"))')

        s = forms[0]
        t = forms[1]
        e = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        exts = [ExtensionPragma('ext', [Value("t")]),
                ExtensionPragma('ext', [Value("s")]),
                ExtensionPragma('ext', [Value("e")])]

        self.assertEqual(e.get_extensions(self.env), exts)


    def test_evaluate_runs_extensions_with_error(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t(property)()')

        t = forms[0]
        e = forms[1]

        self.assertEqual(len(list(self.env._rdf._g.triples((None, None, None)))), 0)

        t.evaluate(self.env)
        with self.assertRaises(CardinalityError):
            e.evaluate(self.env)

        self.assertEqual(len(list(self.env._rdf._g.triples((None, None, None)))), 0)

    def test_evaluate_runs_extensions(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))' +
                                  'e is a t(property)(property=12345)')

        t = forms[0]
        e = forms[1]

        self.assertEqual(len(list(self.env._rdf._g.triples((None, None, None)))), 0)

        t.evaluate(self.env)
        e.evaluate(self.env)

        self.assertEqual(len(list(self.env._rdf._g.triples((None, None, None)))), 1)

    def test_add_object_for_inherited_predicate(self):

        forms = self.parser.parse('t()(x = 1)' +
                                  'e is a t()(x = 2)')

        t = forms[0]
        e = forms[1]

        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env),
                   Name('x').evaluate(self.env),
                   Value(1)),
                  (Name('e').evaluate(self.env),
                   Name('x').evaluate(self.env),
                   Value(2))]

        self.assertEqual(expect, e.as_triples(self.env))

    def test_bodied_expansion_in_template(self):

        forms = self.parser.parse('s()(a = 1)' +
                                  't()(x = self.e is a s()(b = 2))' +
                                  'f is a t()')

        s = forms[0]
        t = forms[1]
        f = forms[2]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))
        self.env.assign_template(t.name.evaluate(self.env), t.as_triples(self.env))

        expect = [(Name('f', 'e').evaluate(self.env),
                   Name('a').evaluate(self.env),
                   Value(1)),
                  (Name('f', 'e').evaluate(self.env),
                   Name('b').evaluate(self.env),
                   Value(2)),
                  (Name('f').evaluate(self.env),
                   Name('x').evaluate(self.env),
                   Name('f', 'e').evaluate(self.env))]

        self.assertEqual(expect, f.as_triples(self.env))
