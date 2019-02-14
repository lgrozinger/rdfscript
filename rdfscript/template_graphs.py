import rdflib

import rdfscript.evaluate as evaluate
import rdfscript.core as core
import rdfscript.utils as utils


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
