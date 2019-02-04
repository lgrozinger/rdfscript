import rdflib

import rdfscript.utils as utils
import rdfscript.core as core


class Template(core.Node):

    def __init__(self, name, parameters, body, location=None):
        core.Node.__init__(self, location)

        for should_be_name in [name] + parameters:
            utils.type_assert(should_be_name, core.Name)
        self._name = name
        self._parameters = parameters
        self._body = body

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return self._parameters

    @property
    def arity(self):
        return len(self.parameters)


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
