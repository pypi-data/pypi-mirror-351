from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.array_ import equals_with
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import safe_hash
from ..Core.data_map import (DataMap, DataMap__set_StaticHash_Z524259A4)
from ..Core.Helper.identifier import (Assay_datamapFileNameFromIdentifier, Study_datamapFileNameFromIdentifier, Workflow_datamapFileNameFromIdentifier, Run_datamapFileNameFromIdentifier)
from ..FileSystem.path import combine_many
from ..Spreadsheet.data_map import (to_fs_workbook, from_fs_workbook)
from .contract import (Contract, DTOType, DTO)

def _007CDatamapPath_007C__007C(input: Array[str]) -> str | None:
    (pattern_matching_result,) = (None,)
    def _arrow3442(x: str, y: str, input: Any=input) -> bool:
        return x == y

    if (len(input) == 3) if (not equals_with(_arrow3442, input, None)) else False:
        if input[0] == "assays":
            if input[2] == "isa.datamap.xlsx":
                pattern_matching_result = 0

            else: 
                pattern_matching_result = 2


        elif input[0] == "studies":
            if input[2] == "isa.datamap.xlsx":
                pattern_matching_result = 1

            else: 
                pattern_matching_result = 2


        else: 
            pattern_matching_result = 2


    else: 
        pattern_matching_result = 2

    if pattern_matching_result == 0:
        any_assay_name: str = input[1]
        return combine_many(input)

    elif pattern_matching_result == 1:
        any_study_name: str = input[1]
        return combine_many(input)

    elif pattern_matching_result == 2:
        return None



