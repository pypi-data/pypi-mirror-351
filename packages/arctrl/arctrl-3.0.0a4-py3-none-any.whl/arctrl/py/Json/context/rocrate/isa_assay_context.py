from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, TypeVar)
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.seq import map
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import (to_enumerable, IEnumerable_1)
from ....fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _expr1619() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Assay.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Assay", string_type), ("ArcAssay", string_type), ("measurement_type", string_type), ("technology_type", string_type), ("technology_platform", string_type), ("data_files", string_type), ("materials", string_type), ("other_materials", string_type), ("samples", string_type), ("characteristic_categories", string_type), ("process_sequence", string_type), ("unit_categories", string_type), ("comments", string_type), ("filename", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Assay: str
    ArcAssay: str
    measurement_type: str
    technology_type: str
    technology_platform: str
    data_files: str
    materials: str
    other_materials: str
    samples: str
    characteristic_categories: str
    process_sequence: str
    unit_categories: str
    comments: str
    filename: str

IContext_reflection = _expr1619

def _arrow1633(__unit: None=None) -> IEncodable:
    class ObjectExpr1620(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1621(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:Dataset")

    class ObjectExpr1622(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:identifier")

    class ObjectExpr1623(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:additionalType")

    class ObjectExpr1624(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:variableMeasured")

    class ObjectExpr1625(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:measurementTechnique")

    class ObjectExpr1626(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:measurementMethod")

    class ObjectExpr1627(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("sdo:hasPart")

    class ObjectExpr1628(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            return helpers_8.encode_string("sdo:creator")

    class ObjectExpr1629(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
            return helpers_9.encode_string("sdo:about")

    class ObjectExpr1630(IEncodable):
        def Encode(self, helpers_10: IEncoderHelpers_1[Any]) -> Any:
            return helpers_10.encode_string("sdo:comment")

    class ObjectExpr1631(IEncodable):
        def Encode(self, helpers_11: IEncoderHelpers_1[Any]) -> Any:
            return helpers_11.encode_string("sdo:url")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1620()), ("Assay", ObjectExpr1621()), ("identifier", ObjectExpr1622()), ("additionalType", ObjectExpr1623()), ("measurementType", ObjectExpr1624()), ("technologyType", ObjectExpr1625()), ("technologyPlatform", ObjectExpr1626()), ("dataFiles", ObjectExpr1627()), ("performers", ObjectExpr1628()), ("processSequence", ObjectExpr1629()), ("comments", ObjectExpr1630()), ("filename", ObjectExpr1631())])
    class ObjectExpr1632(IEncodable):
        def Encode(self, helpers_12: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_12))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_12.encode_object(arg)

    return ObjectExpr1632()


context_jsonvalue: IEncodable = _arrow1633()

__all__ = ["IContext_reflection", "context_jsonvalue"]

