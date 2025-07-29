from __future__ import annotations
from collections.abc import Callable
from typing import Any
from .Contract.arc import try_isaread_contract_from_path
from .Contract.arc_assay import (ARCtrl_ArcAssay__ArcAssay_ToDeleteContract, ARCtrl_ArcAssay__ArcAssay_ToCreateContract_6FCE9E49, ARCtrl_ArcAssay__ArcAssay_ToUpdateContract, ARCtrl_ArcAssay__ArcAssay_tryFromReadContract_Static_7570923F)
from .Contract.arc_investigation import (ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract, ARCtrl_ArcInvestigation__ArcInvestigation_tryFromReadContract_Static_7570923F)
from .Contract.arc_run import (ARCtrl_ArcRun__ArcRun_ToCreateContract_6FCE9E49, ARCtrl_ArcRun__ArcRun_ToUpdateContract, ARCtrl_ArcRun__ArcRun_tryFromReadContract_Static_7570923F)
from .Contract.arc_study import (ARCtrl_ArcStudy__ArcStudy_ToUpdateContract, ARCtrl_ArcStudy__ArcStudy_ToCreateContract_6FCE9E49, ARCtrl_ArcStudy__ArcStudy_tryFromReadContract_Static_7570923F)
from .Contract.arc_workflow import (ARCtrl_ArcWorkflow__ArcWorkflow_ToCreateContract_6FCE9E49, ARCtrl_ArcWorkflow__ArcWorkflow_ToUpdateContract, ARCtrl_ArcWorkflow__ArcWorkflow_tryFromReadContract_Static_7570923F)
from .Contract.contract import (Contract, DTOType, DTO)
from .Contract.datamap import (ARCtrl_DataMap__DataMap_ToCreateContractForStudy_Z721C83C5, ARCtrl_DataMap__DataMap_ToUpdateContractForStudy_Z721C83C5, ARCtrl_DataMap__DataMap_ToCreateContractForAssay_Z721C83C5, ARCtrl_DataMap__DataMap_ToUpdateContractForAssay_Z721C83C5, ARCtrl_DataMap__DataMap_ToCreateContractForWorkflow_Z721C83C5, ARCtrl_DataMap__DataMap_ToUpdateContractForWorkflow_Z721C83C5, ARCtrl_DataMap__DataMap_ToCreateContractForRun_Z721C83C5, ARCtrl_DataMap__DataMap_ToUpdateContractForRun_Z721C83C5, ARCtrl_DataMap__DataMap_tryFromReadContractForAssay_Static, ARCtrl_DataMap__DataMap_tryFromReadContractForStudy_Static, ARCtrl_DataMap__DataMap_tryFromReadContractForWorkflow_Static, ARCtrl_DataMap__DataMap_tryFromReadContractForRun_Static)
from .Contract.git import (Init_createInitContract_6DFDD678, gitattributes_contract, gitignore_contract, Init_createAddRemoteContract_Z721C83C5, Clone_createCloneContract_5000466F)
from .Contract.validation_packages_config import (ValidationPackagesConfigHelper_ConfigFilePath, ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_toCreateContract_Static_724DAE55, ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_toDeleteContract_Static_724DAE55, ValidationPackagesConfigHelper_ReadContract, ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_tryFromReadContract_Static_7570923F)
from .Core.arc_types import (ArcInvestigation, ArcAssay, ArcStudy, ArcWorkflow, ArcRun, ArcWorkflow__get_Identifier, ArcWorkflow__get_DataMap, ArcWorkflow__set_DataMap_51F1E59E, ArcWorkflow__set_StaticHash_Z524259A4, ArcWorkflow__GetLightHashCode, ArcWorkflow__get_StaticHash, ArcWorkflow__Copy_6FCE9E49, ArcInvestigation_reflection)
from .Core.comment import (Comment, Remark)
from .Core.data import Data
from .Core.data_context import DataContext
from .Core.data_map import (DataMap__get_DataContexts, DataMap, DataMap__set_StaticHash_Z524259A4, DataMap__get_StaticHash)
from .Core.Helper.collections_ import ResizeArray_map
from .Core.Helper.identifier import (create_missing_identifier, Study_fileNameFromIdentifier, Study_datamapFileNameFromIdentifier, Assay_fileNameFromIdentifier, Assay_datamapFileNameFromIdentifier, Workflow_fileNameFromIdentifier, Workflow_datamapFileNameFromIdentifier, Run_fileNameFromIdentifier, Run_datamapFileNameFromIdentifier)
from .Core.identifier_setters import set_investigation_identifier
from .Core.ontology_source_reference import OntologySourceReference
from .Core.person import Person
from .Core.publication import Publication
from .Core.Table.arc_table import ArcTable
from .Core.Table.arc_tables import ArcTables
from .Core.Table.composite_cell import CompositeCell
from .Core.Table.composite_column import CompositeColumn
from .FileSystem.file_system import FileSystem
from .FileSystem.file_system_tree import FileSystemTree
from .FileSystem.path import (get_assay_folder_path, get_study_folder_path)
from .Json.encode import default_spaces
from .Spreadsheet.arc_assay import ARCtrl_ArcAssay__ArcAssay_toFsWorkbook_Static_Z2508BE4F
from .Spreadsheet.arc_investigation import ARCtrl_ArcInvestigation__ArcInvestigation_toFsWorkbook_Static_Z720BD3FF
from .Spreadsheet.arc_run import ARCtrl_ArcRun__ArcRun_toFsWorkbook_Static_Z3EFAF6F8
from .Spreadsheet.arc_study import ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_Z4CEFA522
from .Spreadsheet.arc_workflow import ARCtrl_ArcWorkflow__ArcWorkflow_toFsWorkbook_Static_Z1C75CB0E
from .Spreadsheet.data_map import to_fs_workbook
from .ValidationPackages.validation_packages_config import ValidationPackagesConfig
from .ContractIO.contract_io import full_fill_contract_batch_async
from .ContractIO.file_system_helper import get_all_file_paths_async
from .fable_modules.thoth_json_python.decode import Decode_fromString
from .fable_modules.thoth_json_python.encode import to_string
from .fable_modules.fable_library.array_ import (filter, map as map_1, iterate, choose, exists, fold, concat, contains as contains_2, append as append_1, try_pick, exactly_one)
from .fable_modules.fable_library.async_ import run_synchronously
from .fable_modules.fable_library.async_builder import (Async, singleton)
from .fable_modules.fable_library.list import FSharpList
from .fable_modules.fable_library.map import of_seq as of_seq_1
from .fable_modules.fable_library.map_util import add_to_dict
from .fable_modules.fable_library.option import (value as value_3, default_arg, bind)
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.result import FSharpResult_2
from .fable_modules.fable_library.seq import (to_array, contains, delay, append, singleton as singleton_1, map, iterate as iterate_1, try_find, find, empty, collect, to_list)
from .fable_modules.fable_library.set import (of_seq, contains as contains_1, union_many, FSharpSet__Contains)
from .fable_modules.fable_library.string_ import (starts_with_exact, replace, join, to_fail, printf, to_text)
from .fable_modules.fable_library.types import (Array, FSharpRef)
from .fable_modules.fable_library.util import (string_hash, IEnumerable_1, compare_primitives, curry2, ignore, safe_hash, get_enumerator, dispose, to_enumerable)
from .fable_modules.fs_spreadsheet.Cells.fs_cells_collection import Dictionary_tryGet
from .fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from .fable_modules.thoth_json_core.types import IEncodable
from .rocrate_io import (ROCrate_get_decoderDeprecated, ROCrate_get_decoder, ROCrate_encoder_8A8D439)

def _expr3873() -> TypeInfo:
    return class_type("ARCtrl.ARC", None, ARC, ArcInvestigation_reflection())


