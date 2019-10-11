import rdflib
import pdb

from .logic import And
from .error import ExtensionError
from rdfscript.core import Uri, Value

_sbolns = Uri('http://sbols.org/v2#', None)
_toplevels = set([Uri(_sbolns.uri + tl, None) for tl
                  in ['Sequence',
                      'ComponentDefinition',
                      'ModuleDefinition',
                      'Model',
                      'Collection',
                      'GenericTopLevel',
                      'Attachment',
                      'Activity',
                      'Agent',
                      'Plan',
                      'Implementation',
                      'CombinatorialDerivation']])

_sbol_pId = Uri(_sbolns.uri + 'persistentIdentity', None)
_sbol_dId = Uri(_sbolns.uri + 'displayId', None)
_sbol_version = Uri(_sbolns.uri + 'version', None)
_rdf_type = Uri(rdflib.RDF.type, None)


class SbolIdentity:

    def __init__(self):
        pass

    def run(self, triplepack):
        return And(*[SBOLCompliant(s) for s in triplepack.subjects]).run(triplepack)


class SBOLCompliant:

    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):

        subpack = triplepack.sub_pack(self._subject)
        if SBOLcheckTopLevel(subpack):
            SBOLCompliantTopLevel(self._subject).run(triplepack)
        else:
            SBOLCompliantChild(self._subject).run(triplepack)

        return triplepack


class SBOLCompliantTopLevel:

    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):

        subpack = triplepack.sub_pack(self._subject)

        if SBOLdId(subpack) is None:
            dId = self._subject.split()[-1]
            triplepack.set(self._subject, _sbol_dId, Value(dId))

        if SBOLversion(subpack) is not None:
            version_string = str(SBOLversion(subpack).value)
            pId = Uri(self._subject.uri + '/' + version_string)
            triplepack.set(self._subject, _sbol_pId, pId)
        else:
            pId = Uri(self._subject.uri, None)
            triplepack.set(self._subject, _sbol_pId, pId)


class SBOLCompliantChild:

    def __init__(self, for_subject):
        self._subject = for_subject

    def run(self, triplepack):
        print("Calling")
        subpack = triplepack.sub_pack(self._subject)
        parent = SBOLParent(triplepack, self._subject)
        if parent:
            if not triplepack.has(parent, _sbol_pId):
                SBOLCompliant(parent).run(triplepack)

            if triplepack.has(parent, _sbol_version):
                triplepack.set(self._subject,
                               _sbol_version,
                               triplepack.value(parent, _sbol_version))

            if not SBOLdId(subpack):
                dId = self._subject.split()[-1]
                triplepack.set(self._subject, _sbol_dId, Value(dId))
                subpack.set(self._subject, _sbol_dId, Value(dId))

            parentpid = triplepack.value(parent, _sbol_pId)
            pId = Uri(parentpid.uri + '/' + SBOLdId(subpack).value)
            triplepack.set(self._subject, _sbol_pId, pId)
        else:
            pass


class SBOLComplianceError(ExtensionError):

    def __init__(self, helpful_message):
        self._type = 'SBOL2 Compliant URI error'
        self._helpful_message = helpful_message

    def __str__(self):
        return ExtensionError.__str__(self) + format(" %s\n" % self._helpful_message)


def SBOLversion(triplepack):
    return triplepack.value(_sbol_version)


def SBOLpId(triplepack):
    return triplepack.value(_sbol_pId)


def SBOLdId(triplepack):
    return triplepack.value(_sbol_dId)


def SBOLcheckIdentity(triplepack):
    identity = triplepack.subjects.pop()
    if SBOLversion(triplepack):
        return identity.split()[-1] == triplepack.value(_sbol_version).value
    else:
        return True


def SBOLParent(triplepack, child):
    with_child_as_object = triplepack.search((None, None, child))
    possible_parents = set([s for (s, p, o) in with_child_as_object])
    if len(possible_parents) > 1:
        message = format("The SBOL object %s should only have one parent object."
                         % child)
        return possible_parents.pop()
        raise SBOLComplianceError(message)
    elif len(possible_parents) == 1:
        return possible_parents.pop()
    else:
        message = format("The SBOL object %s does not have a parent object."
                         % child)
        raise SBOLComplianceError(message)


def SBOLcheckTopLevel(triplepack):
    _type = triplepack.value(_rdf_type)
    if isinstance(_type, list):
        return any([t in _toplevels for t in _type])
    else:
        return _type in _toplevels
