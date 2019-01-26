import unittest

import rdfscript.core as core

from rdfscript.env import Env

import rdfscript.error as error


class CoreNameTest(unittest.TestCase):

    def setUp(self):
        self.env = Env()

    def tearDown(self):
        None

    def test_name_names(self):

        name = core.Name('first', 'second', 'third')
        self.assertEqual(name.names, ['first', 'second', 'third'])

        u1 = core.Uri('http://test.eg')
        u2 = core.Uri('#fragment')
        name = core.Name(u1, u2)
        self.assertEqual(name.names, [u1, u2])

    def test_name_equal(self):

        name1 = core.Name('first', 'second', 'third')
        name2 = core.Name('first', 'second', 'third', location=True)
        self.assertEqual(name1, name2)

        name3 = core.Name('first', 'second')
        self.assertNotEqual(name1, name3)

    def test_name_init_with_incompatible_type(self):
        with self.assertRaises(error.UnexpectedType):
            core.Name('a', 'b', self)

    def test_not_concrete_p(self):
        self.env.current_self = core.Self()
        not_concrete = core.Name(core.Self(), 'a')
        self.assertFalse(not_concrete.concrete_p(self.env))

    def test_concrete_p(self):
        self.env.current_self = core.Uri('')
        concrete = core.Name(core.Self(), 'a')
        self.assertTrue(concrete.concrete_p(self.env))

    def test_bound_p_bound_one_level_name(self):
        env = Env()
        variable = core.Uri('variable')
        env.add_triples([(env.glowball, variable, core.Value(12345))])

        self.assertTrue(core.Name('variable').bound_p(env))
        self.assertEqual(core.Value(12345), core.Name('variable').bound_p(env))

    def test_bound_p_bound_two_level_name(self):
        env = Env()
        ns = env.glowball
        v = 'variable'
        u = 'symbol'
        v_uri = core.Uri(ns.uri + v)
        u_uri = core.Uri(u)
        env.add_triples([(ns, core.Uri(v), v_uri),
                         (v_uri, u_uri, core.Value(12345))])

        self.assertTrue(core.Name(v, u).bound_p(env))
        self.assertEqual(core.Value(12345), core.Name(v, u).bound_p(env))

    def test_bound_p_bound_one_level_uri(self):
        env = Env()
        env.add_triples(
            [(env.glowball, core.Uri('variable'), core.Value(12345))])

        self.assertTrue(core.Name(core.Uri('variable')).bound_p(env))
        self.assertEqual(core.Value(12345), core.Name('variable').bound_p(env))

    def test_bound_p_bound_two_level_uri(self):
        env = Env()
        ns = env.glowball
        v = 'variable'
        u = 'symbol'
        v_uri = core.Uri(ns.uri + v)
        u_uri = core.Uri(u)
        env.add_triples([(env.glowball, core.Uri(v), v_uri),
                         (v_uri, u_uri, core.Value(12345))])

        self.assertTrue(core.Name(v_uri, u_uri).bound_p(env))
        self.assertEqual(core.Value(12345), core.Name(v, u).bound_p(env))

    def test_bound_p_unbound_one_level_name(self):
        env = Env()

        self.assertFalse(core.Name('variable').bound_p(env))

    def test_bound_p_unbound_two_level_name(self):
        env = Env()
        v = 'variable'
        u = 'symbol'

        self.assertFalse(core.Name(v, u).bound_p(env))

    def test_bound_p_unbound_one_level_uri(self):
        env = Env()

        self.assertFalse(core.Name(core.Uri('variable')).bound_p(env))

    def test_bound_p_unbound_two_level_uri(self):
        env = Env()
        v = 'variable'
        u = 'symbol'

        self.assertFalse(core.Name(core.Uri(v), core.Uri(u)).bound_p(env))

    def test_name_evaluate_unbound_local(self):
        self.env.bind_prefix('prefix', core.Uri('prefix'))
        self.env.prefix = 'prefix'
        name = core.Name('first')
        uri = core.Uri('prefixfirst')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_unbound_local_with_None_prefix(self):
        name = core.Name('first')
        uri = core.Uri('first')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_unbound_prefixed(self):
        self.env.bind_prefix('prefix', core.Uri('prefix'))
        self.env.prefix = 'prefix'
        name = core.Name('first', 'second')
        uri = core.Uri('prefixfirstsecond')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_unbound_prefixed_with_None_prefix(self):
        name = core.Name('first', 'second')
        uri = core.Uri('firstsecond')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_unbound_chained(self):
        self.env.bind_prefix('prefix', core.Uri('prefix'))
        self.env.prefix = 'prefix'
        name = core.Name('first', 'second', 'third', 'fourth')
        uri = core.Uri('prefixfirstsecondthirdfourth')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_unbound_chained_with_None_prefix(self):
        name = core.Name('first', 'second', 'third', 'fourth')
        uri = core.Uri('firstsecondthirdfourth')

        self.assertEqual(uri, name.evaluate(self.env))

    def test_name_evaluate_bound_local(self):

        name = core.Name('first')
        value = core.Value(1)

        do_assign(name, value, self.env)
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_bound_local_before_prefix_change(self):
        name = core.Name('first')
        value = core.Value(1)
        do_assign(name, value, self.env)

        self.env.bind_prefix('prefix', core.Uri('prefix'))
        self.env.prefix = 'prefix'
        self.assertEqual(value, name.evaluate(self.env))

    def test_name_evaluate_bound_local_after_prefix_change(self):
        name = core.Name('first')
        value1 = core.Value(1)
        do_assign(name, value1, self.env)
        self.env.bind_prefix('prefix', core.Uri('prefix'))
        self.env.prefix = 'prefix'

        value2 = core.Value(2)
        do_assign(name, value2, self.env)
        self.assertEqual(value1, name.evaluate(self.env))
        self.assertEqual(value2, core.Name(
            'prefix', 'first').evaluate(self.env))

    def test_name_evaluate_bound_prefixed(self):

        name = core.Name('first', 'second')
        value = core.Value(1)

        do_assign(name, value, self.env)
        self.assertEqual(value, name.evaluate(self.env))

    # def test_name_evaluate_bound_chained(self):

    #     name = Name('first', 'second', 'third', 'fourth')
    #     value = Value(1)

    #     do_assign(name, value, self.env)
    #     self.assertEqual(value, name.evaluate(self.env))

    # def test_name_evaluate_unbound_unresolved_self_prefix(self):

    #     name = Name(Self(), 'first')
    #     self.env.current_self = Name(Self())

    #     self.assertEqual(name.evaluate(self.env), Name(Self(), 'first'))

    # def test_name_evaluate_unbound_unresolved_self_suffix(self):

    #     name = Name('first', Uri('second'), Self())
    #     self.env.current_self = Name(Self())

    #     self.assertEqual(name.evaluate(self.env), name)

    # def test_name_evaluate_bound_prefix(self):

    #     name = Name('first', 'second')
    #     value = Uri('http://first.org/#')

    #     do_assign(Name('first'), value, self.env)

    #     self.assertEqual(name.evaluate(self.env),
    #                      Uri('http://first.org/#second'))

    # def test_name_evaluate_bound_double_prefix(self):

    #     name = Name('first', 'second', 'third')
    #     value = Uri('http://first.org/#second#')

    #     do_assign(Name('first', 'second'), value, self.env)

    #     self.assertEqual(name.evaluate(self.env), Uri(
    #         'http://first.org/#second#third'))

    # def test_name_evaluate_bound_prefix_not_uri(self):

