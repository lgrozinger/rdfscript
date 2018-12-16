import rdflib
import pdb

from .core import (Node,
                   Name,
                   Uri,
                   Self)
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)

from .expansion import Expansion, Argument

class Template(Node):

    def __init__(self, name, parameters, body, base, args, location=None):

        Node.__init__(self, location)
        self._name = name

        self._parameters = []
        for param in parameters:
            self.check_param(param)
            self._parameters.append(Parameter(param.names[0],
                                              parameters.index(param),
                                              location))

        self._base = base
        self._args = [Argument(arg, args.index(arg), location=arg.location)
                      for arg in args]
        self._extensions = []
        self._body = []
        for statement in body:
            if isinstance(statement, ExtensionPragma):
                self._extensions.append(statement)
            else:
                self._body.append(statement)

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @property
    def base(self):
        return self._base

    @property
    def args(self):
        return self._args

    @property
    def body(self):
        return self._body

    def get_extensions(self, env):
        if self._base:
            return self._extensions + self._base.get_extensions(env)
        else:
            return self._extensions

    def check_param(self, param):
        if not isinstance(param, Name):
            raise UnexpectedType(Name, param, self.location)
        elif isinstance(param.names[0], Uri):
            raise UnexpectedType(Name, param.names[0], self.location)
        elif isinstance(param.names[0], Self):
            raise UnexpectedType(Name, param.names[0], self.location)
        elif len(param.names) > 1:
            raise UnexpectedType(Name, param, self.location)
        else:
            return True

    def __eq__(self, other):
        return (isinstance(other, Template) and
                self._name == other.name and
                self._parameters == other.parameters and
                self._base == other.base and
                self._body == other.body)

    def __repr__(self):
        return (f"[TEMPLATE: {self.name}({self.parameters}) from {self.base}\n"
                f"({self.body})\n")

    def forward_parameters(self):
        for arg in self.args:
            for parameter in self.parameters:
                if parameter.is_substitute(arg.value):
                    arg.value = parameter

    def as_triples(self, env):
        triples = []

        if self.base is not None:
            triples += env.lookup_template(self.base.evaluate(env))
            self.forward_parameters()
            triples = [marshal(self.args, triple) for triple in triples]

        for statement in self.body:
            statement.substitute_params(self.parameters)
            old_self = env.current_self
            env.current_self = Self()
            triples += statement.as_triples(env)
            env.current_self = old_self
        return triples

class Parameter(Node):

    def __init__(self, name_string, position, location=None):

        super().__init__(location)
        self._param_name = name_string
        self._position   = position

    @property
    def name(self):
        return self.as_name()

    @property
    def position(self):
        return self._position

    def __eq__(self, other):
        return (isinstance(other, Parameter) and
                self.name == other.name)

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

    def __repr__(self):
        return (f"[RDFscript PROPERTY: {self.name} = {self.value}]\n")

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

        return [(Self(), self.name.evaluate(context), self.value.evaluate(context))]

def marshal(arguments, triple):
    (s, p, o) = triple
    for argument in arguments:
        s = argument.marshal(s)
        p = argument.marshal(p)
        o = argument.marshal(o)

    return (s, p, o)
