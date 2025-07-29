from __future__ import annotations
from typing import Any
from .Core.arc_types import ArcInvestigation
from .Json.ROCrate.ldgraph import (encoder, decoder)
from .Json.ROCrate.ldnode import decoder as decoder_1
from .ROCrate.Generic.dataset import LDDataset
from .ROCrate.ldcontext import LDContext
from .ROCrate.ldobject import (LDNode, LDRef, LDGraph)
from .ROCrate.rocrate_context import (init_v1_1, init_bioschemas_context)
from .conversion import (ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation, ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8)
from .fable_modules.fable_library.date import now
from .fable_modules.fable_library.option import value
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.seq import exactly_one
from .fable_modules.thoth_json_core.decode import map
from .fable_modules.thoth_json_core.types import (IEncodable, Decoder_1)

def _expr3584() -> TypeInfo:
    return class_type("ARCtrl.Json.ARC.ROCrate", None, ROCrate)


class ROCrate:
    ...

ROCrate_reflection = _expr3584

def ROCrate_getDefaultLicense(__unit: None=None) -> str:
    return "ALL RIGHTS RESERVED BY THE AUTHORS"


def ROCrate_get_metadataFileDescriptor(__unit: None=None) -> LDNode:
    node: LDNode = LDNode("ro-crate-metadata.json", ["http://schema.org/CreativeWork"])
    node.SetProperty("http://purl.org/dc/terms/conformsTo", LDRef("https://w3id.org/ro/crate/1.1"))
    node.SetProperty("http://schema.org/about", LDRef("./"))
    return node


def ROCrate_encoder_8A8D439(isa: ArcInvestigation, license: Any | None=None) -> IEncodable:
    license_2: Any = ROCrate_getDefaultLicense() if (license is None) else value(license)
    isa_1: LDNode = ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation(isa)
    LDDataset.set_sddate_published_as_date_time(isa_1, now())
    LDDataset.set_license_as_creative_work(isa_1, license_2)
    graph: LDGraph = isa_1.Flatten()
    context: LDContext = LDContext(None, [init_v1_1(), init_bioschemas_context()])
    graph.SetContext(context)
    graph.AddNode(ROCrate_get_metadataFileDescriptor())
    graph.Compact_InPlace()
    return encoder(graph)


def ROCrate_get_decoder(__unit: None=None) -> Decoder_1[ArcInvestigation]:
    def ctor(graph: LDGraph) -> ArcInvestigation:
        match_value: LDNode | None = graph.TryGetNode("./")
        if match_value is None:
            raise Exception("RO-Crate graph did not contain root data Entity")

        else: 
            return ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(match_value, graph, graph.TryGetContext())


    return map(ctor, decoder)


def ROCrate_get_decoderDeprecated(__unit: None=None) -> Decoder_1[ArcInvestigation]:
    def ctor(ldnode: LDNode) -> ArcInvestigation:
        return ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(exactly_one(LDDataset.get_abouts(ldnode)), None, init_v1_1())

    return map(ctor, decoder_1)


__all__ = ["ROCrate_reflection", "ROCrate_getDefaultLicense", "ROCrate_get_metadataFileDescriptor", "ROCrate_encoder_8A8D439", "ROCrate_get_decoder", "ROCrate_get_decoderDeprecated"]