#     name = Name('first', 'second')
#     value = Value(12345)

#     do_assign(Name('first'), value, self.env)

#     with self.assertRaises(error.UnexpectedType):
#         name.evaluate(self.env)

# def test_name_evaluate_double_bound_prefix_not_uri(self):

#     name = Name('first', 'second', 'third')
#     value = Value(12345)

#     do_assign(Name('first', 'second'), value, self.env)

#     with self.assertRaises(error.UnexpectedType):
#         name.evaluate(self.env)

# def test_name_self_equals_self(self):

#     self.assertEqual(Name(Self()), Self())
#     self.assertEqual(Self(), Name(Self()))
#     self.assertNotEqual(Name(Self(), 'x'), Self())

# def test_name_self_in_context(self):

#     name = Name(Self(), 'name')
#     context = Uri('self')

#     self.env.current_self = context

#     self.assertEqual(name.evaluate(self.env), Uri('selfname'))

# def test_name_self_in_unresolved_context(self):

#     name = Name(Self(), 'name')
#     context = Name(Self())

#     self.env.current_self = context

#     self.assertEqual(name.evaluate(self.env), Name(Self(), 'name'))

# def test_name_self_in_unresolved_context_self_prefix(self):

#     name = Name(Self(), 'name')
#     context = Name(Self(), 'name')

#     self.env.current_self = context

#     self.assertEqual(name.evaluate(self.env), Name(Self(), 'name'))

# def test_uri_first_unbound(self):

#     base = Uri('http://literal.eg/')
#     name = Name(base, 'literal')

#     self.assertEqual(name.evaluate(self.env), Uri(base.uri + 'literal'))


def do_assign(name, value, env):
    core.Assignment(name, value).evaluate(env)