class ARC(ArcInvestigation):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None, cwl: None | None=None, fs: FileSystem | None=None) -> None:
        super().__init__(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)
        this: FSharpRef[ARC] = FSharpRef(None)
        this.contents = self
        self._cwl: None | None = cwl
        def _arrow3872(__unit: None=None) -> FileSystem:
            fs_1: FileSystem = default_arg(fs, FileSystem.create(tree = FileSystemTree(1, "", [])))
            return ARCAux_updateFSByISA(this.contents, fs_1)

        self._fs: FileSystem = _arrow3872()
        self.init_004089: int = 1

    @property
    def FileSystem(self, __unit: None=None) -> FileSystem:
        this: ARC = self
        return this._fs

    @FileSystem.setter
    def FileSystem(self, fs: FileSystem) -> None:
        this: ARC = self
        this._fs = fs

    @staticmethod
    def from_arc_investigation(isa: ArcInvestigation, cwl: None | None=None, fs: FileSystem | None=None) -> ARC:
        return ARC(isa.Identifier, isa.Title, isa.Description, isa.SubmissionDate, isa.PublicReleaseDate, isa.OntologySourceReferences, isa.Publications, isa.Contacts, isa.Assays, isa.Studies, isa.Workflows, isa.Runs, isa.RegisteredStudyIdentifiers, isa.Comments, isa.Remarks, cwl, fs)

    def TryWriteAsync(self, arc_path: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetWriteContracts())

    def TryUpdateAsync(self, arc_path: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetUpdateContracts())

    @staticmethod
    def try_load_async(arc_path: str) -> Async[FSharpResult_2[ARC, Array[str]]]:
        def _arrow3780(__unit: None=None) -> Async[FSharpResult_2[ARC, Array[str]]]:
            def _arrow3779(_arg: Array[str]) -> Async[FSharpResult_2[ARC, Array[str]]]:
                arc: ARC = ARC.from_file_paths(to_array(_arg))
                contracts: Array[Contract] = arc.GetReadContracts()
                def _arrow3778(_arg_1: FSharpResult_2[Array[Contract], Array[str]]) -> Async[FSharpResult_2[ARC, Array[str]]]:
                    ful_filled_contracts: FSharpResult_2[Array[Contract], Array[str]] = _arg_1
                    if ful_filled_contracts.tag == 1:
                        return singleton.Return(FSharpResult_2(1, ful_filled_contracts.fields[0]))

                    else: 
                        arc.SetISAFromContracts(ful_filled_contracts.fields[0])
                        return singleton.Return(FSharpResult_2(0, arc))


                return singleton.Bind(full_fill_contract_batch_async(arc_path, contracts), _arrow3778)

            return singleton.Bind(get_all_file_paths_async(arc_path), _arrow3779)

        return singleton.Delay(_arrow3780)

    def GetAssayRemoveContracts(self, assay_identifier: str) -> Array[Contract]:
        this: ARC = self
        class ObjectExpr3782:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow3781(x: str, y: str) -> bool:
                    return x == y

                return _arrow3781

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(assay_identifier, this.AssayIdentifiers, ObjectExpr3782()):
            raise Exception("ARC does not contain assay with given name")

        assay: ArcAssay = this.GetAssay(assay_identifier)
        studies: Array[ArcStudy] = assay.StudiesRegisteredIn
        super().RemoveAssay(assay_identifier)
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        assay_folder_path: str = get_assay_folder_path(assay_identifier)
        def predicate(p: str) -> bool:
            return not starts_with_exact(p, assay_folder_path)

        filtered_paths: Array[str] = filter(predicate, paths)
        this.SetFilePaths(filtered_paths)
        def _arrow3785(__unit: None=None) -> IEnumerable_1[Contract]:
            def _arrow3784(__unit: None=None) -> IEnumerable_1[Contract]:
                def _arrow3783(__unit: None=None) -> IEnumerable_1[Contract]:
                    return map(ARCtrl_ArcStudy__ArcStudy_ToUpdateContract, studies)

                return append(singleton_1(ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract(this)), delay(_arrow3783))

            return append(singleton_1(ARCtrl_ArcAssay__ArcAssay_ToDeleteContract(assay)), delay(_arrow3784))

        return to_array(delay(_arrow3785))

    def TryRemoveAssayAsync(self, arc_path: str, assay_identifier: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetAssayRemoveContracts(assay_identifier))

    def GetAssayRenameContracts(self, old_assay_identifier: str, new_assay_identifier: str) -> Array[Contract]:
        this: ARC = self
        class ObjectExpr3787:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow3786(x: str, y: str) -> bool:
                    return x == y

                return _arrow3786

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(old_assay_identifier, this.AssayIdentifiers, ObjectExpr3787()):
            raise Exception("ARC does not contain assay with given name")

        super().RenameAssay(old_assay_identifier, new_assay_identifier)
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        old_assay_folder_path: str = get_assay_folder_path(old_assay_identifier)
        new_assay_folder_path: str = get_assay_folder_path(new_assay_identifier)
        def mapping(p: str) -> str:
            return replace(p, old_assay_folder_path, new_assay_folder_path)

        renamed_paths: Array[str] = map_1(mapping, paths, None)
        this.SetFilePaths(renamed_paths)
        def _arrow3789(__unit: None=None) -> IEnumerable_1[Contract]:
            def _arrow3788(__unit: None=None) -> IEnumerable_1[Contract]:
                return this.GetUpdateContracts()

            return append(singleton_1(Contract.create_rename(old_assay_folder_path, new_assay_folder_path)), delay(_arrow3788))

        return to_array(delay(_arrow3789))

    def TryRenameAssayAsync(self, arc_path: str, old_assay_identifier: str, new_assay_identifier: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetAssayRenameContracts(old_assay_identifier, new_assay_identifier))

    def GetStudyRemoveContracts(self, study_identifier: str) -> Array[Contract]:
        this: ARC = self
        super().RemoveStudy(study_identifier)
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        study_folder_path: str = get_study_folder_path(study_identifier)
        def predicate(p: str) -> bool:
            return not starts_with_exact(p, study_folder_path)

        filtered_paths: Array[str] = filter(predicate, paths)
        this.SetFilePaths(filtered_paths)
        return [Contract.create_delete(study_folder_path), ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract(this)]

    def TryRemoveStudyAsync(self, arc_path: str, study_identifier: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetStudyRemoveContracts(study_identifier))

    def GetStudyRenameContracts(self, old_study_identifier: str, new_study_identifier: str) -> Array[Contract]:
        this: ARC = self
        class ObjectExpr3791:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow3790(x: str, y: str) -> bool:
                    return x == y

                return _arrow3790

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(old_study_identifier, this.StudyIdentifiers, ObjectExpr3791()):
            raise Exception("ARC does not contain study with given name")

        super().RenameStudy(old_study_identifier, new_study_identifier)
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        old_study_folder_path: str = get_study_folder_path(old_study_identifier)
        new_study_folder_path: str = get_study_folder_path(new_study_identifier)
        def mapping(p: str) -> str:
            return replace(p, old_study_folder_path, new_study_folder_path)

        renamed_paths: Array[str] = map_1(mapping, paths, None)
        this.SetFilePaths(renamed_paths)
        def _arrow3793(__unit: None=None) -> IEnumerable_1[Contract]:
            def _arrow3792(__unit: None=None) -> IEnumerable_1[Contract]:
                return this.GetUpdateContracts()

            return append(singleton_1(Contract.create_rename(old_study_folder_path, new_study_folder_path)), delay(_arrow3792))

        return to_array(delay(_arrow3793))

    def TryRenameStudyAsync(self, arc_path: str, old_study_identifier: str, new_study_identifier: str) -> Async[FSharpResult_2[Array[Contract], Array[str]]]:
        this: ARC = self
        return full_fill_contract_batch_async(arc_path, this.GetStudyRenameContracts(old_study_identifier, new_study_identifier))

    def WriteAsync(self, arc_path: str) -> Async[None]:
        this: ARC = self
        def _arrow3795(__unit: None=None) -> Async[None]:
            def _arrow3794(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not write ARC, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryWriteAsync(arc_path), _arrow3794)

        return singleton.Delay(_arrow3795)

    def UpdateAsync(self, arc_path: str) -> Async[None]:
        this: ARC = self
        def _arrow3797(__unit: None=None) -> Async[None]:
            def _arrow3796(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not update ARC, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryUpdateAsync(arc_path), _arrow3796)

        return singleton.Delay(_arrow3797)

    def RemoveAssayAsync(self, arc_path: str, assay_identifier: str) -> Async[None]:
        this: ARC = self
        def _arrow3799(__unit: None=None) -> Async[None]:
            def _arrow3798(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not remove assay, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryRemoveAssayAsync(arc_path, assay_identifier), _arrow3798)

        return singleton.Delay(_arrow3799)

    def RenameAssayAsync(self, arc_path: str, old_assay_identifier: str, new_assay_identifier: str) -> Async[None]:
        this: ARC = self
        def _arrow3801(__unit: None=None) -> Async[None]:
            def _arrow3800(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not rename assay, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryRenameAssayAsync(arc_path, old_assay_identifier, new_assay_identifier), _arrow3800)

        return singleton.Delay(_arrow3801)

    def RemoveStudyAsync(self, arc_path: str, study_identifier: str) -> Async[None]:
        this: ARC = self
        def _arrow3803(__unit: None=None) -> Async[None]:
            def _arrow3802(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not remove study, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryRemoveStudyAsync(arc_path, study_identifier), _arrow3802)

        return singleton.Delay(_arrow3803)

    def RenameStudyAsync(self, arc_path: str, old_study_identifier: str, new_study_identifier: str) -> Async[None]:
        this: ARC = self
        def _arrow3805(__unit: None=None) -> Async[None]:
            def _arrow3804(_arg: FSharpResult_2[Array[Contract], Array[str]]) -> Async[None]:
                result: FSharpResult_2[Array[Contract], Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not rename study, failed with the following errors %s"))(appended)
                    return singleton.Zero()

                else: 
                    return singleton.Zero()


            return singleton.Bind(this.TryRenameStudyAsync(arc_path, old_study_identifier, new_study_identifier), _arrow3804)

        return singleton.Delay(_arrow3805)

    @staticmethod
    def load_async(arc_path: str) -> Async[ARC]:
        def _arrow3807(__unit: None=None) -> Async[ARC]:
            def _arrow3806(_arg: FSharpResult_2[ARC, Array[str]]) -> Async[ARC]:
                result: FSharpResult_2[ARC, Array[str]] = _arg
                if result.tag == 1:
                    def mapping(e: str) -> str:
                        return e

                    appended: str = join("\n", map_1(mapping, result.fields[0], None))
                    to_fail(printf("Could not load ARC, failed with the following errors %s"))(appended)
                    return singleton.Return(ARC(create_missing_identifier()))

                else: 
                    return singleton.Return(result.fields[0])


            return singleton.Bind(ARC.try_load_async(arc_path), _arrow3806)

        return singleton.Delay(_arrow3807)

    def Write(self, arc_path: str) -> None:
        this: ARC = self
        run_synchronously(this.WriteAsync(arc_path))

    def Update(self, arc_path: str) -> None:
        this: ARC = self
        run_synchronously(this.UpdateAsync(arc_path))

    def RemoveAssay(self, arc_path: str, assay_identifier: str) -> None:
        this: ARC = self
        run_synchronously(this.RemoveAssayAsync(arc_path, assay_identifier))

    def RenameAssay(self, arc_path: str, old_assay_identifier: str, new_assay_identifier: str) -> None:
        this: ARC = self
        run_synchronously(this.RenameAssayAsync(arc_path, old_assay_identifier, new_assay_identifier))

    def RemoveStudy(self, arc_path: str, study_identifier: str) -> None:
        this: ARC = self
        run_synchronously(this.RemoveStudyAsync(arc_path, study_identifier))

    def RenameStudy(self, arc_path: str, old_study_identifier: str, new_study_identifier: str) -> None:
        this: ARC = self
        run_synchronously(this.RenameStudyAsync(arc_path, old_study_identifier, new_study_identifier))

    @staticmethod
    def load(arc_path: str) -> ARC:
        return run_synchronously(ARC.load_async(arc_path))

    def MakeDataFilesAbsolute(self, __unit: None=None) -> None:
        this: ARC = self
        class ObjectExpr3808:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        files_paths: Any = of_seq(this.FileSystem.Tree.ToFilePaths(), ObjectExpr3808())
        def check_existence_from_root(p: str) -> bool:
            return contains_1(p, files_paths)

        def update_column_option(data_name_function: Callable[[Data], str], col: CompositeColumn | None=None) -> None:
            (pattern_matching_result, col_2) = (None, None)
            if col is not None:
                def _arrow3809(__unit: None=None, data_name_function: Any=data_name_function, col: Any=col) -> bool:
                    col_1: CompositeColumn = col
                    return col_1.Header.IsDataColumn

                if _arrow3809():
                    pattern_matching_result = 0
                    col_2 = col

                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1

            if pattern_matching_result == 0:
                def action(c: CompositeCell, data_name_function: Any=data_name_function, col: Any=col) -> None:
                    if c.AsData.FilePath is not None:
                        new_file_path: str = data_name_function(c.AsData)
                        c.AsData.FilePath = new_file_path


                iterate(action, col_2.Cells)

            elif pattern_matching_result == 1:
                pass


        def update_table(data_name_function_1: Callable[[Data], str], t: ArcTable) -> None:
            update_column_option(data_name_function_1, t.TryGetInputColumn())
            update_column_option(data_name_function_1, t.TryGetOutputColumn())

        def update_data_map(data_name_function_2: Callable[[Data], str], dm: DataMap) -> None:
            def action_1(c_1: DataContext, data_name_function_2: Any=data_name_function_2, dm: Any=dm) -> None:
                if c_1.FilePath is not None:
                    new_file_path_1: str = data_name_function_2(c_1)
                    c_1.FilePath = new_file_path_1


            iterate_1(action_1, DataMap__get_DataContexts(dm))

        def action_3(s: ArcStudy) -> None:
            def f(d: Data, s: Any=s) -> str:
                return d.GetAbsolutePathForStudy(s.Identifier, check_existence_from_root)

            source_1: Array[ArcTable] = s.Tables
            iterate_1(curry2(update_table)(f), source_1)
            if s.DataMap is not None:
                update_data_map(f, value_3(s.DataMap))


        iterate_1(action_3, this.Studies)
        def action_5(a: ArcAssay) -> None:
            def f_1(d_1: Data, a: Any=a) -> str:
                return d_1.GetAbsolutePathForAssay(a.Identifier, check_existence_from_root)

            source_3: Array[ArcTable] = a.Tables
            iterate_1(curry2(update_table)(f_1), source_3)
            if a.DataMap is not None:
                update_data_map(f_1, value_3(a.DataMap))


        iterate_1(action_5, this.Assays)

    @staticmethod
    def from_file_paths(file_paths: Array[str]) -> ARC:
        fs: FileSystem = FileSystem.from_file_paths(file_paths)
        return ARC(create_missing_identifier(), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, fs)

    def SetFilePaths(self, file_paths: Array[str]) -> None:
        this: ARC = self
        tree: FileSystemTree = FileSystemTree.from_file_paths(file_paths)
        this._fs = FileSystem(tree, this._fs.History)

    def GetReadContracts(self, __unit: None=None) -> Array[Contract]:
        this: ARC = self
        return choose(try_isaread_contract_from_path, this._fs.Tree.ToFilePaths(), None)

    def SetISAFromContracts(self, contracts: Array[Contract]) -> None:
        this: ARC = self
        investigation: ArcInvestigation = ARCAux_getArcInvestigationFromContracts(contracts)
        ignore(set_investigation_identifier(investigation.Identifier, this))
        this.Title = investigation.Title
        this.Description = investigation.Description
        this.SubmissionDate = investigation.SubmissionDate
        this.PublicReleaseDate = investigation.PublicReleaseDate
        this.OntologySourceReferences = investigation.OntologySourceReferences
        this.Publications = investigation.Publications
        this.Contacts = investigation.Contacts
        this.Comments = investigation.Comments
        this.Remarks = investigation.Remarks
        this.RegisteredStudyIdentifiers = investigation.RegisteredStudyIdentifiers
        def mapping(tuple: tuple[ArcStudy, FSharpList[ArcAssay]]) -> ArcStudy:
            return tuple[0]

        studies: Array[ArcStudy] = map_1(mapping, ARCAux_getArcStudiesFromContracts(contracts), None)
        assays: Array[ArcAssay] = ARCAux_getArcAssaysFromContracts(contracts)
        workflows: Array[ArcWorkflow] = ARCAux_getArcWorkflowsFromContracts(contracts)
        runs: Array[ArcRun] = ARCAux_getArcRunsFromContracts(contracts)
        def action(ai: str) -> None:
            def predicate(a: ArcAssay, ai: Any=ai) -> bool:
                return a.Identifier == ai

            if not exists(predicate, assays):
                this.DeleteAssay(ai)


        iterate(action, this.AssayIdentifiers)
        def action_1(si: str) -> None:
            def predicate_1(s: ArcStudy, si: Any=si) -> bool:
                return s.Identifier == si

            if not exists(predicate_1, studies):
                this.DeleteStudy(si)


        iterate(action_1, this.StudyIdentifiers)
        def action_2(study: ArcStudy) -> None:
            def predicate_2(s_1: ArcStudy, study: Any=study) -> bool:
                return s_1.Identifier == study.Identifier

            registered_study_opt: ArcStudy | None = try_find(predicate_2, this.Studies)
            if registered_study_opt is None:
                this.AddStudy(study)

            else: 
                registered_study: ArcStudy = registered_study_opt
                registered_study.UpdateReferenceByStudyFile(study, True)

            datamap: DataMap | None = ARCAux_getAssayDataMapFromContracts(study.Identifier, contracts)
            if study.DataMap is None:
                study.DataMap = datamap

            study.StaticHash = study.GetLightHashCode() or 0

        iterate(action_2, studies)
        def action_3(assay: ArcAssay) -> None:
            def predicate_3(a_1: ArcAssay, assay: Any=assay) -> bool:
                return a_1.Identifier == assay.Identifier

            registered_assay_opt: ArcAssay | None = try_find(predicate_3, this.Assays)
            if registered_assay_opt is None:
                this.AddAssay(assay)

            else: 
                registered_assay: ArcAssay = registered_assay_opt
                registered_assay.UpdateReferenceByAssayFile(assay, True)

            def predicate_4(a_2: ArcAssay, assay: Any=assay) -> bool:
                return a_2.Identifier == assay.Identifier

            assay_1: ArcAssay = find(predicate_4, this.Assays)
            updated_tables: ArcTables
            array_6: Array[ArcStudy] = assay_1.StudiesRegisteredIn
            def folder(tables: ArcTables, study_1: ArcStudy, assay: Any=assay) -> ArcTables:
                return ArcTables.update_reference_tables_by_sheets(ArcTables(study_1.Tables), tables, False)

            updated_tables = fold(folder, ArcTables(assay_1.Tables), array_6)
            datamap_1: DataMap | None = ARCAux_getAssayDataMapFromContracts(assay_1.Identifier, contracts)
            if assay_1.DataMap is None:
                assay_1.DataMap = datamap_1

            assay_1.Tables = updated_tables.Tables

        iterate(action_3, assays)
        def action_4(workflow: ArcWorkflow) -> None:
            datamap_2: DataMap | None = ARCAux_getWorkflowDataMapFromContracts(ArcWorkflow__get_Identifier(workflow), contracts)
            if ArcWorkflow__get_DataMap(workflow) is None:
                ArcWorkflow__set_DataMap_51F1E59E(workflow, datamap_2)

            this.AddWorkflow(workflow)
            ArcWorkflow__set_StaticHash_Z524259A4(workflow, ArcWorkflow__GetLightHashCode(workflow))

        iterate(action_4, workflows)
        def action_5(run: ArcRun) -> None:
            datamap_3: DataMap | None = ARCAux_getRunDataMapFromContracts(run.Identifier, contracts)
            if run.DataMap is None:
                run.DataMap = datamap_3

            this.AddRun(run)
            run.StaticHash = run.GetLightHashCode() or 0

        iterate(action_5, runs)
        def action_6(a_3: ArcAssay) -> None:
            a_3.StaticHash = a_3.GetLightHashCode() or 0

        iterate_1(action_6, this.Assays)
        def action_7(s_2: ArcStudy) -> None:
            s_2.StaticHash = s_2.GetLightHashCode() or 0

        iterate_1(action_7, this.Studies)
        this.StaticHash = this.GetLightHashCode() or 0

    def UpdateFileSystem(self, __unit: None=None) -> None:
        this: ARC = self
        new_fs: FileSystem = ARCAux_updateFSByISA(this, this._fs)
        this._fs = new_fs

    def GetWriteContracts(self, skip_update_fs: bool | None=None) -> Array[Contract]:
        this: ARC = self
        if not default_arg(skip_update_fs, False):
            this.UpdateFileSystem()

        workbooks: Any = dict([])
        add_to_dict(workbooks, "isa.investigation.xlsx", (DTOType(4), ARCtrl_ArcInvestigation__ArcInvestigation_toFsWorkbook_Static_Z720BD3FF(this)))
        this.StaticHash = this.GetLightHashCode() or 0
        def action(s: ArcStudy) -> None:
            s.StaticHash = s.GetLightHashCode() or 0
            add_to_dict(workbooks, Study_fileNameFromIdentifier(s.Identifier), (DTOType(1), ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_Z4CEFA522(s)))
            if s.DataMap is not None:
                dm: DataMap = value_3(s.DataMap)
                DataMap__set_StaticHash_Z524259A4(dm, safe_hash(dm))
                add_to_dict(workbooks, Study_datamapFileNameFromIdentifier(s.Identifier), (DTOType(5), to_fs_workbook(dm)))


        iterate_1(action, this.Studies)
        def action_1(a: ArcAssay) -> None:
            a.StaticHash = a.GetLightHashCode() or 0
            add_to_dict(workbooks, Assay_fileNameFromIdentifier(a.Identifier), (DTOType(0), ARCtrl_ArcAssay__ArcAssay_toFsWorkbook_Static_Z2508BE4F(a)))
            if a.DataMap is not None:
                dm_1: DataMap = value_3(a.DataMap)
                DataMap__set_StaticHash_Z524259A4(dm_1, safe_hash(dm_1))
                add_to_dict(workbooks, Assay_datamapFileNameFromIdentifier(a.Identifier), (DTOType(5), to_fs_workbook(dm_1)))


        iterate_1(action_1, this.Assays)
        def action_2(w: ArcWorkflow) -> None:
            ArcWorkflow__set_StaticHash_Z524259A4(w, ArcWorkflow__GetLightHashCode(w))
            add_to_dict(workbooks, Workflow_fileNameFromIdentifier(ArcWorkflow__get_Identifier(w)), (DTOType(2), ARCtrl_ArcWorkflow__ArcWorkflow_toFsWorkbook_Static_Z1C75CB0E(w)))
            if ArcWorkflow__get_DataMap(w) is not None:
                dm_2: DataMap = value_3(ArcWorkflow__get_DataMap(w))
                DataMap__set_StaticHash_Z524259A4(dm_2, safe_hash(dm_2))
                add_to_dict(workbooks, Workflow_datamapFileNameFromIdentifier(ArcWorkflow__get_Identifier(w)), (DTOType(5), to_fs_workbook(dm_2)))


        iterate_1(action_2, this.Workflows)
        def action_3(r: ArcRun) -> None:
            r.StaticHash = r.GetLightHashCode() or 0
            add_to_dict(workbooks, Run_fileNameFromIdentifier(r.Identifier), (DTOType(3), ARCtrl_ArcRun__ArcRun_toFsWorkbook_Static_Z3EFAF6F8(r)))
            if r.DataMap is not None:
                dm_3: DataMap = value_3(r.DataMap)
                DataMap__set_StaticHash_Z524259A4(dm_3, safe_hash(dm_3))
                add_to_dict(workbooks, Run_datamapFileNameFromIdentifier(r.Identifier), (DTOType(5), to_fs_workbook(dm_3)))


        iterate_1(action_3, this.Runs)
        def mapping(fp: str) -> Contract:
            match_value: tuple[DTOType, FsWorkbook] | None = Dictionary_tryGet(fp, workbooks)
            if match_value is None:
                return Contract.create_create(fp, DTOType(10))

            else: 
                wb: FsWorkbook = match_value[1]
                dto: DTOType = match_value[0]
                return Contract.create_create(fp, dto, DTO(0, wb))


        return map_1(mapping, this._fs.Tree.ToFilePaths(True), None)

    def GetUpdateContracts(self, skip_update_fs: bool | None=None) -> Array[Contract]:
        this: ARC = self
        if this.StaticHash == 0:
            this.StaticHash = this.GetLightHashCode() or 0
            return this.GetWriteContracts(skip_update_fs)

        else: 
            def _arrow3834(__unit: None=None) -> IEnumerable_1[Contract]:
                hash_1: int = this.GetLightHashCode() or 0
                def _arrow3833(__unit: None=None) -> IEnumerable_1[Contract]:
                    this.StaticHash = hash_1 or 0
                    def _arrow3814(s: ArcStudy) -> IEnumerable_1[Contract]:
                        hash_2: int = s.GetLightHashCode() or 0
                        def _arrow3813(__unit: None=None) -> IEnumerable_1[Contract]:
                            s.StaticHash = hash_2 or 0
                            match_value: DataMap | None = s.DataMap
                            (pattern_matching_result, dm_2, dm_3) = (None, None, None)
                            if match_value is not None:
                                if DataMap__get_StaticHash(match_value) == 0:
                                    pattern_matching_result = 0
                                    dm_2 = match_value

                                else: 
                                    def _arrow3812(__unit: None=None) -> bool:
                                        dm_1: DataMap = match_value
                                        return DataMap__get_StaticHash(dm_1) != safe_hash(dm_1)

                                    if _arrow3812():
                                        pattern_matching_result = 1
                                        dm_3 = match_value

                                    else: 
                                        pattern_matching_result = 2



                            else: 
                                pattern_matching_result = 2

                            if pattern_matching_result == 0:
                                def _arrow3810(__unit: None=None) -> IEnumerable_1[Contract]:
                                    DataMap__set_StaticHash_Z524259A4(dm_2, safe_hash(dm_2))
                                    return empty()

                                return append(singleton_1(ARCtrl_DataMap__DataMap_ToCreateContractForStudy_Z721C83C5(dm_2, s.Identifier)), delay(_arrow3810))

                            elif pattern_matching_result == 1:
                                def _arrow3811(__unit: None=None) -> IEnumerable_1[Contract]:
                                    DataMap__set_StaticHash_Z524259A4(dm_3, safe_hash(dm_3))
                                    return empty()

                                return append(singleton_1(ARCtrl_DataMap__DataMap_ToUpdateContractForStudy_Z721C83C5(dm_3, s.Identifier)), delay(_arrow3811))

                            elif pattern_matching_result == 2:
                                return empty()


                        return append(ARCtrl_ArcStudy__ArcStudy_ToCreateContract_6FCE9E49(s, True) if (s.StaticHash == 0) else (singleton_1(ARCtrl_ArcStudy__ArcStudy_ToUpdateContract(s)) if (s.StaticHash != hash_2) else empty()), delay(_arrow3813))

                    def _arrow3832(__unit: None=None) -> IEnumerable_1[Contract]:
                        def _arrow3819(a: ArcAssay) -> IEnumerable_1[Contract]:
                            hash_3: int = a.GetLightHashCode() or 0
                            def _arrow3818(__unit: None=None) -> IEnumerable_1[Contract]:
                                a.StaticHash = hash_3 or 0
                                match_value_1: DataMap | None = a.DataMap
                                (pattern_matching_result_1, dm_6, dm_7) = (None, None, None)
                                if match_value_1 is not None:
                                    if DataMap__get_StaticHash(match_value_1) == 0:
                                        pattern_matching_result_1 = 0
                                        dm_6 = match_value_1

                                    else: 
                                        def _arrow3817(__unit: None=None) -> bool:
                                            dm_5: DataMap = match_value_1
                                            return DataMap__get_StaticHash(dm_5) != safe_hash(dm_5)

                                        if _arrow3817():
                                            pattern_matching_result_1 = 1
                                            dm_7 = match_value_1

                                        else: 
                                            pattern_matching_result_1 = 2



                                else: 
                                    pattern_matching_result_1 = 2

                                if pattern_matching_result_1 == 0:
                                    def _arrow3815(__unit: None=None) -> IEnumerable_1[Contract]:
                                        DataMap__set_StaticHash_Z524259A4(dm_6, safe_hash(dm_6))
                                        return empty()

                                    return append(singleton_1(ARCtrl_DataMap__DataMap_ToCreateContractForAssay_Z721C83C5(dm_6, a.Identifier)), delay(_arrow3815))

                                elif pattern_matching_result_1 == 1:
                                    def _arrow3816(__unit: None=None) -> IEnumerable_1[Contract]:
                                        DataMap__set_StaticHash_Z524259A4(dm_7, safe_hash(dm_7))
                                        return empty()

                                    return append(singleton_1(ARCtrl_DataMap__DataMap_ToUpdateContractForAssay_Z721C83C5(dm_7, a.Identifier)), delay(_arrow3816))

                                elif pattern_matching_result_1 == 2:
                                    return empty()


                            return append(ARCtrl_ArcAssay__ArcAssay_ToCreateContract_6FCE9E49(a, True) if (a.StaticHash == 0) else (singleton_1(ARCtrl_ArcAssay__ArcAssay_ToUpdateContract(a)) if (a.StaticHash != hash_3) else empty()), delay(_arrow3818))

                        def _arrow3831(__unit: None=None) -> IEnumerable_1[Contract]:
                            def _arrow3824(w: ArcWorkflow) -> IEnumerable_1[Contract]:
                                hash_4: int = ArcWorkflow__GetLightHashCode(w) or 0
                                def _arrow3823(__unit: None=None) -> IEnumerable_1[Contract]:
                                    ArcWorkflow__set_StaticHash_Z524259A4(w, hash_4)
                                    match_value_2: DataMap | None = ArcWorkflow__get_DataMap(w)
                                    (pattern_matching_result_2, dm_10, dm_11) = (None, None, None)
                                    if match_value_2 is not None:
                                        if DataMap__get_StaticHash(match_value_2) == 0:
                                            pattern_matching_result_2 = 0
                                            dm_10 = match_value_2

                                        else: 
                                            def _arrow3822(__unit: None=None) -> bool:
                                                dm_9: DataMap = match_value_2
                                                return DataMap__get_StaticHash(dm_9) != safe_hash(dm_9)

                                            if _arrow3822():
                                                pattern_matching_result_2 = 1
                                                dm_11 = match_value_2

                                            else: 
                                                pattern_matching_result_2 = 2



                                    else: 
                                        pattern_matching_result_2 = 2

                                    if pattern_matching_result_2 == 0:
                                        def _arrow3820(__unit: None=None) -> IEnumerable_1[Contract]:
                                            DataMap__set_StaticHash_Z524259A4(dm_10, safe_hash(dm_10))
                                            return empty()

                                        return append(singleton_1(ARCtrl_DataMap__DataMap_ToCreateContractForWorkflow_Z721C83C5(dm_10, ArcWorkflow__get_Identifier(w))), delay(_arrow3820))

                                    elif pattern_matching_result_2 == 1:
                                        def _arrow3821(__unit: None=None) -> IEnumerable_1[Contract]:
                                            DataMap__set_StaticHash_Z524259A4(dm_11, safe_hash(dm_11))
                                            return empty()

                                        return append(singleton_1(ARCtrl_DataMap__DataMap_ToUpdateContractForWorkflow_Z721C83C5(dm_11, ArcWorkflow__get_Identifier(w))), delay(_arrow3821))

                                    elif pattern_matching_result_2 == 2:
                                        return empty()


                                return append(ARCtrl_ArcWorkflow__ArcWorkflow_ToCreateContract_6FCE9E49(w, True) if (ArcWorkflow__get_StaticHash(w) == 0) else (singleton_1(ARCtrl_ArcWorkflow__ArcWorkflow_ToUpdateContract(w)) if (ArcWorkflow__get_StaticHash(w) != hash_4) else empty()), delay(_arrow3823))

                            def _arrow3830(__unit: None=None) -> IEnumerable_1[Contract]:
                                def _arrow3829(r: ArcRun) -> IEnumerable_1[Contract]:
                                    hash_5: int = r.GetLightHashCode() or 0
                                    def _arrow3828(__unit: None=None) -> IEnumerable_1[Contract]:
                                        r.StaticHash = hash_5 or 0
                                        match_value_3: DataMap | None = r.DataMap
                                        (pattern_matching_result_3, dm_14, dm_15) = (None, None, None)
                                        if match_value_3 is not None:
                                            if DataMap__get_StaticHash(match_value_3) == 0:
                                                pattern_matching_result_3 = 0
                                                dm_14 = match_value_3

                                            else: 
                                                def _arrow3827(__unit: None=None) -> bool:
                                                    dm_13: DataMap = match_value_3
                                                    return DataMap__get_StaticHash(dm_13) != safe_hash(dm_13)

                                                if _arrow3827():
                                                    pattern_matching_result_3 = 1
                                                    dm_15 = match_value_3

                                                else: 
                                                    pattern_matching_result_3 = 2



                                        else: 
                                            pattern_matching_result_3 = 2

                                        if pattern_matching_result_3 == 0:
                                            def _arrow3825(__unit: None=None) -> IEnumerable_1[Contract]:
                                                DataMap__set_StaticHash_Z524259A4(dm_14, safe_hash(dm_14))
                                                return empty()

                                            return append(singleton_1(ARCtrl_DataMap__DataMap_ToCreateContractForRun_Z721C83C5(dm_14, r.Identifier)), delay(_arrow3825))

                                        elif pattern_matching_result_3 == 1:
                                            def _arrow3826(__unit: None=None) -> IEnumerable_1[Contract]:
                                                DataMap__set_StaticHash_Z524259A4(dm_15, safe_hash(dm_15))
                                                return empty()

                                            return append(singleton_1(ARCtrl_DataMap__DataMap_ToUpdateContractForRun_Z721C83C5(dm_15, r.Identifier)), delay(_arrow3826))

                                        elif pattern_matching_result_3 == 2:
                                            return empty()


                                    return append(ARCtrl_ArcRun__ArcRun_ToCreateContract_6FCE9E49(r, True) if (r.StaticHash == 0) else (singleton_1(ARCtrl_ArcRun__ArcRun_ToUpdateContract(r)) if (r.StaticHash != hash_5) else empty()), delay(_arrow3828))

                                return collect(_arrow3829, this.Runs)

                            return append(collect(_arrow3824, this.Workflows), delay(_arrow3830))

                        return append(collect(_arrow3819, this.Assays), delay(_arrow3831))

                    return append(collect(_arrow3814, this.Studies), delay(_arrow3832))

                return append(singleton_1(ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract(this)) if (this.StaticHash != hash_1) else empty(), delay(_arrow3833))

            return to_array(delay(_arrow3834))


    def GetGitInitContracts(self, branch: str | None=None, repository_address: str | None=None, default_gitignore: bool | None=None) -> Array[Contract]:
        default_gitignore_1: bool = default_arg(default_gitignore, False)
        def _arrow3838(__unit: None=None) -> IEnumerable_1[Contract]:
            def _arrow3837(__unit: None=None) -> IEnumerable_1[Contract]:
                def _arrow3836(__unit: None=None) -> IEnumerable_1[Contract]:
                    def _arrow3835(__unit: None=None) -> IEnumerable_1[Contract]:
                        return singleton_1(Init_createAddRemoteContract_Z721C83C5(value_3(repository_address))) if (repository_address is not None) else empty()

                    return append(singleton_1(gitignore_contract) if default_gitignore_1 else empty(), delay(_arrow3835))

                return append(singleton_1(gitattributes_contract), delay(_arrow3836))

            return append(singleton_1(Init_createInitContract_6DFDD678(branch)), delay(_arrow3837))

        return to_array(delay(_arrow3838))

    @staticmethod
    def get_clone_contract(remote_url: str, merge: bool | None=None, branch: str | None=None, token: tuple[str, str] | None=None, nolfs: bool | None=None) -> Contract:
        return Clone_createCloneContract_5000466F(remote_url, merge, branch, token, nolfs)

    def Copy(self, __unit: None=None) -> ARC:
        this: ARC = self
        next_assays: Array[ArcAssay] = []
        next_studies: Array[ArcStudy] = []
        next_workflows: Array[ArcWorkflow] = []
        next_runs: Array[ArcRun] = []
        enumerator: Any = get_enumerator(this.Assays)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                assay: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                copy: ArcAssay = assay.Copy()
                (next_assays.append(copy))

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Studies)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                copy_1: ArcStudy = study.Copy()
                (next_studies.append(copy_1))

        finally: 
            dispose(enumerator_1)

        enumerator_2: Any = get_enumerator(this.Workflows)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                workflow: ArcWorkflow = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                (next_workflows.append(ArcWorkflow__Copy_6FCE9E49(workflow)))

        finally: 
            dispose(enumerator_2)

        enumerator_3: Any = get_enumerator(this.Runs)
        try: 
            while enumerator_3.System_Collections_IEnumerator_MoveNext():
                run: ArcRun = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                copy_3: ArcRun = run.Copy()
                (next_runs.append(copy_3))

        finally: 
            dispose(enumerator_3)

        def f(c: Comment) -> Comment:
            return c.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f, this.Comments)
        def f_1(c_1: Remark) -> Remark:
            return c_1.Copy()

        next_remarks: Array[Remark] = ResizeArray_map(f_1, this.Remarks)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_contacts: Array[Person] = ResizeArray_map(f_2, this.Contacts)
        def f_3(c_3: Publication) -> Publication:
            return c_3.Copy()

        next_publications: Array[Publication] = ResizeArray_map(f_3, this.Publications)
        def f_4(c_4: OntologySourceReference) -> OntologySourceReference:
            return c_4.Copy()

        next_ontology_source_references: Array[OntologySourceReference] = ResizeArray_map(f_4, this.OntologySourceReferences)
        next_study_identifiers: Array[str] = list(this.RegisteredStudyIdentifiers)
        fs_copy: FileSystem = this._fs.Copy()
        return ARC(this.Identifier, this.Title, this.Description, this.SubmissionDate, this.PublicReleaseDate, next_ontology_source_references, next_publications, next_contacts, next_assays, next_studies, next_workflows, next_runs, next_study_identifiers, next_comments, next_remarks, this._cwl, fs_copy)

    def GetRegisteredPayload(self, IgnoreHidden: bool | None=None) -> FileSystemTree:
        this: ARC = self
        copy: ARC = this.Copy()
        registered_studies: Array[ArcStudy] = copy.Studies[:]
        def mapping(s: ArcStudy) -> Array[ArcAssay]:
            return s.RegisteredAssays[:]

        registered_assays: Array[ArcAssay] = concat(map_1(mapping, registered_studies, None), None)
        class ObjectExpr3839:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        def mapping_1(s_1: ArcStudy) -> Any:
            study_foldername: str = ((("" + "studies") + "/") + s_1.Identifier) + ""
            def _arrow3846(__unit: None=None, s_1: Any=s_1) -> IEnumerable_1[str]:
                def _arrow3845(__unit: None=None) -> IEnumerable_1[str]:
                    def _arrow3844(__unit: None=None) -> IEnumerable_1[str]:
                        def _arrow3843(table: ArcTable) -> IEnumerable_1[str]:
                            def _arrow3842(kv: Any) -> IEnumerable_1[str]:
                                text_value: str = kv[1].ToFreeTextCell().AsFreeText
                                def _arrow3841(__unit: None=None) -> IEnumerable_1[str]:
                                    def _arrow3840(__unit: None=None) -> IEnumerable_1[str]:
                                        return singleton_1(((((("" + study_foldername) + "/") + "protocols") + "/") + text_value) + "")

                                    return append(singleton_1(((((("" + study_foldername) + "/") + "resources") + "/") + text_value) + ""), delay(_arrow3840))

                                return append(singleton_1(text_value), delay(_arrow3841))

                            return collect(_arrow3842, table.Values)

                        return collect(_arrow3843, s_1.Tables)

                    return append(singleton_1(((("" + study_foldername) + "/") + "README.md") + ""), delay(_arrow3844))

                return append(singleton_1(((("" + study_foldername) + "/") + "isa.study.xlsx") + ""), delay(_arrow3845))

            class ObjectExpr3847:
                @property
                def Compare(self) -> Callable[[str, str], int]:
                    return compare_primitives

            return of_seq(to_list(delay(_arrow3846)), ObjectExpr3847())

        class ObjectExpr3848:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        def mapping_2(a: ArcAssay) -> Any:
            assay_foldername: str = ((("" + "assays") + "/") + a.Identifier) + ""
            def _arrow3855(__unit: None=None, a: Any=a) -> IEnumerable_1[str]:
                def _arrow3854(__unit: None=None) -> IEnumerable_1[str]:
                    def _arrow3853(__unit: None=None) -> IEnumerable_1[str]:
                        def _arrow3852(table_1: ArcTable) -> IEnumerable_1[str]:
                            def _arrow3851(kv_1: Any) -> IEnumerable_1[str]:
                                text_value_1: str = kv_1[1].ToFreeTextCell().AsFreeText
                                def _arrow3850(__unit: None=None) -> IEnumerable_1[str]:
                                    def _arrow3849(__unit: None=None) -> IEnumerable_1[str]:
                                        return singleton_1(((((("" + assay_foldername) + "/") + "protocols") + "/") + text_value_1) + "")

                                    return append(singleton_1(((((("" + assay_foldername) + "/") + "dataset") + "/") + text_value_1) + ""), delay(_arrow3849))

                                return append(singleton_1(text_value_1), delay(_arrow3850))

                            return collect(_arrow3851, table_1.Values)

                        return collect(_arrow3852, a.Tables)

                    return append(singleton_1(((("" + assay_foldername) + "/") + "README.md") + ""), delay(_arrow3853))

                return append(singleton_1(((("" + assay_foldername) + "/") + "isa.assay.xlsx") + ""), delay(_arrow3854))

            class ObjectExpr3856:
                @property
                def Compare(self) -> Callable[[str, str], int]:
                    return compare_primitives

            return of_seq(to_list(delay(_arrow3855)), ObjectExpr3856())

        class ObjectExpr3857:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        class ObjectExpr3858:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        include_files: Any = union_many(to_enumerable([of_seq(to_enumerable(["isa.investigation.xlsx", "README.md"]), ObjectExpr3839()), union_many(map_1(mapping_1, registered_studies, None), ObjectExpr3848()), union_many(map_1(mapping_2, registered_assays, None), ObjectExpr3857())]), ObjectExpr3858())
        ignore_hidden: bool = default_arg(IgnoreHidden, True)
        fs_copy: FileSystem = this._fs.Copy()
        def binder(tree_1: FileSystemTree) -> FileSystemTree | None:
            if ignore_hidden:
                def _arrow3859(n_1: str, tree_1: Any=tree_1) -> bool:
                    return not starts_with_exact(n_1, ".")

                return FileSystemTree.filter_folders(_arrow3859)(tree_1)

            else: 
                return tree_1


        def _arrow3861(__unit: None=None) -> FileSystemTree | None:
            tree: FileSystemTree
            def predicate(p: str) -> bool:
                if True if starts_with_exact(p, "workflows") else starts_with_exact(p, "runs"):
                    return True

                else: 
                    return FSharpSet__Contains(include_files, p)


            paths: Array[str] = filter(predicate, FileSystemTree.to_file_paths()(fs_copy.Tree))
            tree = FileSystemTree.from_file_paths(paths)
            def _arrow3860(n: str) -> bool:
                return not starts_with_exact(n, ".")

            return FileSystemTree.filter_files(_arrow3860)(tree) if ignore_hidden else tree

        return default_arg(bind(binder, _arrow3861()), FileSystemTree.from_file_paths([]))

    def GetAdditionalPayload(self, IgnoreHidden: bool | None=None) -> FileSystemTree:
        this: ARC = self
        ignore_hidden: bool = default_arg(IgnoreHidden, True)
        class ObjectExpr3862:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        registered_payload: Any = of_seq(FileSystemTree.to_file_paths()(this.GetRegisteredPayload()), ObjectExpr3862())
        def binder(tree_1: FileSystemTree) -> FileSystemTree | None:
            if ignore_hidden:
                def _arrow3863(n_1: str, tree_1: Any=tree_1) -> bool:
                    return not starts_with_exact(n_1, ".")

                return FileSystemTree.filter_folders(_arrow3863)(tree_1)

            else: 
                return tree_1


        def _arrow3865(__unit: None=None) -> FileSystemTree | None:
            tree: FileSystemTree
            def predicate(p: str) -> bool:
                return not FSharpSet__Contains(registered_payload, p)

            paths: Array[str] = filter(predicate, FileSystemTree.to_file_paths()(this._fs.Copy().Tree))
            tree = FileSystemTree.from_file_paths(paths)
            def _arrow3864(n: str) -> bool:
                return not starts_with_exact(n, ".")

            return FileSystemTree.filter_files(_arrow3864)(tree) if ignore_hidden else tree

        return default_arg(bind(binder, _arrow3865()), FileSystemTree.from_file_paths([]))

    @staticmethod
    def DefaultContracts() -> Any:
        class ObjectExpr3866:
            @property
            def Compare(self) -> Callable[[str, str], int]:
                return compare_primitives

        return of_seq_1(to_enumerable([(".gitignore", gitignore_contract), (".gitattributes", gitattributes_contract)]), ObjectExpr3866())

    @staticmethod
    def from_deprecated_rocrate_json_string(s: str) -> ARC:
        try: 
            s_1: str = replace(s, "bio:additionalProperty", "sdo:additionalProperty")
            isa: ArcInvestigation
            match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(ROCrate_get_decoderDeprecated(), s_1)
            if match_value.tag == 1:
                raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

            else: 
                isa = match_value.fields[0]

            return ARC.from_arc_investigation(isa)

        except Exception as ex:
            arg_1: str = str(ex)
            return to_fail(printf("Could not parse deprecated ARC-RO-Crate metadata: \n%s"))(arg_1)


    @staticmethod
    def from_rocrate_json_string(s: str) -> ARC:
        try: 
            isa: ArcInvestigation
            match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(ROCrate_get_decoder(), s)
            if match_value.tag == 1:
                raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

            else: 
                isa = match_value.fields[0]

            return ARC.from_arc_investigation(isa)

        except Exception as ex:
            arg_1: str = str(ex)
            return to_fail(printf("Could not parse ARC-RO-Crate metadata: \n%s"))(arg_1)


    def ToROCrateJsonString(self, spaces: int | None=None) -> str:
        this: ARC = self
        this.MakeDataFilesAbsolute()
        value: IEncodable = ROCrate_encoder_8A8D439(this)
        return to_string(default_spaces(spaces), value)

    @staticmethod
    def to_rocrate_json_string(spaces: int | None=None) -> Callable[[ARC], str]:
        def _arrow3867(obj: ARC) -> str:
            return obj.ToROCrateJsonString(spaces)

        return _arrow3867

    def GetValidationPackagesConfigWriteContract(self, vpc: ValidationPackagesConfig) -> Contract:
        this: ARC = self
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        class ObjectExpr3869:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow3868(x: str, y: str) -> bool:
                    return x == y

                return _arrow3868

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains_2(ValidationPackagesConfigHelper_ConfigFilePath, paths, ObjectExpr3869()):
            file_paths: Array[str] = append_1([ValidationPackagesConfigHelper_ConfigFilePath], paths, None)
            this.SetFilePaths(file_paths)

        return ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_toCreateContract_Static_724DAE55(vpc)

    def GetValidationPackagesConfigDeleteContract(self, vpc: ValidationPackagesConfig) -> Contract:
        this: ARC = self
        paths: Array[str] = this.FileSystem.Tree.ToFilePaths()
        class ObjectExpr3871:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow3870(x: str, y: str) -> bool:
                    return x == y

                return _arrow3870

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains_2(ValidationPackagesConfigHelper_ConfigFilePath, paths, ObjectExpr3871()):
            def predicate(p: str) -> bool:
                return not (p == ValidationPackagesConfigHelper_ConfigFilePath)

            file_paths: Array[str] = filter(predicate, paths)
            this.SetFilePaths(file_paths)

        return ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_toDeleteContract_Static_724DAE55(vpc)

    def GetValidationPackagesConfigReadContract(self, __unit: None=None) -> Contract:
        return ValidationPackagesConfigHelper_ReadContract

    def GetValidationPackagesConfigFromReadContract(self, contract: Contract) -> ValidationPackagesConfig | None:
        return ARCtrl_ValidationPackages_ValidationPackagesConfig__ValidationPackagesConfig_tryFromReadContract_Static_7570923F(contract)

    def ToFilePaths(self, remove_root: bool | None=None, skip_update_fs: bool | None=None) -> Array[str]:
        this: ARC = self
        if not default_arg(skip_update_fs, False):
            this.UpdateFileSystem()

        return this.FileSystem.Tree.ToFilePaths(remove_root)


