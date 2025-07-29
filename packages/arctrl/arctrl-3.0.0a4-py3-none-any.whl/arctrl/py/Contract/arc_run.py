from __future__ import annotations
from typing import Any
from ..fable_modules.fable_library.array_ import equals_with
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.seq import (to_array, delay, append, collect, singleton, empty)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import IEnumerable_1
from ..Core.arc_types import ArcRun
from ..Core.Helper.identifier import Run_fileNameFromIdentifier
from ..FileSystem.file_system_tree import FileSystemTree
from ..FileSystem.path import (combine_many, get_run_folder_path)
from ..Spreadsheet.arc_run import (ARCtrl_ArcRun__ArcRun_toFsWorkbook_Static_Z3EFAF6F8, ARCtrl_ArcRun__ArcRun_fromFsWorkbook_Static_32154C9D)
from .contract import (Contract, DTOType, DTO)

def _007CRunPath_007C__007C(input: Array[str]) -> str | None:
    (pattern_matching_result,) = (None,)
    def _arrow3470(x: str, y: str, input: Any=input) -> bool:
        return x == y

    if (len(input) == 3) if (not equals_with(_arrow3470, input, None)) else False:
        if input[0] == "runs":
            if input[2] == "isa.run.xlsx":
                pattern_matching_result = 0

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        any_run_name: str = input[1]
        return combine_many(input)

    elif pattern_matching_result == 1:
        return None



def ARCtrl_ArcRun__ArcRun_ToCreateContract_6FCE9E49(this: ArcRun, WithFolder: bool | None=None) -> Array[Contract]:
    with_folder: bool = default_arg(WithFolder, False)
    path: str = Run_fileNameFromIdentifier(this.Identifier)
    c: Contract = Contract.create_create(path, DTOType(3), DTO(0, ARCtrl_ArcRun__ArcRun_toFsWorkbook_Static_Z3EFAF6F8(this)))
    def _arrow3474(__unit: None=None, this: Any=this, WithFolder: Any=WithFolder) -> IEnumerable_1[Contract]:
        def _arrow3472(__unit: None=None) -> IEnumerable_1[Contract]:
            folder_fs: FileSystemTree = FileSystemTree.create_runs_folder([FileSystemTree.create_run_folder(this.Identifier)])
            def _arrow3471(p: str) -> IEnumerable_1[Contract]:
                return singleton(Contract.create_create(p, DTOType(10))) if ((p != "runs/.gitkeep") if (p != path) else False) else empty()

            return collect(_arrow3471, folder_fs.ToFilePaths(False))

        def _arrow3473(__unit: None=None) -> IEnumerable_1[Contract]:
            return singleton(c)

        return append(_arrow3472() if with_folder else empty(), delay(_arrow3473))

    return to_array(delay(_arrow3474))


def ARCtrl_ArcRun__ArcRun_ToUpdateContract(this: ArcRun) -> Contract:
    path: str = Run_fileNameFromIdentifier(this.Identifier)
    return Contract.create_update(path, DTOType(3), DTO(0, ARCtrl_ArcRun__ArcRun_toFsWorkbook_Static_Z3EFAF6F8(this)))


def ARCtrl_ArcRun__ArcRun_ToDeleteContract(this: ArcRun) -> Contract:
    path: str = get_run_folder_path(this.Identifier)
    return Contract.create_delete(path)


def ARCtrl_ArcRun__ArcRun_toDeleteContract_Static_Z3EFAF6F8(run: ArcRun) -> Contract:
    return ARCtrl_ArcRun__ArcRun_ToDeleteContract(run)


def ARCtrl_ArcRun__ArcRun_toCreateContract_Static_Z71974BBF(run: ArcRun, WithFolder: bool | None=None) -> Array[Contract]:
    return ARCtrl_ArcRun__ArcRun_ToCreateContract_6FCE9E49(run, WithFolder)


def ARCtrl_ArcRun__ArcRun_toUpdateContract_Static_Z3EFAF6F8(run: ArcRun) -> Contract:
    return ARCtrl_ArcRun__ArcRun_ToUpdateContract(run)


def ARCtrl_ArcRun__ArcRun_tryFromReadContract_Static_7570923F(c: Contract) -> ArcRun | None:
    (pattern_matching_result, fsworkbook) = (None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 3:
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
        return ARCtrl_ArcRun__ArcRun_fromFsWorkbook_Static_32154C9D(fsworkbook)

    elif pattern_matching_result == 1:
        return None



__all__ = ["_007CRunPath_007C__007C", "ARCtrl_ArcRun__ArcRun_ToCreateContract_6FCE9E49", "ARCtrl_ArcRun__ArcRun_ToUpdateContract", "ARCtrl_ArcRun__ArcRun_ToDeleteContract", "ARCtrl_ArcRun__ArcRun_toDeleteContract_Static_Z3EFAF6F8", "ARCtrl_ArcRun__ArcRun_toCreateContract_Static_Z71974BBF", "ARCtrl_ArcRun__ArcRun_toUpdateContract_Static_Z3EFAF6F8", "ARCtrl_ArcRun__ArcRun_tryFromReadContract_Static_7570923F"]

