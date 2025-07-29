from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (of_array, FSharpList, map as map_1, empty, of_seq, cons, reverse)
from ...fable_modules.fable_library.map_util import add_to_dict
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.seq import map
from ...fable_modules.fable_library.seq2 import List_distinct
from ...fable_modules.fable_library.string_ import (starts_with_exact, join)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import (string_hash, IEnumerable_1, IEnumerator)
from ...Core.arc_types import (ArcWorkflow_make, ArcWorkflow, ArcWorkflow__get_Identifier, ArcWorkflow__get_WorkflowType, ArcWorkflow__get_Parameters, ArcWorkflow__get_Components, ArcWorkflow__get_SubWorkflowIdentifiers, ArcWorkflow__get_Title, ArcWorkflow__get_Description, ArcWorkflow__get_URI, ArcWorkflow__get_Version, ArcWorkflow__get_Comments)
from ...Core.comment import (Comment, Remark)
from ...Core.Helper.collections_ import (Option_fromValueWithDefault, ResizeArray_iter)
from ...Core.Helper.identifier import (create_missing_identifier, Workflow_tryIdentifierFromFileName, Workflow_fileNameFromIdentifier)
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.component import Component
from ...Core.Process.protocol_parameter import ProtocolParameter
from .comment import (Comment_fromString, Comment_toString)
from .conversions import (ProtocolParameter_fromAggregatedStrings, Component_fromAggregatedStrings, ProtocolParameter_toAggregatedStrings, Component_toAggregatedStrings)
from .sparse_table import (SparseTable__TryGetValueDefault_5BAE6133, SparseTable__TryGetValue_11FD62A8, SparseTable, SparseTable_Create_Z2192E64B, SparseTable_FromRows_Z5579EC29, SparseTable_ToRows_759CAFC1)

identifier_label: str = "Identifier"

title_label: str = "Title"

description_label: str = "Description"

workflow_type_label: str = "Type"

type_term_accession_number_label: str = "Type Term Accession Number"

type_term_source_reflabel: str = "Type Term Source REF"

sub_workflow_identifiers_label: str = "Sub Workflow Identifiers"

uri_label: str = "URI"

version_label: str = "Version"

parameters_name_label: str = "Parameters Name"

parameters_term_accession_number_label: str = "Parameters Term Accession Number"

parameters_term_source_reflabel: str = "Parameters Term Source REF"

components_name_label: str = "Components Name"

components_type_label: str = "Components Type"

components_type_term_accession_number_label: str = "Components Type Term Accession Number"

components_type_term_source_reflabel: str = "Components Type Term Source REF"

file_name_label: str = "File Name"

labels: FSharpList[str] = of_array([identifier_label, title_label, description_label, workflow_type_label, type_term_accession_number_label, type_term_source_reflabel, sub_workflow_identifiers_label, uri_label, version_label, parameters_name_label, parameters_term_accession_number_label, parameters_term_source_reflabel, components_name_label, components_type_label, components_type_term_accession_number_label, components_type_term_source_reflabel, file_name_label])

