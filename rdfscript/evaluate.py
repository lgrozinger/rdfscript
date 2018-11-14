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
                         Expansion)

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

def evaluate_value(value, env):

    return value.as_rdfliteral()

def evaluate_template(template, env):

    root_node = env.resolve_name(template.name.prefix,
                                 template.name.localname)

    template_ns = rdflib.Namespace(root_node)

    triples = []

    for parameter in template.parameters:
        param_predicate = template_ns['parameter' + str(parameter.position)]
        triples.append((root_node, param_predicate, parameter.as_rdfbnode()))

    template.parameterise()

    for body_statement in template.body:
        if isinstance(body_statement, Property):
            triples.append((root_node,
                            evaluate(body_statement.name, env),
                            evaluate(body_statement.value, env)))

        elif isinstance(body_statement, InstanceExp):
            pass

    env.put_template(root_node, triples)

def evaluate_expansion(expansion, env):

    template = expansion.template

    if isinstance(template, Uri):
        template_uri = evaluate_uri(template, env)
    elif isinstance(template, Name):
        template_uri = env.resolve_name(template.localname, prefix=template.prefix)
    else:
        raise SyntaxError("Invalid template: %s at %s" % (template, template.location))


    triples = env.get_template(template_uri)

    ## replace parameters with given arguments

    ## replace the root node with the name of the instancebody

    ## add to the user context



    pass

def unknown_node(node, env):
    return node

_handler_index = {
    Uri          : evaluate_uri,
    Name         : evaluate_name,
    PrefixPragma : evaluate_prefixpragma,
    Assignment   : evaluate_assignment,
    Value        : evaluate_value,
    Template     : evaluate_template,
    Expansion    : evaluate_expansion,
}
