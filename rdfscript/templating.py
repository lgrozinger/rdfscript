import rdflib

from .core import Node, Name

class Parameter(Node):
    """Env's abstraction of a RDF BNode for a template parameter."""

    def __init__(self, parameter_name, position, location):

        super().__init__(location)
        self._param_name = parameter_name
        self._binding    = rdflib.BNode()
        self._position   = position

    @property
    def name(self):
        return self._param_name

    @property
    def binding(self):
        return self._binding

    @property
    def position(self):
        return self._position

    def __eq__(self, other):
        return (isinstance(other, Parameter) and
                self._param_name == other.name and
                self.position == other.position)

    def __repr__(self):
        return format("<RDFscript PARAM: %s>" % self._python_val)

    def as_rdfbnode(self):
        return self._binding

    def as_name(self):
        return Name(None, self.name, None)

    def isBound(self):
        return not isinstance(self._binding, rdflib.BNode)

    def bind(self, binding):
        self._binding = binding

class Argument(Node):

    def __init__(self, value_expr, position, location):

        super().__init__(location)
        self._value = value_expr
        self._position   = position

    @property
    def value(self):
        return self._value

    @property
    def position(self):
        return self._position

    def __eq__(self, other):
        return (isinstance(other, Argument) and
                self.value == other.value and
                self.position == other.position)

    def __repr__(self):
        return format("<RDFscript ARG: %s>" % self._value)

class Property(Node):

    def __init__(self, name, value, location):

        super().__init__(location)
        self._name          = name
        self._value         = value

    def __eq__(self, other):
        return (isinstance(other, Property) and
                self.name == other.name and
                self.value == other.value)

    def __repr__(self):
        return format("<RDFscript PROPERTY: %s>" % self.name)

    # def parameterise(self, parameters):
    #     for param in parameters:
    #         if self.name == param.as_name():
    #             self._name = param
    #         if self.value == param.as_name():
    #             self._value = param

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

class Expansion(Node):

    def __init__(self, template, name, args, body, location):

        super().__init__(location)
        self._template      = template
        self._name          = name
        self._args          = args
        self._body          = body

    def __eq__(self, other):
        return (isinstance(other, Expansion) and
                self.template_name == other.template_name and
                self.name == other.name and
                self.args == other.args and
                self.body == other.body)

    def __repr__(self):
        return format("<RDFscript EXPANSION: %s : %s>" % self.name, self.template_name)

    @property
    def name(self):
        return self._name

    @property
    def template(self):
        return self._template_name

    @property
    def args(self):
        return self._args

    @property
    def body(self):
        return self._body

    def as_triples(self, env):
        p = self._template_name.prefix
        l = self._template_name.localname
        template = env.lookup(env.resolve_name(p, l))

        triples = [sub_args(triple) for triple in template.as_triples()]

        triples = [sub_name(triple) for triple in triples]

        for expr in self._body:
            if isinstance(expr, Property):
                triples.append(self._name, expr.name, expr.value)
            elif isinstance(expr, Expansion):
                for triple in expr.as_triples(env):
                    triples.append(triple)

        return triples

    def sub_name(self, triple):
        (s, p, o) = triple
        if isinstance(s, Name) and s == self._template_name:
            s = self._name
        if isinstance(p, Name) and p == self._template_name:
            p = self._name
        if isinstance(o, Name) and o == self._template_name:
            o = self._name

        return (s, p, o)

    def sub_args(self, triple):
        (s, p, o) = triple
        for arg in self._args:
            if isinstance(s, Parameter) and s.position == arg.position:
                s = arg
            if isinstance(p, Parameter) and p.position == arg.position:
                p = arg
            if isinstance(o, Parameter) and o.position == arg.position:
                o = arg
        return (s, p, o)

class Template(Node):
    """Env's abstraction of a RDF subgraph for a template."""

    def __init__(self, name, parameters, body, location, base_template=None):

        super().__init__(location)
        self._name          = name

        #self._base_parameters = []
        self._parameters    = parameters

        # for parameter in parameters:
        #     if (base_template and
        #         parameter in base_template.parameters):
        #         self._base_parameters.append(parameter)
        #     else:
        #         self._parameters.append(parameter)

        self._base_template = base_template
        self._body          = body

    # def parameterise(self):
    #     for body_statement in self.body:
    #         body_statement.parameterise(self._parameters)

    @property
    def name(self):
        return self._name

    @property
    def base_parameters(self):
        return self._base_parameters

    @property
    def parameters(self):
        return self._parameters

    @property
    def base(self):
        return self._base_template

    @property
    def body(self):
        return self._body

    def __eq__(self, other):
        return (isinstance(other, Template) and
                self._name == other.name and
                self._parameters == other.parameters and
                self._base_template == other.base and
                self._body == other.body)

    def __repr__(self):
        return format("<RDFscript TEMPLATE: %s, from %s>" % (self._name, self._base_template))

    def as_triples(self, env):

        if self._base_template:
            p = self._base_template.prefix
            l = self._base_template.localname
            base = env.lookup(env.resolve_name(p, l))

            triples = base.as_triples(env)
        else:
            triples = []

        for expr in self._body:
            if isinstance(expr, Property):
                triples.append(self._name, expr.name, expr.value)
            elif isinstance(expr, Expansion):
                for triple in expr.as_triples(env):
                    triples.append(triple)

        return paramterise_triples(triples)

class Assignment(Node):

    def __init__(self, name, value, location):

        super().__init__(location)
        self._name  = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Assignment) and
                self.name == other.name and
                self.value == other.value)

    def __repr__(self):
        return format("ASSIGN: (%s to %s)" %
                      (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


def parameterise_triples(triples, parameters):
    parameterised = []
    for (s, p, o) in triples:
        for param in parameters:
            if s == param.as_name():
                s = param
            if p == param.as_name():
                p = param
            if o == param.as_name():
                o = param

        parameterised.append((s, p, o))

    return parameterised