def from_string(identifier: str | None, title: str | None, description: str | None, workflow_type: str | None, workflow_type_term_accession_number: str | None, workflow_type_term_source_ref: str | None, subworkflow_identifiers: str | None, uri: str | None, version: str | None, parameters_name: str, parameters_term_accession_number: str, parameters_term_source_ref: str, components_name: str, components_type: str, components_type_term_accession_number: str, components_type_term_source_ref: str, file_name: str | None, comments: Array[Comment]) -> ArcWorkflow:
    subworkflow_identifiers_2: Array[str]
    if subworkflow_identifiers is None:
        subworkflow_identifiers_2 = []

    else: 
        subworkflow_identifiers_1: str = subworkflow_identifiers
        def mapping(s: str, identifier: Any=identifier, title: Any=title, description: Any=description, workflow_type: Any=workflow_type, workflow_type_term_accession_number: Any=workflow_type_term_accession_number, workflow_type_term_source_ref: Any=workflow_type_term_source_ref, subworkflow_identifiers: Any=subworkflow_identifiers, uri: Any=uri, version: Any=version, parameters_name: Any=parameters_name, parameters_term_accession_number: Any=parameters_term_accession_number, parameters_term_source_ref: Any=parameters_term_source_ref, components_name: Any=components_name, components_type: Any=components_type, components_type_term_accession_number: Any=components_type_term_accession_number, components_type_term_source_ref: Any=components_type_term_source_ref, file_name: Any=file_name, comments: Any=comments) -> str:
            return s.strip()

        subworkflow_identifiers_2 = list(map(mapping, subworkflow_identifiers_1.split(";")))

    workflow_type_1: OntologyAnnotation | None
    v: OntologyAnnotation = OntologyAnnotation.create(workflow_type, workflow_type_term_source_ref, workflow_type_term_accession_number)
    workflow_type_1 = Option_fromValueWithDefault(OntologyAnnotation(), v)
    parameters: Array[ProtocolParameter] = list(ProtocolParameter_fromAggregatedStrings(";", parameters_name, parameters_term_source_ref, parameters_term_accession_number))
    components: Array[Component] = list(Component_fromAggregatedStrings(";", components_name, components_type, components_type_term_source_ref, components_type_term_accession_number))
    def _arrow1206(__unit: None=None, identifier: Any=identifier, title: Any=title, description: Any=description, workflow_type: Any=workflow_type, workflow_type_term_accession_number: Any=workflow_type_term_accession_number, workflow_type_term_source_ref: Any=workflow_type_term_source_ref, subworkflow_identifiers: Any=subworkflow_identifiers, uri: Any=uri, version: Any=version, parameters_name: Any=parameters_name, parameters_term_accession_number: Any=parameters_term_accession_number, parameters_term_source_ref: Any=parameters_term_source_ref, components_name: Any=components_name, components_type: Any=components_type, components_type_term_accession_number: Any=components_type_term_accession_number, components_type_term_source_ref: Any=components_type_term_source_ref, file_name: Any=file_name, comments: Any=comments) -> str:
        match_value: str | None = Workflow_tryIdentifierFromFileName(file_name)
        return match_value if (match_value is not None) else create_missing_identifier()

    return ArcWorkflow_make((create_missing_identifier() if (file_name is None) else _arrow1206()) if (identifier is None) else identifier, title, description, workflow_type_1, uri, version, subworkflow_identifiers_2, parameters, components, None, [], comments)


