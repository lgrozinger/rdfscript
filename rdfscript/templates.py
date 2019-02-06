import rdflib

import rdfscript.evaluate as evaluate
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
            parameter = match[0],

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


def set_template_type(template, rt):
    type_uri = core.lang_uri(template)
    type_predicate = utils.from_rdf(rdflib.RDF.type)
    names = template.name.names + [type_predicate]
    rt.bind(type_uri, core.Name(*names))


def template_context(template, rt):
    context = rt.context(template.name)

    if context is None:
        set_template_type(template, rt)
        context = rt.context(template.name)

    return context


def hang_params(template, rt):
    for (parameter, index) in template.parameters:
        predicate = core.params_uri(index)
        param_uri = utils.name_to_uri(parameter)
        context = template_context(template, rt)

        context.put(utils.contextualise_uri(param_uri, context), predicate)


def get_param(template, index, rt):
    context = template_context(template, rt)
    return context.get(core.params_uri(index))


def hang_body(template, rt):
    for statement in template.body:
        hang_three(template, statement, rt)


def hang_three(template, three, rt):
    for possible_param in [three.one, three.two, three.three]:
        i = template.is_parameter(possible_param)
        if i:
            possible_param = get_param(template, i, rt)

    step_one = core.Three(template.name, core.triple_uri(1), three.one)
    step_two = core.Three(three.one, core.triple_uri(2), three.two)
    step_three = core.Three(three.two, core.triple_uri(3), three.three)

    for step in [step_one, step_two, step_three]:
        evaluate.evaluate(step, rt)
