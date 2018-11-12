import rdflib

class Node:

    def __init__(self, location):

        self._location = location

    @property
    def location(self):
        return self._location

    @property
    def line(self):
        return self._location.position.line

    @property
    def col(self):
        return self._location.position.col

    @property
    def position(self):
        return self._location.position

    @property
    def file(self):
        return self._location.filename

class Name(Node):
    """Env's abstraction of a identifier node in the RDF graph."""

    def __init__(self, prefix, localname, location):

        super().__init__(location)
        self._prefix = prefix
        self._localname = localname

    def __eq__(self, other):
        return (isinstance(other, Name) and
                self.prefix == other.prefix and
                self.localname == other.localname)

    def __repr__(self):
        return format("<RDFscript NAME: <%s%s> >" % (self.prefix, self.localname))

    @property
    def prefix(self):
        return self._prefix

    @property
    def localname(self):
        return self._localname

    def as_uriref(self, graph):

        all_namespaces      = graph.namespaces()
        matching_namespaces = [ns for (prefix, ns)
                               in all_namespaces
                               if prefix == self._prefix]

        if not len(matching_namespaces) == 1:
            raise NameError(self._prefix)
        else:
            return rdflib.URIRef(matching_namespaces[0])

class Uri(Node):
    """Env's abstraction of a URI"""

    def __init__(self, uri, location):

        super().__init__(location)
        self._uri = uri

    def __eq__(self, other):
        return (isinstance(other, Uri) and
                self.uri == other.uri)

    def __repr__(self):
        return format("<RDFscript URI: %s>" % self._python_val)

    def as_uriref(self):
        return rdflib.URIRef(self._uri)

class Value(Node):
    """Env's abstraction of a literal node in the RDF graph."""

    def __init__(self, python_literal, location):

        super().__init__(location)
        self._python_val = python_literal

    def __eq__(self, other):
        return (isinstance(other, Value) and
                self.as_pythonval == other.as_pythonval)

    def __repr__(self):
        return format("<RDFscript VALUE: %s>" % self.as_pythonval())

    def as_pythonval(self):

        return self._python_val

    def as_rdfliteral(self):

        return rdflib.Literal(self._python_val)

class Parameter:
    """Env's abstraction of a RDF BNode for a template parameter."""

    def __init__(self, parameter_name):

        self._param_name = parameter_name
        self._binding    = rdflib.BNode()

    @property
    def name(self):
        return self._param_name

    @property
    def binding(self):
        return self._binding

    def __eq__(self, other):
        return (isinstance(other, Parameter) and
                self.name == other.name)

    def __repr__(self):
        return format("<RDFscript PARAMETER: %s>" % self.name)

    def as_rdfbnode(self):
        return self._binding

    def isBound(self):
        return not isinstance(self._binding, rdflib.BNode)

    def bind(self, binding):
        self._binding = binding

class Template:
    """Env's abstraction of a RDF subgraph for a template."""

    def __init__(self, name, parameters, body, base_template=None):

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
        return (isinstance(other, Template) and
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
