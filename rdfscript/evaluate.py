import rdflib
import pdb

import rdfscript.core as core
import rdfscript.utils as utils
import rdfscript.pragma as pragma
import rdfscript.error as error
import rdfscript.templates as templates


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
    hang_params(template, rt)
    hang_body(template, rt)

    return template.name


def set_template_type(template, rt):
    type_uri = core.lang_uri(template)
    type_predicate = utils.from_rdf(rdflib.RDF.type)
    names = template.name.names + [type_predicate]
    rt.bind(type_uri, core.Name(*names))


def template_context(template, rt):
    context = rt.context(template.name)

    if context is None:
        set_template_type(template, rt)
        context = rt.context(template.name)

    return context


def hang_params(template, rt):
    for (parameter, index) in template.parameters:
        predicate = core.params_uri(index)
        param_uri = utils.name_to_uri(parameter)
        context = template_context(template, rt)

        context.put(utils.contextualise_uri(param_uri, context), predicate)


def get_param(template, index, rt):
    context = template_context(template, rt)
    return context.get(core.params_uri(index))


def hang_body(template, rt):
    for statement in template.body:
        hang_three(template, statement, rt)


def hang_three(template, three, rt):

    def sub_params(possible_param):
        result = possible_param
        i = template.is_parameter(possible_param)
        if i:
            result = get_param(template, i, rt)

        return result

    three.map(sub_params)
    step_one = core.Three(template.name, core.triple_uri(1), three.one)
    step_two = core.Three(three.one, core.triple_uri(2), three.two)
    step_three = core.Three(three.two, core.triple_uri(3), three.three)

    for step in [step_one, step_two, step_three]:
        evaluate(step, rt)


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
    core.Three: evaluate_three,
    core.Two: evaluate_two,
    templates.Template: evaluate_template,
    pragma.PrefixPragma: evaluate_prefix,
    pragma.DefaultPrefixPragma: evaluate_defaultprefix,
    pragma.UsingPragma: evaluate_using,
    type(None): unknown_node,
}
