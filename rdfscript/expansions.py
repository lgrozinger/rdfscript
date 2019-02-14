import rdfscript.core as core
import rdfscript.utils as utils


class Expansion(core.Node):

    def __init__(self, name, template, arguments, body, location=None):
        core.Node.__init__(self, location)

        self._name = name
        self._args = list(zip(arguments, range(1, len(arguments) + 1)))

        for statement in body:
            utils.type_assert(statement, core.Three)
        self._body = body
        self._template = template

    def __str__(self):
        return format("%s = %s(%s)(%s)" % (self.name,
                                           self.template,
                                           self.args,
                                           self.body))

    def __repr__(self):
        return format("Expansion(%s, %s, %s)" % (self.name,
                                                 self.args,
                                                 self.body,
                                                 self.template))

    def __eq__(self, other):
        return isinstance(other, Expansion) \
            and self.name == other.name \
            and self.args == other.args \
            and self.body == other.body \
            and self.template == other.template

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    @property
    def body(self):
        return self._body

    @property
    def arity(self):
        return len(self.parameters)

    @property
    def template(self):
        return self._template

    def is_parameter(self, possible_param):
        parameter = False
        match = [i for (name, i) in self.parameters if name == possible_param]
        if match:
            parameter = match[0]

        return parameter
