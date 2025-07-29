from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.list import (choose, of_array, FSharpList, singleton, empty)
from ..fable_modules.fable_library.option import (map, default_arg, value as value_9, bind)
from ..fable_modules.fable_library.seq import (map as map_1, to_list, delay, append, empty as empty_1, singleton as singleton_1, try_pick, length)
from ..fable_modules.fable_library.string_ import replace
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import IEnumerable_1
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, resize_array, IGetters, list_1 as list_1_2, map as map_2)
from ..fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ..fable_modules.thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..Core.arc_types import ArcAssay
from ..Core.comment import Comment
from ..Core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, JsonTypes_composeTechnologyPlatform, JsonTypes_decomposeTechnologyPlatform)
from ..Core.data import Data
from ..Core.data_map import DataMap
from ..Core.Helper.collections_ import (Option_fromValueWithDefault, ResizeArray_filter)
from ..Core.Helper.identifier import (Assay_fileNameFromIdentifier, create_missing_identifier, Assay_tryIdentifierFromFileName)
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.person import Person
from ..Core.Process.material_attribute import MaterialAttribute
from ..Core.Process.process import Process
from ..Core.Process.process_sequence import (get_data, get_units, get_characteristics)
from ..Core.Table.arc_table import ArcTable
from ..Core.Table.arc_tables import ArcTables
from ..Core.Table.composite_cell import CompositeCell
from .comment import (encoder as encoder_7, decoder as decoder_4, ROCrate_encoder as ROCrate_encoder_4, ROCrate_decoder as ROCrate_decoder_3, ISAJson_encoder as ISAJson_encoder_3, ISAJson_decoder as ISAJson_decoder_2)
from .context.rocrate.isa_assay_context import context_jsonvalue
from .data import (ROCrate_encoder as ROCrate_encoder_2, ISAJson_encoder as ISAJson_encoder_1)
from .DataMap.data_map import (encoder as encoder_4, decoder as decoder_2, encoder_compressed as encoder_compressed_2, decoder_compressed as decoder_compressed_2)
from .decode import Decode_objectNoAdditionalProperties
from .encode import (try_include, try_include_seq, try_include_list)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderPropertyValue, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderPropertyValue, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (encoder as encoder_6, decoder as decoder_3, ROCrate_encoder as ROCrate_encoder_1, ROCrate_decoder as ROCrate_decoder_2)
from .Process.assay_materials import encoder as encoder_9
from .Process.material_attribute import encoder as encoder_8
from .Process.process import (ROCrate_encoder as ROCrate_encoder_3, ROCrate_decoder as ROCrate_decoder_1, ISAJson_encoder as ISAJson_encoder_2, ISAJson_decoder as ISAJson_decoder_1)
from .Table.arc_table import (encoder as encoder_5, decoder as decoder_1, encoder_compressed as encoder_compressed_1, decoder_compressed as decoder_compressed_1)

__A_ = TypeVar("__A_")

