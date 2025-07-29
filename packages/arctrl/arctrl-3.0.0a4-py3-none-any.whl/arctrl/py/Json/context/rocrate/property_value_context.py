from __future__ import annotations
from typing import (Any, TypeVar)
from ....fable_modules.fable_library.seq import map
from ....fable_modules.fable_library.util import (to_enumerable, IEnumerable_1)
from ....fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1)

__A_ = TypeVar("__A_")

def _arrow1618(__unit: None=None) -> IEncodable:
    class ObjectExpr1605(IEncodable):
        def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
            return helpers.encode_string("http://schema.org/")

    class ObjectExpr1606(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
            return helpers_1.encode_string("sdo:additionalType")

    class ObjectExpr1607(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
            return helpers_2.encode_string("sdo:alternateName")

    class ObjectExpr1608(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
            return helpers_3.encode_string("sdo:measurementMethod")

    class ObjectExpr1609(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any]) -> Any:
            return helpers_4.encode_string("sdo:description")

    class ObjectExpr1610(IEncodable):
        def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
            return helpers_5.encode_string("sdo:name")

    class ObjectExpr1611(IEncodable):
        def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
            return helpers_6.encode_string("sdo:propertyID")

    class ObjectExpr1612(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any]) -> Any:
            return helpers_7.encode_string("sdo:value")

    class ObjectExpr1613(IEncodable):
        def Encode(self, helpers_8: IEncoderHelpers_1[Any]) -> Any:
            return helpers_8.encode_string("sdo:valueReference")

    class ObjectExpr1614(IEncodable):
        def Encode(self, helpers_9: IEncoderHelpers_1[Any]) -> Any:
            return helpers_9.encode_string("sdo:unitText")

    class ObjectExpr1615(IEncodable):
        def Encode(self, helpers_10: IEncoderHelpers_1[Any]) -> Any:
            return helpers_10.encode_string("sdo:unitCode")

    class ObjectExpr1616(IEncodable):
        def Encode(self, helpers_11: IEncoderHelpers_1[Any]) -> Any:
            return helpers_11.encode_string("sdo:disambiguatingDescription")

    values: IEnumerable_1[tuple[str, IEncodable]] = to_enumerable([("sdo", ObjectExpr1605()), ("additionalType", ObjectExpr1606()), ("alternateName", ObjectExpr1607()), ("measurementMethod", ObjectExpr1608()), ("description", ObjectExpr1609()), ("category", ObjectExpr1610()), ("categoryCode", ObjectExpr1611()), ("value", ObjectExpr1612()), ("valueCode", ObjectExpr1613()), ("unit", ObjectExpr1614()), ("unitCode", ObjectExpr1615()), ("comments", ObjectExpr1616())])
    class ObjectExpr1617(IEncodable):
        def Encode(self, helpers_12: IEncoderHelpers_1[Any]) -> Any:
            def mapping(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_12))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping, values)
            return helpers_12.encode_object(arg)

    return ObjectExpr1617()


context_jsonvalue: IEncodable = _arrow1618()

__all__ = ["context_jsonvalue"]

