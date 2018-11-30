import rdflib
import pdb

from .core import Node, Name, Uri, Self
from .error import (TemplateNotFound,
                    UnexpectedType)
from .pragma import (ExtensionPragma)

class Template(Node):

    def __init__(self, name, parameters, body, base, location):

        super().__init__(location)
        self._name          = name

        self._parameters = []
        for param in parameters:
            self.check_param(param)
            self._parameters.append(Parameter(param.localname,
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

    def parameterise(self):
        if self.base:
            self.base.parameterise(self.parameters)

        for statement in self.body:
            try:
                statement.parameterise(self.parameters)
            except AttributeError:
                pass

        for extension in self._extensions:
            extension.parameterise(self.parameters)

    def bind(self, args):

        for statement in self.body:
            try:
                statement.bind(args)
            except AttributeError:
                pass

        if self.base:
            self.base.bind(args)

    def de_name(self, env):
        self._name = self.name.as_uri(env)
        for statement in self.body:
            try:
                statement.de_name(env)
            except AttributeError:
                pass

        if self.base:
            self.base.de_name(env)

    def check_param(self, param):
        if not isinstance(param, Name):
            raise UnexpectedType(Name, param, self.location)

    def prefixify(self, prefix):

        self._name.prefixify(prefix)
        if self._base:
            self._base.prefixify(prefix)

        for expr in self._body:
            if not isinstance(expr, ExtensionPragma):
                expr.prefixify(prefix)

    def as_uri(self, env):
        return self._name.as_uri(env)

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

        if self._base:
            triples = [self.replace_names(triple) for triple in self._base.as_triples(env)]
        else:
            triples = []

        for expr in self._body:
            if isinstance(expr, Property):
                triples.append((self._name.as_uri(env), expr.name, expr.value))
            elif isinstance(expr, Expansion):
                for triple in expr.as_triples(env):
                    triples.append(triple)
            elif isinstance(expr, ExtensionPragma):
                self._extensions.append(expr)

        return parameterise_triples(triples, self._parameters)

    def replace_names(self, triple):
        (s, p, o) = triple
        return (self.replace_name(s),
                self.replace_name(p),
                self.replace_name(o))

    def replace_name(self, victim):
        if isinstance(victim, Name) and victim == self._base.name:
            return self._name
        else:
            return victim


class Expansion(Node):

    def __init__(self, name, template, args, body, location):

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
        p = self.template.prefix
        l = self.template.localname
        template = env.lookup_template(env.resolve_name(p, l))
        return template.get_extensions(env) + self._extensions

    def parameterise(self, parameters):
        for param in parameters:
            if self.name == param.name:
                self._name = param

            if self.template == param.name:
                self._template = param

            self._args = [Argument(param, arg.position, arg.location) if arg.value == param.name
                          else arg
                          for arg in self.args]

        for statement in self.body:
            try:
                statement.parameterise(parameters)
            except AttributeError:
                pass

        for extension in self._extensions:
            extension.parameterise(parameters)

    def bind(self, args):

        for arg in args:
            if (isinstance(self.name, Parameter) and
                self.name.position == arg.position):
                self._name = arg.value

            if (isinstance(self.template, Parameter) and
                self.template.position == arg.position):
                self._template = arg.value

            self._args = [Argument(arg.value, myarg.position, myarg.location)
                          if isinstance(myarg.value, Parameter) and myarg.value.position == arg.position
                          else myarg
                          for myarg in self.args]

    def de_name(self, env):
        if isinstance(self.name, Name):
            self._name = self.name.as_uri(env)

        if isinstance(self.template, Name):
            self._template = self.template.as_uri(env)

        self._args = [Argument(arg.value.as_uri(env), arg.position, arg.location)
                      if isinstance(arg.value, Name)
                      else arg
                      for arg in self.args]

        for statement in self.body:
            try:
                statement.de_name(env)
            except AttributeError:
                pass

    def as_triples(self, env):
        p = self.template.prefix
        l = self.template.localname
        template = env.lookup_template(env.resolve_name(p, l))
        if not template:
            raise TemplateNotFound(self._template, self._location)
        elif not isinstance(template, Template):
            raise UnexpectedType(Template, template, self._location)

        triples = [self.sub_args(triple) for triple in template.as_triples(env)]

        for expr in self._body:
            if isinstance(expr, Property):
                triples.append((self._name, expr.name, expr.value))
            elif isinstance(expr, Expansion):
                for triple in expr.as_triples(env):
                    triples.append(triple)
            elif isinstance(expr, ExtensionPragma):
                self._extensions.append(expr)

        triples = [self.replace_names(triple, env) for triple in triples]

        return triples

    def replace_names(self, triple, env):
        (s, p, o) = triple
        return (self.replace_name(s, env),
                self.replace_name(p, env),
                self.replace_name(o, env))

    def replace_name(self, victim, env):
        if isinstance(victim, Uri) and victim == self._template.as_uri(env):
            return self._name.as_uri(env)
        elif isinstance(victim, Self):
            return self._name.as_uri(env)
        else:
            return victim

    def sub_args(self, triple):
        (s, p, o) = triple
        for arg in self._args:
            if isinstance(s, Parameter) and s.position == arg.position:
                s = arg.value
            if isinstance(p, Parameter) and p.position == arg.position:
                p = arg.value
            if isinstance(o, Parameter) and o.position == arg.position:
                o = arg.value
        return (s, p, o)

class Parameter(Node):

    def __init__(self, name_string, position, location):

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
        return Name(None, self._param_name, None)

class Argument(Node):

    def __init__(self, value_expr, position, location):

        super().__init__(location)
        self._value    = value_expr
        self._position = position

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
        return (f"<RDFscript PROPERTY: {self.name} = {self.value}>\n")

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def parameterise(self, parameters):
        for param in parameters:
            if self.value == param.name:
                self._value = param

            if self.name == param.name:
                self._name = param

        try:
            self.value.parameterise(parameters)
        except AttributeError:
            pass

    def bind(self, args):
        for arg in args:
            if (isinstance(self.name, Parameter) and
                self.name.position == arg.position):
                self._name = arg.value

            if (isinstance(self.value, Parameter) and
                self.value.position == arg.position):
                self._value= arg.value

        try:
            self.name.bind(args)
        except AttributeError:
            pass

        try:
            self.value.bind(args)
        except AttributeError:
            pass

    def de_name(self, env):
        if isinstance(self.name, Name):
            self._name = self.name.as_uri(env)

        if isinstance(self.value, Name):
            self._value = self.value.as_uri(env)

        try:
            self.value.de_name(env)
        except AttributeError:
            pass

    def prefixify(self, prefix):
        if isinstance(self._name, Name):
            self._name.prefixify(prefix)

        if isinstance(self._value, Name) or isinstance(self._value, Expansion):
            self._value.prefixify(prefix)

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
