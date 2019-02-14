import rdflib
import pdb

import rdfscript.core as core
import rdfscript.utils as utils
import rdfscript.pragma as pragma
import rdfscript.error as error
import rdfscript.templates as templates
import rdfscript.template_graphs as tgraphs


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


def evaluate_three(three, rt):
    e_one = evaluate(three.one, rt)
    e_two = evaluate(three.two, rt)
    e_three = evaluate(three.three, rt)

    utils.type_assert(e_one, core.Uri)
    utils.type_assert(e_two, core.Uri)
    utils.type_assert(e_three, core.Uri, core.Value)

    rt._g.graph.add(utils.to_rdf_triple((e_one, e_two, e_three)))
    return three.one


def evaluate_two(two, rt):
    e_one = evaluate(two.one, rt)
    e_two = evaluate(two.two, rt)

    utils.type_assert(e_one, core.Uri)
    utils.type_assert(e_two, core.Uri)

    s = utils.to_rdf(e_one)
    p = utils.to_rdf(e_two)
    o = rt._g.graph.value(subject=s, predicate=p)

    if o is not None:
        o = utils.from_rdf(o)

    return o


def evaluate_prefix(pragma, rt):
    uri = pragma.uri
    if isinstance(uri, core.Name):
        uri = rt.binding(uri)

    utils.type_assert(uri, core.Uri)
    utils.type_assert(pragma.prefix, core.Name)

    rt.add_prefix(pragma.prefix, uri)
    return pragma.prefix


def evaluate_defaultprefix(pragma, rt):
    prefix = pragma.prefix
    utils.type_assert(prefix, core.Name)

    rt.prefix = prefix
    return prefix


def evaluate_import(pragma, env):
    if not env.evalppppP_import(evaluate(pragma.target, env)):
        raise FailToImport(
            pragma.target, env.get_current_path(), pragma.location)

    return pragma.target


def evaluate_using(pragma, rt):
    utils.type_assert(pragma.prefix, core.Name)

    context = rt.context(pragma.prefix)
    edges = context.out_edges()
    for edge in edges:
        (where, what) = edge
        rt.bind(what, core.Name(where.uri))

    return pragma.prefix


def evaluate_template(template, rt):
    tgraphs.hang_params(template, rt)
    tgraphs.hang_body(template, rt)

    return template.name


def evaluate_extensionpragma(pragma, env):
    ext = env.get_extension(pragma.name)

    if not ext:
        raise NoSuchExtension(pragma.name, pragma.location)
    else:
        args = [evaluate(arg, env) for arg in pragma.args]
        return ext(*args)


def evaluate_value(value, env):

    return value


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
    core.Three: evaluate_three,
    core.Two: evaluate_two,
    templates.Template: evaluate_template,
    pragma.PrefixPragma: evaluate_prefix,
    pragma.DefaultPrefixPragma: evaluate_defaultprefix,
    pragma.UsingPragma: evaluate_using,
    type(None): unknown_node,
}
