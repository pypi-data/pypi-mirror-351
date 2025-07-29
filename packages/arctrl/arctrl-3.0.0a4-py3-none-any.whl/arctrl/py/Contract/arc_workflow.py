from __future__ import annotations
from typing import Any
from ..fable_modules.fable_library.array_ import equals_with
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.seq import (to_array, delay, append, collect, singleton, empty)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import IEnumerable_1
from ..Core.arc_types import (ArcWorkflow__get_Identifier, ArcWorkflow)
from ..Core.Helper.identifier import Workflow_fileNameFromIdentifier
from ..FileSystem.file_system_tree import FileSystemTree
from ..FileSystem.path import (combine_many, get_workflow_folder_path)
from ..Spreadsheet.arc_workflow import (ARCtrl_ArcWorkflow__ArcWorkflow_toFsWorkbook_Static_Z1C75CB0E, ARCtrl_ArcWorkflow__ArcWorkflow_fromFsWorkbook_Static_32154C9D)
from .contract import (Contract, DTOType, DTO)

def _007CWorkflowPath_007C__007C(input: Array[str]) -> str | None:
    (pattern_matching_result,) = (None,)
    def _arrow3465(x: str, y: str, input: Any=input) -> bool:
        return x == y

    if (len(input) == 3) if (not equals_with(_arrow3465, input, None)) else False:
        if input[0] == "workflows":
            if input[2] == "isa.workflow.xlsx":
                pattern_matching_result = 0

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        any_workflow_name: str = input[1]
        return combine_many(input)

    elif pattern_matching_result == 1:
        return None



def ARCtrl_ArcWorkflow__ArcWorkflow_ToCreateContract_6FCE9E49(this: ArcWorkflow, WithFolder: bool | None=None) -> Array[Contract]:
    with_folder: bool = default_arg(WithFolder, False)
    path: str = Workflow_fileNameFromIdentifier(ArcWorkflow__get_Identifier(this))
    c: Contract = Contract.create_create(path, DTOType(2), DTO(0, ARCtrl_ArcWorkflow__ArcWorkflow_toFsWorkbook_Static_Z1C75CB0E(this)))
    def _arrow3469(__unit: None=None, this: Any=this, WithFolder: Any=WithFolder) -> IEnumerable_1[Contract]:
        def _arrow3467(__unit: None=None) -> IEnumerable_1[Contract]:
            folder_fs: FileSystemTree = FileSystemTree.create_workflows_folder([FileSystemTree.create_workflow_folder(ArcWorkflow__get_Identifier(this))])
            def _arrow3466(p: str) -> IEnumerable_1[Contract]:
                return singleton(Contract.create_create(p, DTOType(10))) if ((p != "workflows/.gitkeep") if (p != path) else False) else empty()

            return collect(_arrow3466, folder_fs.ToFilePaths(False))

        def _arrow3468(__unit: None=None) -> IEnumerable_1[Contract]:
            return singleton(c)

        return append(_arrow3467() if with_folder else empty(), delay(_arrow3468))

    return to_array(delay(_arrow3469))


def ARCtrl_ArcWorkflow__ArcWorkflow_ToUpdateContract(this: ArcWorkflow) -> Contract:
    path: str = Workflow_fileNameFromIdentifier(ArcWorkflow__get_Identifier(this))
    return Contract.create_update(path, DTOType(2), DTO(0, ARCtrl_ArcWorkflow__ArcWorkflow_toFsWorkbook_Static_Z1C75CB0E(this)))


def ARCtrl_ArcWorkflow__ArcWorkflow_ToDeleteContract(this: ArcWorkflow) -> Contract:
    path: str = get_workflow_folder_path(ArcWorkflow__get_Identifier(this))
    return Contract.create_delete(path)


def ARCtrl_ArcWorkflow__ArcWorkflow_toDeleteContract_Static_Z1C75CB0E(workflow: ArcWorkflow) -> Contract:
    return ARCtrl_ArcWorkflow__ArcWorkflow_ToDeleteContract(workflow)


def ARCtrl_ArcWorkflow__ArcWorkflow_toCreateContract_Static_3B1E4D7B(workflow: ArcWorkflow, WithFolder: bool | None=None) -> Array[Contract]:
    return ARCtrl_ArcWorkflow__ArcWorkflow_ToCreateContract_6FCE9E49(workflow, WithFolder)


def ARCtrl_ArcWorkflow__ArcWorkflow_toUpdateContract_Static_Z1C75CB0E(workflow: ArcWorkflow) -> Contract:
    return ARCtrl_ArcWorkflow__ArcWorkflow_ToUpdateContract(workflow)


def ARCtrl_ArcWorkflow__ArcWorkflow_tryFromReadContract_Static_7570923F(c: Contract) -> ArcWorkflow | None:
    (pattern_matching_result, fsworkbook) = (None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 2:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        pattern_matching_result = 0
                        fsworkbook = c.DTO.fields[0]

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
        return ARCtrl_ArcWorkflow__ArcWorkflow_fromFsWorkbook_Static_32154C9D(fsworkbook)

    elif pattern_matching_result == 1:
        return None



__all__ = ["_007CWorkflowPath_007C__007C", "ARCtrl_ArcWorkflow__ArcWorkflow_ToCreateContract_6FCE9E49", "ARCtrl_ArcWorkflow__ArcWorkflow_ToUpdateContract", "ARCtrl_ArcWorkflow__ArcWorkflow_ToDeleteContract", "ARCtrl_ArcWorkflow__ArcWorkflow_toDeleteContract_Static_Z1C75CB0E", "ARCtrl_ArcWorkflow__ArcWorkflow_toCreateContract_Static_3B1E4D7B", "ARCtrl_ArcWorkflow__ArcWorkflow_toUpdateContract_Static_Z1C75CB0E", "ARCtrl_ArcWorkflow__ArcWorkflow_tryFromReadContract_Static_7570923F"]

