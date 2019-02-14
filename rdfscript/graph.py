import rdflib

import rdfscript.context as context
import rdfscript.error as error
import rdfscript.utils as utils
import rdfscript.core as core
import rdfscript.evaluate as evaluate


class EnvironmentGraph:

    def __init__(self):
        blank = rdflib.URIRef('')
        self._graph = rdflib.ConjunctiveGraph(identifier=blank)
        self._graph.bind('RDFScript', rdflib.URIRef(core.__lang__))

    @property
    def graph(self):
        return self._graph

    @property
    def root(self):
        return utils.from_rdf(self.graph.identifier)

    @property
    def root_context(self):
        return self.get_context(self.root)

    def get_context(self, rooted_at):
        rdflib_root = utils.to_rdf(rooted_at)
        rdflib_graph = self.graph.get_context(rdflib_root)
        return context.Context(rdflib_graph)

    def bind_prefix(self, prefix, uri):
        p = prefix.names[0]
        u = utils.to_rdf(uri)
        self.graph.bind(p, u)
        self.root_context.put(uri, core.Uri(p))
        return prefix

    def prefix_to_uri(self, prefix):
        namespaces = self.graph.namespaces()
        matching = [n for (p, n) in namespaces if p == prefix.names[0]]
        if len(matching) == 1:
            matching = utils.from_rdf(matching[0])
        elif len(matching) == 0:
            raise error.PrefixError(prefix, prefix.location)

        return matching

    def uri_to_prefix(self, uri):
        u = utils.to_rdf(uri)
        namespaces = self.graph.namespaces()
        matching = [p for (p, n) in namespaces if n == u]

        if len(matching) == 1:
            matching = matching[0]
        elif len(matching) == 0:
            raise error.PrefixError(uri, uri.location)

        return core.Name(matching)


def set_template_type(template, rt):
    type_uri = core.lang_uri(template)
    type_predicate = utils.from_rdf(rdflib.RDF.type)
    names = template.name.names + [type_predicate]
    rt.bind(type_uri, core.Name(*names))


def object_context(obj, rt):
    context = rt.context(obj.name)

    if context is None:
        set_template_type(obj, rt)
        context = rt.context(obj.name)

    return context


def hang_params(template, rt):
    for (parameter, index) in template.parameters:
        predicate = core.params_uri(index)
        param_uri = utils.name_to_uri(parameter)
        context = object_context(template, rt)

        context.put(utils.contextualise_uri(param_uri, context), predicate)


def get_param(template, index, rt):
    context = object_context(template, rt)
    return context.get(core.params_uri(index))


def hang_body(template, rt):
    for statement in template.body:
        hang_three(template, statement, rt)


def hang_three(template, three, rt):

    def sub_params(possible_param):
        result = possible_param
        i = template.is_parameter(possible_param)
        if i:
            result = get_param(template, i, rt)

        return result

    three.map(sub_params)
    step_one = core.Three(template.name, core.triple_uri(1), three.one)
    step_two = core.Three(three.one, core.triple_uri(2), three.two)
    step_three = core.Three(three.two, core.triple_uri(3), three.three)

    for step in [step_one, step_two, step_three]:
        evaluate.evaluate(step, rt)