ARC_reflection = _expr3873

def ARC__ctor_5BB4A6F7(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None, cwl: None | None=None, fs: FileSystem | None=None) -> ARC:
    return ARC(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks, cwl, fs)


def ARCAux_getArcAssaysFromContracts(contracts: Array[Contract]) -> Array[ArcAssay]:
    def chooser(c: Contract, contracts: Any=contracts) -> ArcAssay | None:
        return ARCtrl_ArcAssay__ArcAssay_tryFromReadContract_Static_7570923F(c)

    return choose(chooser, contracts, None)


def ARCAux_getArcStudiesFromContracts(contracts: Array[Contract]) -> Array[tuple[ArcStudy, FSharpList[ArcAssay]]]:
    def chooser(c: Contract, contracts: Any=contracts) -> tuple[ArcStudy, FSharpList[ArcAssay]] | None:
        return ARCtrl_ArcStudy__ArcStudy_tryFromReadContract_Static_7570923F(c)

    return choose(chooser, contracts, None)


def ARCAux_getArcWorkflowsFromContracts(contracts: Array[Contract]) -> Array[ArcWorkflow]:
    def chooser(c: Contract, contracts: Any=contracts) -> ArcWorkflow | None:
        return ARCtrl_ArcWorkflow__ArcWorkflow_tryFromReadContract_Static_7570923F(c)

    return choose(chooser, contracts, None)


