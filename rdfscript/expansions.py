import rdfscript.core as core
import rdfscript.utils as utils


class Expansion(core.Node):

    def __init__(self, template, arguments, body, location=None):
        core.Node.__init__(self, location)

        self._args = list(zip(arguments, range(1, len(arguments) + 1)))

        for statement in body:
            utils.type_assert(statement, core.Three)
        self._body = body
        self._template = template

    def __str__(self):
        return format("%s = %s(%s)(%s)" % (self.template,
                                           self.args,
                                           self.body))

    def __repr__(self):
        return format("Expansion(%s, %s, %s)" % (self.template,
                                                 self.args,
                                                 self.body))

    def __eq__(self, other):
        return isinstance(other, Expansion) \
            and self.args == other.args \
            and self.body == other.body \
            and self.template == other.template

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
