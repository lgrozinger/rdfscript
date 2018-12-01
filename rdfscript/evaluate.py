import rdflib
import logging
import pdb

from .core import (Uri,
                   Value,
                   Name,
                   Self)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma,
                     ExtensionPragma)

from .templating import (Assignment,
                         Template,
                         Property,
                         Argument,
                         Expansion)

from .error import (UnknownConstruct,
                    PrefixError,
                    FailToImport,
                    NoSuchExtension,
                    ExtensionFailure)

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
        raise FailToImport(pragma.target, env.get_current_path(), pragma.location)

    return pragma.target

def evaluate_extensionpragma(pragma, env):
    ext = env.get_extension(pragma.name)

    if not ext:
        raise NoSuchExtension(pragma.name, pragma.location)
    else:
        args = [evaluate(arg, env) for arg in pragma.args]
        return ext(*args)

def evaluate_self(myself, env):

    return evaluate_name(Name(None, '', myself.location), env)

def evaluate_value(value, env):

    return value.as_rdfliteral()

def evaluate_template(template, env):

    template.parameterise()
    template.prefixify(env.default_prefix)
    template_uri = env.resolve_name(template.name.prefix, template.name.localname)
    env.assign_template(template_uri, template)

def evaluate_expansion(expansion, env):

    expansion.prefixify(env.default_prefix)
    raw_triples = expansion.as_triples(env)

    evaluated_triples = [(evaluate(s, env), evaluate(p, env), evaluate(o, env))
                          for (s, p, o) in raw_triples]

    final_triples = evaluated_triples
    for extension in expansion.get_extensions(env):
        e = evaluate(extension, env)
        result = e.run(final_triples, env)
        if not result:
            if e.failure_message:
                raise ExtensionFailure(e.failure_message, expansion.location)
            else:
                raise ExtensionFailure(None, expansion.location)
        else:
            final_triples = result

    env.add_triples(final_triples)

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
    ExtensionPragma     : evaluate_extensionpragma,
    Assignment          : evaluate_assignment,
    Value               : evaluate_value,
    Template            : evaluate_template,
    Expansion           : evaluate_expansion,
    Argument            : evaluate_argument,
    Self                : evaluate_self,
    type(None)          : unknown_node,
}
