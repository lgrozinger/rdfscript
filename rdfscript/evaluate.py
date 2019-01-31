import rdflib
import logging
import pdb

import rdfscript.core as core
import rdfscript.utils as utils
import rdfscript.pragma as pragma
import rdfscript.error as error


def evaluate(node, env):
    return _handler_index.get(type(node), unknown_node)(node, env)


def evaluate_uri(uri, env):
    return uri


def evaluate_name(name, rt):
    utils.type_assert(name, core.Name)
    result = rt.binding(name)
    return result


def evaluate_assignment(assignment, rt):
    name = assignment.name
    utils.type_assert(name, core.Name)
    existing_binding = rt.bound_p(name)
    if existing_binding:
        raise error.BindingError(name, existing_binding, name.location)

    value = evaluate(assignment.value, rt)
    utils.type_assert(value, core.Uri, core.Value)

    rt.bind(value, name)
    return value


def evaluate_prefixpragma(pragma, rt):
    uri = pragma.uri
    if isinstance(uri, core.Name):
        uri = rt.binding(uri)

    utils.type_assert(uri, core.Uri)
    utils.type_assert(pragma.prefix, core.Name)

    rt.add_prefix(pragma.prefix, uri)
    return pragma.prefix


def evaluate_defaultprefixpragma(pragma, rt):
    prefix = pragma.prefix
    utils.type_assert(prefix, core.Name)

    rt.prefix = prefix
    return prefix


def evaluate_importpragma(pragma, env):
    if not env.eval_import(evaluate(pragma.target, env)):
        raise FailToImport(
            pragma.target, env.get_current_path(), pragma.location)

    return pragma.target


def evaluate_extensionpragma(pragma, env):
    ext = env.get_extension(pragma.name)

    if not ext:
        raise NoSuchExtension(pragma.name, pragma.location)
    else:
        args = [evaluate(arg, env) for arg in pragma.args]
        return ext(*args)


def evaluate_self(myself, env):

    return env.lookup(myself.uri(env)) or myself.uri(env)


def evaluate_value(value, env):

    return value


def evaluate_template(template, env):

    template.parameterise()
    template.de_name(env)
    env.assign_template(template.name, template)

    return template.name


def evaluate_expansion(expansion, env):

    expansion.de_name(env)
    raw_triples = expansion.replace_self(expansion.as_triples(env), env)

    evaluated_triples = [(evaluate(s, env), evaluate(p, env), evaluate(o, env))
                         for (s, p, o) in raw_triples]

    final_triples = evaluated_triples
    pack = TriplePack(final_triples, env._symbol_table, env._template_table)
    for extension in expansion.get_extensions(env):
        e = evaluate(extension, env)
        e.run(pack)

    env.add_triples(pack.triples)

    return expansion.name


def evaluate_argument(argument, env):

    return evaluate(argument.value, env)


def evaluate_triple(triple, env):
    (s, p, o) = triple
    env.add_triples([(evaluate(s, env), evaluate(p, env), evaluate(o, env))])


def property_as_triple(subject, prop, env):
    return (subject, evaluate(prop.name, env), evaluate(prop.value, env))


def replace_in_triple(triple, victim, replacement):
    (s, p, o) = triple
    if s == victim:
        s = replacement
    if p == victim:
        p = replacement
    if o == victim:
        o = replacement

    return (s, p, o)


def unknown_node(node, env):
    raise error.UnknownConstruct(node, node.location)


_handler_index = {
    core.Uri: evaluate_uri,
    core.Name: evaluate_name,
    core.Assignment: evaluate_assignment,
    core.Value: evaluate_value,
    pragma.PrefixPragma: evaluate_prefixpragma,
    pragma.DefaultPrefixPragma: evaluate_defaultprefixpragma,
    type(None): unknown_node,
}
