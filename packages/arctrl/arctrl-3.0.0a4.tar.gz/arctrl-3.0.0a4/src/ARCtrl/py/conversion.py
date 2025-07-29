from __future__ import annotations
from collections.abc import Callable
from typing import Any
from .Core.arc_types import (ArcAssay, ArcStudy, ArcInvestigation)
from .Core.comment import Comment
from .Core.data import (Data, DataAux_pathAndSelectorFromName)
from .Core.data_context import (DataContext__get_Explication, DataContext__get_Unit, DataContext__get_ObjectType, DataContext__get_GeneratedBy, DataContext__get_Description, DataContext__get_Label, DataContext, DataContext__ctor_Z780A8A2A)
from .Core.data_file import (DataFile__get_AsString, DataFile, DataFile_fromString_Z721C83C5)
from .Core.data_map import (DataMap__get_DataContexts, DataMap, DataMap__ctor_4E3220A7, DataMap_init)
from .Core.Helper.collections_ import (Option_fromValueWithDefault, Option_fromSeq, ResizeArray_map, ResizeArray_singleton, ResizeArray_create, ResizeArray_zip, ResizeArray_appendSingleton, ResizeArray_tryPick, ResizeArray_distinct, ResizeArray_append, ResizeArray_choose, ResizeArray_collect, ResizeArray_filter, ResizeArray_tryFind, ResizeArray_groupBy)
from .Core.Helper.identifier import create_missing_identifier
from .Core.Helper.orcid import try_get_orcid_number
from .Core.Helper.regex import ActivePatterns__007CRegex_007C__007C
from .Core.ontology_annotation import OntologyAnnotation
from .Core.person import Person
from .Core.publication import Publication
from .Core.Table.arc_table import ArcTable
from .Core.Table.arc_table_aux import Unchecked_alignByHeaders
from .Core.Table.arc_tables import ArcTables
from .Core.Table.composite_cell import CompositeCell
from .Core.Table.composite_header import (CompositeHeader, IOType)
from .Json.decode import Decode_datetime
from .Json.encode import date_time
from .Json.ROCrate.ldnode import (decoder as decoder_1, encoder)
from .ROCrate.Generic.comment import LDComment
from .ROCrate.Generic.dataset import LDDataset
from .ROCrate.Generic.defined_term import LDDefinedTerm
from .ROCrate.Generic.file import LDFile
from .ROCrate.Generic.lab_process import LDLabProcess
from .ROCrate.Generic.lab_protocol import LDLabProtocol
from .ROCrate.Generic.organization import LDOrganization
from .ROCrate.Generic.person import LDPerson
from .ROCrate.Generic.property_value import LDPropertyValue
from .ROCrate.Generic.sample import LDSample
from .ROCrate.Generic.scholarly_article import LDScholarlyArticle
from .ROCrate.ldcontext import LDContext
from .ROCrate.ldobject import (LDNode, LDRef, LDGraph)
from .fable_modules.thoth_json_python.decode import Decode_fromString
from .fable_modules.thoth_json_python.encode import to_string
from .fable_modules.fable_library.array_ import singleton as singleton_1
from .fable_modules.fable_library.date import now
from .fable_modules.fable_library.int32 import (try_parse, parse)
from .fable_modules.fable_library.list import (FSharpList, choose, length, empty, map as map_2, sort_by, singleton as singleton_2, initialize, collect, of_seq)
from .fable_modules.fable_library.map_util import get_item_from_dict
from .fable_modules.fable_library.option import (value as value_4, map, default_arg, bind)
from .fable_modules.fable_library.range import range_big_int
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.reg_exp import (get_item, groups)
from .fable_modules.fable_library.result import FSharpResult_2
from .fable_modules.fable_library.seq import (indexed, to_list, filter, try_pick, choose as choose_1, map as map_1, max, delay, append, empty as empty_1, singleton, fold, zip, is_empty)
from .fable_modules.fable_library.seq2 import (List_groupBy, List_distinct)
from .fable_modules.fable_library.string_ import (to_text, printf, to_fail, remove, join)
from .fable_modules.fable_library.system_text import (StringBuilder__ctor, StringBuilder__Append_244C7CD6, StringBuilder__Clear)
from .fable_modules.fable_library.types import (FSharpRef, to_string as to_string_1, Array)
from .fable_modules.fable_library.util import (int32_to_string, IEnumerable_1, compare_primitives, string_hash, get_enumerator, dispose, ignore, equals, safe_hash)

def DateTime_tryFromString(s: str) -> Any | None:
    try: 
        def _arrow3672(__unit: None=None) -> Any:
            match_value: FSharpResult_2[Any, str] = Decode_fromString(Decode_datetime, s)
            if match_value.tag == 1:
                raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

            else: 
                return match_value.fields[0]


        return _arrow3672()

    except Exception as match_value_1:
        return None



def DateTime_toString(d: Any) -> str:
    return to_string(0, date_time(d))


def ColumnIndex_tryInt(str_1: str) -> int | None:
    match_value: tuple[bool, int]
    out_arg: int = 0
    def _arrow3673(__unit: None=None, str_1: Any=str_1) -> int:
        return out_arg

    def _arrow3674(v: int, str_1: Any=str_1) -> None:
        nonlocal out_arg
        out_arg = v or 0

    match_value = (try_parse(str_1, 511, False, 32, FSharpRef(_arrow3673, _arrow3674)), out_arg)
    if match_value[0]:
        return match_value[1]

    else: 
        return None



ColumnIndex_orderName: str = "columnIndex"

def ColumnIndex_tryGetIndex(node: LDNode) -> int | None:
    match_value: Any | None = node.TryGetPropertyAsSingleton(ColumnIndex_orderName)
    (pattern_matching_result, ci) = (None, None)
    if match_value is not None:
        if str(type(value_4(match_value))) == "<class \'str\'>":
            pattern_matching_result = 0
            ci = value_4(match_value)

        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return ColumnIndex_tryInt(ci)

    elif pattern_matching_result == 1:
        return None



def ColumnIndex_setIndex(node: LDNode, index: int) -> None:
    node.SetProperty(ColumnIndex_orderName, int32_to_string(index))


def ARCtrl_ROCrate_LDNode__LDNode_GetColumnIndex(this: LDNode) -> int:
    return value_4(ColumnIndex_tryGetIndex(this))


def ARCtrl_ROCrate_LDNode__LDNode_TryGetColumnIndex(this: LDNode) -> int | None:
    return ColumnIndex_tryGetIndex(this)


def ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4(this: LDNode, index: int) -> None:
    ColumnIndex_setIndex(this, index)


def _expr3675() -> TypeInfo:
    return class_type("ARCtrl.Conversion.BaseTypes", None, BaseTypes)


class BaseTypes:
    ...

BaseTypes_reflection = _expr3675

def BaseTypes_composeComment_Z13201A7E(comment: Comment) -> LDNode:
    name: str
    match_value: str | None = comment.Name
    if match_value is None:
        raise Exception("Comment must have a name")

    else: 
        name = match_value

    return LDComment.create(name, None, comment.Value)


def BaseTypes_decomposeComment_Z2F770004(comment: LDNode, context: LDContext | None=None) -> Comment:
    return Comment(LDComment.get_name_as_string(comment, context), LDComment.try_get_text_as_string(comment, context))


def BaseTypes_ontologyTermFromNameAndID_40457300(name: str | None=None, id: str | None=None) -> OntologyAnnotation:
    if id is None:
        return OntologyAnnotation.create(name)

    else: 
        t: str = id
        return OntologyAnnotation.from_term_annotation(t, name)



def BaseTypes_tryOntologyTermFromNameAndID_40457300(name: str | None=None, id: str | None=None) -> OntologyAnnotation | None:
    if (id is None) if (name is None) else False:
        return None

    else: 
        return BaseTypes_ontologyTermFromNameAndID_40457300(name, id)



def BaseTypes_composeDefinedTerm_ZDED3A0F(term: OntologyAnnotation) -> LDNode:
    tan: str | None = Option_fromValueWithDefault("", term.TermAccessionAndOntobeeUrlIfShort)
    return LDDefinedTerm.create(term.NameText, None, tan)


def BaseTypes_decomposeDefinedTerm_Z2F770004(term: LDNode, context: LDContext | None=None) -> OntologyAnnotation:
    return BaseTypes_ontologyTermFromNameAndID_40457300(LDDefinedTerm.get_name_as_string(term, context), LDDefinedTerm.try_get_term_code_as_string(term, context))


def BaseTypes_composePropertyValueFromOA_ZDED3A0F(term: OntologyAnnotation) -> LDNode:
    tan: str | None = Option_fromValueWithDefault("", term.TermAccessionAndOntobeeUrlIfShort)
    return LDPropertyValue.create(term.NameText, None, None, tan)


def BaseTypes_decomposePropertyValueToOA_Z2F770004(term: LDNode, context: LDContext | None=None) -> OntologyAnnotation:
    return BaseTypes_ontologyTermFromNameAndID_40457300(LDPropertyValue.get_name_as_string(term, context), LDPropertyValue.try_get_property_idas_string(term, context))


def BaseTypes_valuesOfCell_Z436420FE(value: CompositeCell) -> tuple[str | None, str | None, str | None, str | None]:
    if value.tag == 0:
        if value.fields[0].is_empty():
            return (None, None, None, None)

        elif value.fields[0].TANInfo is not None:
            return (value.fields[0].Name, value.fields[0].TermAccessionAndOntobeeUrlIfShort, None, None)

        else: 
            return (value.fields[0].Name, None, None, None)


    elif value.tag == 2:
        pattern_input: tuple[str | None, str | None] = ((None, None)) if value.fields[1].is_empty() else ((value.fields[1].Name, Option_fromValueWithDefault("", value.fields[1].TermAccessionAndOntobeeUrlIfShort)))
        return (Option_fromValueWithDefault("", value.fields[0]), None, pattern_input[0], pattern_input[1])

    elif value.tag == 3:
        raise Exception("Data cell should not be parsed to isa value")

    elif value.fields[0] == "":
        return (None, None, None, None)

    else: 
        return (value.fields[0], None, None, None)



def BaseTypes_termOfHeader_6CAF647B(header: CompositeHeader) -> tuple[str, str | None]:
    (pattern_matching_result, oa) = (None, None)
    if header.tag == 0:
        pattern_matching_result = 0
        oa = header.fields[0]

    elif header.tag == 3:
        pattern_matching_result = 0
        oa = header.fields[0]

    elif header.tag == 2:
        pattern_matching_result = 0
        oa = header.fields[0]

    elif header.tag == 1:
        pattern_matching_result = 0
        oa = header.fields[0]

    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return (oa.NameText, oa.TermAccessionAndOntobeeUrlIfShort if (oa.TANInfo is not None) else None)

    elif pattern_matching_result == 1:
        return to_fail(printf("header %O should not be parsed to isa value"))(header)



def BaseTypes_composeComponent(header: CompositeHeader, value: CompositeCell) -> LDNode:
    pattern_input: tuple[str | None, str | None, str | None, str | None] = BaseTypes_valuesOfCell_Z436420FE(value)
    pattern_input_1: tuple[str, str | None] = BaseTypes_termOfHeader_6CAF647B(header)
    return LDPropertyValue.create_component(pattern_input_1[0], pattern_input[0], None, pattern_input_1[1], pattern_input[3], pattern_input[2], pattern_input[1])


def BaseTypes_composeParameterValue(header: CompositeHeader, value: CompositeCell) -> LDNode:
    pattern_input: tuple[str | None, str | None, str | None, str | None] = BaseTypes_valuesOfCell_Z436420FE(value)
    pattern_input_1: tuple[str, str | None] = BaseTypes_termOfHeader_6CAF647B(header)
    return LDPropertyValue.create_parameter_value(pattern_input_1[0], pattern_input[0], None, pattern_input_1[1], pattern_input[3], pattern_input[2], pattern_input[1])


def BaseTypes_composeFactorValue(header: CompositeHeader, value: CompositeCell) -> LDNode:
    pattern_input: tuple[str | None, str | None, str | None, str | None] = BaseTypes_valuesOfCell_Z436420FE(value)
    pattern_input_1: tuple[str, str | None] = BaseTypes_termOfHeader_6CAF647B(header)
    return LDPropertyValue.create_factor_value(pattern_input_1[0], pattern_input[0], None, pattern_input_1[1], pattern_input[3], pattern_input[2], pattern_input[1])


def BaseTypes_composeCharacteristicValue(header: CompositeHeader, value: CompositeCell) -> LDNode:
    pattern_input: tuple[str | None, str | None, str | None, str | None] = BaseTypes_valuesOfCell_Z436420FE(value)
    pattern_input_1: tuple[str, str | None] = BaseTypes_termOfHeader_6CAF647B(header)
    return LDPropertyValue.create_characteristic_value(pattern_input_1[0], pattern_input[0], None, pattern_input_1[1], pattern_input[3], pattern_input[2], pattern_input[1])


def BaseTypes_composeFreetextMaterialName(header_ft: str, name: str) -> str:
    return ((("" + header_ft) + "=") + name) + ""


