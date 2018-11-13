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
                self._param_name == other._param_name)

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

    def parameterise(self, parameters):
        for param in parameters:
            if self.name == param.as_name():
                self._name = param.as_rdfbnode()
            if self.value == param.as_name():
                self._value = param.as_rdfbnode()

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

class InstanceExp(Node):
    pass

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

    def parameterise(self):
        for body_statement in self.body:
            body_statement.parameterise(self._parameters)

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
