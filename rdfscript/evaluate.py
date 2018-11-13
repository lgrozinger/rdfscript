import rdflib

from .core import (Uri,
                   Value,
                   Name)

from .pragma import (PrefixPragma,
                     DefaultPrefixPragma,
                     ImportPragma)

from .templating import (Assignment,
                         Template,
                         Property,
                         InstanceExp)

def evaluate(node, env):

    return _handler_index.get(type(node), unknown_node)(node, env)

def unknown_node(node, env):

    print("Unknown node type encountered.")
    return None

def evaluate_uri(uri, env):

    return uri.as_uriref()

def evaluate_name(name, env):

    return env.lookup(env.resolve_name(name.localname,
                                       prefix=name.prefix))

def evaluate_assignment(assignment, env):

    uri   = env.resolve_name(assignment.name.localname,
                             prefix = assignment.name.prefix)
    value = evaluate(assignment.value, env)

    env.assign(uri, value)

    return value

def evaluate_prefixpragma(pragma, env):

    uri = pragma.uri
    return env.bind_prefix(pragma.prefix, evaluate_uri(uri, env))

def evaluate_value(value, env):

    return value.as_rdfliteral()

def evaluate_template(template, env):

    root_node = env.resolve_name(template.name.localname,
                                 template.name.prefix)

    triples = []

    for parameter in template.parameters:
        triples.append(
    template.parameterise()

    for body_statement in template.body:
        if isinstance(body_statement, Property):
            triples.append((root_node, body_statement.name, body_statement.value))
        elif isinstance(body_statement, InstanceExp):
            pass

    env.put_template(triples)

_handler_index = {
    Uri          : evaluate_uri,
    Name         : evaluate_name,
    PrefixPragma : evaluate_prefixpragma,
    Assignment   : evaluate_assignment,
    Value        : evaluate_value,
    Template     : evaluate_template
}
