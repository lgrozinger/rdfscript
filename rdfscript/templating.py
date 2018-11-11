from .core import Node

class Parameter(Node):
    """Env's abstraction of a RDF BNode for a template parameter."""

    def __init__(self, parameter_name, location):

        super().__init__(location)
        self._param_name = parameter_name
        self._binding    = rdflib.BNode()

    @property
    def name(self):
        return self._param_name

    @property
    def binding(self):
        return self._binding

    def __eq__(self, other):
        return (isParameter(other) and
                self._param_name == other._param_name)

    def __repr__(self):
        return format("<RDFscript VALUE: %s>" % self._python_val)

    def as_rdfbnode(self):
        return self._binding

    def isBound(self):
        return not isinstance(self._binding, rdflib.BNode)

    def bind(self, binding):
        self._binding = binding

class Template(Node):
    """Env's abstraction of a RDF subgraph for a template."""

    def __init__(self, name, parameters, body, location, base_template=None):

        super().__init__(location)
        self._name          = name

        self._base_parameters = []
        self._parameters      = []

        for parameter in parameters:
            if (base_template
                and parameter in base_template.parameters):
                self._base_parameters.append(parameter)
            else:
                self._parameters.append(parameter)

        self._base_template = base_template
        self._body          = body

    @property
    def name(self):
        return self._name

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
        return (isTemplate(other) and
                self._name == other.name and
                self._parameters == other.parameters and
                self._base_template == other.base_template and
                self._body == other.body)

    def __repr__(self):
        return format("<RDFscript TEMPLATE: %s>" % self._name)

    def pass_arguments(self, name_arg_pairs):

        for name, argument in name_arg_pairs:

            try:
                parameter = Parameter(name)

                if parameter in self.parameters:
                    self._parameters[self._parameters.index(parameter)].bind(argument)
                else:
                    self._base_parameters[self._base_parameters.index(parameter)].bind(argument)

            except ValueError:
                ## call out to logger, handler, try to recover, etc.
                raise

        for parameter in self._parameters + self._base_parameters:
            if not parameter.isBound():
                ## required argument not given
                raise

    def as_instance(self, instance_name, arguments):

        template_namespace = rdflib.Namespace(template_uri)

        self.pass_arguments(arguments)

        triples = self.base_template.as_instance(instance_name,
                                                 self._base_parameters)
