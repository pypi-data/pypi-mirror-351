from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..Contract.contract import (Contract, DTOType, DTO as DTO_2)
from ..FileSystem.path import combine
from ..cross_async import (catch_with, start_sequential)
from ..fable_modules.fable_library.array_ import (fold, append)
from ..fable_modules.fable_library.async_builder import (singleton, Async)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.string_ import (to_text, printf)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import curry2
from ..fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from .file_system_helper import (read_file_xlsx_async, read_file_text_async, ensure_directory_of_file_async, write_file_text_async, write_file_xlsx_async, rename_file_or_directory_async, delete_file_or_directory_async)

def fulfill_read_contract_async(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e_1: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3626(__unit: None=None, e_1: Any=e_1) -> str:
            arg_4: str = str(e_1)
            return to_text(printf("Error reading contract %s: %s"))(c.Path)(arg_4)

        return FSharpResult_2(1, _arrow3626())

    def _arrow3632(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        def _arrow3629(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
            match_value: DTOType | None = c.DTOType
            (pattern_matching_result,) = (None,)
            if match_value is not None:
                if match_value.tag == 0:
                    pattern_matching_result = 0

                elif match_value.tag == 4:
                    pattern_matching_result = 0

                elif match_value.tag == 1:
                    pattern_matching_result = 0

                elif match_value.tag == 2:
                    pattern_matching_result = 0

                elif match_value.tag == 3:
                    pattern_matching_result = 0

                elif match_value.tag == 5:
                    pattern_matching_result = 0

                elif match_value.tag == 10:
                    pattern_matching_result = 1

                else: 
                    pattern_matching_result = 2


            else: 
                pattern_matching_result = 2

            if pattern_matching_result == 0:
                path: str = combine(base_path, c.Path)
                def _arrow3627(_arg: FsWorkbook) -> Async[FSharpResult_2[Contract, str]]:
                    return singleton.Return(FSharpResult_2(0, Contract(c.Operation, c.Path, c.DTOType, DTO_2(0, _arg))))

                return singleton.Bind(read_file_xlsx_async(path), _arrow3627)

            elif pattern_matching_result == 1:
                path_1: str = combine(base_path, c.Path)
                def _arrow3628(_arg_1: str) -> Async[FSharpResult_2[Contract, str]]:
                    return singleton.Return(FSharpResult_2(0, Contract(c.Operation, c.Path, c.DTOType, DTO_2(1, _arg_1))))

                return singleton.Bind(read_file_text_async(path_1), _arrow3628)

            elif pattern_matching_result == 2:
                return singleton.Return(FSharpResult_2(1, to_text(printf("Contract %s is neither an ISA nor a freetext contract"))(c.Path)))


        def _arrow3631(_arg_2: Exception) -> Async[FSharpResult_2[Contract, str]]:
            def _arrow3630(__unit: None=None) -> str:
                arg_2: str = str(_arg_2)
                return to_text(printf("Error reading contract %s: %s"))(c.Path)(arg_2)

            return singleton.Return(FSharpResult_2(1, _arrow3630()))

        return singleton.TryWith(singleton.Delay(_arrow3629), _arrow3631)

    return catch_with(f, singleton.Delay(_arrow3632))


def fullfill_contract_batch_async_by(contract_f: Callable[[str, Contract], Async[FSharpResult_2[Contract, str]]], base_path: str, cs: Array[Contract]) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
    def _arrow3634(__unit: None=None, contract_f: Any=contract_f, base_path: Any=base_path, cs: Any=cs) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        def _arrow3633(_arg: Array[FSharpResult_2[Contract, str]]) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
            def folder(acc: FSharpResult_2[Array[Contract], Array[str]], cr: FSharpResult_2[Contract, str]) -> FSharpResult_2[Array[Contract], Array[str]]:
                copy_of_struct: FSharpResult_2[Array[Contract], Array[str]] = acc
                if copy_of_struct.tag == 1:
                    copy_of_struct_1: FSharpResult_2[Contract, str] = cr
                    if copy_of_struct_1.tag == 1:
                        return FSharpResult_2(1, append(copy_of_struct.fields[0], [copy_of_struct_1.fields[0]], None))

                    else: 
                        return FSharpResult_2(1, copy_of_struct.fields[0])


                else: 
                    copy_of_struct_2: FSharpResult_2[Contract, str] = cr
                    if copy_of_struct_2.tag == 1:
                        return FSharpResult_2(1, [copy_of_struct_2.fields[0]])

                    else: 
                        return FSharpResult_2(0, append(copy_of_struct.fields[0], [copy_of_struct_2.fields[0]], None))



            res: FSharpResult_2[Array[Contract], Array[str]] = fold(folder, FSharpResult_2(0, []), _arg)
            return singleton.Return(res)

        return singleton.Bind(start_sequential(curry2(contract_f)(base_path), cs), _arrow3633)

    return singleton.Delay(_arrow3634)


def fulfill_write_contract_async(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e_1: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3635(__unit: None=None, e_1: Any=e_1) -> str:
            arg_4: str = str(e_1)
            return to_text(printf("Error writing contract %s: %s"))(c.Path)(arg_4)

        return FSharpResult_2(1, _arrow3635())

    def _arrow3645(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        def _arrow3642(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
            match_value: DTO_2 | None = c.DTO
            if match_value is None:
                path_2: str = combine(base_path, c.Path)
                def _arrow3637(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3636(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_text_async(path_2, ""), _arrow3636)

                return singleton.Bind(ensure_directory_of_file_async(path_2), _arrow3637)

            elif match_value.tag == 1:
                t: str = match_value.fields[0]
                path: str = combine(base_path, c.Path)
                def _arrow3639(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3638(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_text_async(path, t), _arrow3638)

                return singleton.Bind(ensure_directory_of_file_async(path), _arrow3639)

            elif match_value.tag == 0:
                wb: Any = match_value.fields[0]
                path_1: str = combine(base_path, c.Path)
                def _arrow3641(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3640(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_xlsx_async(path_1, wb), _arrow3640)

                return singleton.Bind(ensure_directory_of_file_async(path_1), _arrow3641)

            else: 
                return singleton.Return(FSharpResult_2(1, to_text(printf("Contract %s is not an ISA contract"))(c.Path)))


        def _arrow3644(_arg_6: Exception) -> Async[FSharpResult_2[Contract, str]]:
            def _arrow3643(__unit: None=None) -> str:
                arg_2: str = str(_arg_6)
                return to_text(printf("Error writing contract %s: %s"))(c.Path)(arg_2)

            return singleton.Return(FSharpResult_2(1, _arrow3643()))

        return singleton.TryWith(singleton.Delay(_arrow3642), _arrow3644)

    return catch_with(f, singleton.Delay(_arrow3645))


def fulfill_update_contract_async(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e_1: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3646(__unit: None=None, e_1: Any=e_1) -> str:
            arg_4: str = str(e_1)
            return to_text(printf("Error updating contract %s: %s"))(c.Path)(arg_4)

        return FSharpResult_2(1, _arrow3646())

    def _arrow3656(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        def _arrow3653(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
            match_value: DTO_2 | None = c.DTO
            if match_value is None:
                path_2: str = combine(base_path, c.Path)
                def _arrow3648(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3647(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_text_async(path_2, ""), _arrow3647)

                return singleton.Bind(ensure_directory_of_file_async(path_2), _arrow3648)

            elif match_value.tag == 1:
                t: str = match_value.fields[0]
                path: str = combine(base_path, c.Path)
                def _arrow3650(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3649(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_text_async(path, t), _arrow3649)

                return singleton.Bind(ensure_directory_of_file_async(path), _arrow3650)

            elif match_value.tag == 0:
                wb: Any = match_value.fields[0]
                path_1: str = combine(base_path, c.Path)
                def _arrow3652(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    def _arrow3651(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                        return singleton.Return(FSharpResult_2(0, c))

                    return singleton.Bind(write_file_xlsx_async(path_1, wb), _arrow3651)

                return singleton.Bind(ensure_directory_of_file_async(path_1), _arrow3652)

            else: 
                return singleton.Return(FSharpResult_2(1, to_text(printf("Contract %s is not an ISA contract"))(c.Path)))


        def _arrow3655(_arg_6: Exception) -> Async[FSharpResult_2[Contract, str]]:
            def _arrow3654(__unit: None=None) -> str:
                arg_2: str = str(_arg_6)
                return to_text(printf("Error updating contract %s: %s"))(c.Path)(arg_2)

            return singleton.Return(FSharpResult_2(1, _arrow3654()))

        return singleton.TryWith(singleton.Delay(_arrow3653), _arrow3655)

    return catch_with(f, singleton.Delay(_arrow3656))


def fullfill_rename_contract_async(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e_1: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3657(__unit: None=None, e_1: Any=e_1) -> str:
            arg_5: str = str(e_1)
            return to_text(printf("Error renaming contract %s: %s"))(c.Path)(arg_5)

        return FSharpResult_2(1, _arrow3657())

    def _arrow3662(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        def _arrow3659(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
            match_value: DTO_2 | None = c.DTO
            (pattern_matching_result, t_2) = (None, None)
            if match_value is not None:
                if match_value.tag == 1:
                    if match_value.fields[0] == c.Path:
                        pattern_matching_result = 0

                    else: 
                        pattern_matching_result = 1
                        t_2 = match_value.fields[0]


                else: 
                    pattern_matching_result = 2


            else: 
                pattern_matching_result = 2

            if pattern_matching_result == 0:
                return singleton.Return(FSharpResult_2(1, to_text(printf("Rename Contract %s old and new Path are the same"))(c.Path)))

            elif pattern_matching_result == 1:
                new_path: str = combine(base_path, t_2)
                old_path: str = combine(base_path, c.Path)
                def _arrow3658(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                    return singleton.Return(FSharpResult_2(0, c))

                return singleton.Bind(rename_file_or_directory_async(old_path, new_path), _arrow3658)

            elif pattern_matching_result == 2:
                return singleton.Return(FSharpResult_2(1, to_text(printf("Rename Contract %s does not contain new Path"))(c.Path)))


        def _arrow3661(_arg_1: Exception) -> Async[FSharpResult_2[Contract, str]]:
            def _arrow3660(__unit: None=None) -> str:
                arg_3: str = str(_arg_1)
                return to_text(printf("Error renaming contract %s: %s"))(c.Path)(arg_3)

            return singleton.Return(FSharpResult_2(1, _arrow3660()))

        return singleton.TryWith(singleton.Delay(_arrow3659), _arrow3661)

    return catch_with(f, singleton.Delay(_arrow3662))


def fullfill_delete_contract_async(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e_1: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3663(__unit: None=None, e_1: Any=e_1) -> str:
            arg_3: str = str(e_1)
            return to_text(printf("Error deleting contract %s: %s"))(c.Path)(arg_3)

        return FSharpResult_2(1, _arrow3663())

    def _arrow3668(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        def _arrow3665(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
            path: str = combine(base_path, c.Path)
            def _arrow3664(__unit: None=None) -> Async[FSharpResult_2[Contract, str]]:
                return singleton.Return(FSharpResult_2(0, c))

            return singleton.Bind(delete_file_or_directory_async(path), _arrow3664)

        def _arrow3667(_arg_1: Exception) -> Async[FSharpResult_2[Contract, str]]:
            def _arrow3666(__unit: None=None) -> str:
                arg_1: str = str(_arg_1)
                return to_text(printf("Error deleting contract %s: %s"))(c.Path)(arg_1)

            return singleton.Return(FSharpResult_2(1, _arrow3666()))

        return singleton.TryWith(singleton.Delay(_arrow3665), _arrow3667)

    return catch_with(f, singleton.Delay(_arrow3668))


def full_fill_contract(base_path: str, c: Contract) -> Async[FSharpResult_2[Contract, str]]:
    def f(e: Exception, base_path: Any=base_path, c: Any=c) -> FSharpResult_2[Contract, str]:
        def _arrow3669(__unit: None=None, e: Any=e) -> str:
            arg_2: str = str(e)
            return to_text(printf("Error fulfilling contract %s: %s"))(c.Path)(arg_2)

        return FSharpResult_2(1, _arrow3669())

    def _arrow3670(__unit: None=None, base_path: Any=base_path, c: Any=c) -> Async[FSharpResult_2[Contract, str]]:
        match_value: str = c.Operation
        return singleton.ReturnFrom(fulfill_read_contract_async(base_path, c)) if (match_value == "READ") else (singleton.ReturnFrom(fulfill_write_contract_async(base_path, c)) if (match_value == "CREATE") else (singleton.ReturnFrom(fulfill_update_contract_async(base_path, c)) if (match_value == "UPDATE") else (singleton.ReturnFrom(fullfill_delete_contract_async(base_path, c)) if (match_value == "DELETE") else (singleton.ReturnFrom(fullfill_rename_contract_async(base_path, c)) if (match_value == "RENAME") else singleton.Return(FSharpResult_2(1, to_text(printf("Operation %A not supported"))(c.Operation)))))))

    return catch_with(f, singleton.Delay(_arrow3670))


def full_fill_contract_batch_async(base_path: str, cs: Array[Contract]) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
    def _arrow3671(base_path_1: str, c: Contract, base_path: Any=base_path, cs: Any=cs) -> Async[FSharpResult_2[Contract, str]]:
        return full_fill_contract(base_path_1, c)

    return fullfill_contract_batch_async_by(_arrow3671, base_path, cs)


__all__ = ["fulfill_read_contract_async", "fullfill_contract_batch_async_by", "fulfill_write_contract_async", "fulfill_update_contract_async", "fullfill_rename_contract_async", "fullfill_delete_contract_async", "full_fill_contract", "full_fill_contract_batch_async"]

