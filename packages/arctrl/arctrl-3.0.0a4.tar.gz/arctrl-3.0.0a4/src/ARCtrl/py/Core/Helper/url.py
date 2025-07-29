from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.util import to_enumerable
from .collections_ import (Dictionary_ofSeq, Dictionary_tryFind)

def OntobeeParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.obolibrary.org/obo/") + "") + tsr) + "_") + local_tan) + ""


def BioregistryParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://bioregistry.io/") + "") + tsr) + ":") + local_tan) + ""


def OntobeeDPBOParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.org/nfdi4plants/ontology/dpbo/") + "") + tsr) + "_") + local_tan) + ""


def MSParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ms/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def POParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/po/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def ROParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ro/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def _arrow474(tsr: str) -> Callable[[str], str]:
    def _arrow473(local_tan: str) -> str:
        return OntobeeDPBOParser(tsr, local_tan)

    return _arrow473


def _arrow476(tsr_1: str) -> Callable[[str], str]:
    def _arrow475(local_tan_1: str) -> str:
        return MSParser(tsr_1, local_tan_1)

    return _arrow475


def _arrow478(tsr_2: str) -> Callable[[str], str]:
    def _arrow477(local_tan_2: str) -> str:
        return POParser(tsr_2, local_tan_2)

    return _arrow477


def _arrow480(tsr_3: str) -> Callable[[str], str]:
    def _arrow479(local_tan_3: str) -> str:
        return ROParser(tsr_3, local_tan_3)

    return _arrow479


def _arrow482(tsr_4: str) -> Callable[[str], str]:
    def _arrow481(local_tan_4: str) -> str:
        return BioregistryParser(tsr_4, local_tan_4)

    return _arrow481


def _arrow484(tsr_5: str) -> Callable[[str], str]:
    def _arrow483(local_tan_5: str) -> str:
        return BioregistryParser(tsr_5, local_tan_5)

    return _arrow483


def _arrow486(tsr_6: str) -> Callable[[str], str]:
    def _arrow485(local_tan_6: str) -> str:
        return BioregistryParser(tsr_6, local_tan_6)

    return _arrow485


def _arrow488(tsr_7: str) -> Callable[[str], str]:
    def _arrow487(local_tan_7: str) -> str:
        return BioregistryParser(tsr_7, local_tan_7)

    return _arrow487


def _arrow490(tsr_8: str) -> Callable[[str], str]:
    def _arrow489(local_tan_8: str) -> str:
        return BioregistryParser(tsr_8, local_tan_8)

    return _arrow489


def _arrow492(tsr_9: str) -> Callable[[str], str]:
    def _arrow491(local_tan_9: str) -> str:
        return BioregistryParser(tsr_9, local_tan_9)

    return _arrow491


def _arrow494(tsr_10: str) -> Callable[[str], str]:
    def _arrow493(local_tan_10: str) -> str:
        return BioregistryParser(tsr_10, local_tan_10)

    return _arrow493


def _arrow496(tsr_11: str) -> Callable[[str], str]:
    def _arrow495(local_tan_11: str) -> str:
        return BioregistryParser(tsr_11, local_tan_11)

    return _arrow495


def _arrow498(tsr_12: str) -> Callable[[str], str]:
    def _arrow497(local_tan_12: str) -> str:
        return BioregistryParser(tsr_12, local_tan_12)

    return _arrow497


def _arrow500(tsr_13: str) -> Callable[[str], str]:
    def _arrow499(local_tan_13: str) -> str:
        return BioregistryParser(tsr_13, local_tan_13)

    return _arrow499


def _arrow502(tsr_14: str) -> Callable[[str], str]:
    def _arrow501(local_tan_14: str) -> str:
        return BioregistryParser(tsr_14, local_tan_14)

    return _arrow501


uri_parser_collection: Any = Dictionary_ofSeq(to_enumerable([("DPBO", _arrow474), ("MS", _arrow476), ("PO", _arrow478), ("RO", _arrow480), ("ENVO", _arrow482), ("CHEBI", _arrow484), ("GO", _arrow486), ("OBI", _arrow488), ("PATO", _arrow490), ("PECO", _arrow492), ("TO", _arrow494), ("UO", _arrow496), ("EFO", _arrow498), ("NCIT", _arrow500), ("OMP", _arrow502)]))

def create_oauri(tsr: str, local_tan: str) -> str:
    match_value: Callable[[str, str], str] | None = Dictionary_tryFind(tsr, uri_parser_collection)
    if match_value is None:
        return OntobeeParser(tsr, local_tan)

    else: 
        return match_value(tsr)(local_tan)



__all__ = ["OntobeeParser", "BioregistryParser", "OntobeeDPBOParser", "MSParser", "POParser", "ROParser", "uri_parser_collection", "create_oauri"]

