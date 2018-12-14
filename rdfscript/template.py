import rdflib
import pdb

from .core import (Node,
                   Name,
                   Uri,
                   Self)
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)

from .expansion import Expansion

class Template(Node):

    def __init__(self, name, parameters, body, base, location=None):

        Node.__init__(self, location)
        self._name = name

        self._parameters = []
        for param in parameters:
            self.check_param(param)
            self._parameters.append(Parameter(param.names[0],
                                              parameters.index(param),
                                              location))

        self._base          = base
        self._extensions    = []
        self._body          = []
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
        return (f"<RDFscript TEMPLATE: {self.name}\n"
                f" Specialised from:\n  {self.base}\n"
                f" With parameters:\n  {self.parameters}\n"
                f" And body:\n  {self.body}\n")

    def as_triples(self, env):
        triples = []
        for statement in self.body:
            old_self = env.self_uri
            env.self_uri = Self()
            triples += statement.as_triples(env)

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
        return format("<RDFscript PARAM: %s>" % self.name)

    def as_name(self):
        return Name(self._param_name)

class Property(Node):

    def __init__(self, name, value, location=None):

        Node.__init__(location)
        self._name          = name
        self._value         = value

    def __eq__(self, other):
        return (isinstance(other, Property) and
                self.name == other.name and
                self.value == other.value)

    def __repr__(self):
        return (f"<RDFscript PROPERTY: {self.name} = {self.value}>\n")

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def as_triples(self, context):

        return [(Self(), self.name, self.value)]
