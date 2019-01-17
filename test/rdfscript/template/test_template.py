import unittest

from rdfscript.rdfscriptparser import RDFScriptParser
from rdfscript.env import Env
from rdfscript.core import (Name,
                            Uri,
                            Self,
                            Value)

from rdfscript.template import (Template,
                                Parameter,
                                check_param_is_name,
                                sub_params_in_triples,
                                replace_self_in_name)

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

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notname)

        self.assertTrue(check_param_is_name(name))

    def test_check_param_not_simple_name(self):

        notparam = Name(Uri('x'))

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notparam)

        notparam = Name(Self())

        with self.assertRaises(UnexpectedType):
            check_param_is_name(notparam)

    def test_check_param_too_many_names(self):

        notparam = Name('x', 'y')

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

        self.env.assign_template(a.name.evaluate(
            self.env), a.as_triples(self.env))
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

        forms = self.parser.parse('a()(x = 1) b()(y = e = a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y'), Name('e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self(self):

        forms = self.parser.parse('a()(x = 1) b()(self.y = e = a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name('e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name(Self(), 'y'), Name('e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_expansion_in_property_with_self_as_name(self):

        forms = self.parser.parse('a()(x = 1) b()(y = self.e = a())')
        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)

        expect = [(Name(Self(), 'e'), Name('x').evaluate(self.env), Value(1)),
                  (Self(), Name('y'), Name(Self(), 'e'))]

        self.assertEqual(expect, b.as_triples(self.env))

    def test_as_triples_with_base_with_self_named_expansion(self):

        forms = self.parser.parse('s()(z=self) t()(x=self.e = s())')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)

        e = Name(Self(), 'e')

        expect_s = [(Name(Self()), Name('z'), Self())]
        expect_t = [(e, Name('z').evaluate(self.env), e),
                    (Name(Self()), Name('x'), e)]

        self.assertEqual(expect_s, s.as_triples(self.env))
        self.assertEqual(expect_t, t.as_triples(self.env))

    def test_as_triples_with_expansion_as_argument(self):

        forms = self.parser.parse('r()(y=1) s(exp)(x=exp)' +
                                  't()(s(e = r()))')

        r = forms[0]
        s = forms[1]
        t = forms[2]

        r.evaluate(self.env)
        s.evaluate(self.env)

        e = self.parser.parse('e = r()')[0]

        expect = [(Self(), Name('x').evaluate(self.env), e)]

        self.assertEqual(expect, t.as_triples(self.env))

    def test_evaluate_stores_triples(self):

        forms = self.parser.parse('t()(x=1 y=2)')
        t = forms[0]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_of_base(self):

        forms = self.parser.parse('s()(z=3)t()(x=1 y=2 s())')
        s = forms[0]
        t = forms[1]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), Value(3))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_of_bases(self):

        forms = self.parser.parse('q()(a=4) s()(z=3)t()(x=1 y=2 s() q())')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), Value(3)),
                  (Name(Self()), Name('a').evaluate(self.env), Value(4))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_of_chained_bases(self):

        forms = self.parser.parse('q()(a=4) s()(z=3 q())t()(x=1 y=2 s())')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), Value(3)),
                  (Name(Self()), Name('a').evaluate(self.env), Value(4))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_parameterised_bases(self):

        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q("s"))' +
                                  't()(x=1 y=2 s("t"))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), Value("t")),
                  (Name(Self()), Name('a').evaluate(self.env), Value("s"))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_forward_parameterised_bases(self):

        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q(t))' +
                                  't()(x=1 y=2 s("t"))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), Value("t")),
                  (Name(Self()), Name('a').evaluate(self.env), Value("t"))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_unevaluated_parameter(self):

        forms = self.parser.parse('q(p)(a=p)' +
                                  's(t)(z=t q(t))' +
                                  't(t)(x=1 y=2 s(t))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        param = Parameter('t', 0)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), param),
                  (Name(Self()), Name('a').evaluate(self.env), param)]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_unevaluated_parameters(self):

        forms = self.parser.parse('q(p)(a=p)' +
                                  's(u,v)(z=u q(v))' +
                                  't(a,b)(x=1 y=2 s(a,b))')
        q = forms[0]
        s = forms[1]
        t = forms[2]

        self.assertFalse(self.env.lookup_template(t.name.evaluate(self.env)))

        q.evaluate(self.env)
        s.evaluate(self.env)
        t.evaluate(self.env)

        a = Parameter('a', 0)
        b = Parameter('b', 1)

        found = self.env.lookup_template(t.name.evaluate(self.env))
        expect = [(Name(Self()), Name('x').evaluate(self.env), Value(1)),
                  (Name(Self()), Name('y').evaluate(self.env), Value(2)),
                  (Name(Self()), Name('z').evaluate(self.env), a),
                  (Name(Self()), Name('a').evaluate(self.env), b)]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_as_property(self):

        forms = self.parser.parse('a(x)(p=x)' +
                                  'b()(q = e = a(2))')

        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        b.evaluate(self.env)

        env = self.env
        me = Name(Self())

        found = env.lookup_template(b.name.evaluate(env))
        expect = [(Name('e').evaluate(env), Name('p').evaluate(env), Value(2)),
                  (me, Name('q').evaluate(env), Name('e').evaluate(env))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_in_body(self):

        forms = self.parser.parse('a(x)(p=x)' +
                                  'b()(e = a(2))')

        a = forms[0]
        b = forms[1]

        a.evaluate(self.env)
        b.evaluate(self.env)

        env = self.env

        found = env.lookup_template(b.name.evaluate(env))
        expect = [(Name('e').evaluate(env), Name('p').evaluate(env), Value(2))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_expansion_in_argument(self):

        forms = self.parser.parse('a(x)(p=x)' +
                                  'b(x)(e=x)' +
                                  'c()(b(f = a(2)))')

        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)
        c.evaluate(self.env)

        env = self.env
        me = Name(Self())

        found = env.lookup_template(c.name.evaluate(env))
        expect = [(Name('f').evaluate(env), Name('p').evaluate(env), Value(2)),
                  (me, Name('e').evaluate(env), Name('f').evaluate(env))]

        self.assertEqual(found, expect)

    def test_evaluate_stores_triples_with_expansions(self):

        forms = self.parser.parse('a(x)(e=x)' +
                                  'b(y)(p=y)' +
                                  'c()(a(f = b(1))' +
                                  '    q = g = b(2)' +
                                  '    h = b(3))')

        a = forms[0]
        b = forms[1]
        c = forms[2]

        a.evaluate(self.env)
        b.evaluate(self.env)
        c.evaluate(self.env)

        me = Name(Self())
        env = self.env

        f = Name('f').evaluate(env)
        g = Name('g').evaluate(env)
        h = Name('h').evaluate(env)

        found = env.lookup_template(c.name.evaluate(env))
        expect = [(f, Name('p').evaluate(env), Value(1)),
                  (me, Name('e').evaluate(env), f),
                  (g, Name('p').evaluate(env), Value(2)),
                  (me, Name('q').evaluate(env), g),
                  (h, Name('p').evaluate(env), Value(3))]

        self.assertEqual(found, expect)

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

        self.assertEqual(found, [ExtensionPragma(
            'E', []), ExtensionPragma('F', [])])

    def test_evaluate_stores_base_extensions(self):

        forms = self.parser.parse(
            's()(@extension F()) t()(s() @extension E())')
        s = forms[0]
        t = forms[1]

        s.evaluate(self.env)
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))
        expect = [ExtensionPragma('F', []), ExtensionPragma('E', [])]

        self.assertEqual(found, expect)

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
        expect = [ExtensionPragma('E', [Name('argument').evaluate(self.env)])]

        self.assertEqual(found, expect)

    def test_evaluate_extension_self_name(self):

        forms = self.parser.parse('t()(@extension E(self.argument))')
        t = forms[0]

        self.env.current_self = Name(Self())
        t.evaluate(self.env)

        found = self.env.lookup_extensions(t.name.evaluate(self.env))
        expect = [ExtensionPragma('E', [Name(Self(), 'argument')])]

        self.assertEqual(found, expect)

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
                                  't()(self.e = s()(b = 2))')

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
                                  't()(x = self.e = s()(b = 2))')

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

    def test_replace_self_with_name(self):

        name = Name(Self(), 'name')

        name = replace_self_in_name(name, Name('self'))

        self.assertEqual(name, Name('self', 'name'))

    def test_replace_self_with_dotted_name(self):

        name = Name(Self(), 'name')

        name = replace_self_in_name(name, Name('self', 'self', 'self'))

        self.assertEqual(name, Name('self', 'self', 'self', 'name'))

    def test_replace_self_with_uri(self):

        name = Name(Self(), 'name')

        name = replace_self_in_name(name, Uri('self'))

        self.assertEqual(name, Name(Uri('self'), 'name'))

    def test_as_triples_multiple_inheritance(self):

        forms = self.parser.parse('s()(a=123)' +
                                  't()(b=456)' +
                                  'u()(s() t())')

        s = forms[0]
        t = forms[1]
        u = forms[2]

        s.evaluate(self.env)
        t.evaluate(self.env)

        expect = [(Name(Self()),
                   Name('a').evaluate(self.env),
                   Value(123)),
                  (Name(Self()),
                   Name('b').evaluate(self.env),
                   Value(456))]

        self.assertEqual(expect, u.as_triples(self.env))

    def test_as_triples_nested_multiple_inheritance(self):

        forms = self.parser.parse('s()(a=123)' +
                                  't()(s() b=456)' +
                                  'u()(s() t() c=789)' +
                                  'v()(s() t() u())')

        s = forms[0]
        t = forms[1]
        u = forms[2]
        v = forms[3]

        s.evaluate(self.env)
        t.evaluate(self.env)
        u.evaluate(self.env)

        a = (Name(Self()), Name('a').evaluate(self.env), Value(123))
        b = (Name(Self()), Name('b').evaluate(self.env), Value(456))
        c = (Name(Self()), Name('c').evaluate(self.env), Value(789))

        expect = [a, a, b, a, a, b, c]

        self.assertEqual(expect, v.as_triples(self.env))