def ARCAux_getArcRunsFromContracts(contracts: Array[Contract]) -> Array[ArcRun]:
    def chooser(c: Contract, contracts: Any=contracts) -> ArcRun | None:
        return ARCtrl_ArcRun__ArcRun_tryFromReadContract_Static_7570923F(c)

    return choose(chooser, contracts, None)


def ARCAux_getAssayDataMapFromContracts(assay_identifier: str, contracts: Array[Contract]) -> DataMap | None:
    def chooser(c: Contract, assay_identifier: Any=assay_identifier, contracts: Any=contracts) -> DataMap | None:
        return ARCtrl_DataMap__DataMap_tryFromReadContractForAssay_Static(assay_identifier, c)

    return try_pick(chooser, contracts)


def ARCAux_getStudyDataMapFromContracts(study_identifier: str, contracts: Array[Contract]) -> DataMap | None:
    def chooser(c: Contract, study_identifier: Any=study_identifier, contracts: Any=contracts) -> DataMap | None:
        return ARCtrl_DataMap__DataMap_tryFromReadContractForStudy_Static(study_identifier, c)

    return try_pick(chooser, contracts)


def ARCAux_getWorkflowDataMapFromContracts(workflow_identifier: str, contracts: Array[Contract]) -> DataMap | None:
    def chooser(c: Contract, workflow_identifier: Any=workflow_identifier, contracts: Any=contracts) -> DataMap | None:
        return ARCtrl_DataMap__DataMap_tryFromReadContractForWorkflow_Static(workflow_identifier, c)

    return try_pick(chooser, contracts)


