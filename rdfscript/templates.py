import rdfscript.utils as utils
import rdfscript.core as core


class Template(core.Node):

    def __init__(self, name, parameters, body, location=None):
        core.Node.__init__(self, location)

        for should_be_name in [name] + parameters:
            utils.type_assert(should_be_name, core.Name)
        self._name = name
        self._parameters = list(zip(parameters, range(1, len(parameters) + 1)))

        for statement in body:
            # TODO: add inheritance here (anon-Expansion)
            # TODO: add properties here
            utils.type_assert(statement, core.Three)
        self._body = body

    def __str__(self):
        return format("%s(%s)(%s)" % (self.name,
                                      self.parameters,
                                      self.body))

    def __repr__(self):
        return format("Template(%s, %s, %s)" % (self.name,
                                                self.parameters,
                                                self.body))

    def __eq__(self, other):
        return isinstance(other, Template) \
            and self.name == other.name \
            and self.parameters == other.parameters \
            and self.body == other.body

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
    def arity(self):
        return len(self.parameters)

    def is_parameter(self, possible_param):
        parameter = False
        match = [i for (name, i) in self.parameters if name == possible_param]
        if match:
            parameter = match[0]

        return parameter


class Property(core.Node):

    def __init__(self, name, value, location=None):
        core.Node.__init__(self, location)
        self._name = name
        self._value = value

    def __eq__(self, other):
        return (isinstance(other, Property) and
                self.name == other.name and
                self.value == other.value)

    def __str__(self):
        return format("%s = %s\n" % (self.name, self.value))

    def __repr__(self):
        return format("Property(%s, %s)" % (self.name, self.value))

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


def as_triples(template, rt):
    return []
