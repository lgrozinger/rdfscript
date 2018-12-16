import rdfscript.template as template
from .core import (Node,
                   Name,
                   Uri,
                   Self)
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)


class Expansion(Node):

    def __init__(self, name, template, args, body, location=None):

        super().__init__(location)
        self._template      = template
        self._name          = name
        self._args          = []
        for arg in args:
            if isinstance(arg, Argument):
                self._args.append(Argument(arg.value, args.index(arg), location))
            else:
                self._args.append(Argument(arg, args.index(arg), location))

        self._extensions    = []
        self._body          = []
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
        return (f"<RDFscript EXPANSION: {self.name}\n"
                f" Based on:\n  {self.template}\n"
                f" With Args:\n  {self.args}\n"
                f" And body:\n  {self.body}\n")

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
        template = env.lookup_template(self.template)
        return template.get_extensions(env) + self._extensions

    def as_triples(self, env):

        try:
            triples = env.lookup_template(self.template.evaluate(env))
            triples = [template.marshal(self.args, triple) for triple in triples]
        except KeyError:
            raise TemplateNotFound(self.template, self.template.location)

        old_self = env.current_self
        env.current_self = self.name.evaluate(env)

        for statement in self.body:
            triples += statement.as_triples(env)

        triples = [(s.evaluate(env), p.evaluate(env), o.evaluate(env))
                    for (s, p, o) in triples]

        env.current_self = old_self

        return triples

class Argument(Node):

    def __init__(self, value_expr, position, location=None):

        super().__init__(location)
        self._value    = value_expr
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

    def __repr__(self):
        return format("[RDFscript ARG: %s]" % self._value)

    def marshal(self, param):
        if (isinstance(param, template.Parameter) and
            param.position == self.position):
            return self.value
        else:
            return param
