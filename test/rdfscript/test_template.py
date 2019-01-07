import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Self,
                            Value)

from rdfscript.template import (Template,
                                Parameter,
                                Argument,
                                check_param_is_name,
                                sub_params_in_triples)

from rdfscript.pragma import ExtensionPragma

from rdfscript.error import UnexpectedType


class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()
        self.maxDiff = None

    def tearDown(self):
        None

    def test_init(self):

        template = Template(Name('x'), [], [])

        self.assertEqual(template.name, Name('x'))

    def test_check_param_not_name(self):

        name = Name('x')
        notname = Value(1)
        template = Template(Name('x'), [], [])

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notname)

        self.assertTrue(check_param_is_name(name))

    def test_check_param_not_simple_name(self):

        notparam = Name(Uri('x'))
        template = Template(Name('x'), [], [])

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notparam)

        notparam = Name(Self())

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notparam)

    def test_check_param_too_many_names(self):

        notparam = Name('x', 'y')
        template = Template(Name('x'), [], [])

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notparam)

    def test_as_triples_empty(self):

        template = Template(Name('x'), [], [])

        self.assertEqual(template.as_triples(self.env), [])

    def test_as_triples_simple_triple(self):

        template = self.parser.parse('t()(x = z)')[0]
        expect = [(Self(),
                   Name('x'),
                   Name('z'))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_simple_triple_with_self(self):

        template = self.parser.parse('t()(x = self)')[0]
        expect = [(Self(), Name('x'), Name(Self()))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_multiple_properties(self):

        template = self.parser.parse('t()(x = y z = 12345)')[0]
        expect = [(Self(),
                   Name('x'),
                   Name('y')),
                  (Self(),
                   Name('z'),
                   Value(12345))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_with_base(self):

        forms = self.parser.parse('a()(x = 1) b()(a() y = 2)')
        base = forms[0]
        specialised = forms[1]

        base.evaluate(self.env)

        expect = [(Self(), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y'), Value(2))]

        self.assertEqual(specialised.as_triples(self.env), expect)

    def test_as_triples_with_base_chain(self):

        forms = self.parser.parse('a()(x=1)' +
                                  'b()(a() y=2)' +
                                  'c()(b() z=3)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)

        expect = [(Self(), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y').evaluate(self.env), Value(2)),
                  (Self(), Name('z'), Value(3))]

        self.assertEqual(c.as_triples(self.env), expect)

    def test_as_triples_with_base_with_self(self):

        forms = self.parser.parse('a()(x = self) b()(a() y = 2)')
        base = forms[0]
        specialised = forms[1]

        base.evaluate(self.env)

        expect = [(Self(), Name('x').evaluate(self.env), Name(Self())),
                  (Self(), Name('y'), Value(2))]

        self.assertEqual(specialised.as_triples(self.env), expect)

    def test_as_triples_params(self):

        forms = self.parser.parse('a(x)(property = x)')
        a = forms[0]

        expect = [(Self(), Name('property'), Parameter('x', 0))]
        self.assertEqual(a.as_triples(self.env), expect)

    def test_as_triples_with_base_with_params(self):

        forms = self.parser.parse('a(x)(x = 12345) b(y)(a(y))')
        a = forms[0]
        b = forms[1]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))
        expect = [(Self(), Parameter('y', 0), Value(12345))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_args(self):

        forms = self.parser.parse('a(x)(x = 12345) b()(a(12345))')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        expect = [(Self(), Value(12345), Value(12345))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_multiple_base_args_and_parameters(self):

        forms = self.parser.parse('a(x, y)(x = y)' +
                                  'b(x, y)(a(x, "string") z=y)' +
                                  'c(x, y)(b(1, 2) x=y)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)

        expect = [(Self(), Value(1), Value("string")),
                  (Self(), Name('z').evaluate(self.env), Value(2)),
                  (Self(), Parameter('x', 0), Parameter('y', 0))]

        self.assertEqual(expect, c.as_triples(self.env))

    def test_current_self_preserved(self):

        forms = self.parser.parse('a(x, y, z)(self=self)')
        a = forms[0]

        previous_self = self.env.current_self
        a.as_triples(self.env)
        new_self = self.env.current_self
        self.assertEqual(previous_self, new_self)

    def test_as_triples_with_expansion_in_property(self):

        forms = self.parser.parse('a()(x = 1) b()(y = e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y'), Name('e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self(self):

        forms = self.parser.parse('a()(x = 1) b()(self.y = e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name(Self(), 'y'), Name('e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self_as_name(self):

        forms = self.parser.parse('a()(x = 1) b()(y = self.e is a a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name(Self(), 'e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y'), Name(Self(), 'e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_self_named_expansion(self):

        forms = self.parser.parse('s()(z=self) t()(x=self.e is a s())')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)

        expect_s = [(Name(Self()), Name('z'), Self())]
        expect_t = [(Name(Self(), 'e'), Name('z').evaluate(self.env), Name(Self(), 'e')),
                    (Name(Self()), Name('x'), Name(Self(), 'e'))]

        self.assertEqual(expect_s, s.as_triples(self.env))
        self.assertEqual(expect_t, t.as_triples(self.env))

    def test_as_triples_with_expansion_as_argument(self):

        forms = self.parser.parse('r()(y=1) s(exp)(x=exp)' +
                                  't()(s(e is a r()))')

        r = forms[0]
        s = forms[1]
        t = forms[2]

        r.evaluate(self.env)
        s.evaluate(self.env)

        expect = [(Self(),
                   Name('x').evaluate(self.env),
                   Name('e').evaluate(self.env))]

        self.assertEqual(expect, t.as_triples(self.env))

    def test_evaluate_stores_triples(self):

        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        t.evaluate(self.env)

        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2))]

        self.assertEqual(self.env.lookup_template(t.name.evaluate(self.env)), expect)

    def test_init_extensions(self):

        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        expect = [ExtensionPragma('E', []), ExtensionPragma('F', [])]
        self.assertEqual(t.collect_extensions(self.env), expect)

    def test_evaluate_stores_extensions(self):

        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', []), ExtensionPragma('F', [])])

    def test_evaluate_stores_base_extensions(self):

        forms = self.parser.parse('s()(@extension F()) t()(s() @extension E())')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', []), ExtensionPragma('F', [])])

    def test_evaluate_extension_arguments(self):

        forms = self.parser.parse('t()(@extension E(12345))')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', [Value(12345)])])

    def test_evaluate_extension_arguments_name(self):

        forms = self.parser.parse('t()(@extension E(argument))')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', [Name('argument').evaluate(self.env)])])

    def test_evaluate_extension_self_name(self):

        forms = self.parser.parse('t()(@extension E(self.argument))')
        t = forms[0]

        self.env.current_self = Name(Self())
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', [Name(Self(), 'argument')])])

    def test_evaluate_to_template_name(self):

        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertEqual(t.name.evaluate(self.env), t.evaluate(self.env))

    def test_extension_parameters(self):

        forms = self.parser.parse('t(a)(@extension AtLeastOne(a))')
        t = forms[0]

        t.evaluate(self.env)

        atleastone = self.env.lookup_extensions(t.name.evaluate(self.env))[0]
        arg = t.parameters[0]

        self.assertEqual(arg, atleastone.args[0])

    def test_extension_parameters_multiple(self):

        forms = self.parser.parse('t(a, b)(@extension AtLeastOne(a, b))')
        t = forms[0]

        t.evaluate(self.env)

        atleastone = self.env.lookup_extensions(t.name.evaluate(self.env))[0]
        args = t.parameters

        self.assertEqual(args, atleastone.args)

    def test_bodied_expansion_in_template(self):

        forms = self.parser.parse('s()(a = 1)' +
                                  't()(self.e is a s()(b = 2))')

        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)

        expect = [(Name(Self(), 'e'),
                   Name('a').evaluate(self.env),
                   Value(1)),
                  (Name(Self(), 'e'),
                   Name('b'),
                   Value(2))]

        self.assertEqual(expect, t.as_triples(self.env))


    def test_bodied_expansion_in_template_property(self):

        forms = self.parser.parse('s()(a = 1)' +
                                  't()(x = self.e is a s()(b = 2))')

        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)

        expect = [(Name(Self(), 'e'),
                   Name('a').evaluate(self.env),
                   Value(1)),
                  (Name(Self(), 'e'),
                   Name('b'),
                   Value(2)),
                  (Name(Self()),
                   Name('x'),
                   Name(Self(), 'e'))]

        self.assertEqual(expect, t.as_triples(self.env))

    def test_sub_params_in_triples(self):

        params = [Parameter('x', 0), Parameter('y', 1)]
        unsubbed = [(Name('x'), Name('y'), Value(12345)),
                    (Name('z'), Name('x'), Name('y'))]

        subbed = [(params[0], params[1], Value(12345)),
                    (Name('z'), params[0], params[1])]

        self.assertEqual(sub_params_in_triples(params, unsubbed), subbed)
