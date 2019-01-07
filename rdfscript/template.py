from .core import (Node,
                   Name,
                   Uri,
                   Self)
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)

class Template(Node):

    def __init__(self, name, parameters, body, location=None):

        Node.__init__(self, location)
        self._name = name

        self._parameters = []
        for param in parameters:
            check_param_is_name(param)
            self._parameters.append(Parameter(param.names[0],
                                              parameters.index(param),
                                              location))

        self._extensions = []
        self._body = body

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @property
    def body(self):
        return self._body

    @property
    def extensions(self):
        return self._extensions

    def __eq__(self, other):
        return (isinstance(other, Template) and
                self._name == other.name and
                self._parameters == other.parameters and
                self._body == other.body)

    def __repr__(self):
        return format("[TEMPLATE: %s (%s)\n(%s)\n"
                      % (self.name, self.parameters, self.body))

    def as_triples(self, context):
        triples = []

        old_self = context.current_self
        context.current_self = Name(Self())
        for statement in self.body:
            if not isinstance(statement, ExtensionPragma):
                triples += statement.as_triples(context)

        context.current_self = old_self

        triples = sub_params_in_triples(self.parameters, triples)

        return triples

    def store_triples(self, context):

        unevaluated_triples = self.as_triples(context)

        def triple_eval(triple):
            (s, p, o) =  triple
            return (s.evaluate(context),
                    p.evaluate(context),
                    o.evaluate(context))

        evaluated_triples = [triple_eval(triple) for triple in unevaluated_triples]

        uri = self.name.evaluate(context)
        context.assign_template(uri, evaluated_triples)

        return evaluated_triples

    def collect_extensions(self, context):

        collected = []

        for statement in self.body:
            if isinstance(statement, ExtensionPragma):
                collected.append(statement)
            elif isinstance(statement, Expansion) and statement.name is None:
                collected += statement.get_extensions(context)

        return collected

    def store_extensions(self, context):

        extensions = self.collect_extensions(context)
        for ext in extensions:
            ext.substitute_params(self.parameters)

        old_self = context.current_self
        context.current_self = Name(Self())
        extensions = [ext.evaluate(context) for ext in extensions]
        context.current_self = old_self

        uri = self.name.evaluate(context)
        context.assign_extensions(uri, extensions)

        return extensions

    def evaluate(self, context):

        old_self = context.current_self
        context.current_self = Name(Self())

        self.store_triples(context)
        self.store_extensions(context)

        context.current_self = old_self

        return self.name.evaluate(context)


class Parameter(Node):

    def __init__(self, name_string, position, location=None):

        super().__init__(location)
        self._param_name = name_string
        self._position = position

    @property
    def name(self):
        return self.as_name()

    @property
    def position(self):
        return self._position

    def __eq__(self, other):
        return (isinstance(other, Parameter) and
                self.name == other.name)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return format("[RDFscript PARAM: %s]" % self.name)

    def as_name(self):
        return Name(self._param_name)

    def is_substitute(self, name):
        return (isinstance(name, Name) and
                len(name.names) == 1 and
                isinstance(name.names[0], str) and
                name.names[0] == self._param_name)

    def evaluate(self, env):
        return self