def from_sparse_table(matrix: SparseTable) -> ArcWorkflow:
    def mapping(k: str, matrix: Any=matrix) -> Comment:
        return Comment_fromString(k, SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (k, 0)))

    comments: FSharpList[Comment] = map_1(mapping, matrix.CommentKeys)
    return from_string(SparseTable__TryGetValue_11FD62A8(matrix, (identifier_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (title_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (description_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (workflow_type_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (type_term_accession_number_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (type_term_source_reflabel, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (sub_workflow_identifiers_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (uri_label, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (version_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (parameters_name_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (parameters_term_accession_number_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (parameters_term_source_reflabel, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (components_name_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (components_type_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (components_type_term_accession_number_label, 0)), SparseTable__TryGetValueDefault_5BAE6133(matrix, "", (components_type_term_source_reflabel, 0)), SparseTable__TryGetValue_11FD62A8(matrix, (file_name_label, 0)), list(comments))


def to_sparse_table(workflow: ArcWorkflow) -> SparseTable:
    matrix: SparseTable = SparseTable_Create_Z2192E64B(None, labels, None, 2)
    comment_keys: FSharpList[str] = empty()
    pattern_input: tuple[str, str] = (("", "")) if starts_with_exact(ArcWorkflow__get_Identifier(workflow), "MISSING_IDENTIFIER_") else ((ArcWorkflow__get_Identifier(workflow), Workflow_fileNameFromIdentifier(ArcWorkflow__get_Identifier(workflow))))
    wt: dict[str, Any]
    tt: OntologyAnnotation = default_arg(ArcWorkflow__get_WorkflowType(workflow), OntologyAnnotation())
    wt = OntologyAnnotation.to_string_object(tt, True)
    p_agg: dict[str, Any] = ProtocolParameter_toAggregatedStrings(";", of_seq(ArcWorkflow__get_Parameters(workflow)))
    c_agg: dict[str, Any] = Component_toAggregatedStrings(";", of_seq(ArcWorkflow__get_Components(workflow)))
    sub_workflows_agg: str = join(";", ArcWorkflow__get_SubWorkflowIdentifiers(workflow))
    add_to_dict(matrix.Matrix, (identifier_label, 1), pattern_input[0])
    add_to_dict(matrix.Matrix, (title_label, 1), default_arg(ArcWorkflow__get_Title(workflow), ""))
    add_to_dict(matrix.Matrix, (description_label, 1), default_arg(ArcWorkflow__get_Description(workflow), ""))
    add_to_dict(matrix.Matrix, (workflow_type_label, 1), wt["TermName"])
    add_to_dict(matrix.Matrix, (type_term_accession_number_label, 1), wt["TermAccessionNumber"])
    add_to_dict(matrix.Matrix, (type_term_source_reflabel, 1), wt["TermSourceREF"])
    add_to_dict(matrix.Matrix, (sub_workflow_identifiers_label, 1), sub_workflows_agg)
    add_to_dict(matrix.Matrix, (uri_label, 1), default_arg(ArcWorkflow__get_URI(workflow), ""))
    add_to_dict(matrix.Matrix, (version_label, 1), default_arg(ArcWorkflow__get_Version(workflow), ""))
    add_to_dict(matrix.Matrix, (parameters_name_label, 1), p_agg["TermNameAgg"])
    add_to_dict(matrix.Matrix, (parameters_term_accession_number_label, 1), p_agg["TermAccessionNumberAgg"])
    add_to_dict(matrix.Matrix, (parameters_term_source_reflabel, 1), p_agg["TermSourceREFAgg"])
    add_to_dict(matrix.Matrix, (components_name_label, 1), c_agg["NameAgg"])
    add_to_dict(matrix.Matrix, (components_type_label, 1), c_agg["TermNameAgg"])
    add_to_dict(matrix.Matrix, (components_type_term_accession_number_label, 1), c_agg["TermAccessionNumberAgg"])
    add_to_dict(matrix.Matrix, (components_type_term_source_reflabel, 1), c_agg["TermSourceREFAgg"])
    add_to_dict(matrix.Matrix, (file_name_label, 1), pattern_input[1])
    def f(comment: Comment, workflow: Any=workflow) -> None:
        nonlocal comment_keys
        pattern_input_1: tuple[str, str] = Comment_toString(comment)
        n: str = pattern_input_1[0]
        comment_keys = cons(n, comment_keys)
        add_to_dict(matrix.Matrix, (n, 1), pattern_input_1[1])

    ResizeArray_iter(f, ArcWorkflow__get_Comments(workflow))
    class ObjectExpr1209:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1208(x: str, y: str) -> bool:
                return x == y

            return _arrow1208

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    return SparseTable(matrix.Matrix, matrix.Keys, reverse(List_distinct(comment_keys, ObjectExpr1209())), matrix.ColumnCount)


def from_rows(line_number: int, rows: IEnumerator[IEnumerable_1[tuple[int, str]]]) -> tuple[str | None, int, FSharpList[Remark], ArcWorkflow]:
    tupled_arg: tuple[str | None, int, FSharpList[Remark], SparseTable] = SparseTable_FromRows_Z5579EC29(rows, labels, line_number, "Workflow")
    return (tupled_arg[0], tupled_arg[1], tupled_arg[2], from_sparse_table(tupled_arg[3]))


def to_rows(workflow: ArcWorkflow) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
    return SparseTable_ToRows_759CAFC1(to_sparse_table(workflow), "Workflow")


__all__ = ["identifier_label", "title_label", "description_label", "workflow_type_label", "type_term_accession_number_label", "type_term_source_reflabel", "sub_workflow_identifiers_label", "uri_label", "version_label", "parameters_name_label", "parameters_term_accession_number_label", "parameters_term_source_reflabel", "components_name_label", "components_type_label", "components_type_term_accession_number_label", "components_type_term_source_reflabel", "file_name_label", "labels", "from_string", "from_sparse_table", "to_sparse_table", "from_rows", "to_rows"]