def BaseTypes_composeFile_3A03A101(d: Data) -> LDNode:
    def mapping(dt: DataFile, d: Any=d) -> str:
        return DataFile__get_AsString(dt)

    data_type: str | None = map(mapping, d.DataType)
    return LDFile.create(d.NameText, d.NameText, None, data_type, d.Format, d.SelectorFormat)


def BaseTypes_decomposeFile_Z2F770004(f: LDNode, context: LDContext | None=None) -> Data:
    def mapping(dt: str, f: Any=f, context: Any=context) -> DataFile:
        return DataFile_fromString_Z721C83C5(dt)

    data_type: DataFile | None = map(mapping, LDFile.try_get_disambiguating_description_as_string(f, context))
    format: str | None = LDFile.try_get_encoding_format_as_string(f, context)
    selector_format: str | None = LDFile.try_get_usage_info_as_string(f, context)
    return Data(None, LDFile.get_name_as_string(f, context), data_type, format, selector_format)


def BaseTypes_composeFragmentDescriptor_Z4C0BEF62(dc: DataContext) -> LDNode:
    if dc.Name is None:
        raise Exception("RO-Crate parsing of DataContext failed: Cannot create a fragment descriptor without a name.")

    id: str = LDPropertyValue.gen_id_fragment_descriptor(dc.NameText)
    def mapping(e: OntologyAnnotation, dc: Any=dc) -> tuple[str | None, str | None]:
        return (e.Name, Option_fromValueWithDefault("", e.TermAccessionAndOntobeeUrlIfShort))

    pattern_input: tuple[str | None, str | None] = default_arg(map(mapping, DataContext__get_Explication(dc)), (None, None))
    def mapping_1(u: OntologyAnnotation, dc: Any=dc) -> tuple[str | None, str | None]:
        return (u.Name, Option_fromValueWithDefault("", u.TermAccessionAndOntobeeUrlIfShort))

    pattern_input_1: tuple[str | None, str | None] = default_arg(map(mapping_1, DataContext__get_Unit(dc)), (None, None))
    def f(c: Comment, dc: Any=dc) -> str:
        return to_string_1(c)

    disambiguating_descriptions: Array[str] | None = Option_fromSeq(ResizeArray_map(f, dc.Comments))
    data_fragment: LDNode = BaseTypes_composeFile_3A03A101(dc)
    def mapping_2(term: OntologyAnnotation, dc: Any=dc) -> LDNode:
        return BaseTypes_composeDefinedTerm_ZDED3A0F(term)

    pattern: LDNode | None = map(mapping_2, DataContext__get_ObjectType(dc))
    data_fragment.SetProperty(LDFile.about(), LDRef(id))
    data_fragment.SetOptionalProperty(LDFile.pattern(), pattern)
    return LDPropertyValue.create_fragment_descriptor(dc.NameText, pattern_input[0], None, pattern_input_1[1], pattern_input_1[0], pattern_input[1], DataContext__get_GeneratedBy(dc), DataContext__get_Description(dc), DataContext__get_Label(dc), disambiguating_descriptions, data_fragment)


def BaseTypes_decomposeFragmentDescriptor_Z6839B9E8(fd: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> DataContext:
    file: LDNode | None = LDPropertyValue.try_get_subject_of(fd, graph, context)
    name: str
    if file is None:
        raise Exception("RO-Crate parsing of DataContext failed: Cannot decompose a fragment descriptor without a name.")

    else: 
        f: LDNode = file
        name = LDFile.get_name_as_string(f, context)

    def mapping(pa: LDNode, fd: Any=fd, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposeDefinedTerm_Z2F770004(pa, context)

    def binder(f_1: LDNode, fd: Any=fd, graph: Any=graph, context: Any=context) -> LDNode | None:
        return LDFile.try_get_pattern_as_defined_term(f_1, graph, context)

    object_type: OntologyAnnotation | None = map(mapping, bind(binder, file))
    def binder_1(f_2: LDNode, fd: Any=fd, graph: Any=graph, context: Any=context) -> str | None:
        return LDFile.try_get_encoding_format_as_string(f_2, context)

    format: str | None = bind(binder_1, file)
    def binder_2(f_3: LDNode, fd: Any=fd, graph: Any=graph, context: Any=context) -> str | None:
        return LDFile.try_get_usage_info_as_string(f_3, context)

    selector_format: str | None = bind(binder_2, file)
    explication: OntologyAnnotation | None = BaseTypes_tryOntologyTermFromNameAndID_40457300(LDPropertyValue.try_get_value_as_string(fd), LDPropertyValue.try_get_value_reference_as_string(fd))
    unit: OntologyAnnotation | None = BaseTypes_tryOntologyTermFromNameAndID_40457300(LDPropertyValue.try_get_unit_text_as_string(fd), LDPropertyValue.try_get_unit_code_as_string(fd))
    generated_by: str | None = LDPropertyValue.try_get_measurement_method_as_string(fd)
    description: str | None = LDPropertyValue.try_get_description_as_string(fd)
    def f_4(s: str, fd: Any=fd, graph: Any=graph, context: Any=context) -> Comment:
        return Comment.from_string(s)

    return DataContext__ctor_Z780A8A2A(None, name, None, format, selector_format, explication, unit, object_type, LDPropertyValue.try_get_alternate_name_as_string(fd), description, generated_by, ResizeArray_map(f_4, LDPropertyValue.get_disambiguating_descriptions_as_string(fd)))


def BaseTypes_composeProcessInput(header: CompositeHeader, value: CompositeCell) -> LDNode:
    if header.tag == 11:
        if header.fields[0].tag == 1:
            return LDSample.create_sample(value.AsFreeText)

        elif header.fields[0].tag == 3:
            return LDSample.create_material(value.AsFreeText)

        elif header.fields[0].tag == 2:
            if value.tag == 1:
                ft: str = value.fields[0]
                return LDFile.create(ft, ft)

            elif value.tag == 3:
                return BaseTypes_composeFile_3A03A101(value.fields[0])

            else: 
                return to_fail(printf("Could not parse input data %O"))(value)


        elif header.fields[0].tag == 4:
            n: LDNode = LDNode(BaseTypes_composeFreetextMaterialName(header.fields[0].fields[0], value.AsFreeText), [header.fields[0].fields[0]])
            n.SetProperty(LDSample.name(), value.AsFreeText)
            return n

        else: 
            return LDSample.create_source(value.AsFreeText)


    else: 
        return to_fail(printf("Could not parse input header %O"))(header)



def BaseTypes_composeProcessOutput(header: CompositeHeader, value: CompositeCell) -> LDNode:
    (pattern_matching_result, ft_1) = (None, None)
    if header.tag == 12:
        if header.fields[0].tag == 1:
            pattern_matching_result = 0

        elif header.fields[0].tag == 3:
            pattern_matching_result = 1

        elif header.fields[0].tag == 2:
            pattern_matching_result = 2

        elif header.fields[0].tag == 4:
            pattern_matching_result = 3
            ft_1 = header.fields[0].fields[0]

        else: 
            pattern_matching_result = 0


    else: 
        pattern_matching_result = 4

    if pattern_matching_result == 0:
        return LDSample.create_sample(value.AsFreeText)

    elif pattern_matching_result == 1:
        return LDSample.create_material(value.AsFreeText)

    elif pattern_matching_result == 2:
        if value.tag == 1:
            ft: str = value.fields[0]
            return LDFile.create(ft, ft)

        elif value.tag == 3:
            return BaseTypes_composeFile_3A03A101(value.fields[0])

        else: 
            return to_fail(printf("Could not parse output data %O"))(value)


    elif pattern_matching_result == 3:
        n: LDNode = LDNode(BaseTypes_composeFreetextMaterialName(ft_1, value.AsFreeText), [ft_1])
        n.SetProperty(LDSample.name(), value.AsFreeText)
        return n

    elif pattern_matching_result == 4:
        return to_fail(printf("Could not parse output header %O"))(header)



def BaseTypes_headerOntologyOfPropertyValue_Z2F770004(pv: LDNode, context: LDContext | None=None) -> OntologyAnnotation:
    n: str = LDPropertyValue.get_name_as_string(pv, context)
    match_value: str | None = LDPropertyValue.try_get_property_idas_string(pv, context)
    if match_value is None:
        return OntologyAnnotation(n)

    else: 
        n_ref: str = match_value
        return OntologyAnnotation.from_term_annotation(n_ref, n)



def BaseTypes_cellOfPropertyValue_Z2F770004(pv: LDNode, context: LDContext | None=None) -> CompositeCell:
    v: str | None = LDPropertyValue.try_get_value_as_string(pv, context)
    v_ref: str | None = LDPropertyValue.try_get_value_reference_as_string(pv, context)
    u: str | None = LDPropertyValue.try_get_unit_text_as_string(pv, context)
    u_ref: str | None = LDPropertyValue.try_get_unit_code_as_string(pv, context)
    (pattern_matching_result, vr, u_1, u_ref_1) = (None, None, None, None)
    if v_ref is None:
        if u is None:
            if u_ref is None:
                pattern_matching_result = 3

            else: 
                pattern_matching_result = 2
                u_ref_1 = u_ref


        elif u_ref is not None:
            pattern_matching_result = 2
            u_ref_1 = u_ref

        else: 
            pattern_matching_result = 1
            u_1 = u


    elif u is None:
        if u_ref is None:
            pattern_matching_result = 0
            vr = v_ref

        else: 
            pattern_matching_result = 4


    else: 
        pattern_matching_result = 4

    if pattern_matching_result == 0:
        return CompositeCell(0, OntologyAnnotation.from_term_annotation(vr, v))

    elif pattern_matching_result == 1:
        return CompositeCell(2, default_arg(v, ""), OntologyAnnotation(u_1))

    elif pattern_matching_result == 2:
        return CompositeCell(2, default_arg(v, ""), OntologyAnnotation.from_term_annotation(u_ref_1, u))

    elif pattern_matching_result == 3:
        return CompositeCell(0, OntologyAnnotation(v))

    elif pattern_matching_result == 4:
        arg: str = default_arg(v, "")
        return to_fail(printf("Could not parse value %s with unit %O and unit reference %O"))(arg)(u)(u_ref)



def BaseTypes_decomposeComponent_Z2F770004(c: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    return (CompositeHeader(0, BaseTypes_headerOntologyOfPropertyValue_Z2F770004(c, context)), BaseTypes_cellOfPropertyValue_Z2F770004(c, context))


def BaseTypes_decomposeParameterValue_Z2F770004(c: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    return (CompositeHeader(3, BaseTypes_headerOntologyOfPropertyValue_Z2F770004(c, context)), BaseTypes_cellOfPropertyValue_Z2F770004(c, context))


def BaseTypes_decomposeFactorValue_Z2F770004(c: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    return (CompositeHeader(2, BaseTypes_headerOntologyOfPropertyValue_Z2F770004(c, context)), BaseTypes_cellOfPropertyValue_Z2F770004(c, context))


def BaseTypes_decomposeCharacteristicValue_Z2F770004(c: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    return (CompositeHeader(1, BaseTypes_headerOntologyOfPropertyValue_Z2F770004(c, context)), BaseTypes_cellOfPropertyValue_Z2F770004(c, context))


def BaseTypes_decomposeProcessInput_Z2F770004(pn: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    if LDSample.validate_source(pn, context):
        return (CompositeHeader(11, IOType(0)), CompositeCell(1, LDSample.get_name_as_string(pn, context)))

    elif LDSample.validate_material(pn, context):
        return (CompositeHeader(11, IOType(3)), CompositeCell(1, LDSample.get_name_as_string(pn, context)))

    elif LDSample.validate(pn, context):
        return (CompositeHeader(11, IOType(1)), CompositeCell(1, LDSample.get_name_as_string(pn, context)))

    elif LDFile.validate(pn, context):
        return (CompositeHeader(11, IOType(2)), CompositeCell(3, BaseTypes_decomposeFile_Z2F770004(pn, context)))

    else: 
        n: LDNode = pn
        return (CompositeHeader(11, IOType(4, n.SchemaType[0])), CompositeCell(1, LDSample.get_name_as_string(n, context)))



def BaseTypes_decomposeProcessOutput_Z2F770004(pn: LDNode, context: LDContext | None=None) -> tuple[CompositeHeader, CompositeCell]:
    if LDSample.validate_material(pn, context):
        return (CompositeHeader(12, IOType(3)), CompositeCell(1, LDSample.get_name_as_string(pn, context)))

    elif LDSample.validate(pn, context):
        return (CompositeHeader(12, IOType(1)), CompositeCell(1, LDSample.get_name_as_string(pn, context)))

    elif LDFile.validate(pn, context):
        return (CompositeHeader(12, IOType(2)), CompositeCell(3, BaseTypes_decomposeFile_Z2F770004(pn, context)))

    else: 
        n: LDNode = pn
        return (CompositeHeader(12, IOType(4, n.SchemaType[0])), CompositeCell(1, LDSample.get_name_as_string(n, context)))



def BaseTypes_composeTechnologyPlatform_ZDED3A0F(tp: OntologyAnnotation) -> str:
    match_value: dict[str, Any] | None = tp.TANInfo
    if match_value is None:
        return ("" + tp.NameText) + ""

    else: 
        return ((("" + tp.NameText) + " (") + tp.TermAccessionShort) + ")"



def BaseTypes_decomposeTechnologyPlatform_Z721C83C5(name: str) -> OntologyAnnotation:
    active_pattern_result: Any | None = ActivePatterns__007CRegex_007C__007C("^(?<value>.+) \\((?<ontology>[^(]*:[^)]*)\\)$", name)
    if active_pattern_result is not None:
        r: Any = active_pattern_result
        oa: OntologyAnnotation
        tan: str = get_item(groups(r), "ontology") or ""
        oa = OntologyAnnotation.from_term_annotation(tan)
        v: str = get_item(groups(r), "value") or ""
        return OntologyAnnotation.create(v, oa.TermSourceREF, oa.TermAccessionNumber)

    else: 
        return OntologyAnnotation.create(name)



def _expr3676() -> TypeInfo:
    return class_type("ARCtrl.Conversion.ProcessConversion", None, ProcessConversion)


class ProcessConversion:
    ...

ProcessConversion_reflection = _expr3676

def ProcessConversion_tryGetProtocolType_Z6839B9E8(pv: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> OntologyAnnotation | None:
    match_value: LDNode | None = LDLabProtocol.try_get_intended_use_as_defined_term(pv, graph, context)
    if match_value is None:
        match_value_1: str | None = LDLabProtocol.try_get_intended_use_as_string(pv, context)
        if match_value_1 is None:
            return None

        else: 
            s: str = match_value_1
            return OntologyAnnotation.create(s)


    else: 
        return BaseTypes_decomposeDefinedTerm_Z2F770004(match_value, context)



def ProcessConversion_composeProcessName(process_name_root: str, i: int) -> str:
    return ((("" + process_name_root) + "_") + str(i)) + ""


def ProcessConversion_decomposeProcessName_Z721C83C5(name: str) -> tuple[str, int | None]:
    active_pattern_result: Any | None = ActivePatterns__007CRegex_007C__007C("(?<name>.+)_(?<num>\\d+)", name)
    if active_pattern_result is not None:
        r: Any = active_pattern_result
        return (get_item(groups(r), "name") or "", parse(get_item(groups(r), "num") or "", 511, False, 32))

    else: 
        return (name, None)



def ProcessConversion_tryComponentGetter(general_i: int, value_i: int, value_header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if value_header.tag == 0:
        def Value(matrix: Any, general_i: Any=general_i, value_i: Any=value_i, value_header: Any=value_header) -> Callable[[int], LDNode]:
            def _arrow3677(i: int, matrix: Any=matrix) -> LDNode:
                c: LDNode = BaseTypes_composeComponent(value_header, get_item_from_dict(matrix, (general_i, i)))
                ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4(c, value_i)
                return c

            return _arrow3677

        return Value

    else: 
        return None



def ProcessConversion_tryParameterGetter(general_i: int, value_i: int, value_header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if value_header.tag == 3:
        def Value(matrix: Any, general_i: Any=general_i, value_i: Any=value_i, value_header: Any=value_header) -> Callable[[int], LDNode]:
            def _arrow3678(i: int, matrix: Any=matrix) -> LDNode:
                p: LDNode = BaseTypes_composeParameterValue(value_header, get_item_from_dict(matrix, (general_i, i)))
                ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4(p, value_i)
                return p

            return _arrow3678

        return Value

    else: 
        return None



def ProcessConversion_tryFactorGetter(general_i: int, value_i: int, value_header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if value_header.tag == 2:
        def Value(matrix: Any, general_i: Any=general_i, value_i: Any=value_i, value_header: Any=value_header) -> Callable[[int], LDNode]:
            def _arrow3679(i: int, matrix: Any=matrix) -> LDNode:
                f: LDNode = BaseTypes_composeFactorValue(value_header, get_item_from_dict(matrix, (general_i, i)))
                ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4(f, value_i)
                return f

            return _arrow3679

        return Value

    else: 
        return None



def ProcessConversion_tryCharacteristicGetter(general_i: int, value_i: int, value_header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if value_header.tag == 1:
        def Value(matrix: Any, general_i: Any=general_i, value_i: Any=value_i, value_header: Any=value_header) -> Callable[[int], LDNode]:
            def _arrow3680(i: int, matrix: Any=matrix) -> LDNode:
                c: LDNode = BaseTypes_composeCharacteristicValue(value_header, get_item_from_dict(matrix, (general_i, i)))
                ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4(c, value_i)
                return c

            return _arrow3680

        return Value

    else: 
        return None



def ProcessConversion_tryGetProtocolTypeGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if header.tag == 4:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], LDNode]:
            def _arrow3681(i: int, matrix: Any=matrix) -> LDNode:
                return BaseTypes_composeDefinedTerm_ZDED3A0F(get_item_from_dict(matrix, (general_i, i)).AsTerm)

            return _arrow3681

        return Value

    else: 
        return None



def ProcessConversion_tryGetProtocolREFGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], str] | None:
    if header.tag == 8:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], str]:
            def _arrow3682(i: int, matrix: Any=matrix) -> str:
                return get_item_from_dict(matrix, (general_i, i)).AsFreeText

            return _arrow3682

        return Value

    else: 
        return None



def ProcessConversion_tryGetProtocolDescriptionGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], str] | None:
    if header.tag == 5:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], str]:
            def _arrow3683(i: int, matrix: Any=matrix) -> str:
                return get_item_from_dict(matrix, (general_i, i)).AsFreeText

            return _arrow3683

        return Value

    else: 
        return None



def ProcessConversion_tryGetProtocolURIGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], str] | None:
    if header.tag == 6:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], str]:
            def _arrow3684(i: int, matrix: Any=matrix) -> str:
                return get_item_from_dict(matrix, (general_i, i)).AsFreeText

            return _arrow3684

        return Value

    else: 
        return None



