import rdflib

import rdfscript.core as core
import rdfscript.error as error


def to_rdf(language_object):
    if isinstance(language_object, core.Uri):
        return rdflib.URIRef(language_object.uri)
    elif isinstance(language_object, core.Value):
        return rdflib.Literal(language_object.value)
    else:
        raise TypeError


def from_rdf(rdf_object):
    if isinstance(rdf_object, rdflib.URIRef):
        return core.Uri(rdf_object.toPython())
    elif isinstance(rdf_object, rdflib.Literal):
        return core.Value(rdf_object.toPython())
    elif isinstance(rdf_object, rdflib.Namespace):
        return from_rdf(rdflib.URIRef(rdf_object))
    elif isinstance(rdf_object, rdflib.BNode):
        return from_rdf(rdflib.URIRef(rdf_object))
    else:
        raise TypeError


def triple_map(function, triple):
    return tuple([function(t) for t in triple])


def from_rdf_triple(triple):
    return triple_map(from_rdf, triple)


def from_rdf_triples(triples):
    return [from_rdf_triple(t) for t in list(triples)]


def to_rdf_triple(triple):
    return triple_map(to_rdf, triple)


def to_rdf_triples(triples):
    return [to_rdf_triple(t) for t in list(triples)]


def name_to_uri(name):
    result = core.Uri('')
    for step in name.names:
        try:
            result.extend(step, delimiter='')
        except AttributeError:
            result.extend(core.Uri(step), delimiter='')

    return result


def contextualise_uri(uri, context):
    context_uri = context.root
    return core.Uri(context_uri.uri + uri.uri)


def type_assert(this_is, *of_type):
    if isinstance(this_is, of_type):
        return True
    else:
        try:
            raise error.UnexpectedType(of_type, this_is, this_is.location)
        except AttributeError:
            raise error.UnexpectedType(of_type, this_is, None)
