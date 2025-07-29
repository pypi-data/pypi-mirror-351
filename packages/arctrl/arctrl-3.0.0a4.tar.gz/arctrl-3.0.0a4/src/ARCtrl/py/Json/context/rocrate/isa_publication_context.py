from __future__ import annotations
from dataclasses import dataclass
from typing import (Any, TypeVar)
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.seq import map
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import (to_enumerable, IEnumerable_1)
from ....fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _expr1826() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Publication.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Publication", string_type), ("pub_med_id", string_type), ("doi", string_type), ("title", string_type), ("status", string_type), ("author_list", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Publication: str
    pub_med_id: str
    doi: str
    title: str
    status: str
    author_list: str
    comments: str

IContext_reflection = _expr1826

def _arrow1836(__unit: None=None) -> IEncodable:
    class ObjectExpr1827(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1828(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:ScholarlyArticle")

    class ObjectExpr1829(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:url")

    class ObjectExpr1830(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:sameAs")

    class ObjectExpr1831(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:headline")

    class ObjectExpr1832(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:creativeWorkStatus")

    class ObjectExpr1833(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:author")

    class ObjectExpr1834(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("sdo:disambiguatingDescription")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1827()), ("Publication", ObjectExpr1828()), ("pubMedID", ObjectExpr1829()), ("doi", ObjectExpr1830()), ("title", ObjectExpr1831()), ("status", ObjectExpr1832()), ("authorList", ObjectExpr1833()), ("comments", ObjectExpr1834())])
    class ObjectExpr1835(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_8))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_8.encode_object(arg)

    return ObjectExpr1835()


context_jsonvalue: IEncodable = _arrow1836()

__all__ = ["IContext_reflection", "context_jsonvalue"]