def ARCtrl_DataMap__DataMap_ToCreateContractForAssay_Z721C83C5(this: DataMap, assay_identifier: str) -> Contract:
    path: str = Assay_datamapFileNameFromIdentifier(assay_identifier)
    return Contract.create_create(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToUpdateContractForAssay_Z721C83C5(this: DataMap, assay_identifier: str) -> Contract:
    path: str = Assay_datamapFileNameFromIdentifier(assay_identifier)
    return Contract.create_update(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToDeleteContractForAssay_Z721C83C5(this: DataMap, assay_identifier: str) -> Contract:
    path: str = Assay_datamapFileNameFromIdentifier(assay_identifier)
    return Contract.create_delete(path)


def ARCtrl_DataMap__DataMap_toDeleteContractForAssay_Static_Z721C83C5(assay_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3443(data_map: DataMap, assay_identifier: Any=assay_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToDeleteContractForAssay_Z721C83C5(data_map, assay_identifier)

    return _arrow3443


def ARCtrl_DataMap__DataMap_toUpdateContractForAssay_Static_Z721C83C5(assay_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3444(data_map: DataMap, assay_identifier: Any=assay_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToUpdateContractForAssay_Z721C83C5(data_map, assay_identifier)

    return _arrow3444


def ARCtrl_DataMap__DataMap_tryFromReadContractForAssay_Static(assay_identifier: str, c: Contract) -> DataMap | None:
    path: str = Assay_datamapFileNameFromIdentifier(assay_identifier)
    (pattern_matching_result, fsworkbook_1, p_1) = (None, None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 5:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        def _arrow3445(__unit: None=None, assay_identifier: Any=assay_identifier, c: Any=c) -> bool:
                            fsworkbook: Any = c.DTO.fields[0]
                            return c.Path == path

                        if _arrow3445():
                            pattern_matching_result = 0
                            fsworkbook_1 = c.DTO.fields[0]
                            p_1 = c.Path

                        else: 
                            pattern_matching_result = 1


                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        dm: DataMap = from_fs_workbook(fsworkbook_1)
        DataMap__set_StaticHash_Z524259A4(dm, safe_hash(dm))
        return dm

    elif pattern_matching_result == 1:
        return None



def ARCtrl_DataMap__DataMap_ToCreateContractForStudy_Z721C83C5(this: DataMap, study_identifier: str) -> Contract:
    path: str = Study_datamapFileNameFromIdentifier(study_identifier)
    return Contract.create_create(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToUpdateContractForStudy_Z721C83C5(this: DataMap, study_identifier: str) -> Contract:
    path: str = Study_datamapFileNameFromIdentifier(study_identifier)
    return Contract.create_update(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToDeleteContractForStudy_Z721C83C5(this: DataMap, study_identifier: str) -> Contract:
    path: str = Study_datamapFileNameFromIdentifier(study_identifier)
    return Contract.create_delete(path)


def ARCtrl_DataMap__DataMap_toDeleteContractForStudy_Static_Z721C83C5(study_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3446(data_map: DataMap, study_identifier: Any=study_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToDeleteContractForStudy_Z721C83C5(data_map, study_identifier)

    return _arrow3446


def ARCtrl_DataMap__DataMap_toUpdateContractForStudy_Static_Z721C83C5(study_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3447(data_map: DataMap, study_identifier: Any=study_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToUpdateContractForStudy_Z721C83C5(data_map, study_identifier)

    return _arrow3447


def ARCtrl_DataMap__DataMap_tryFromReadContractForStudy_Static(study_identifier: str, c: Contract) -> DataMap | None:
    path: str = Study_datamapFileNameFromIdentifier(study_identifier)
    (pattern_matching_result, fsworkbook_1, p_1) = (None, None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 5:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        def _arrow3448(__unit: None=None, study_identifier: Any=study_identifier, c: Any=c) -> bool:
                            fsworkbook: Any = c.DTO.fields[0]
                            return c.Path == path

                        if _arrow3448():
                            pattern_matching_result = 0
                            fsworkbook_1 = c.DTO.fields[0]
                            p_1 = c.Path

                        else: 
                            pattern_matching_result = 1


                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        dm: DataMap = from_fs_workbook(fsworkbook_1)
        DataMap__set_StaticHash_Z524259A4(dm, safe_hash(dm))
        return dm

    elif pattern_matching_result == 1:
        return None



def ARCtrl_DataMap__DataMap_ToCreateContractForWorkflow_Z721C83C5(this: DataMap, workflow_identifier: str) -> Contract:
    path: str = Workflow_datamapFileNameFromIdentifier(workflow_identifier)
    return Contract.create_create(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToUpdateContractForWorkflow_Z721C83C5(this: DataMap, workflow_identifier: str) -> Contract:
    path: str = Workflow_datamapFileNameFromIdentifier(workflow_identifier)
    return Contract.create_update(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToDeleteContractForWorkflow_Z721C83C5(this: DataMap, workflow_identifier: str) -> Contract:
    path: str = Workflow_datamapFileNameFromIdentifier(workflow_identifier)
    return Contract.create_delete(path)


def ARCtrl_DataMap__DataMap_toDeleteContractForWorkflow_Static_Z721C83C5(workflow_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3449(data_map: DataMap, workflow_identifier: Any=workflow_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToDeleteContractForWorkflow_Z721C83C5(data_map, workflow_identifier)

    return _arrow3449


def ARCtrl_DataMap__DataMap_toUpdateContractForWorkflow_Static_Z721C83C5(workflow_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3450(data_map: DataMap, workflow_identifier: Any=workflow_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToUpdateContractForWorkflow_Z721C83C5(data_map, workflow_identifier)

    return _arrow3450


def ARCtrl_DataMap__DataMap_tryFromReadContractForWorkflow_Static(workflow_identifier: str, c: Contract) -> DataMap | None:
    path: str = Workflow_datamapFileNameFromIdentifier(workflow_identifier)
    (pattern_matching_result, fsworkbook_1, p_1) = (None, None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 5:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        def _arrow3451(__unit: None=None, workflow_identifier: Any=workflow_identifier, c: Any=c) -> bool:
                            fsworkbook: Any = c.DTO.fields[0]
                            return c.Path == path

                        if _arrow3451():
                            pattern_matching_result = 0
                            fsworkbook_1 = c.DTO.fields[0]
                            p_1 = c.Path

                        else: 
                            pattern_matching_result = 1


                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        dm: DataMap = from_fs_workbook(fsworkbook_1)
        DataMap__set_StaticHash_Z524259A4(dm, safe_hash(dm))
        return dm

    elif pattern_matching_result == 1:
        return None



def ARCtrl_DataMap__DataMap_ToCreateContractForRun_Z721C83C5(this: DataMap, run_identifier: str) -> Contract:
    path: str = Run_datamapFileNameFromIdentifier(run_identifier)
    return Contract.create_create(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToUpdateContractForRun_Z721C83C5(this: DataMap, run_identifier: str) -> Contract:
    path: str = Run_datamapFileNameFromIdentifier(run_identifier)
    return Contract.create_update(path, DTOType(5), DTO(0, to_fs_workbook(this)))


def ARCtrl_DataMap__DataMap_ToDeleteContractForRun_Z721C83C5(this: DataMap, run_identifier: str) -> Contract:
    path: str = Run_datamapFileNameFromIdentifier(run_identifier)
    return Contract.create_delete(path)


def ARCtrl_DataMap__DataMap_toDeleteContractForRun_Static_Z721C83C5(run_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3452(data_map: DataMap, run_identifier: Any=run_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToDeleteContractForRun_Z721C83C5(data_map, run_identifier)

    return _arrow3452


def ARCtrl_DataMap__DataMap_toUpdateContractForRun_Static_Z721C83C5(run_identifier: str) -> Callable[[DataMap], Contract]:
    def _arrow3453(data_map: DataMap, run_identifier: Any=run_identifier) -> Contract:
        return ARCtrl_DataMap__DataMap_ToUpdateContractForRun_Z721C83C5(data_map, run_identifier)

    return _arrow3453


def ARCtrl_DataMap__DataMap_tryFromReadContractForRun_Static(run_identifier: str, c: Contract) -> DataMap | None:
    path: str = Run_datamapFileNameFromIdentifier(run_identifier)
    (pattern_matching_result, fsworkbook_1, p_1) = (None, None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 5:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        def _arrow3454(__unit: None=None, run_identifier: Any=run_identifier, c: Any=c) -> bool:
                            fsworkbook: Any = c.DTO.fields[0]
                            return c.Path == path

                        if _arrow3454():
                            pattern_matching_result = 0
                            fsworkbook_1 = c.DTO.fields[0]
                            p_1 = c.Path

                        else: 
                            pattern_matching_result = 1


                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        dm: DataMap = from_fs_workbook(fsworkbook_1)
        DataMap__set_StaticHash_Z524259A4(dm, safe_hash(dm))
        return dm

    elif pattern_matching_result == 1:
        return None



__all__ = ["_007CDatamapPath_007C__007C", "ARCtrl_DataMap__DataMap_ToCreateContractForAssay_Z721C83C5", "ARCtrl_DataMap__DataMap_ToUpdateContractForAssay_Z721C83C5", "ARCtrl_DataMap__DataMap_ToDeleteContractForAssay_Z721C83C5", "ARCtrl_DataMap__DataMap_toDeleteContractForAssay_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_toUpdateContractForAssay_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_tryFromReadContractForAssay_Static", "ARCtrl_DataMap__DataMap_ToCreateContractForStudy_Z721C83C5", "ARCtrl_DataMap__DataMap_ToUpdateContractForStudy_Z721C83C5", "ARCtrl_DataMap__DataMap_ToDeleteContractForStudy_Z721C83C5", "ARCtrl_DataMap__DataMap_toDeleteContractForStudy_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_toUpdateContractForStudy_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_tryFromReadContractForStudy_Static", "ARCtrl_DataMap__DataMap_ToCreateContractForWorkflow_Z721C83C5", "ARCtrl_DataMap__DataMap_ToUpdateContractForWorkflow_Z721C83C5", "ARCtrl_DataMap__DataMap_ToDeleteContractForWorkflow_Z721C83C5", "ARCtrl_DataMap__DataMap_toDeleteContractForWorkflow_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_toUpdateContractForWorkflow_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_tryFromReadContractForWorkflow_Static", "ARCtrl_DataMap__DataMap_ToCreateContractForRun_Z721C83C5", "ARCtrl_DataMap__DataMap_ToUpdateContractForRun_Z721C83C5", "ARCtrl_DataMap__DataMap_ToDeleteContractForRun_Z721C83C5", "ARCtrl_DataMap__DataMap_toDeleteContractForRun_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_toUpdateContractForRun_Static_Z721C83C5", "ARCtrl_DataMap__DataMap_tryFromReadContractForRun_Static"]