class Property(Node):

    def __init__(self, name, value, location=None):

        Node.__init__(self, location)
        self._name = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Property) and
                self.name == other.name and
                self.value == other.value)

    def __str__(self):
        return format("%s = %s\n" % (self.name, self.value))

    def __repr__(self):
        return format("%s = %s\n" % (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def substitute_params(self, parameters):

        for parameter in parameters:
            if parameter.is_substitute(self.name):
                self._name = parameter
            if parameter.is_substitute(self.value):
                self._value = parameter

    def as_triples(self, context):

        triples = []
        # both (names)??? and values can be expansions as well????
        if isinstance(self.value, Expansion):
            triples += self.value.as_triples(context)
            triples += [(Name(Self()),
                         self.name,
                         self.value.name)]
            return triples
        else:
            return [(context.current_self,
                     self.name,
                     self.value)]

class Expansion(Node):

    def __init__(self, name, template, args, body, location=None):

        super().__init__(location)
        self._template = template
        self._name = name
        self._args = []
        for arg in args:
            if isinstance(arg, Argument):
                self._args.append(Argument(arg.value,
                                           args.index(arg),
                                           location))
            else:
                self._args.append(Argument(arg,
                                           args.index(arg),
                                           location))

        self._extensions = []
        self._body = []
        for statement in body:
            if isinstance(statement, ExtensionPragma):
                self._extensions.append(statement)
            else:
                self._body.append(statement)

    def __eq__(self, other):
        return (isinstance(other, Expansion) and
                self.template == other.template and
                self.name == other.name and
                self.args == other.args and
                self.body == other.body)

    def __repr__(self):
        return format("%s is a %s(%s)\n  (%s)\n" % (self.name, self.template, self.args, self.body))

    @property
    def name(self):
        return self._name

    @property
    def template(self):
        return self._template

    @property
    def args(self):
        return self._args

    @property
    def body(self):
        return self._body

    def get_extensions(self, env):
        template_uri = self.template.evaluate(env)

        raw_extensions = env.lookup_extensions(template_uri)
        processed_extensions = []
        for ext in raw_extensions:
            ext_args = ext.args
            for arg in self.args:
                ext_args = [arg.marshal(ext_arg) for ext_arg in ext_args]
            processed_extensions += [ExtensionPragma(ext.name, ext_args)]

        return processed_extensions + self._extensions

    def as_triples(self, env):

        try:
            triples = env.lookup_template(self.template.evaluate(env))
            triples = [marshal(self.args, triple) for triple in triples]
        except KeyError:
            raise TemplateNotFound(self.template, self.template.location)

        old_self = env.current_self
        env.current_self = self.name
        for statement in self.body:
            triples += statement.as_triples(env)
        env.current_self = old_self

        return triples

    def evaluate(self, env):

        triples = self.as_triples(env)
        old_self = env.current_self
        env.current_self = self.name.evaluate(env)

        for ext in self.get_extensions(env):
            triples = ext.run(env, triples)

        env.current_self = old_self

        env.add_triples(triples)

        return self.name.evaluate(env)


class Argument(Node):

    def __init__(self, value_expr, position, location=None):

        super().__init__(location)
        self._value = value_expr
        self._position = position

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def position(self):
        return self._position

    def __eq__(self, other):
        return (isinstance(other, Argument) and
                self.value == other.value and
                self.position == other.position)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return format("[RDFscript ARG: %s]" % self._value)

    def marshal(self, param):
        if isinstance(param, Parameter) and param.position == self.position:
            return self.value
        else:
            return param

    def evaluate(self, context):
        return self.value.evaluate(context)


def marshal(arguments, triple):
    (s, p, o) = triple
    for argument in arguments:
        s = argument.marshal(s)
        p = argument.marshal(p)
        o = argument.marshal(o)

    return (s, p, o)

def sub_params_in_triples(parameters, triples):

    def sub(parameters, triple):
        (s, p, o) = triple
        for parameter in parameters:
            if parameter.is_substitute(s):
                s = parameter
            if parameter.is_substitute(p):
                p = parameter
            if parameter.is_substitute(o):
                o = parameter

        return (s, p, o)

    subbed = [sub(parameters, triple) for triple in triples]

    return subbed

def check_param_is_name(param):
    if not isinstance(param, Name):
        raise UnexpectedType(Name, param, param.location)
    elif isinstance(param.names[0], Uri):
        raise UnexpectedType(Name, param.names[0], param.location)
    elif isinstance(param.names[0], Self):
        raise UnexpectedType(Name, param.names[0], param.location)
    elif len(param.names) > 1:
        raise UnexpectedType(Name, param, param.location)
    else:
        return True

def with_self(context, _self, fun):
    old_self = context.current_self
    context.current_self = _self
    try:
        fun()
    finally:
        context.current_self = old_self