def encoder(assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2902(__unit: None=None, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2901(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2901()

    def _arrow2904(value_1: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2903(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2903()

    def _arrow2906(value_3: str, assay: Any=assay) -> IEncodable:
        class ObjectExpr2905(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2905()

    def _arrow2907(oa: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2908(oa_1: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2909(oa_2: OntologyAnnotation, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2910(dm: DataMap, assay: Any=assay) -> IEncodable:
        return encoder_4(dm)

    def _arrow2911(table: ArcTable, assay: Any=assay) -> IEncodable:
        return encoder_5(table)

    def _arrow2912(person: Person, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2913(comment: Comment, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2902()), try_include("Title", _arrow2904, assay.Title), try_include("Description", _arrow2906, assay.Description), try_include("MeasurementType", _arrow2907, assay.MeasurementType), try_include("TechnologyType", _arrow2908, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2909, assay.TechnologyPlatform), try_include("DataMap", _arrow2910, assay.DataMap), try_include_seq("Tables", _arrow2911, assay.Tables), try_include_seq("Performers", _arrow2912, assay.Performers), try_include_seq("Comments", _arrow2913, assay.Comments)]))
    class ObjectExpr2914(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2914()


def _arrow2925(get: IGetters) -> ArcAssay:
    def _arrow2915(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow2916(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow2917(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow2918(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow2919(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow2920(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow2921(__unit: None=None) -> Array[ArcTable] | None:
        arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_1)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Tables", arg_13)

    def _arrow2922(__unit: None=None) -> DataMap | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("DataMap", decoder_2)

    def _arrow2923(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Performers", arg_17)

    def _arrow2924(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Comments", arg_19)

    return ArcAssay.create(_arrow2915(), _arrow2916(), _arrow2917(), _arrow2918(), _arrow2919(), _arrow2920(), _arrow2921(), _arrow2922(), _arrow2923(), _arrow2924())


decoder: Decoder_1[ArcAssay] = object(_arrow2925)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, assay: ArcAssay) -> IEncodable:
    def chooser(tupled_arg: tuple[str, IEncodable | None], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2929(__unit: None=None, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        value: str = assay.Identifier
        class ObjectExpr2928(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2928()

    def _arrow2931(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2930(IEncodable):
            def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                return helpers_1.encode_string(value_1)

        return ObjectExpr2930()

    def _arrow2933(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        class ObjectExpr2932(IEncodable):
            def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                return helpers_2.encode_string(value_3)

        return ObjectExpr2932()

    def _arrow2934(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa)

    def _arrow2935(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow2936(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow2937(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_1(string_table, oa_table, cell_table, table)

    def _arrow2938(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_compressed_2(string_table, oa_table, cell_table, dm)

    def _arrow2939(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_6(person)

    def _arrow2940(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> IEncodable:
        return encoder_7(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("Identifier", _arrow2929()), try_include("Title", _arrow2931, assay.Title), try_include("Description", _arrow2933, assay.Description), try_include("MeasurementType", _arrow2934, assay.MeasurementType), try_include("TechnologyType", _arrow2935, assay.TechnologyType), try_include("TechnologyPlatform", _arrow2936, assay.TechnologyPlatform), try_include_seq("Tables", _arrow2937, assay.Tables), try_include("DataMap", _arrow2938, assay.DataMap), try_include_seq("Performers", _arrow2939, assay.Performers), try_include_seq("Comments", _arrow2940, assay.Comments)]))
    class ObjectExpr2941(IEncodable):
        def Encode(self, helpers_3: IEncoderHelpers_1[Any], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_3.encode_object(arg)

    return ObjectExpr2941()


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcAssay]:
    def _arrow2952(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcAssay:
        def _arrow2942(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow2943(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow2944(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow2945(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow2946(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow2947(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow2948(__unit: None=None) -> Array[ArcTable] | None:
            arg_13: Decoder_1[Array[ArcTable]] = resize_array(decoder_compressed_1(string_table, oa_table, cell_table))
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Tables", arg_13)

        def _arrow2949(__unit: None=None) -> DataMap | None:
            arg_15: Decoder_1[DataMap] = decoder_compressed_2(string_table, oa_table, cell_table)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("DataMap", arg_15)

        def _arrow2950(__unit: None=None) -> Array[Person] | None:
            arg_17: Decoder_1[Array[Person]] = resize_array(decoder_3)
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Performers", arg_17)

        def _arrow2951(__unit: None=None) -> Array[Comment] | None:
            arg_19: Decoder_1[Array[Comment]] = resize_array(decoder_4)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Comments", arg_19)

        return ArcAssay.create(_arrow2942(), _arrow2943(), _arrow2944(), _arrow2945(), _arrow2946(), _arrow2947(), _arrow2948(), _arrow2949(), _arrow2950(), _arrow2951())

    return object(_arrow2952)


def ROCrate_genID(a: ArcAssay) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyAssay"

    else: 
        return ("assays/" + replace(match_value, " ", "_")) + "/"



def ROCrate_encoder(study_name: str | None, a: ArcAssay) -> IEncodable:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    def chooser(tupled_arg: tuple[str, IEncodable | None], study_name: Any=study_name, a: Any=a) -> tuple[str, IEncodable] | None:
        def mapping(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
            return (tupled_arg[0], v_1)

        return map(mapping, tupled_arg[1])

    def _arrow2956(__unit: None=None, study_name: Any=study_name, a: Any=a) -> IEncodable:
        value: str = ROCrate_genID(a)
        class ObjectExpr2955(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                return helpers.encode_string(value)

        return ObjectExpr2955()

    class ObjectExpr2957(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_1.encode_string("Assay")

    class ObjectExpr2958(IEncodable):
        def Encode(self, helpers_2: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_2.encode_string("Assay")

    def _arrow2960(__unit: None=None, study_name: Any=study_name, a: Any=a) -> IEncodable:
        value_3: str = a.Identifier
        class ObjectExpr2959(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any]) -> Any:
                return helpers_3.encode_string(value_3)

        return ObjectExpr2959()

    class ObjectExpr2961(IEncodable):
        def Encode(self, helpers_4: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            return helpers_4.encode_string(file_name)

    def _arrow2963(value_5: str, study_name: Any=study_name, a: Any=a) -> IEncodable:
        class ObjectExpr2962(IEncodable):
            def Encode(self, helpers_5: IEncoderHelpers_1[Any]) -> Any:
                return helpers_5.encode_string(value_5)

        return ObjectExpr2962()

    def _arrow2965(value_7: str, study_name: Any=study_name, a: Any=a) -> IEncodable:
        class ObjectExpr2964(IEncodable):
            def Encode(self, helpers_6: IEncoderHelpers_1[Any]) -> Any:
                return helpers_6.encode_string(value_7)

        return ObjectExpr2964()

    def _arrow2966(oa: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderPropertyValue(oa)

    def _arrow2967(oa_1: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow2968(oa_2: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_2)

    def _arrow2969(oa_3: Person, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_1(oa_3)

    def _arrow2970(oa_4: Data, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_2(oa_4)

    def _arrow2972(__unit: None=None, study_name: Any=study_name, a: Any=a) -> Callable[[Process], IEncodable]:
        assay_name: str | None = a.Identifier
        def _arrow2971(oa_5: Process) -> IEncodable:
            return ROCrate_encoder_3(study_name, assay_name, oa_5)

        return _arrow2971

    def _arrow2973(comment: Comment, study_name: Any=study_name, a: Any=a) -> IEncodable:
        return ROCrate_encoder_4(comment)

    values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("@id", _arrow2956()), ("@type", list_1_1(singleton(ObjectExpr2957()))), ("additionalType", ObjectExpr2958()), ("identifier", _arrow2960()), ("filename", ObjectExpr2961()), try_include("title", _arrow2963, a.Title), try_include("description", _arrow2965, a.Description), try_include("measurementType", _arrow2966, a.MeasurementType), try_include("technologyType", _arrow2967, a.TechnologyType), try_include("technologyPlatform", _arrow2968, a.TechnologyPlatform), try_include_seq("performers", _arrow2969, a.Performers), try_include_list("dataFiles", _arrow2970, data_files), try_include_list("processSequence", _arrow2972(), processes), try_include_seq("comments", _arrow2973, a.Comments), ("@context", context_jsonvalue)]))
    class ObjectExpr2974(IEncodable):
        def Encode(self, helpers_7: IEncoderHelpers_1[Any], study_name: Any=study_name, a: Any=a) -> Any:
            def mapping_1(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_7))

            arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_1, values)
            return helpers_7.encode_object(arg)

    return ObjectExpr2974()


def _arrow2984(get: IGetters) -> ArcAssay:
    def _arrow2975(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    identifier: str = default_arg(_arrow2975(), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow2976(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ROCrate_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow2976())
    def _arrow2977(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow2978(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow2979(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("measurementType", OntologyAnnotation_ROCrate_decoderPropertyValue)

    def _arrow2980(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow2981(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("technologyPlatform", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow2982(__unit: None=None) -> Array[Person] | None:
        arg_16: Decoder_1[Array[Person]] = resize_array(ROCrate_decoder_2)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("performers", arg_16)

    def _arrow2983(__unit: None=None) -> Array[Comment] | None:
        arg_18: Decoder_1[Array[Comment]] = resize_array(ROCrate_decoder_3)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_18)

    return ArcAssay(identifier, _arrow2977(), _arrow2978(), _arrow2979(), _arrow2980(), _arrow2981(), tables, None, _arrow2982(), _arrow2983())


ROCrate_decoder: Decoder_1[ArcAssay] = object(_arrow2984)

def ISAJson_encoder(study_name: str | None, id_map: Any | None, a: ArcAssay) -> IEncodable:
    def f(a_1: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> IEncodable:
        file_name: str = Assay_fileNameFromIdentifier(a_1.Identifier)
        processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a_1)
        def encoder_1(oa: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        encoded_units: tuple[str, IEncodable | None] = try_include_list("unitCategories", encoder_1, get_units(processes))
        def encoder_2(value_1: MaterialAttribute, a_1: Any=a_1) -> IEncodable:
            return encoder_8(id_map, value_1)

        encoded_characteristics: tuple[str, IEncodable | None] = try_include_list("characteristicCategories", encoder_2, get_characteristics(processes))
        def _arrow2985(ps: FSharpList[Process], a_1: Any=a_1) -> IEncodable:
            return encoder_9(id_map, ps)

        encoded_materials: tuple[str, IEncodable | None] = try_include("materials", _arrow2985, Option_fromValueWithDefault(empty(), processes))
        def encoder_3(oa_1: Data, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_1(id_map, oa_1)

        encoced_data_files: tuple[str, IEncodable | None] = try_include_list("dataFiles", encoder_3, get_data(processes))
        units: FSharpList[OntologyAnnotation] = get_units(processes)
        def _arrow2988(__unit: None=None, a_1: Any=a_1) -> IEnumerable_1[Comment]:
            def _arrow2987(__unit: None=None) -> IEnumerable_1[Comment]:
                def _arrow2986(__unit: None=None) -> IEnumerable_1[Comment]:
                    return singleton_1(Comment.create("description", value_9(a_1.Description))) if (a_1.Description is not None) else empty_1()

                return append(singleton_1(Comment.create("title", value_9(a_1.Title))) if (a_1.Title is not None) else empty_1(), delay(_arrow2986))

            return append(a_1.Comments if (len(a_1.Comments) > 0) else empty_1(), delay(_arrow2987))

        comments: FSharpList[Comment] = to_list(delay(_arrow2988))
        def chooser(tupled_arg: tuple[str, IEncodable | None], a_1: Any=a_1) -> tuple[str, IEncodable] | None:
            def mapping_1(v_1: IEncodable, tupled_arg: Any=tupled_arg) -> tuple[str, IEncodable]:
                return (tupled_arg[0], v_1)

            return map(mapping_1, tupled_arg[1])

        class ObjectExpr2990(IEncodable):
            def Encode(self, helpers: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                return helpers.encode_string(file_name)

        def _arrow2992(value_5: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr2991(IEncodable):
                def Encode(self, helpers_1: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_1.encode_string(value_5)

            return ObjectExpr2991()

        def _arrow2993(oa_2: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_2)

        def _arrow2994(oa_3: OntologyAnnotation, a_1: Any=a_1) -> IEncodable:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_3)

        def _arrow2996(value_7: str, a_1: Any=a_1) -> IEncodable:
            class ObjectExpr2995(IEncodable):
                def Encode(self, helpers_2: IEncoderHelpers_1[Any]) -> Any:
                    return helpers_2.encode_string(value_7)

            return ObjectExpr2995()

        def mapping(tp: OntologyAnnotation, a_1: Any=a_1) -> str:
            return JsonTypes_composeTechnologyPlatform(tp)

        def _arrow2998(__unit: None=None, a_1: Any=a_1) -> Callable[[Process], IEncodable]:
            assay_name: str | None = a_1.Identifier
            def _arrow2997(oa_4: Process) -> IEncodable:
                return ISAJson_encoder_2(study_name, assay_name, id_map, oa_4)

            return _arrow2997

        def _arrow2999(comment: Comment, a_1: Any=a_1) -> IEncodable:
            return ISAJson_encoder_3(id_map, comment)

        values: FSharpList[tuple[str, IEncodable]] = choose(chooser, of_array([("filename", ObjectExpr2990()), try_include("@id", _arrow2992, ROCrate_genID(a_1)), try_include("measurementType", _arrow2993, a_1.MeasurementType), try_include("technologyType", _arrow2994, a_1.TechnologyType), try_include("technologyPlatform", _arrow2996, map(mapping, a_1.TechnologyPlatform)), encoced_data_files, encoded_materials, encoded_characteristics, encoded_units, try_include_list("processSequence", _arrow2998(), processes), try_include_seq("comments", _arrow2999, comments)]))
        class ObjectExpr3000(IEncodable):
            def Encode(self, helpers_3: IEncoderHelpers_1[Any], a_1: Any=a_1) -> Any:
                def mapping_2(tupled_arg_1: tuple[str, IEncodable]) -> tuple[str, __A_]:
                    return (tupled_arg_1[0], tupled_arg_1[1].Encode(helpers_3))

                arg: IEnumerable_1[tuple[str, __A_]] = map_1(mapping_2, values)
                return helpers_3.encode_object(arg)

        return ObjectExpr3000()

    if id_map is not None:
        def _arrow3001(a_2: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> str:
            return ROCrate_genID(a_2)

        return encode(_arrow3001, f, a, id_map)

    else: 
        return f(a)



ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "measurementType", "technologyType", "technologyPlatform", "dataFiles", "materials", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow3007(get: IGetters) -> ArcAssay:
    def _arrow3002(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Assay_tryIdentifierFromFileName, _arrow3002()), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow3003(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(ISAJson_decoder_1)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow3003())
    comments: Array[Comment] | None
    arg_6: Decoder_1[Array[Comment]] = resize_array(ISAJson_decoder_2)
    object_arg_2: IOptionalGetter = get.Optional
    comments = object_arg_2.Field("comments", arg_6)
    def binder(c: Array[Comment]) -> str | None:
        def chooser(x: Comment, c: Any=c) -> str | None:
            if (value_9(x.Name) == "title") if (x.Name is not None) else False:
                return x.Value

            else: 
                return None


        return try_pick(chooser, c)

    title: str | None = bind(binder, comments)
    def binder_1(c_1: Array[Comment]) -> str | None:
        def chooser_1(x_1: Comment, c_1: Any=c_1) -> str | None:
            if (value_9(x_1.Name) == "description") if (x_1.Name is not None) else False:
                return x_1.Value

            else: 
                return None


        return try_pick(chooser_1, c_1)

    description: str | None = bind(binder_1, comments)
    def binder_2(c_2: Array[Comment]) -> Array[Comment] | None:
        def f(x_2: Comment, c_2: Any=c_2) -> bool:
            if x_2.Name is None:
                return True

            elif value_9(x_2.Name) != "title":
                return value_9(x_2.Name) != "description"

            else: 
                return False


        match_value: Array[Comment] = ResizeArray_filter(f, c_2)
        if length(match_value) == 0:
            return None

        else: 
            return match_value


    comments_1: Array[Comment] | None = bind(binder_2, comments)
    def _arrow3004(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("measurementType", OntologyAnnotation_ISAJson_decoder)

    def _arrow3005(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyType", OntologyAnnotation_ISAJson_decoder)

    def _arrow3006(__unit: None=None) -> OntologyAnnotation | None:
        arg_12: Decoder_1[OntologyAnnotation] = map_2(JsonTypes_decomposeTechnologyPlatform, string)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("technologyPlatform", arg_12)

    return ArcAssay(identifier, title, description, _arrow3004(), _arrow3005(), _arrow3006(), tables, None, None, comments_1)


ISAJson_decoder: Decoder_1[ArcAssay] = Decode_objectNoAdditionalProperties(ISAJson_allowedFields, _arrow3007)

__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed", "ROCrate_genID", "ROCrate_encoder", "ROCrate_decoder", "ISAJson_encoder", "ISAJson_allowedFields", "ISAJson_decoder"]