def ProcessConversion_tryGetProtocolVersionGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], str] | None:
    if header.tag == 7:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], str]:
            def _arrow3685(i: int, matrix: Any=matrix) -> str:
                return get_item_from_dict(matrix, (general_i, i)).AsFreeText

            return _arrow3685

        return Value

    else: 
        return None



def ProcessConversion_tryGetInputGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if header.tag == 11:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], LDNode]:
            def _arrow3686(i: int, matrix: Any=matrix) -> LDNode:
                return BaseTypes_composeProcessInput(header, get_item_from_dict(matrix, (general_i, i)))

            return _arrow3686

        return Value

    else: 
        return None



def ProcessConversion_tryGetOutputGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if header.tag == 12:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], LDNode]:
            def _arrow3687(i: int, matrix: Any=matrix) -> LDNode:
                return BaseTypes_composeProcessOutput(header, get_item_from_dict(matrix, (general_i, i)))

            return _arrow3687

        return Value

    else: 
        return None



def ProcessConversion_tryGetCommentGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], str] | None:
    if header.tag == 14:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], str]:
            def _arrow3688(i: int, matrix: Any=matrix) -> str:
                return to_string_1(Comment(header.fields[0], get_item_from_dict(matrix, (general_i, i)).AsFreeText))

            return _arrow3688

        return Value

    else: 
        return None



def ProcessConversion_tryGetPerformerGetter(general_i: int, header: CompositeHeader) -> Callable[[Any, int], LDNode] | None:
    if header.tag == 9:
        def Value(matrix: Any, general_i: Any=general_i, header: Any=header) -> Callable[[int], LDNode]:
            def _arrow3689(i: int, matrix: Any=matrix) -> LDNode:
                performer: str = get_item_from_dict(matrix, (general_i, i)).AsFreeText
                return LDPerson.create(performer)

            return _arrow3689

        return Value

    else: 
        return None



