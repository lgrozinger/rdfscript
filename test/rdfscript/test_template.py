import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Self,
                            Value)

from rdfscript.template import (Template,
                                Parameter,
                                Argument)

from rdfscript.pragma import ExtensionPragma

from rdfscript.error import UnexpectedType


class TemplateClassTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()
        self.parser = RDFScriptParser()

    def tearDown(self):
        None

    def test_init(self):

        template = Template(Name('x'), [], [], None, [])

        self.assertEqual(template.name, Name('x'))

    def test_check_param_not_name(self):

        name = Name('x')
        notname = Value(1)
        template = Template(Name('x'), [], [], None, [])

        with self.assertRaises(UnexpectedType):
            template.check_param(notname)

        self.assertTrue(template.check_param(name))

    def test_check_param_not_simple_name(self):

        notparam = Name(Uri('x'))
        template = Template(Name('x'), [], [], None, [])

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

        notparam = Name(Self())

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

    def test_check_param_too_many_names(self):

        notparam = Name('x', 'y')
        template = Template(Name('x'), [], [], None, [])

        with self.assertRaises(UnexpectedType):
            template.check_param(notparam)

    def test_as_triples_empty(self):

        template = Template(Name('x'), [], [], None, [])

        self.assertEqual(template.as_triples(self.env), [])

    def test_as_triples_simple_triple(self):

        template = self.parser.parse('t()(x = z)')[0]
        expect = [(Self(),
                   Name('x').evaluate(self.env),
                   Name('z').evaluate(self.env))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_simple_triple_with_self(self):

        template = self.parser.parse('t()(x = self)')[0]
        expect = [(Self(), Name('x').evaluate(self.env), Name(Self()))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_multiple_properties(self):

        template = self.parser.parse('t()(x = y z = 12345)')[0]
        expect = [(Self(),
                   Name('x').evaluate(self.env),
                   Name('y').evaluate(self.env)),
                  (Self(),
                   Name('z').evaluate(self.env),
                   Value(12345))]

        self.assertEqual(template.as_triples(self.env), expect)

    def test_as_triples_with_base(self):

        forms = self.parser.parse('a()(x = 1) b() from a()(y = 2)')
        base = forms[0]
        specialised = forms[1]

        self.env.assign_template(base.name.evaluate(self.env),
                                 base.as_triples(self.env))

        expect = [(Self(), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y').evaluate(self.env), Value(2))]

        self.assertEqual(specialised.as_triples(self.env), expect)

    def test_as_triples_with_base_chain(self):

        forms = self.parser.parse('a()(x=1)' +
                                  'b() from a()(y=2)' +
                                  'c() from b()(z=3)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        self.env.assign_template(a.name.evaluate(self.env),
                                 a.as_triples(self.env))
        self.env.assign_template(b.name.evaluate(self.env),
                                 b.as_triples(self.env))

        expect = [(Self(), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y').evaluate(self.env), Value(2)),
                  (Self(), Name('z').evaluate(self.env), Value(3))]

        self.assertEqual(c.as_triples(self.env), expect)

    def test_as_triples_with_base_with_self(self):

        forms = self.parser.parse('a()(x = self) b() from a()(y = 2)')
        base = forms[0]
        specialised = forms[1]

        self.env.assign_template(base.name.evaluate(self.env), base.as_triples(self.env))
        expect = [(Self(), Name('x').evaluate(self.env), Name(Self())),
                  (Self(), Name('y').evaluate(self.env), Value(2))]

        self.assertEqual(specialised.as_triples(self.env), expect)

    def test_as_triples_params(self):

        forms = self.parser.parse('a(x)(property = x)')
        a = forms[0]

        expect = [(Self(), Name('property').evaluate(self.env), Parameter('x', 0))]
        self.assertEqual(a.as_triples(self.env), expect)

    def test_as_triples_with_base_with_params(self):

        forms = self.parser.parse('a(x)(x = 12345) b(y) from a(y)')
        a = forms[0]
        b = forms[1]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))
        expect = [(Self(), Parameter('y', 0), Value(12345))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_args(self):

        forms = self.parser.parse('a(x)(x = 12345) b() from a(12345)')
        a = forms[0]
        b = forms[1]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))
        expect = [(Self(), Value(12345), Value(12345))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_multiple_base_args_and_parameters(self):

        forms = self.parser.parse('a(x, y)(x = y)' +
                                  'b(x, y) from a(x, "string")(z=y)' +
                                  'c(x, y) from b(1, 2)(x=y)')
        a = forms[0]
        b = forms[1]
        c = forms[2]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))
        self.env.assign_template(b.name.evaluate(self.env), b.as_triples(self.env))

        expect = [(Self(), Value(1), Value("string")),
                  (Self(), Name('z').evaluate(self.env), Value(2)),
                  (Self(), Parameter('x', 0), Parameter('y', 0))]

        self.assertEqual(expect, c.as_triples(self.env))

    def test_forward_parameters(self):

        forms = self.parser.parse('b(y) from a(y)')
        b = forms[0]

        self.assertEqual(b.args, [Argument(Name('y'), 0)])
        b.forward_parameters()

        self.assertEqual(b.args, [Argument(Parameter('y', 0), 0)])

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

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y').evaluate(self.env), Name('e').evaluate(self.env)),]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self(self):

        forms = self.parser.parse('a()(x = 1) b()(self.y = e is a a())')
        a = forms[0]
        b = forms[1]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))

        expect = [(Name('e').evaluate(self.env), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name(Self(), 'y'), Name('e').evaluate(self.env)),]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self_as_name(self):

        forms = self.parser.parse('a()(x = 1) b()(y = self.e is a a())')
        a = forms[0]
        b = forms[1]

        self.env.assign_template(a.name.evaluate(self.env), a.as_triples(self.env))

        expect = [(Name(Self(), 'e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y').evaluate(self.env), Name(Self(), 'e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_self_named_expansion(self):

        forms = self.parser.parse('s()(z=self) t()(x=self.e is a s())')
        s = forms[0]
        t = forms[1]

        self.env.assign_template(s.name.evaluate(self.env), s.as_triples(self.env))

        expect_s = [(Self(), Name('z').evaluate(self.env), Self())]
        expect_t = [(Name(Self(), 'e'), Name('z').evaluate(self.env), Name(Self(), 'e')),
                    (Self(), Name('x').evaluate(self.env), Name(Self(), 'e'))]

        self.assertEqual(expect_s, s.as_triples(self.env))
        self.assertEqual(expect_t, t.as_triples(self.env))

    def test_as_triples_with_expansion_as_argument(self):

        forms = self.parser.parse('r()(y=1) s(exp)(x=exp)' +
                                  't() from s(e is a r())')

        r = forms[0]
        s = forms[1]
        t = forms[2]

        self.env.assign_template(r.name.evaluate(self.env),
                                 r.as_triples(self.env))
        self.env.assign_template(s.name.evaluate(self.env),
                                 s.as_triples(self.env))

        expect = [(Self(),
                   Name('x').evaluate(self.env),
                   Name('e').evaluate(self.env))]

        self.assertEqual(expect, t.as_triples(self.env))

    def test_evaluate_stores_triples(self):

        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        t.evaluate(self.env)

        self.assertEqual(self.env.lookup_template(t.name.evaluate(self.env)),
                         t.as_triples(self.env))

    def test_init_extensions(self):

        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        self.assertEqual(t.extensions, [ExtensionPragma('E', []), ExtensionPragma('F', [])])


    def test_evaluate_stores_extensions(self):

        forms = self.parser.parse('t()(@extension E() @extension F())')
        t = forms[0]

        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))

        self.assertEqual(found, [ExtensionPragma('E', []), ExtensionPragma('F', [])])

    def test_evaluate_stores_base_extensions(self):

        forms = self.parser.parse('s()(@extension F()) t() from s()(@extension E())')
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