def ARCAux_getRunDataMapFromContracts(run_identifier: str, contracts: Array[Contract]) -> DataMap | None:
    def chooser(c: Contract, run_identifier: Any=run_identifier, contracts: Any=contracts) -> DataMap | None:
        return ARCtrl_DataMap__DataMap_tryFromReadContractForRun_Static(run_identifier, c)

    return try_pick(chooser, contracts)


def ARCAux_getArcInvestigationFromContracts(contracts: Array[Contract]) -> ArcInvestigation:
    def chooser(c: Contract, contracts: Any=contracts) -> ArcInvestigation | None:
        return ARCtrl_ArcInvestigation__ArcInvestigation_tryFromReadContract_Static_7570923F(c)

    return exactly_one(choose(chooser, contracts, None))


def ARCAux_updateFSByISA(isa: ArcInvestigation, fs: FileSystem) -> FileSystem:
    assays_folder: FileSystemTree
    def mapping(a: ArcAssay, isa: Any=isa, fs: Any=fs) -> FileSystemTree:
        return FileSystemTree.create_assay_folder(a.Identifier, a.DataMap is not None)

    assays: Array[FileSystemTree] = map_1(mapping, to_array(isa.Assays), None)
    assays_folder = FileSystemTree.create_assays_folder(assays)
    studies_folder: FileSystemTree
    def mapping_1(s: ArcStudy, isa: Any=isa, fs: Any=fs) -> FileSystemTree:
        return FileSystemTree.create_study_folder(s.Identifier, s.DataMap is not None)

    studies: Array[FileSystemTree] = map_1(mapping_1, to_array(isa.Studies), None)
    studies_folder = FileSystemTree.create_studies_folder(studies)
    workflows_folder: FileSystemTree
    def mapping_2(w: ArcWorkflow, isa: Any=isa, fs: Any=fs) -> FileSystemTree:
        return FileSystemTree.create_workflow_folder(ArcWorkflow__get_Identifier(w), ArcWorkflow__get_DataMap(w) is not None)

    workflows: Array[FileSystemTree] = map_1(mapping_2, to_array(isa.Workflows), None)
    workflows_folder = FileSystemTree.create_workflows_folder(workflows)
    runs_folder: FileSystemTree
    def mapping_3(r: ArcRun, isa: Any=isa, fs: Any=fs) -> FileSystemTree:
        return FileSystemTree.create_run_folder(r.Identifier, r.DataMap is not None)

    runs: Array[FileSystemTree] = map_1(mapping_3, to_array(isa.Runs), None)
    runs_folder = FileSystemTree.create_runs_folder(runs)
    investigation: FileSystemTree = FileSystemTree.create_investigation_file()
    tree_1: FileSystem
    tree: FileSystemTree = FileSystemTree.create_root_folder([investigation, assays_folder, studies_folder, workflows_folder, runs_folder])
    tree_1 = FileSystem.create(tree = tree)
    return fs.Union(tree_1)


def ARCAux_updateFSByCWL(cwl: None | None, fs: FileSystem) -> FileSystem:
    workflows: FileSystemTree = FileSystemTree.create_workflows_folder([])
    runs: FileSystemTree = FileSystemTree.create_runs_folder([])
    tree_1: FileSystem
    tree: FileSystemTree = FileSystemTree.create_root_folder([workflows, runs])
    tree_1 = FileSystem.create(tree = tree)
    return fs.Union(tree_1)


__all__ = ["ARC_reflection", "ARCAux_getArcAssaysFromContracts", "ARCAux_getArcStudiesFromContracts", "ARCAux_getArcWorkflowsFromContracts", "ARCAux_getArcRunsFromContracts", "ARCAux_getAssayDataMapFromContracts", "ARCAux_getStudyDataMapFromContracts", "ARCAux_getWorkflowDataMapFromContracts", "ARCAux_getRunDataMapFromContracts", "ARCAux_getArcInvestigationFromContracts", "ARCAux_updateFSByISA", "ARCAux_updateFSByCWL"]

