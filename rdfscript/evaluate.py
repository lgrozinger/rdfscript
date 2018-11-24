import rdflib
import logging

from .core import (Uri,
                   Value,
                   Name)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma)

from .templating import (Assignment,
                         Template,
                         Property,
                         Argument,
                         Expansion)

from .error import (UnknownConstruct,
                    PrefixError,
                    FailToImport)

def evaluate(node, env):

    return _handler_index.get(type(node), unknown_node)(node, env)

def evaluate_uri(uri, env):

    return uri.as_uriref()

def evaluate_name(name, env):

    resolved_name = env.resolve_name(name.prefix, name.localname)

    lookup = env.lookup(resolved_name)

    return lookup or resolved_name

def evaluate_assignment(assignment, env):

    uri   = env.resolve_name(assignment.name.prefix,
                             assignment.name.localname)

    value = evaluate(assignment.value, env)

    env.assign(uri, value)

    return value

def evaluate_prefixpragma(pragma, env):

    uri = pragma.uri
    return env.bind_prefix(pragma.prefix, evaluate(uri, env))

def evaluate_defaultprefixpragma(pragma, env):

    if not env.set_default_prefix(pragma.prefix):
        raise PrefixError(pragma.prefix, pragma.location)
    else:
        return pragma.prefix

def evaluate_importpragma(pragma, env):
    if not env.eval_import(evaluate(pragma.target, env)):
        raise FailToImport(pragma.target, pragma.location)

    return pragma.target

def evaluate_value(value, env):

    return value.as_rdfliteral()

def evaluate_template(template, env):

    template.parameterise()
    template.prefixify(env.default_prefix)
    template_uri = env.resolve_name(template.name.prefix, template.name.localname)
    env.assign_template(template_uri, template)

def evaluate_expansion(expansion, env):

    #expansion.prefixify(env.default_prefix)
    raw_triples = expansion.as_triples(env)

    for triple in raw_triples:
        evaluate_triple(triple, env)

    return evaluate(expansion.name, env)

def evaluate_argument(argument, env):

    return evaluate(argument.value, env)

def evaluate_triple(triple, env):
    (s, p, o) = triple
    env.add_triples([(evaluate(s, env), evaluate(p, env), evaluate(o, env))])

def property_as_triple(subject, prop, env):
    return (subject, evaluate(prop.name, env), evaluate(prop.value, env))

def replace_in_triple(triple, victim, replacement):
    (s, p, o) = triple
    if s == victim: s = replacement
    if p == victim: p = replacement
    if o == victim: o = replacement

    return (s, p, o)

def unknown_node(node, env):
    raise UnknownConstruct(node, node.location)

_handler_index = {
    Uri                 : evaluate_uri,
    Name                : evaluate_name,
    PrefixPragma        : evaluate_prefixpragma,
    DefaultPrefixPragma : evaluate_defaultprefixpragma,
    ImportPragma        : evaluate_importpragma,
    Assignment          : evaluate_assignment,
    Value               : evaluate_value,
    Template            : evaluate_template,
    Expansion           : evaluate_expansion,
    Argument            : evaluate_argument,
    type(None)          : unknown_node,
}