def ProcessConversion_getProcessGetter(assay_name: str | None, study_name: str | None, process_name_root: str, headers: IEnumerable_1[CompositeHeader]) -> Callable[[Any, int], LDNode]:
    headers_1: IEnumerable_1[tuple[int, CompositeHeader]] = indexed(headers)
    def predicate(arg: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> bool:
        return arg[1].IsCvParamColumn

    value_headers: FSharpList[tuple[int, tuple[int, CompositeHeader]]] = to_list(indexed(filter(predicate, headers_1)))
    def chooser(tupled_arg: tuple[int, tuple[int, CompositeHeader]], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        _arg: tuple[int, CompositeHeader] = tupled_arg[1]
        return ProcessConversion_tryCharacteristicGetter(_arg[0], tupled_arg[0], _arg[1])

    char_getters: FSharpList[Callable[[Any, int], LDNode]] = choose(chooser, value_headers)
    def chooser_1(tupled_arg_1: tuple[int, tuple[int, CompositeHeader]], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        _arg_1: tuple[int, CompositeHeader] = tupled_arg_1[1]
        return ProcessConversion_tryFactorGetter(_arg_1[0], tupled_arg_1[0], _arg_1[1])

    factor_value_getters: FSharpList[Callable[[Any, int], LDNode]] = choose(chooser_1, value_headers)
    def chooser_2(tupled_arg_2: tuple[int, tuple[int, CompositeHeader]], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        _arg_2: tuple[int, CompositeHeader] = tupled_arg_2[1]
        return ProcessConversion_tryParameterGetter(_arg_2[0], tupled_arg_2[0], _arg_2[1])

    parameter_value_getters: FSharpList[Callable[[Any, int], LDNode]] = choose(chooser_2, value_headers)
    def chooser_3(tupled_arg_3: tuple[int, tuple[int, CompositeHeader]], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        _arg_3: tuple[int, CompositeHeader] = tupled_arg_3[1]
        return ProcessConversion_tryComponentGetter(_arg_3[0], tupled_arg_3[0], _arg_3[1])

    component_getters: FSharpList[Callable[[Any, int], LDNode]] = choose(chooser_3, value_headers)
    def chooser_4(tupled_arg_4: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        return ProcessConversion_tryGetProtocolTypeGetter(tupled_arg_4[0], tupled_arg_4[1])

    protocol_type_getter: Callable[[Any, int], LDNode] | None = try_pick(chooser_4, headers_1)
    def chooser_5(tupled_arg_5: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], str] | None:
        return ProcessConversion_tryGetProtocolREFGetter(tupled_arg_5[0], tupled_arg_5[1])

    protocol_refgetter: Callable[[Any, int], str] | None = try_pick(chooser_5, headers_1)
    def chooser_6(tupled_arg_6: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], str] | None:
        return ProcessConversion_tryGetProtocolDescriptionGetter(tupled_arg_6[0], tupled_arg_6[1])

    protocol_description_getter: Callable[[Any, int], str] | None = try_pick(chooser_6, headers_1)
    def chooser_7(tupled_arg_7: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], str] | None:
        return ProcessConversion_tryGetProtocolURIGetter(tupled_arg_7[0], tupled_arg_7[1])

    protocol_urigetter: Callable[[Any, int], str] | None = try_pick(chooser_7, headers_1)
    def chooser_8(tupled_arg_8: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], str] | None:
        return ProcessConversion_tryGetProtocolVersionGetter(tupled_arg_8[0], tupled_arg_8[1])

    protocol_version_getter: Callable[[Any, int], str] | None = try_pick(chooser_8, headers_1)
    def chooser_9(tupled_arg_9: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        return ProcessConversion_tryGetPerformerGetter(tupled_arg_9[0], tupled_arg_9[1])

    performer_getter: Callable[[Any, int], LDNode] | None = try_pick(chooser_9, headers_1)
    def chooser_10(tupled_arg_10: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], str] | None:
        return ProcessConversion_tryGetCommentGetter(tupled_arg_10[0], tupled_arg_10[1])

    comment_getters: FSharpList[Callable[[Any, int], str]] = to_list(choose_1(chooser_10, headers_1))
    input_getter_1: Callable[[Any, int], Array[LDNode]]
    def chooser_11(tupled_arg_11: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        return ProcessConversion_tryGetInputGetter(tupled_arg_11[0], tupled_arg_11[1])

    match_value: Callable[[Any, int], LDNode] | None = try_pick(chooser_11, headers_1)
    if match_value is None:
        def _arrow3691(matrix_1: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3690(i_1: int) -> Array[LDNode]:
                def mapping_1(f_1: Callable[[Any, int], LDNode]) -> LDNode:
                    return f_1(matrix_1)(i_1)

                chars_1: Array[LDNode] = list(map_1(mapping_1, char_getters))
                return ResizeArray_singleton(LDSample.create_sample(((("" + process_name_root) + "_Input_") + str(i_1)) + "", None, chars_1))

            return _arrow3690

        def _arrow3693(matrix_2: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3692(i_2: int) -> Array[LDNode]:
                return []

            return _arrow3692

        input_getter_1 = _arrow3691 if (length(char_getters) != 0) else _arrow3693

    else: 
        input_getter: Callable[[Any, int], LDNode] = match_value
        def _arrow3695(matrix: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3694(i: int) -> Array[LDNode]:
                def mapping(f: Callable[[Any, int], LDNode]) -> LDNode:
                    return f(matrix)(i)

                chars: Array[LDNode] = list(map_1(mapping, char_getters))
                input: LDNode = input_getter(matrix)(i)
                if len(chars) > 0:
                    LDSample.set_additional_properties(input, chars)

                return ResizeArray_singleton(input)

            return _arrow3694

        input_getter_1 = _arrow3695

    output_getter_1: Callable[[Any, int], Array[LDNode]]
    def chooser_12(tupled_arg_12: tuple[int, CompositeHeader], assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[Any, int], LDNode] | None:
        return ProcessConversion_tryGetOutputGetter(tupled_arg_12[0], tupled_arg_12[1])

    match_value_1: Callable[[Any, int], LDNode] | None = try_pick(chooser_12, headers_1)
    if match_value_1 is None:
        def _arrow3697(matrix_4: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3696(i_4: int) -> Array[LDNode]:
                def mapping_3(f_3: Callable[[Any, int], LDNode]) -> LDNode:
                    return f_3(matrix_4)(i_4)

                factors_1: Array[LDNode] = list(map_1(mapping_3, factor_value_getters))
                return ResizeArray_singleton(LDSample.create_sample(((("" + process_name_root) + "_Output_") + str(i_4)) + "", None, factors_1))

            return _arrow3696

        def _arrow3699(matrix_5: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3698(i_5: int) -> Array[LDNode]:
                return []

            return _arrow3698

        output_getter_1 = _arrow3697 if (length(factor_value_getters) != 0) else _arrow3699

    else: 
        output_getter: Callable[[Any, int], LDNode] = match_value_1
        def _arrow3701(matrix_3: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], Array[LDNode]]:
            def _arrow3700(i_3: int) -> Array[LDNode]:
                def mapping_2(f_2: Callable[[Any, int], LDNode]) -> LDNode:
                    return f_2(matrix_3)(i_3)

                factors: Array[LDNode] = list(map_1(mapping_2, factor_value_getters))
                output: LDNode = output_getter(matrix_3)(i_3)
                if len(factors) > 0:
                    LDSample.set_additional_properties(output, factors)

                return ResizeArray_singleton(output)

            return _arrow3700

        output_getter_1 = _arrow3701

    def _arrow3704(matrix_6: Any, assay_name: Any=assay_name, study_name: Any=study_name, process_name_root: Any=process_name_root, headers: Any=headers) -> Callable[[int], LDNode]:
        def _arrow3703(i_6: int) -> LDNode:
            def mapping_4(tuple_1: tuple[int, int]) -> int:
                return tuple_1[1]

            class ObjectExpr3702:
                @property
                def Compare(self) -> Callable[[int, int], int]:
                    return compare_primitives

            pn: str = process_name_root if ((1 + max(map_1(mapping_4, matrix_6.keys()), ObjectExpr3702())) == 1) else ProcessConversion_composeProcessName(process_name_root, i_6)
            def mapping_5(f_4: Callable[[Any, int], LDNode]) -> LDNode:
                return f_4(matrix_6)(i_6)

            paramvalues: Array[LDNode] | None = map(list, Option_fromValueWithDefault(empty(), map_2(mapping_5, parameter_value_getters)))
            def mapping_7(f_5: Callable[[Any, int], str]) -> str:
                return f_5(matrix_6)(i_6)

            comments: Array[str] | None = map(list, Option_fromValueWithDefault(empty(), map_2(mapping_7, comment_getters)))
            def mapping_9(f_6: Callable[[Any, int], LDNode]) -> LDNode:
                return f_6(matrix_6)(i_6)

            components: Array[LDNode] | None = map(list, Option_fromValueWithDefault(empty(), map_2(mapping_9, component_getters)))
            id: str = LDLabProcess.gen_id(process_name_root, assay_name, study_name) + (("_" + str(i_6)) + "")
            protocol: LDNode | None
            def mapping_11(f_7: Callable[[Any, int], str]) -> str:
                return f_7(matrix_6)(i_6)

            name: str | None = map(mapping_11, protocol_refgetter)
            protocol_id: str = LDLabProtocol.gen_id(name, process_name_root)
            def mapping_12(f_8: Callable[[Any, int], str]) -> str:
                return f_8(matrix_6)(i_6)

            def mapping_13(f_9: Callable[[Any, int], LDNode]) -> LDNode:
                return f_9(matrix_6)(i_6)

            def mapping_14(f_10: Callable[[Any, int], str]) -> str:
                return f_10(matrix_6)(i_6)

            def mapping_15(f_11: Callable[[Any, int], str]) -> str:
                return f_11(matrix_6)(i_6)

            protocol = LDLabProtocol.create(protocol_id, name, map(mapping_12, protocol_description_getter), map(mapping_13, protocol_type_getter), None, None, components, None, map(mapping_14, protocol_urigetter), map(mapping_15, protocol_version_getter))
            match_value: Array[LDNode] = input_getter_1(matrix_6)(i_6)
            match_value_1: Array[LDNode] = output_getter_1(matrix_6)(i_6)
            def mapping_16(f_12: Callable[[Any, int], LDNode]) -> LDNode:
                return f_12(matrix_6)(i_6)

            agent: LDNode | None = map(mapping_16, performer_getter)
            return LDLabProcess.create(pn, match_value, match_value_1, id, agent, protocol, paramvalues, None, comments)

        return _arrow3703

    return _arrow3704


def ProcessConversion_groupProcesses_Z27F0B586(processes: FSharpList[LDNode], graph: LDGraph | None=None, context: LDContext | None=None) -> FSharpList[tuple[str, FSharpList[LDNode]]]:
    def projection(p: LDNode, processes: Any=processes, graph: Any=graph, context: Any=context) -> str:
        match_value: str | None = LDLabProcess.try_get_name_as_string(p, context)
        match_value_1: LDNode | None = LDLabProcess.try_get_executes_lab_protocol(p, graph, context)
        (pattern_matching_result, name_3, protocol_2, name_4, name_5, protocol_3) = (None, None, None, None, None, None)
        if match_value is not None:
            if ProcessConversion_decomposeProcessName_Z721C83C5(match_value)[1] is not None:
                pattern_matching_result = 0
                name_3 = match_value

            elif match_value_1 is not None:
                def _arrow3705(__unit: None=None, p: Any=p) -> bool:
                    protocol: LDNode = match_value_1
                    return LDLabProtocol.try_get_name_as_string(protocol, context) is not None

                if _arrow3705():
                    pattern_matching_result = 1
                    protocol_2 = match_value_1

                else: 
                    def _arrow3706(__unit: None=None, p: Any=p) -> bool:
                        name_1: str = match_value
                        return name_1.find("_") >= 0

                    if _arrow3706():
                        pattern_matching_result = 2
                        name_4 = match_value

                    else: 
                        pattern_matching_result = 3
                        name_5 = match_value



            else: 
                def _arrow3707(__unit: None=None, p: Any=p) -> bool:
                    name_2: str = match_value
                    return name_2.find("_") >= 0

                if _arrow3707():
                    pattern_matching_result = 2
                    name_4 = match_value

                else: 
                    pattern_matching_result = 3
                    name_5 = match_value



        elif match_value_1 is not None:
            def _arrow3708(__unit: None=None, p: Any=p) -> bool:
                protocol_1: LDNode = match_value_1
                return LDLabProtocol.try_get_name_as_string(protocol_1, context) is not None

            if _arrow3708():
                pattern_matching_result = 1
                protocol_2 = match_value_1

            else: 
                pattern_matching_result = 4
                protocol_3 = match_value_1


        else: 
            pattern_matching_result = 5

        if pattern_matching_result == 0:
            return ProcessConversion_decomposeProcessName_Z721C83C5(name_3)[0]

        elif pattern_matching_result == 1:
            return default_arg(LDLabProtocol.try_get_name_as_string(protocol_2, context), "")

        elif pattern_matching_result == 2:
            return remove(name_4, name_4.rfind("_"))

        elif pattern_matching_result == 3:
            return name_5

        elif pattern_matching_result == 4:
            return protocol_3.Id

        elif pattern_matching_result == 5:
            return create_missing_identifier()


    class ObjectExpr3710:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow3709(x: str, y: str) -> bool:
                return x == y

            return _arrow3709

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    return List_groupBy(projection, processes, ObjectExpr3710())


def ProcessConversion_processToRows_Z6839B9E8(p: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> Array[FSharpList[tuple[CompositeHeader, CompositeCell]]]:
    def f(ppv: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> tuple[tuple[CompositeHeader, CompositeCell], int | None]:
        return (BaseTypes_decomposeParameterValue_Z2F770004(ppv, context), ColumnIndex_tryGetIndex(ppv))

    pvs: Array[tuple[tuple[CompositeHeader, CompositeCell], int | None]] = ResizeArray_map(f, LDLabProcess.get_parameter_values(p, graph, context))
    components: Array[tuple[tuple[CompositeHeader, CompositeCell], int | None]]
    match_value: LDNode | None = LDLabProcess.try_get_executes_lab_protocol(p, graph, context)
    if match_value is None:
        components = []

    else: 
        prot: LDNode = match_value
        def f_1(ppv_1: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> tuple[tuple[CompositeHeader, CompositeCell], int | None]:
            return (BaseTypes_decomposeComponent_Z2F770004(ppv_1, context), ColumnIndex_tryGetIndex(ppv_1))

        components = ResizeArray_map(f_1, LDLabProtocol.get_components(prot, graph, context))

    prot_vals: FSharpList[tuple[CompositeHeader, CompositeCell]]
    match_value_1: LDNode | None = LDLabProcess.try_get_executes_lab_protocol(p, graph, context)
    if match_value_1 is None:
        prot_vals = empty()

    else: 
        prot_1: LDNode = match_value_1
        def _arrow3719(__unit: None=None, p: Any=p, graph: Any=graph, context: Any=context) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
            def _arrow3711(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                match_value_2: str | None = LDLabProtocol.try_get_name_as_string(prot_1, context)
                if match_value_2 is None:
                    return empty_1()

                else: 
                    return singleton((CompositeHeader(8), CompositeCell(1, match_value_2)))


            def _arrow3718(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                def _arrow3712(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                    match_value_3: str | None = LDLabProtocol.try_get_description_as_string(prot_1, context)
                    if match_value_3 is None:
                        return empty_1()

                    else: 
                        return singleton((CompositeHeader(5), CompositeCell(1, match_value_3)))


                def _arrow3717(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                    def _arrow3713(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                        match_value_4: str | None = LDLabProtocol.try_get_url(prot_1, context)
                        if match_value_4 is None:
                            return empty_1()

                        else: 
                            return singleton((CompositeHeader(6), CompositeCell(1, match_value_4)))


                    def _arrow3716(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                        def _arrow3714(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                            match_value_5: str | None = LDLabProtocol.try_get_version_as_string(prot_1, context)
                            if match_value_5 is None:
                                return empty_1()

                            else: 
                                return singleton((CompositeHeader(7), CompositeCell(1, match_value_5)))


                        def _arrow3715(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                            match_value_6: OntologyAnnotation | None = ProcessConversion_tryGetProtocolType_Z6839B9E8(prot_1, graph, context)
                            if match_value_6 is None:
                                return empty_1()

                            else: 
                                return singleton((CompositeHeader(4), CompositeCell(0, match_value_6)))


                        return append(_arrow3714(), delay(_arrow3715))

                    return append(_arrow3713(), delay(_arrow3716))

                return append(_arrow3712(), delay(_arrow3717))

            return append(_arrow3711(), delay(_arrow3718))

        prot_vals = to_list(delay(_arrow3719))

    def f_2(c: str, p: Any=p, graph: Any=graph, context: Any=context) -> tuple[CompositeHeader, CompositeCell]:
        c_1: Comment = Comment.from_string(c)
        return (CompositeHeader(14, default_arg(c_1.Name, "")), CompositeCell(1, default_arg(c_1.Value, "")))

    comments: Array[tuple[CompositeHeader, CompositeCell]] = ResizeArray_map(f_2, LDLabProcess.get_disambiguating_descriptions_as_string(p, context))
    inputs: Array[LDNode] = LDLabProcess.get_objects(p, graph, context)
    outputs: Array[LDNode] = LDLabProcess.get_results(p, graph, context)
    def _arrow3720(Value: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> LDNode | None:
        return Value

    def _arrow3721(Value_1: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> LDNode | None:
        return Value_1

    def _arrow3722(Value_2: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> LDNode | None:
        return Value_2

    def _arrow3723(Value_3: LDNode, p: Any=p, graph: Any=graph, context: Any=context) -> LDNode | None:
        return Value_3

    pattern_input: tuple[Array[LDNode | None], Array[LDNode | None]] = ((ResizeArray_create(len(outputs), None), ResizeArray_map(_arrow3720, outputs))) if ((len(outputs) != 0) if (len(inputs) == 0) else False) else (((ResizeArray_map(_arrow3721, inputs), ResizeArray_create(len(inputs), None))) if ((len(outputs) == 0) if (len(inputs) != 0) else False) else ((ResizeArray_map(_arrow3722, inputs), ResizeArray_map(_arrow3723, outputs))))
    outputs_1: Array[LDNode | None] = pattern_input[1]
    inputs_1: Array[LDNode | None] = pattern_input[0]
    if (len(outputs_1) == 0) if (len(inputs_1) == 0) else False:
        def mapping(tuple_1: tuple[tuple[CompositeHeader, CompositeCell], int | None], p: Any=p, graph: Any=graph, context: Any=context) -> tuple[CompositeHeader, CompositeCell]:
            return tuple_1[0]

        def projection(arg: tuple[tuple[CompositeHeader, CompositeCell], int | None], p: Any=p, graph: Any=graph, context: Any=context) -> int:
            return default_arg(arg[1], 10000)

        def _arrow3725(__unit: None=None, p: Any=p, graph: Any=graph, context: Any=context) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
            def _arrow3724(__unit: None=None) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
                return pvs

            return append(components, delay(_arrow3724))

        class ObjectExpr3726:
            @property
            def Compare(self) -> Callable[[int, int], int]:
                return compare_primitives

        vals: FSharpList[tuple[CompositeHeader, CompositeCell]] = map_2(mapping, sort_by(projection, to_list(delay(_arrow3725)), ObjectExpr3726()))
        def _arrow3729(__unit: None=None, p: Any=p, graph: Any=graph, context: Any=context) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
            def _arrow3728(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                def _arrow3727(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                    return comments

                return append(vals, delay(_arrow3727))

            return append(prot_vals, delay(_arrow3728))

        return ResizeArray_singleton(to_list(delay(_arrow3729)))

    else: 
        def f_5(tupled_arg: tuple[LDNode | None, LDNode | None], p: Any=p, graph: Any=graph, context: Any=context) -> FSharpList[tuple[CompositeHeader, CompositeCell]]:
            i: LDNode | None = tupled_arg[0]
            o: LDNode | None = tupled_arg[1]
            chars: Array[tuple[tuple[CompositeHeader, CompositeCell], int | None]]
            if i is None:
                chars = []

            else: 
                i_1: LDNode = i
                def f_3(cv: LDNode, tupled_arg: Any=tupled_arg) -> tuple[tuple[CompositeHeader, CompositeCell], int | None]:
                    return (BaseTypes_decomposeCharacteristicValue_Z2F770004(cv, context), ColumnIndex_tryGetIndex(cv))

                chars = ResizeArray_map(f_3, LDSample.get_characteristics(i_1, graph, context))

            factors: Array[tuple[tuple[CompositeHeader, CompositeCell], int | None]]
            if o is None:
                factors = []

            else: 
                o_1: LDNode = o
                def f_4(fv: LDNode, tupled_arg: Any=tupled_arg) -> tuple[tuple[CompositeHeader, CompositeCell], int | None]:
                    return (BaseTypes_decomposeFactorValue_Z2F770004(fv, context), ColumnIndex_tryGetIndex(fv))

                factors = ResizeArray_map(f_4, LDSample.get_factors(o_1, graph, context))

            def mapping_1(tuple_3: tuple[tuple[CompositeHeader, CompositeCell], int | None], tupled_arg: Any=tupled_arg) -> tuple[CompositeHeader, CompositeCell]:
                return tuple_3[0]

            def projection_1(arg_1: tuple[tuple[CompositeHeader, CompositeCell], int | None], tupled_arg: Any=tupled_arg) -> int:
                return default_arg(arg_1[1], 10000)

            def _arrow3733(__unit: None=None, tupled_arg: Any=tupled_arg) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
                def _arrow3732(__unit: None=None) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
                    def _arrow3731(__unit: None=None) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
                        def _arrow3730(__unit: None=None) -> IEnumerable_1[tuple[tuple[CompositeHeader, CompositeCell], int | None]]:
                            return factors

                        return append(pvs, delay(_arrow3730))

                    return append(components, delay(_arrow3731))

                return append(chars, delay(_arrow3732))

            class ObjectExpr3734:
                @property
                def Compare(self) -> Callable[[int, int], int]:
                    return compare_primitives

            vals_1: FSharpList[tuple[CompositeHeader, CompositeCell]] = map_2(mapping_1, sort_by(projection_1, to_list(delay(_arrow3733)), ObjectExpr3734()))
            def _arrow3739(__unit: None=None, tupled_arg: Any=tupled_arg) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                def _arrow3738(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                    def _arrow3737(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                        def _arrow3736(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                            def _arrow3735(__unit: None=None) -> IEnumerable_1[tuple[CompositeHeader, CompositeCell]]:
                                return singleton(BaseTypes_decomposeProcessOutput_Z2F770004(value_4(o), context)) if (o is not None) else empty_1()

                            return append(comments, delay(_arrow3735))

                        return append(vals_1, delay(_arrow3736))

                    return append(prot_vals, delay(_arrow3737))

                return append(singleton(BaseTypes_decomposeProcessInput_Z2F770004(value_4(i), context)) if (i is not None) else empty_1(), delay(_arrow3738))

            return to_list(delay(_arrow3739))

        return ResizeArray_map(f_5, ResizeArray_zip(inputs_1, outputs_1))



def CompositeRow_toProtocol(table_name: str, row: IEnumerable_1[tuple[CompositeHeader, CompositeCell]]) -> LDNode:
    def folder(p: LDNode, hc: tuple[CompositeHeader, CompositeCell], table_name: Any=table_name, row: Any=row) -> LDNode:
        (pattern_matching_result, oa, v, v_1, v_2, v_3) = (None, None, None, None, None, None)
        if hc[0].tag == 4:
            if hc[1].tag == 0:
                pattern_matching_result = 0
                oa = hc[1].fields[0]

            else: 
                pattern_matching_result = 6


        elif hc[0].tag == 7:
            if hc[1].tag == 1:
                pattern_matching_result = 1
                v = hc[1].fields[0]

            else: 
                pattern_matching_result = 6


        elif hc[0].tag == 6:
            if hc[1].tag == 1:
                pattern_matching_result = 2
                v_1 = hc[1].fields[0]

            else: 
                pattern_matching_result = 6


        elif hc[0].tag == 5:
            if hc[1].tag == 1:
                pattern_matching_result = 3
                v_2 = hc[1].fields[0]

            else: 
                pattern_matching_result = 6


        elif hc[0].tag == 8:
            if hc[1].tag == 1:
                pattern_matching_result = 4
                v_3 = hc[1].fields[0]

            else: 
                pattern_matching_result = 6


        elif hc[0].tag == 0:
            if hc[1].tag == 0:
                pattern_matching_result = 5

            elif hc[1].tag == 2:
                pattern_matching_result = 5

            else: 
                pattern_matching_result = 6


        else: 
            pattern_matching_result = 6

        if pattern_matching_result == 0:
            LDLabProtocol.set_intended_use_as_defined_term(p, BaseTypes_composeDefinedTerm_ZDED3A0F(oa))

        elif pattern_matching_result == 1:
            LDLabProtocol.set_version_as_string(p, v)

        elif pattern_matching_result == 2:
            LDLabProtocol.set_url(p, v_1)

        elif pattern_matching_result == 3:
            LDLabProtocol.set_description_as_string(p, v_2)

        elif pattern_matching_result == 4:
            LDLabProtocol.set_name_as_string(p, v_3)

        elif pattern_matching_result == 5:
            new_c: Array[LDNode] = ResizeArray_appendSingleton(BaseTypes_composeComponent(hc[0], hc[1]), LDLabProtocol.get_lab_equipments(p))
            LDLabProtocol.set_lab_equipments(p, new_c)

        return p

    return fold(folder, LDLabProtocol.create(table_name, table_name), row)


def ARCtrl_ArcTable__ArcTable_fromProtocol_Static_Z6839B9E8(p: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcTable:
    name: str = LDLabProtocol.get_name_as_string(p, context)
    t: ArcTable = ArcTable.init(name)
    enumerator: Any = get_enumerator(LDLabProtocol.get_components(p, graph, context))
    try: 
        while enumerator.System_Collections_IEnumerator_MoveNext():
            c: LDNode = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
            pattern_input: tuple[CompositeHeader, CompositeCell] = BaseTypes_decomposeComponent_Z2F770004(c, context)
            t.AddColumn(pattern_input[0], singleton_1(pattern_input[1], None), ARCtrl_ROCrate_LDNode__LDNode_TryGetColumnIndex(c))

    finally: 
        dispose(enumerator)

    def mapping(d: str, p: Any=p, graph: Any=graph, context: Any=context) -> None:
        t.AddProtocolDescriptionColumn([d])

    ignore(map(mapping, LDLabProtocol.try_get_description_as_string(p, context)))
    def mapping_1(d_1: str, p: Any=p, graph: Any=graph, context: Any=context) -> None:
        t.AddProtocolVersionColumn([d_1])

    ignore(map(mapping_1, LDLabProtocol.try_get_version_as_string(p, context)))
    def mapping_2(d_2: OntologyAnnotation, p: Any=p, graph: Any=graph, context: Any=context) -> None:
        t.AddProtocolTypeColumn([d_2])

    ignore(map(mapping_2, ProcessConversion_tryGetProtocolType_Z6839B9E8(p, None, context)))
    def mapping_3(d_3: str, p: Any=p, graph: Any=graph, context: Any=context) -> None:
        t.AddProtocolUriColumn([d_3])

    ignore(map(mapping_3, LDLabProtocol.try_get_url(p, context)))
    t.AddProtocolNameColumn([name])
    return t


def ARCtrl_ArcTable__ArcTable_GetProtocols(this: ArcTable) -> FSharpList[LDNode]:
    if this.RowCount == 0:
        def _arrow3740(__unit: None=None, this: Any=this) -> LDNode:
            source: Array[CompositeHeader] = this.Headers
            def folder(p: LDNode, h: CompositeHeader) -> LDNode:
                if h.tag == 0:
                    oa: OntologyAnnotation = h.fields[0]
                    match_value: str = oa.NameText
                    match_value_1: str = oa.TermAccessionOntobeeUrl
                    new_c: Array[LDNode] = ResizeArray_appendSingleton(LDPropertyValue.create_component(match_value, "Empty Component Value", None, match_value_1), LDLabProtocol.get_lab_equipments(p))
                    LDLabProtocol.set_lab_equipments(p, new_c)

                return p

            return fold(folder, LDLabProtocol.create(create_missing_identifier(), this.Name), source)

        return singleton_2(_arrow3740())

    else: 
        def _arrow3741(i: int, this: Any=this) -> LDNode:
            row: IEnumerable_1[tuple[CompositeHeader, CompositeCell]]
            source_2: Array[CompositeCell] = this.GetRow(i, True)
            row = zip(this.Headers, source_2)
            return CompositeRow_toProtocol(this.Name, row)

        class ObjectExpr3742:
            @property
            def Equals(self) -> Callable[[LDNode, LDNode], bool]:
                return equals

            @property
            def GetHashCode(self) -> Callable[[LDNode], int]:
                return safe_hash

        return List_distinct(initialize(this.RowCount, _arrow3741), ObjectExpr3742())



def ARCtrl_ArcTable__ArcTable_GetProcesses_40457300(this: ArcTable, assay_name: str | None=None, study_name: str | None=None) -> FSharpList[LDNode]:
    if this.RowCount == 0:
        return singleton_2(LDLabProcess.create(this.Name))

    else: 
        getter: Callable[[Any, int], LDNode] = ProcessConversion_getProcessGetter(assay_name, study_name, this.Name, this.Headers)
        def _arrow3744(__unit: None=None, this: Any=this, assay_name: Any=assay_name, study_name: Any=study_name) -> IEnumerable_1[LDNode]:
            def _arrow3743(i: int) -> LDNode:
                return getter(this.Values)(i)

            return map_1(_arrow3743, range_big_int(0, 1, this.RowCount - 1))

        return to_list(delay(_arrow3744))



def ARCtrl_ArcTable__ArcTable_fromProcesses_Static_Z3575FB5F(name: str, ps: FSharpList[LDNode], graph: LDGraph | None=None, context: LDContext | None=None) -> ArcTable:
    def mapping(p: LDNode, name: Any=name, ps: Any=ps, graph: Any=graph, context: Any=context) -> FSharpList[FSharpList[tuple[CompositeHeader, CompositeCell]]]:
        return of_seq(ProcessConversion_processToRows_Z6839B9E8(p, graph, context))

    tupled_arg: tuple[Array[CompositeHeader], Any] = Unchecked_alignByHeaders(True, collect(mapping, ps))
    return ArcTable.create(name, tupled_arg[0], tupled_arg[1])


def ARCtrl_ArcTables__ArcTables_GetProcesses_40457300(this: ArcTables, assay_name: str | None=None, study_name: str | None=None) -> FSharpList[LDNode]:
    def mapping(t: ArcTable, this: Any=this, assay_name: Any=assay_name, study_name: Any=study_name) -> FSharpList[LDNode]:
        return ARCtrl_ArcTable__ArcTable_GetProcesses_40457300(t, assay_name, study_name)

    return collect(mapping, to_list(this.Tables))


def ARCtrl_ArcTables__ArcTables_fromProcesses_Static_Z27F0B586(ps: FSharpList[LDNode], graph: LDGraph | None=None, context: LDContext | None=None) -> ArcTables:
    def mapping_1(tupled_arg: tuple[str, FSharpList[LDNode]], ps: Any=ps, graph: Any=graph, context: Any=context) -> ArcTable:
        def mapping(p: LDNode, tupled_arg: Any=tupled_arg) -> FSharpList[FSharpList[tuple[CompositeHeader, CompositeCell]]]:
            return of_seq(ProcessConversion_processToRows_Z6839B9E8(p, graph, context))

        tupled_arg_1: tuple[Array[CompositeHeader], Any] = Unchecked_alignByHeaders(True, collect(mapping, tupled_arg[1]))
        return ArcTable.create(tupled_arg[0], tupled_arg_1[0], tupled_arg_1[1])

    return ArcTables(list(map_2(mapping_1, ProcessConversion_groupProcesses_Z27F0B586(ps, graph, context))))


def _expr3745() -> TypeInfo:
    return class_type("ARCtrl.Conversion.DatamapConversion", None, DatamapConversion)


class DatamapConversion:
    ...

DatamapConversion_reflection = _expr3745

def DatamapConversion_composeFragmentDescriptors_Z8923FA3(datamap: DataMap) -> Array[LDNode]:
    def f(dc: DataContext, datamap: Any=datamap) -> LDNode:
        return BaseTypes_composeFragmentDescriptor_Z4C0BEF62(dc)

    return ResizeArray_map(f, DataMap__get_DataContexts(datamap))


def DatamapConversion_decomposeFragmentDescriptors_Z6E59645F(fragment_descriptors: Array[LDNode], graph: LDGraph | None=None, context: LDContext | None=None) -> DataMap:
    def f(fd: LDNode, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> DataContext:
        return BaseTypes_decomposeFragmentDescriptor_Z6839B9E8(fd, graph, context)

    return DataMap__ctor_4E3220A7(ResizeArray_map(f, fragment_descriptors))


def _expr3746() -> TypeInfo:
    return class_type("ARCtrl.Conversion.PersonConversion", None, PersonConversion)


class PersonConversion:
    ...

PersonConversion_reflection = _expr3746

def PersonConversion_get_orcidKey(__unit: None=None) -> str:
    return "ORCID"


def PersonConversion_composeAffiliation_Z721C83C5(affiliation: str) -> LDNode:
    try: 
        match_value: FSharpResult_2[LDNode, str] = Decode_fromString(decoder_1, affiliation)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as match_value_1:
        return LDOrganization.create(affiliation)



def PersonConversion_decomposeAffiliation_Z2F770004(affiliation: LDNode, context: LDContext | None=None) -> str:
    def predicate(n: str, affiliation: Any=affiliation, context: Any=context) -> bool:
        return n != LDOrganization.name()

    if is_empty(filter(predicate, affiliation.GetPropertyNames(context))):
        return LDOrganization.get_name_as_string(affiliation, context)

    else: 
        return to_string(0, encoder(affiliation))



def PersonConversion_composeAddress_Z721C83C5(address: str) -> Any:
    try: 
        def _arrow3747(__unit: None=None) -> LDNode:
            match_value: FSharpResult_2[LDNode, str] = Decode_fromString(decoder_1, address)
            if match_value.tag == 1:
                raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

            else: 
                return match_value.fields[0]


        return _arrow3747()

    except Exception as match_value_1:
        return address



def PersonConversion_decomposeAddress_4E60E31B(address: Any=None) -> str:
    if str(type(address)) == "<class \'str\'>":
        return address

    elif isinstance(address, LDNode):
        return to_string(0, encoder(address))

    else: 
        raise Exception("Address must be a string or a Json.LDNode")



def PersonConversion_composePerson_Z64D846DC(person: Person) -> LDNode:
    given_name: str
    match_value: str | None = person.FirstName
    if match_value is None:
        raise Exception("Person must have a given name")

    else: 
        given_name = match_value

    def f(term: OntologyAnnotation, person: Any=person) -> LDNode:
        return BaseTypes_composeDefinedTerm_ZDED3A0F(term)

    job_titles: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f, person.Roles))
    def f_1(c: Comment, person: Any=person) -> str:
        return to_string_1(c)

    disambiguating_descriptions: Array[str] | None = Option_fromSeq(ResizeArray_map(f_1, person.Comments))
    def mapping(address: str, person: Any=person) -> Any:
        return PersonConversion_composeAddress_Z721C83C5(address)

    address_1: Any | None = map(mapping, person.Address)
    def mapping_1(affiliation: str, person: Any=person) -> LDNode:
        return PersonConversion_composeAffiliation_Z721C83C5(affiliation)

    affiliation_1: LDNode | None = map(mapping_1, person.Affiliation)
    return LDPerson.create(given_name, person.ORCID, None, affiliation_1, person.EMail, person.LastName, None, job_titles, person.MidInitials, address_1, disambiguating_descriptions, person.Fax, person.Phone)


def PersonConversion_decomposePerson_Z6839B9E8(person: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> Person:
    orcid: str | None = try_get_orcid_number(person.Id)
    address: str | None
    match_value: str | None = LDPerson.try_get_address_as_string(person, context)
    if match_value is None:
        match_value_1: LDNode | None = LDPerson.try_get_address_as_postal_address(person, graph, context)
        address = None if (match_value_1 is None) else PersonConversion_decomposeAddress_4E60E31B(match_value_1)

    else: 
        address = match_value

    def f(r: LDNode, person: Any=person, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposeDefinedTerm_Z2F770004(r, context)

    roles: Array[OntologyAnnotation] = ResizeArray_map(f, LDPerson.get_job_titles_as_defined_term(person, graph, context))
    def f_1(s_1: str, person: Any=person, graph: Any=graph, context: Any=context) -> Comment:
        return Comment.from_string(s_1)

    comments: Array[Comment] = ResizeArray_map(f_1, LDPerson.get_disambiguating_descriptions_as_string(person, context))
    def mapping(a_3: LDNode, person: Any=person, graph: Any=graph, context: Any=context) -> str:
        return PersonConversion_decomposeAffiliation_Z2F770004(a_3, context)

    affiliation: str | None = map(mapping, LDPerson.try_get_affiliation(person, graph, context))
    return Person.create(orcid, LDPerson.try_get_family_name_as_string(person, context), LDPerson.get_given_name_as_string(person, context), LDPerson.try_get_additional_name_as_string(person, context), LDPerson.try_get_email_as_string(person, context), LDPerson.try_get_telephone_as_string(person, context), LDPerson.try_get_fax_number_as_string(person, context), address, affiliation, roles, comments)


def _expr3748() -> TypeInfo:
    return class_type("ARCtrl.Conversion.ScholarlyArticleConversion", None, ScholarlyArticleConversion)


class ScholarlyArticleConversion:
    ...

ScholarlyArticleConversion_reflection = _expr3748

def ScholarlyArticleConversion_composeAuthor_Z721C83C5(author: str) -> LDNode:
    try: 
        match_value: FSharpResult_2[LDNode, str] = Decode_fromString(decoder_1, author)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as match_value_1:
        return LDPerson.create(author)



def ScholarlyArticleConversion_splitAuthors_Z721C83C5(a: str) -> Array[str]:
    bracket_count: int = 0
    authors: Array[str] = []
    sb: Any = StringBuilder__ctor()
    with get_enumerator(list(a)) as enumerator:
        while enumerator.System_Collections_IEnumerator_MoveNext():
            c: str = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
            if c == "{":
                bracket_count = (bracket_count + 1) or 0
                ignore(StringBuilder__Append_244C7CD6(sb, c))

            elif c == "}":
                bracket_count = (bracket_count - 1) or 0
                ignore(StringBuilder__Append_244C7CD6(sb, c))

            elif (bracket_count == 0) if (c == ",") else False:
                (authors.append(to_string_1(sb)))
                ignore(StringBuilder__Clear(sb))

            else: 
                ignore(StringBuilder__Append_244C7CD6(sb, c))

    (authors.append(to_string_1(sb)))
    return authors


def ScholarlyArticleConversion_composeAuthors_Z721C83C5(authors: str) -> Array[LDNode]:
    def mapping(author: str, authors: Any=authors) -> LDNode:
        return ScholarlyArticleConversion_composeAuthor_Z721C83C5(author)

    return list(map_1(mapping, ScholarlyArticleConversion_splitAuthors_Z721C83C5(authors)))


def ScholarlyArticleConversion_decomposeAuthor_Z2F770004(author: LDNode, context: LDContext | None=None) -> str:
    def predicate(n: str, author: Any=author, context: Any=context) -> bool:
        return n != LDPerson.given_name()

    if is_empty(filter(predicate, author.GetPropertyNames(context))):
        return LDPerson.get_given_name_as_string(author, context)

    else: 
        return to_string(0, encoder(author))



def ScholarlyArticleConversion_decomposeAuthors_1AAAE9A5(authors: Array[LDNode], context: LDContext | None=None) -> str:
    def f(a: LDNode, authors: Any=authors, context: Any=context) -> str:
        return ScholarlyArticleConversion_decomposeAuthor_Z2F770004(a, context)

    return join(",", ResizeArray_map(f, authors))


def ScholarlyArticleConversion_composeScholarlyArticle_D324A6D(publication: Publication) -> LDNode:
    title: str
    match_value: str | None = publication.Title
    if match_value is None:
        raise Exception("Publication must have a title")

    else: 
        title = match_value

    def mapping(authors: str, publication: Any=publication) -> Array[LDNode]:
        return ScholarlyArticleConversion_composeAuthors_Z721C83C5(authors)

    authors_1: Array[LDNode] | None = map(mapping, publication.Authors)
    def f(comment: Comment, publication: Any=publication) -> LDNode:
        return BaseTypes_composeComment_Z13201A7E(comment)

    comments: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f, publication.Comments))
    def _arrow3750(__unit: None=None, publication: Any=publication) -> IEnumerable_1[LDNode]:
        def _arrow3749(__unit: None=None) -> IEnumerable_1[LDNode]:
            return singleton(LDPropertyValue.create_pub_med_id(value_4(publication.PubMedID))) if ((value_4(publication.PubMedID) != "") if (publication.PubMedID is not None) else False) else empty_1()

        return append(singleton(LDPropertyValue.create_doi(value_4(publication.DOI))) if ((value_4(publication.DOI) != "") if (publication.DOI is not None) else False) else empty_1(), delay(_arrow3749))

    identifiers: Array[LDNode] = list(to_list(delay(_arrow3750)))
    def mapping_1(term: OntologyAnnotation, publication: Any=publication) -> LDNode:
        return BaseTypes_composeDefinedTerm_ZDED3A0F(term)

    status: LDNode | None = map(mapping_1, publication.Status)
    return LDScholarlyArticle.create(title, identifiers, None, authors_1, None, status, comments)


def ScholarlyArticleConversion_decomposeScholarlyArticle_Z6839B9E8(sa: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> Publication:
    title: str = LDScholarlyArticle.get_headline_as_string(sa, context)
    def mapping(a: Array[LDNode], sa: Any=sa, graph: Any=graph, context: Any=context) -> str:
        return ScholarlyArticleConversion_decomposeAuthors_1AAAE9A5(a, context)

    authors: str | None = map(mapping, Option_fromSeq(LDScholarlyArticle.get_authors(sa, graph, context)))
    def f(c: LDNode, sa: Any=sa, graph: Any=graph, context: Any=context) -> Comment:
        return BaseTypes_decomposeComment_Z2F770004(c, context)

    comments: Array[Comment] = ResizeArray_map(f, LDScholarlyArticle.get_comments(sa, graph, context))
    def mapping_1(s: LDNode, sa: Any=sa, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposeDefinedTerm_Z2F770004(s, context)

    status: OntologyAnnotation | None = map(mapping_1, LDScholarlyArticle.try_get_creative_work_status(sa, graph, context))
    identifiers: Array[LDNode] = LDScholarlyArticle.get_identifiers_as_property_value(sa, graph, context)
    doi: str | None
    def f_1(i: LDNode, sa: Any=sa, graph: Any=graph, context: Any=context) -> str | None:
        return LDPropertyValue.try_get_as_doi(i, context)

    _arg: str | None = ResizeArray_tryPick(f_1, identifiers)
    doi = LDScholarlyArticle.try_get_same_as_as_string(sa, context) if (_arg is None) else _arg
    pub_med_id: str | None
    def f_2(i_1: LDNode, sa: Any=sa, graph: Any=graph, context: Any=context) -> str | None:
        return LDPropertyValue.try_get_as_pub_med_id(i_1, context)

    _arg_1: str | None = ResizeArray_tryPick(f_2, identifiers)
    pub_med_id = LDScholarlyArticle.try_get_url_as_string(sa, context) if (_arg_1 is None) else _arg_1
    return Publication.create(pub_med_id, doi, authors, title, status, comments)


def _expr3751() -> TypeInfo:
    return class_type("ARCtrl.Conversion.AssayConversion", None, AssayConversion)


class AssayConversion:
    ...

AssayConversion_reflection = _expr3751

def AssayConversion_getDataFilesFromProcesses_6BABD1B0(processes: Array[LDNode], fragment_descriptors: Array[LDNode] | None=None, graph: LDGraph | None=None, context: LDContext | None=None) -> Array[LDNode]:
    def f(df: LDNode, processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> LDNode | None:
        return LDPropertyValue.try_get_subject_of(df, graph, context)

    def f_1(p: LDNode, processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> Array[LDNode]:
        return ResizeArray_append(LDLabProcess.get_objects_as_data(p, graph, context), LDLabProcess.get_results_as_data(p, graph, context))

    data: Array[LDNode] = ResizeArray_distinct(ResizeArray_append(ResizeArray_choose(f, default_arg(fragment_descriptors, [])), ResizeArray_collect(f_1, processes)))
    def f_2(d: LDNode, processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> bool:
        return DataAux_pathAndSelectorFromName(d.Id)[1] is None

    files: Array[LDNode] = ResizeArray_filter(f_2, data)
    def f_7(tupled_arg: tuple[str, Array[LDNode]], processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> LDNode:
        path: str = tupled_arg[0]
        fragments: Array[LDNode] = tupled_arg[1]
        file: LDNode
        def f_5(d_3: LDNode, tupled_arg: Any=tupled_arg) -> bool:
            return d_3.Id == path

        match_value: LDNode | None = ResizeArray_tryFind(f_5, files)
        if match_value is None:
            comments: Array[LDNode] | None = Option_fromSeq(LDFile.get_comments(fragments[0], graph, context))
            file = LDFile.create(path, path, comments, LDFile.try_get_disambiguating_description_as_string(fragments[0], context), LDFile.try_get_encoding_format_as_string(fragments[0], context), None, fragments[0].TryGetContext())

        else: 
            file = match_value

        LDDataset.set_has_parts(file, fragments, context)
        return file

    def f_4(d_2: LDNode, processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> str:
        return DataAux_pathAndSelectorFromName(d_2.Id)[0]

    def f_3(d_1: LDNode, processes: Any=processes, fragment_descriptors: Any=fragment_descriptors, graph: Any=graph, context: Any=context) -> bool:
        return DataAux_pathAndSelectorFromName(d_1.Id)[1] is not None

    return ResizeArray_append(files, ResizeArray_map(f_7, ResizeArray_groupBy(f_4, ResizeArray_filter(f_3, data))))


def AssayConversion_composeAssay_1501C0F8(assay: ArcAssay) -> LDNode:
    def mapping(term: OntologyAnnotation, assay: Any=assay) -> LDNode:
        return BaseTypes_composeDefinedTerm_ZDED3A0F(term)

    measurement_method: LDNode | None = map(mapping, assay.TechnologyType)
    def mapping_1(term_1: OntologyAnnotation, assay: Any=assay) -> LDNode:
        return BaseTypes_composeDefinedTerm_ZDED3A0F(term_1)

    measurement_technique: LDNode | None = map(mapping_1, assay.TechnologyPlatform)
    def mapping_2(term_2: OntologyAnnotation, assay: Any=assay) -> LDNode:
        return BaseTypes_composePropertyValueFromOA_ZDED3A0F(term_2)

    variable_measured: LDNode | None = map(mapping_2, assay.MeasurementType)
    def f(c: Person, assay: Any=assay) -> LDNode:
        return PersonConversion_composePerson_Z64D846DC(c)

    creators: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f, assay.Performers))
    process_sequence: Array[LDNode] | None = Option_fromSeq(list(ARCtrl_ArcTables__ArcTables_GetProcesses_40457300(ArcTables(assay.Tables), assay.Identifier)))
    def mapping_3(datamap: DataMap, assay: Any=assay) -> Array[LDNode]:
        return DatamapConversion_composeFragmentDescriptors_Z8923FA3(datamap)

    fragment_descriptors: Array[LDNode] | None = map(mapping_3, assay.DataMap)
    def mapping_4(ps: Array[LDNode], assay: Any=assay) -> Array[LDNode]:
        return AssayConversion_getDataFilesFromProcesses_6BABD1B0(ps, fragment_descriptors)

    data_files: Array[LDNode] | None = map(mapping_4, process_sequence)
    def _arrow3752(__unit: None=None, assay: Any=assay) -> Array[LDNode] | None:
        fds_1: Array[LDNode] = fragment_descriptors
        return fds_1

    def _arrow3753(__unit: None=None, assay: Any=assay) -> Array[LDNode] | None:
        vm_1: LDNode = variable_measured
        return ResizeArray_singleton(vm_1)

    def _arrow3754(__unit: None=None, assay: Any=assay) -> Array[LDNode] | None:
        fds: Array[LDNode] = fragment_descriptors
        vm: LDNode = variable_measured
        return ResizeArray_appendSingleton(vm, fds)

    variable_measureds: Array[LDNode] | None = (None if (fragment_descriptors is None) else _arrow3752()) if (variable_measured is None) else (_arrow3753() if (fragment_descriptors is None) else _arrow3754())
    def f_1(c_1: Comment, assay: Any=assay) -> LDNode:
        return BaseTypes_composeComment_Z13201A7E(c_1)

    comments: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f_1, assay.Comments))
    return LDDataset.create_assay(assay.Identifier, None, assay.Title, assay.Description, creators, data_files, measurement_method, measurement_technique, variable_measureds, process_sequence, comments)


def AssayConversion_decomposeAssay_Z6839B9E8(assay: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcAssay:
    def mapping(m: LDNode, assay: Any=assay, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposeDefinedTerm_Z2F770004(m, context)

    measurement_method: OntologyAnnotation | None = map(mapping, LDDataset.try_get_measurement_method_as_defined_term(assay, graph, context))
    def mapping_1(m_1: LDNode, assay: Any=assay, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposeDefinedTerm_Z2F770004(m_1, context)

    measurement_technique: OntologyAnnotation | None = map(mapping_1, LDDataset.try_get_measurement_technique_as_defined_term(assay, graph, context))
    def mapping_2(v: LDNode, assay: Any=assay, graph: Any=graph, context: Any=context) -> OntologyAnnotation:
        return BaseTypes_decomposePropertyValueToOA_Z2F770004(v, context)

    variable_measured: OntologyAnnotation | None = map(mapping_2, LDDataset.try_get_variable_measured_as_measurement_type(assay, graph, context))
    def f(c: LDNode, assay: Any=assay, graph: Any=graph, context: Any=context) -> Person:
        return PersonConversion_decomposePerson_Z6839B9E8(c, graph, context)

    perfomers: Array[Person] = ResizeArray_map(f, LDDataset.get_creators(assay, graph, context))
    data_map: DataMap | None
    v_1: DataMap = DatamapConversion_decomposeFragmentDescriptors_Z6E59645F(LDDataset.get_variable_measured_as_fragment_descriptors(assay, graph, context), graph, context)
    data_map = Option_fromValueWithDefault(DataMap_init(), v_1)
    tables: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_Z27F0B586(of_seq(LDDataset.get_abouts_as_lab_process(assay, graph, context)), graph, context)
    def f_1(c_1: LDNode, assay: Any=assay, graph: Any=graph, context: Any=context) -> Comment:
        return BaseTypes_decomposeComment_Z2F770004(c_1, context)

    comments: Array[Comment] = ResizeArray_map(f_1, LDDataset.get_comments(assay, graph, context))
    return ArcAssay.create(LDDataset.get_identifier_as_string(assay, context), LDDataset.try_get_name_as_string(assay, context), LDDataset.try_get_description_as_string(assay, context), variable_measured, measurement_method, measurement_technique, tables.Tables, data_map, perfomers, comments)


def _expr3755() -> TypeInfo:
    return class_type("ARCtrl.Conversion.StudyConversion", None, StudyConversion)


class StudyConversion:
    ...

StudyConversion_reflection = _expr3755

def StudyConversion_composeStudy_1680536E(study: ArcStudy) -> LDNode:
    def _arrow3756(s: str, study: Any=study) -> Any | None:
        return DateTime_tryFromString(s)

    date_created: Any | None = bind(_arrow3756, study.SubmissionDate)
    def _arrow3757(s_1: str, study: Any=study) -> Any | None:
        return DateTime_tryFromString(s_1)

    date_published: Any | None = bind(_arrow3757, study.PublicReleaseDate)
    date_modified: Any = now()
    def f(p: Publication, study: Any=study) -> LDNode:
        return ScholarlyArticleConversion_composeScholarlyArticle_D324A6D(p)

    publications: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f, study.Publications))
    def f_1(c: Person, study: Any=study) -> LDNode:
        return PersonConversion_composePerson_Z64D846DC(c)

    creators: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f_1, study.Contacts))
    process_sequence: Array[LDNode] | None = Option_fromSeq(list(ARCtrl_ArcTables__ArcTables_GetProcesses_40457300(ArcTables(study.Tables), None, study.Identifier)))
    def mapping(datamap: DataMap, study: Any=study) -> Array[LDNode]:
        return DatamapConversion_composeFragmentDescriptors_Z8923FA3(datamap)

    fragment_descriptors: Array[LDNode] | None = map(mapping, study.DataMap)
    def mapping_1(ps: Array[LDNode], study: Any=study) -> Array[LDNode]:
        return AssayConversion_getDataFilesFromProcesses_6BABD1B0(ps, fragment_descriptors)

    data_files: Array[LDNode] | None = map(mapping_1, process_sequence)
    def f_2(c_1: Comment, study: Any=study) -> LDNode:
        return BaseTypes_composeComment_Z13201A7E(c_1)

    comments: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f_2, study.Comments))
    return LDDataset.create_study(study.Identifier, None, creators, date_created, date_published, date_modified, study.Description, data_files, study.Title, publications, fragment_descriptors, comments, None, process_sequence)


def StudyConversion_decomposeStudy_Z6839B9E8(study: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcStudy:
    def _arrow3758(d: Any, study: Any=study, graph: Any=graph, context: Any=context) -> str:
        return DateTime_toString(d)

    date_created: str | None = map(_arrow3758, LDDataset.try_get_date_created_as_date_time(study, context))
    def _arrow3759(d_1: Any, study: Any=study, graph: Any=graph, context: Any=context) -> str:
        return DateTime_toString(d_1)

    date_published: str | None = map(_arrow3759, LDDataset.try_get_date_published_as_date_time(study, context))
    def f(p: LDNode, study: Any=study, graph: Any=graph, context: Any=context) -> Publication:
        return ScholarlyArticleConversion_decomposeScholarlyArticle_Z6839B9E8(p, graph, context)

    publications: Array[Publication] = ResizeArray_map(f, LDDataset.get_citations(study, graph, context))
    def f_1(c: LDNode, study: Any=study, graph: Any=graph, context: Any=context) -> Person:
        return PersonConversion_decomposePerson_Z6839B9E8(c, graph, context)

    creators: Array[Person] = ResizeArray_map(f_1, LDDataset.get_creators(study, graph, context))
    data_map: DataMap | None
    v: DataMap = DatamapConversion_decomposeFragmentDescriptors_Z6E59645F(LDDataset.get_variable_measured_as_fragment_descriptors(study, graph, context), graph, context)
    data_map = Option_fromValueWithDefault(DataMap_init(), v)
    tables: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_Z27F0B586(of_seq(LDDataset.get_abouts_as_lab_process(study, graph, context)), graph, context)
    def f_2(c_1: LDNode, study: Any=study, graph: Any=graph, context: Any=context) -> Comment:
        return BaseTypes_decomposeComment_Z2F770004(c_1, context)

    comments: Array[Comment] = ResizeArray_map(f_2, LDDataset.get_comments(study, graph, context))
    return ArcStudy.create(LDDataset.get_identifier_as_string(study, context), LDDataset.try_get_name_as_string(study, context), LDDataset.try_get_description_as_string(study, context), date_created, date_published, publications, creators, None, tables.Tables, data_map, None, comments)


def _expr3760() -> TypeInfo:
    return class_type("ARCtrl.Conversion.InvestigationConversion", None, InvestigationConversion)


class InvestigationConversion:
    ...

InvestigationConversion_reflection = _expr3760

def InvestigationConversion_composeInvestigation_Z720BD3FF(investigation: ArcInvestigation) -> LDNode:
    name: str
    match_value: str | None = investigation.Title
    if match_value is None:
        raise Exception("Investigation must have a title")

    else: 
        name = match_value

    def _arrow3761(s: str, investigation: Any=investigation) -> Any | None:
        return DateTime_tryFromString(s)

    date_created: Any | None = bind(_arrow3761, investigation.SubmissionDate)
    def _arrow3762(s_1: str, investigation: Any=investigation) -> Any | None:
        return DateTime_tryFromString(s_1)

    date_published: Any = default_arg(bind(_arrow3762, investigation.PublicReleaseDate), now())
    def f(p: Publication, investigation: Any=investigation) -> LDNode:
        return ScholarlyArticleConversion_composeScholarlyArticle_D324A6D(p)

    publications: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f, investigation.Publications))
    def f_1(c: Person, investigation: Any=investigation) -> LDNode:
        return PersonConversion_composePerson_Z64D846DC(c)

    creators: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f_1, investigation.Contacts))
    def f_2(c_1: Comment, investigation: Any=investigation) -> LDNode:
        return BaseTypes_composeComment_Z13201A7E(c_1)

    comments: Array[LDNode] | None = Option_fromSeq(ResizeArray_map(f_2, investigation.Comments))
    def _arrow3763(__unit: None=None, investigation: Any=investigation) -> Array[LDNode]:
        b: Array[LDNode] = ResizeArray_map(AssayConversion_composeAssay_1501C0F8, investigation.Assays)
        return ResizeArray_append(ResizeArray_map(StudyConversion_composeStudy_1680536E, investigation.Studies), b)

    has_parts: Array[LDNode] | None = Option_fromSeq(_arrow3763())
    mentions: Array[LDNode] | None = Option_fromSeq([])
    return LDDataset.create_investigation(investigation.Identifier, name, None, creators, date_created, date_published, None, investigation.Description, has_parts, publications, comments, mentions)


def InvestigationConversion_decomposeInvestigation_Z6839B9E8(investigation: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcInvestigation:
    title: str | None
    match_value: str | None = LDDataset.try_get_name_as_string(investigation, context)
    title = LDDataset.try_get_headline_as_string(investigation, context) if (match_value is None) else match_value
    def _arrow3764(d: Any, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> str:
        return DateTime_toString(d)

    date_created: str | None = map(_arrow3764, LDDataset.try_get_date_created_as_date_time(investigation, context))
    def _arrow3765(d_1: Any, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> str:
        return DateTime_toString(d_1)

    date_published: str | None = map(_arrow3765, LDDataset.try_get_date_published_as_date_time(investigation, context))
    def f(p: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> Publication:
        return ScholarlyArticleConversion_decomposeScholarlyArticle_Z6839B9E8(p, graph, context)

    publications: Array[Publication] = ResizeArray_map(f, LDDataset.get_citations(investigation, graph, context))
    def f_1(c: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> Person:
        return PersonConversion_decomposePerson_Z6839B9E8(c, graph, context)

    creators: Array[Person] = ResizeArray_map(f_1, LDDataset.get_creators(investigation, graph, context))
    datasets: Array[LDNode] = LDDataset.get_has_parts_as_dataset(investigation, graph, context)
    def f_3(d_3: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> ArcStudy:
        return StudyConversion_decomposeStudy_Z6839B9E8(d_3, graph, context)

    def f_2(d_2: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> bool:
        return LDDataset.validate_study(d_2, context)

    studies: Array[ArcStudy] = ResizeArray_map(f_3, ResizeArray_filter(f_2, datasets))
    def f_5(d_5: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> ArcAssay:
        return AssayConversion_decomposeAssay_Z6839B9E8(d_5, graph, context)

    def f_4(d_4: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> bool:
        return LDDataset.validate_assay(d_4, context)

    assays: Array[ArcAssay] = ResizeArray_map(f_5, ResizeArray_filter(f_4, datasets))
    def f_6(c_1: LDNode, investigation: Any=investigation, graph: Any=graph, context: Any=context) -> Comment:
        return BaseTypes_decomposeComment_Z2F770004(c_1, context)

    comments: Array[Comment] = ResizeArray_map(f_6, LDDataset.get_comments(investigation, graph, context))
    return ArcInvestigation.create(LDDataset.get_identifier_as_string(investigation, context), title, LDDataset.try_get_description_as_string(investigation, context), date_created, date_published, None, publications, creators, assays, studies, None, None, None, comments)


def ARCtrl_ArcAssay__ArcAssay_ToROCrateAssay(this: ArcAssay) -> LDNode:
    return AssayConversion_composeAssay_1501C0F8(this)


def ARCtrl_ArcAssay__ArcAssay_fromROCrateAssay_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcAssay:
    return AssayConversion_decomposeAssay_Z6839B9E8(a, graph, context)


def ARCtrl_ArcStudy__ArcStudy_ToROCrateStudy(this: ArcStudy) -> LDNode:
    return StudyConversion_composeStudy_1680536E(this)


def ARCtrl_ArcStudy__ArcStudy_fromROCrateStudy_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcStudy:
    return StudyConversion_decomposeStudy_Z6839B9E8(a, graph, context)


def ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation(this: ArcInvestigation) -> LDNode:
    return InvestigationConversion_composeInvestigation_Z720BD3FF(this)


def ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcInvestigation:
    return InvestigationConversion_decomposeInvestigation_Z6839B9E8(a, graph, context)


def _expr3766() -> TypeInfo:
    return class_type("ARCtrl.Conversion.TypeExtensions.Conversion", None, TypeExtensions_Conversion)


class TypeExtensions_Conversion:
    @staticmethod
    def arc_assay_to_dataset(a: ArcAssay) -> LDNode:
        return ARCtrl_ArcAssay__ArcAssay_ToROCrateAssay(a)

    @staticmethod
    def dataset_to_arc_assay(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcAssay:
        return ARCtrl_ArcAssay__ArcAssay_fromROCrateAssay_Static_Z6839B9E8(a, graph, context)

    @staticmethod
    def arc_study_to_dataset(a: ArcStudy) -> LDNode:
        return ARCtrl_ArcStudy__ArcStudy_ToROCrateStudy(a)

    @staticmethod
    def dataset_to_arc_study(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcStudy:
        return ARCtrl_ArcStudy__ArcStudy_fromROCrateStudy_Static_Z6839B9E8(a, graph, context)

    @staticmethod
    def arc_investigation_to_dataset(a: ArcInvestigation) -> LDNode:
        return ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation(a)

    @staticmethod
    def dataset_to_arc_investigation(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcInvestigation:
        return ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8(a, graph, context)


TypeExtensions_Conversion_reflection = _expr3766

def ARCtrl_ROCrate_Dataset__Dataset_toArcAssay_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcAssay:
    return AssayConversion_decomposeAssay_Z6839B9E8(a, graph, context)


def ARCtrl_ROCrate_Dataset__Dataset_fromArcAssay_Static_1501C0F8(a: ArcAssay) -> LDNode:
    return AssayConversion_composeAssay_1501C0F8(a)


def ARCtrl_ROCrate_Dataset__Dataset_toArcStudy_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcStudy:
    return StudyConversion_decomposeStudy_Z6839B9E8(a, graph, context)


def ARCtrl_ROCrate_Dataset__Dataset_fromArcStudy_Static_1680536E(a: ArcStudy) -> LDNode:
    return StudyConversion_composeStudy_1680536E(a)


def ARCtrl_ROCrate_Dataset__Dataset_toArcInvestigation_Static_Z6839B9E8(a: LDNode, graph: LDGraph | None=None, context: LDContext | None=None) -> ArcInvestigation:
    return InvestigationConversion_decomposeInvestigation_Z6839B9E8(a, graph, context)


def ARCtrl_ROCrate_Dataset__Dataset_fromArcInvestigation_Static_Z720BD3FF(a: ArcInvestigation) -> LDNode:
    return InvestigationConversion_composeInvestigation_Z720BD3FF(a)


__all__ = ["DateTime_tryFromString", "DateTime_toString", "ColumnIndex_tryInt", "ColumnIndex_orderName", "ColumnIndex_tryGetIndex", "ColumnIndex_setIndex", "ARCtrl_ROCrate_LDNode__LDNode_GetColumnIndex", "ARCtrl_ROCrate_LDNode__LDNode_TryGetColumnIndex", "ARCtrl_ROCrate_LDNode__LDNode_SetColumnIndex_Z524259A4", "BaseTypes_reflection", "BaseTypes_composeComment_Z13201A7E", "BaseTypes_decomposeComment_Z2F770004", "BaseTypes_ontologyTermFromNameAndID_40457300", "BaseTypes_tryOntologyTermFromNameAndID_40457300", "BaseTypes_composeDefinedTerm_ZDED3A0F", "BaseTypes_decomposeDefinedTerm_Z2F770004", "BaseTypes_composePropertyValueFromOA_ZDED3A0F", "BaseTypes_decomposePropertyValueToOA_Z2F770004", "BaseTypes_valuesOfCell_Z436420FE", "BaseTypes_termOfHeader_6CAF647B", "BaseTypes_composeComponent", "BaseTypes_composeParameterValue", "BaseTypes_composeFactorValue", "BaseTypes_composeCharacteristicValue", "BaseTypes_composeFreetextMaterialName", "BaseTypes_composeFile_3A03A101", "BaseTypes_decomposeFile_Z2F770004", "BaseTypes_composeFragmentDescriptor_Z4C0BEF62", "BaseTypes_decomposeFragmentDescriptor_Z6839B9E8", "BaseTypes_composeProcessInput", "BaseTypes_composeProcessOutput", "BaseTypes_headerOntologyOfPropertyValue_Z2F770004", "BaseTypes_cellOfPropertyValue_Z2F770004", "BaseTypes_decomposeComponent_Z2F770004", "BaseTypes_decomposeParameterValue_Z2F770004", "BaseTypes_decomposeFactorValue_Z2F770004", "BaseTypes_decomposeCharacteristicValue_Z2F770004", "BaseTypes_decomposeProcessInput_Z2F770004", "BaseTypes_decomposeProcessOutput_Z2F770004", "BaseTypes_composeTechnologyPlatform_ZDED3A0F", "BaseTypes_decomposeTechnologyPlatform_Z721C83C5", "ProcessConversion_reflection", "ProcessConversion_tryGetProtocolType_Z6839B9E8", "ProcessConversion_composeProcessName", "ProcessConversion_decomposeProcessName_Z721C83C5", "ProcessConversion_tryComponentGetter", "ProcessConversion_tryParameterGetter", "ProcessConversion_tryFactorGetter", "ProcessConversion_tryCharacteristicGetter", "ProcessConversion_tryGetProtocolTypeGetter", "ProcessConversion_tryGetProtocolREFGetter", "ProcessConversion_tryGetProtocolDescriptionGetter", "ProcessConversion_tryGetProtocolURIGetter", "ProcessConversion_tryGetProtocolVersionGetter", "ProcessConversion_tryGetInputGetter", "ProcessConversion_tryGetOutputGetter", "ProcessConversion_tryGetCommentGetter", "ProcessConversion_tryGetPerformerGetter", "ProcessConversion_getProcessGetter", "ProcessConversion_groupProcesses_Z27F0B586", "ProcessConversion_processToRows_Z6839B9E8", "CompositeRow_toProtocol", "ARCtrl_ArcTable__ArcTable_fromProtocol_Static_Z6839B9E8", "ARCtrl_ArcTable__ArcTable_GetProtocols", "ARCtrl_ArcTable__ArcTable_GetProcesses_40457300", "ARCtrl_ArcTable__ArcTable_fromProcesses_Static_Z3575FB5F", "ARCtrl_ArcTables__ArcTables_GetProcesses_40457300", "ARCtrl_ArcTables__ArcTables_fromProcesses_Static_Z27F0B586", "DatamapConversion_reflection", "DatamapConversion_composeFragmentDescriptors_Z8923FA3", "DatamapConversion_decomposeFragmentDescriptors_Z6E59645F", "PersonConversion_reflection", "PersonConversion_get_orcidKey", "PersonConversion_composeAffiliation_Z721C83C5", "PersonConversion_decomposeAffiliation_Z2F770004", "PersonConversion_composeAddress_Z721C83C5", "PersonConversion_decomposeAddress_4E60E31B", "PersonConversion_composePerson_Z64D846DC", "PersonConversion_decomposePerson_Z6839B9E8", "ScholarlyArticleConversion_reflection", "ScholarlyArticleConversion_composeAuthor_Z721C83C5", "ScholarlyArticleConversion_splitAuthors_Z721C83C5", "ScholarlyArticleConversion_composeAuthors_Z721C83C5", "ScholarlyArticleConversion_decomposeAuthor_Z2F770004", "ScholarlyArticleConversion_decomposeAuthors_1AAAE9A5", "ScholarlyArticleConversion_composeScholarlyArticle_D324A6D", "ScholarlyArticleConversion_decomposeScholarlyArticle_Z6839B9E8", "AssayConversion_reflection", "AssayConversion_getDataFilesFromProcesses_6BABD1B0", "AssayConversion_composeAssay_1501C0F8", "AssayConversion_decomposeAssay_Z6839B9E8", "StudyConversion_reflection", "StudyConversion_composeStudy_1680536E", "StudyConversion_decomposeStudy_Z6839B9E8", "InvestigationConversion_reflection", "InvestigationConversion_composeInvestigation_Z720BD3FF", "InvestigationConversion_decomposeInvestigation_Z6839B9E8", "ARCtrl_ArcAssay__ArcAssay_ToROCrateAssay", "ARCtrl_ArcAssay__ArcAssay_fromROCrateAssay_Static_Z6839B9E8", "ARCtrl_ArcStudy__ArcStudy_ToROCrateStudy", "ARCtrl_ArcStudy__ArcStudy_fromROCrateStudy_Static_Z6839B9E8", "ARCtrl_ArcInvestigation__ArcInvestigation_ToROCrateInvestigation", "ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateInvestigation_Static_Z6839B9E8", "TypeExtensions_Conversion_reflection", "ARCtrl_ROCrate_Dataset__Dataset_toArcAssay_Static_Z6839B9E8", "ARCtrl_ROCrate_Dataset__Dataset_fromArcAssay_Static_1501C0F8", "ARCtrl_ROCrate_Dataset__Dataset_toArcStudy_Static_Z6839B9E8", "ARCtrl_ROCrate_Dataset__Dataset_fromArcStudy_Static_1680536E", "ARCtrl_ROCrate_Dataset__Dataset_toArcInvestigation_Static_Z6839B9E8", "ARCtrl_ROCrate_Dataset__Dataset_fromArcInvestigation_Static_Z720BD3FF"]

