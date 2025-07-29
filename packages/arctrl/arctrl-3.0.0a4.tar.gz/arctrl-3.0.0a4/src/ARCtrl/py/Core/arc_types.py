from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.array_ import (contains as contains_1, remove_in_place, add_range_in_place)
from ..fable_modules.fable_library.option import (map, default_arg, value as value_5)
from ..fable_modules.fable_library.range import range_big_int
from ..fable_modules.fable_library.reflection import (TypeInfo, class_type)
from ..fable_modules.fable_library.resize_array import find_index
from ..fable_modules.fable_library.seq import (to_array, filter, contains, for_all, length, fold, to_list, delay, map as map_1, item, choose, exists, try_find_index, iterate, remove_at, try_find, append as append_4, collect)
from ..fable_modules.fable_library.seq2 import Array_distinct
from ..fable_modules.fable_library.string_ import (to_text, printf)
from ..fable_modules.fable_library.types import (Array, FSharpRef)
from ..fable_modules.fable_library.util import (string_hash, IEnumerable_1, get_enumerator, dispose, equals, safe_hash, to_enumerable, ignore)
from .comment import (Comment, Remark)
from .data_map import (DataMap, DataMap__Copy)
from .Helper.collections_ import (ResizeArray_map, ResizeArray_filter, ResizeArray_choose)
from .Helper.hash_codes import (box_hash_array, box_hash_option, box_hash_seq)
from .Helper.identifier import check_valid_characters
from .ontology_annotation import OntologyAnnotation
from .ontology_source_reference import OntologySourceReference
from .person import Person
from .Process.component import Component
from .Process.protocol_parameter import ProtocolParameter
from .publication import Publication
from .Table.arc_table import ArcTable
from .Table.arc_tables import (ArcTables, ArcTables_reflection, ArcTablesAux_getIOMap, ArcTablesAux_applyIOMap)
from .Table.composite_cell import CompositeCell
from .Table.composite_column import CompositeColumn
from .Table.composite_header import CompositeHeader

def _expr948() -> TypeInfo:
    return class_type("ARCtrl.ArcAssay", None, ArcAssay, ArcTables_reflection())


class ArcAssay(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        performers_1: Array[Person] = default_arg(performers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        def _arrow947(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_0040129: str = _arrow947()
        self.title_0040133: str | None = title
        self.description_0040134: str | None = description
        self.investigation: ArcInvestigation | None = None
        self.measurement_type_0040136: OntologyAnnotation | None = measurement_type
        self.technology_type_0040137: OntologyAnnotation | None = technology_type
        self.technology_platform_0040138: OntologyAnnotation | None = technology_platform
        self.data_map: DataMap | None = datamap
        self.performers_0040140_002D1: Array[Person] = performers_1
        self.comments_0040141_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcAssay = self
        return this.identifier_0040129

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcAssay = self
        this.identifier_0040129 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcAssay = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcAssay = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcAssay = self
        return this.title_0040133

    @Title.setter
    def Title(self, t: str | None=None) -> None:
        this: ArcAssay = self
        this.title_0040133 = t

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcAssay = self
        return this.description_0040134

    @Description.setter
    def Description(self, d: str | None=None) -> None:
        this: ArcAssay = self
        this.description_0040134 = d

    @property
    def MeasurementType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.measurement_type_0040136

    @MeasurementType.setter
    def MeasurementType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.measurement_type_0040136 = n

    @property
    def TechnologyType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.technology_type_0040137

    @TechnologyType.setter
    def TechnologyType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.technology_type_0040137 = n

    @property
    def TechnologyPlatform(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcAssay = self
        return this.technology_platform_0040138

    @TechnologyPlatform.setter
    def TechnologyPlatform(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcAssay = self
        this.technology_platform_0040138 = n

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcAssay = self
        return this.data_map

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcAssay = self
        this.data_map = n

    @property
    def Performers(self, __unit: None=None) -> Array[Person]:
        this: ArcAssay = self
        return this.performers_0040140_002D1

    @Performers.setter
    def Performers(self, n: Array[Person]) -> None:
        this: ArcAssay = self
        this.performers_0040140_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcAssay = self
        return this.comments_0040141_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcAssay = self
        this.comments_0040141_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcAssay = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcAssay = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcAssay:
        return ArcAssay(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcAssay:
        return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, measurement_type: OntologyAnnotation | None, technology_type: OntologyAnnotation | None, technology_platform: OntologyAnnotation | None, tables: Array[ArcTable], datamap: DataMap | None, performers: Array[Person], comments: Array[Comment]) -> ArcAssay:
        return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)

    @staticmethod
    def FileName() -> str:
        return "isa.assay.xlsx"

    @property
    def StudiesRegisteredIn(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcAssay = self
        match_value: ArcInvestigation | None = this.Investigation
        if match_value is None:
            return []

        else: 
            i: ArcInvestigation = match_value
            def predicate(s: ArcStudy) -> bool:
                source: Array[str] = s.RegisteredAssayIdentifiers
                class ObjectExpr899:
                    @property
                    def Equals(self) -> Callable[[str, str], bool]:
                        def _arrow898(x: str, y: str) -> bool:
                            return x == y

                        return _arrow898

                    @property
                    def GetHashCode(self) -> Callable[[str], int]:
                        return string_hash

                return contains(this.Identifier, source, ObjectExpr899())

            return to_array(filter(predicate, i.Studies))


    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow900(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.AddTable(table, index)
            return c

        return _arrow900

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow901(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow901

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcAssay], tuple[ArcAssay, ArcTable]]:
        def _arrow902(assay: ArcAssay) -> tuple[ArcAssay, ArcTable]:
            c: ArcAssay = assay.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow902

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow903(assay: ArcAssay) -> ArcAssay:
            c: ArcAssay = assay.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow903

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcAssay], ArcTable]:
        def _arrow904(assay: ArcAssay) -> ArcTable:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetTableAt(index)

        return _arrow904

    @staticmethod
    def get_table(name: str) -> Callable[[ArcAssay], ArcTable]:
        def _arrow905(assay: ArcAssay) -> ArcTable:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetTable(name)

        return _arrow905

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow906(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateTableAt(index, table)
            return new_assay

        return _arrow906

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow907(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateTable(name, table)
            return new_assay

        return _arrow907

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow908(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.SetTableAt(index, table)
            return new_assay

        return _arrow908

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow909(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.SetTable(name, table)
            return new_assay

        return _arrow909

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow910(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveTableAt(index)
            return new_assay

        return _arrow910

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow911(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveTable(name)
            return new_assay

        return _arrow911

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow912(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.MapTableAt(index, update_fun)
            return new_assay

        return _arrow912

    @staticmethod
    def update_table_by(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow913(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.MapTable(name, update_fun)
            return new_assay

        return _arrow913

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow914(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RenameTableAt(index, new_name)
            return new_assay

        return _arrow914

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow915(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RenameTable(name, new_name)
            return new_assay

        return _arrow915

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow916(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_assay

        return _arrow916

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow917(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_assay

        return _arrow917

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow918(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumnAt(table_index, column_index)
            return new_assay

        return _arrow918

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow919(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumn(table_name, column_index)
            return new_assay

        return _arrow919

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow920(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateColumnAt(table_index, column_index, header, cells)
            return new_assay

        return _arrow920

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow921(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateColumn(table_name, column_index, header, cells)
            return new_assay

        return _arrow921

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcAssay], CompositeColumn]:
        def _arrow922(assay: ArcAssay) -> CompositeColumn:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetColumnAt(table_index, column_index)

        return _arrow922

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcAssay], CompositeColumn]:
        def _arrow923(assay: ArcAssay) -> CompositeColumn:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetColumn(table_name, column_index)

        return _arrow923

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow924(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddRowAt(table_index, cells, row_index)
            return new_assay

        return _arrow924

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow925(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.AddRow(table_name, cells, row_index)
            return new_assay

        return _arrow925

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow926(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveColumnAt(table_index, row_index)
            return new_assay

        return _arrow926

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow927(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.RemoveRow(table_name, row_index)
            return new_assay

        return _arrow927

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow928(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateRowAt(table_index, row_index, cells)
            return new_assay

        return _arrow928

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcAssay], ArcAssay]:
        def _arrow929(assay: ArcAssay) -> ArcAssay:
            new_assay: ArcAssay = assay.Copy()
            new_assay.UpdateRow(table_name, row_index, cells)
            return new_assay

        return _arrow929

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcAssay], Array[CompositeCell]]:
        def _arrow930(assay: ArcAssay) -> Array[CompositeCell]:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetRowAt(table_index, row_index)

        return _arrow930

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcAssay], Array[CompositeCell]]:
        def _arrow931(assay: ArcAssay) -> Array[CompositeCell]:
            new_assay: ArcAssay = assay.Copy()
            return new_assay.GetRow(table_name, row_index)

        return _arrow931

    @staticmethod
    def set_performers(performers: Array[Person], assay: ArcAssay) -> ArcAssay:
        assay.Performers = performers
        return assay

    def Copy(self, __unit: None=None) -> ArcAssay:
        this: ArcAssay = self
        def f(c: ArcTable) -> ArcTable:
            return c.Copy()

        next_tables: Array[ArcTable] = ResizeArray_map(f, this.Tables)
        def f_1(c_1: Comment) -> Comment:
            return c_1.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f_1, this.Comments)
        next_data_map: DataMap | None = map(DataMap__Copy, this.DataMap)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_performers: Array[Person] = ResizeArray_map(f_2, this.Performers)
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        measurement_type: OntologyAnnotation | None = this.MeasurementType
        technology_type: OntologyAnnotation | None = this.TechnologyType
        technology_platform: OntologyAnnotation | None = this.TechnologyPlatform
        return ArcAssay.make(identifier, title, description, measurement_type, technology_type, technology_platform, next_tables, next_data_map, next_performers, next_comments)

    def UpdateBy(self, assay: ArcAssay, only_replace_existing: bool | None=None, append_sequences: bool | None=None) -> None:
        this: ArcAssay = self
        only_replace_existing_1: bool = default_arg(only_replace_existing, False)
        append_sequences_1: bool = default_arg(append_sequences, False)
        update_always: bool = not only_replace_existing_1
        if True if (assay.Title is not None) else update_always:
            this.Title = assay.Title

        if True if (assay.Description is not None) else update_always:
            this.Description = assay.Description

        if True if (assay.MeasurementType is not None) else update_always:
            this.MeasurementType = assay.MeasurementType

        if True if (assay.TechnologyType is not None) else update_always:
            this.TechnologyType = assay.TechnologyType

        if True if (assay.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = assay.TechnologyPlatform

        if True if (len(assay.Tables) != 0) else update_always:
            s: Array[ArcTable]
            origin: Array[ArcTable] = this.Tables
            next_1: Array[ArcTable] = assay.Tables
            if not append_sequences_1:
                def f(x: ArcTable) -> ArcTable:
                    return x

                s = ResizeArray_map(f, next_1)

            else: 
                combined: Array[ArcTable] = []
                enumerator: Any = get_enumerator(origin)
                try: 
                    while enumerator.System_Collections_IEnumerator_MoveNext():
                        e: ArcTable = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr932:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e, combined, ObjectExpr932()):
                            (combined.append(e))


                finally: 
                    dispose(enumerator)

                enumerator_1: Any = get_enumerator(next_1)
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        e_1: ArcTable = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr933:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_1, combined, ObjectExpr933()):
                            (combined.append(e_1))


                finally: 
                    dispose(enumerator_1)

                s = combined

            this.Tables = s

        if True if (len(assay.Performers) != 0) else update_always:
            s_1: Array[Person]
            origin_1: Array[Person] = this.Performers
            next_1_1: Array[Person] = assay.Performers
            if not append_sequences_1:
                def f_1(x_3: Person) -> Person:
                    return x_3

                s_1 = ResizeArray_map(f_1, next_1_1)

            else: 
                combined_1: Array[Person] = []
                enumerator_2: Any = get_enumerator(origin_1)
                try: 
                    while enumerator_2.System_Collections_IEnumerator_MoveNext():
                        e_2: Person = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr934:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_2, combined_1, ObjectExpr934()):
                            (combined_1.append(e_2))


                finally: 
                    dispose(enumerator_2)

                enumerator_1_1: Any = get_enumerator(next_1_1)
                try: 
                    while enumerator_1_1.System_Collections_IEnumerator_MoveNext():
                        e_1_1: Person = enumerator_1_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr935:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_1_1, combined_1, ObjectExpr935()):
                            (combined_1.append(e_1_1))


                finally: 
                    dispose(enumerator_1_1)

                s_1 = combined_1

            this.Performers = s_1

        if True if (len(assay.Comments) != 0) else update_always:
            s_2: Array[Comment]
            origin_2: Array[Comment] = this.Comments
            next_1_2: Array[Comment] = assay.Comments
            if not append_sequences_1:
                def f_2(x_6: Comment) -> Comment:
                    return x_6

                s_2 = ResizeArray_map(f_2, next_1_2)

            else: 
                combined_2: Array[Comment] = []
                enumerator_3: Any = get_enumerator(origin_2)
                try: 
                    while enumerator_3.System_Collections_IEnumerator_MoveNext():
                        e_3: Comment = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr936:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_3, combined_2, ObjectExpr936()):
                            (combined_2.append(e_3))


                finally: 
                    dispose(enumerator_3)

                enumerator_1_2: Any = get_enumerator(next_1_2)
                try: 
                    while enumerator_1_2.System_Collections_IEnumerator_MoveNext():
                        e_1_2: Comment = enumerator_1_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr937:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_1_2, combined_2, ObjectExpr937()):
                            (combined_2.append(e_1_2))


                finally: 
                    dispose(enumerator_1_2)

                s_2 = combined_2

            this.Comments = s_2


    def __str__(self, __unit: None=None) -> str:
        this: ArcAssay = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: OntologyAnnotation | None = this.MeasurementType
        arg_4: OntologyAnnotation | None = this.TechnologyType
        arg_5: OntologyAnnotation | None = this.TechnologyPlatform
        arg_6: Array[ArcTable] = this.Tables
        arg_7: Array[Person] = this.Performers
        arg_8: Array[Comment] = this.Comments
        return to_text(printf("ArcAssay({\r\n    Identifier = \"%s\",\r\n    Title = %A,\r\n    Description = %A,\r\n    MeasurementType = %A,\r\n    TechnologyType = %A,\r\n    TechnologyPlatform = %A,\r\n    Tables = %A,\r\n    Performers = %A,\r\n    Comments = %A\r\n})"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcAssay = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcAssay = self
        this.Investigation = None

    def UpdateReferenceByAssayFile(self, assay: ArcAssay, only_replace_existing: bool | None=None) -> None:
        this: ArcAssay = self
        update_always: bool = not default_arg(only_replace_existing, False)
        if True if (assay.Title is not None) else update_always:
            this.Title = assay.Title

        if True if (assay.Description is not None) else update_always:
            this.Description = assay.Description

        if True if (assay.MeasurementType is not None) else update_always:
            this.MeasurementType = assay.MeasurementType

        if True if (assay.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = assay.TechnologyPlatform

        if True if (assay.TechnologyType is not None) else update_always:
            this.TechnologyType = assay.TechnologyType

        if True if (len(assay.Tables) != 0) else update_always:
            this.Tables = assay.Tables

        if True if (len(assay.Comments) != 0) else update_always:
            this.Comments = assay.Comments

        this.DataMap = assay.DataMap
        if True if (len(assay.Performers) != 0) else update_always:
            this.Performers = assay.Performers


    def StructurallyEquals(self, other: ArcAssay) -> bool:
        this: ArcAssay = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow940(__unit: None=None) -> bool:
            a: IEnumerable_1[ArcTable] = this.Tables
            b: IEnumerable_1[ArcTable] = other.Tables
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow939(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow938(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow938, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow939))) if (length(a) == length(b)) else False

        def _arrow943(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Performers
            b_1: IEnumerable_1[Person] = other.Performers
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow942(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow941(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow941, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow942))) if (length(a_1) == length(b_1)) else False

        def _arrow946(__unit: None=None) -> bool:
            a_2: IEnumerable_1[Comment] = this.Comments
            b_2: IEnumerable_1[Comment] = other.Comments
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow945(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow944(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow944, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow945))) if (length(a_2) == length(b_2)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.MeasurementType, other.MeasurementType), equals(this.TechnologyType, other.TechnologyType), equals(this.TechnologyPlatform, other.TechnologyPlatform), equals(this.DataMap, other.DataMap), _arrow940(), _arrow943(), _arrow946()]))

    def ReferenceEquals(self, other: ArcAssay) -> bool:
        this: ArcAssay = self
        return this is other

    def __eq__(self, other: Any=None) -> bool:
        this: ArcAssay = self
        return this.StructurallyEquals(other) if isinstance(other, ArcAssay) else False

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcAssay = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcAssay = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_option(this.DataMap), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])


ArcAssay_reflection = _expr948

def ArcAssay__ctor_11E1F34(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcAssay:
    return ArcAssay(identifier, title, description, measurement_type, technology_type, technology_platform, tables, datamap, performers, comments)


def _expr1017() -> TypeInfo:
    return class_type("ARCtrl.ArcStudy", None, ArcStudy, ArcTables_reflection())


class ArcStudy(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        publications_1: Array[Publication] = default_arg(publications, [])
        contacts_1: Array[Person] = default_arg(contacts, [])
        study_design_descriptors_1: Array[OntologyAnnotation] = default_arg(study_design_descriptors, [])
        registered_assay_identifiers_1: Array[str] = default_arg(registered_assay_identifiers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        def _arrow1016(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_0040579: str = _arrow1016()
        self.investigation: ArcInvestigation | None = None
        self.title_0040584: str | None = title
        self.description_0040585: str | None = description
        self.submission_date_0040586: str | None = submission_date
        self.public_release_date_0040587: str | None = public_release_date
        self.publications_0040588_002D1: Array[Publication] = publications_1
        self.contacts_0040589_002D1: Array[Person] = contacts_1
        self.study_design_descriptors_0040590_002D1: Array[OntologyAnnotation] = study_design_descriptors_1
        self.datamap_0040591: DataMap | None = datamap
        self.registered_assay_identifiers_0040592_002D1: Array[str] = registered_assay_identifiers_1
        self.comments_0040593_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcStudy = self
        return this.identifier_0040579

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcStudy = self
        this.identifier_0040579 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcStudy = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcStudy = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.title_0040584

    @Title.setter
    def Title(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.title_0040584 = n

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.description_0040585

    @Description.setter
    def Description(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.description_0040585 = n

    @property
    def SubmissionDate(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.submission_date_0040586

    @SubmissionDate.setter
    def SubmissionDate(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.submission_date_0040586 = n

    @property
    def PublicReleaseDate(self, __unit: None=None) -> str | None:
        this: ArcStudy = self
        return this.public_release_date_0040587

    @PublicReleaseDate.setter
    def PublicReleaseDate(self, n: str | None=None) -> None:
        this: ArcStudy = self
        this.public_release_date_0040587 = n

    @property
    def Publications(self, __unit: None=None) -> Array[Publication]:
        this: ArcStudy = self
        return this.publications_0040588_002D1

    @Publications.setter
    def Publications(self, n: Array[Publication]) -> None:
        this: ArcStudy = self
        this.publications_0040588_002D1 = n

    @property
    def Contacts(self, __unit: None=None) -> Array[Person]:
        this: ArcStudy = self
        return this.contacts_0040589_002D1

    @Contacts.setter
    def Contacts(self, n: Array[Person]) -> None:
        this: ArcStudy = self
        this.contacts_0040589_002D1 = n

    @property
    def StudyDesignDescriptors(self, __unit: None=None) -> Array[OntologyAnnotation]:
        this: ArcStudy = self
        return this.study_design_descriptors_0040590_002D1

    @StudyDesignDescriptors.setter
    def StudyDesignDescriptors(self, n: Array[OntologyAnnotation]) -> None:
        this: ArcStudy = self
        this.study_design_descriptors_0040590_002D1 = n

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcStudy = self
        return this.datamap_0040591

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcStudy = self
        this.datamap_0040591 = n

    @property
    def RegisteredAssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcStudy = self
        return this.registered_assay_identifiers_0040592_002D1

    @RegisteredAssayIdentifiers.setter
    def RegisteredAssayIdentifiers(self, n: Array[str]) -> None:
        this: ArcStudy = self
        this.registered_assay_identifiers_0040592_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcStudy = self
        return this.comments_0040593_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcStudy = self
        this.comments_0040593_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcStudy = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcStudy:
        return ArcStudy(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> ArcStudy:
        return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, submission_date: str | None, public_release_date: str | None, publications: Array[Publication], contacts: Array[Person], study_design_descriptors: Array[OntologyAnnotation], tables: Array[ArcTable], datamap: DataMap | None, registered_assay_identifiers: Array[str], comments: Array[Comment]) -> ArcStudy:
        return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)

    @property
    def is_empty(self, __unit: None=None) -> bool:
        this: ArcStudy = self
        return (len(this.Comments) == 0) if ((len(this.RegisteredAssayIdentifiers) == 0) if ((len(this.Tables) == 0) if ((len(this.StudyDesignDescriptors) == 0) if ((len(this.Contacts) == 0) if ((len(this.Publications) == 0) if (equals(this.PublicReleaseDate, None) if (equals(this.SubmissionDate, None) if (equals(this.Description, None) if equals(this.Title, None) else False) else False) else False) else False) else False) else False) else False) else False) else False

    @staticmethod
    def FileName() -> str:
        return "isa.study.xlsx"

    @property
    def RegisteredAssayIdentifierCount(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return len(this.RegisteredAssayIdentifiers)

    @property
    def RegisteredAssayCount(self, __unit: None=None) -> int:
        this: ArcStudy = self
        return len(this.RegisteredAssays)

    @property
    def RegisteredAssays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def chooser(assay_identifier: str) -> ArcAssay | None:
            return inv.TryGetAssay(assay_identifier)

        return list(choose(chooser, this.RegisteredAssayIdentifiers))

    @property
    def VacantAssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def predicate(arg: str) -> bool:
            return not inv.ContainsAssay(arg)

        return list(filter(predicate, this.RegisteredAssayIdentifiers))

    def AddRegisteredAssay(self, assay: ArcAssay) -> None:
        this: ArcStudy = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        inv.AddAssay(assay)
        inv.RegisterAssay(this.Identifier, assay.Identifier)

    @staticmethod
    def add_registered_assay(assay: ArcAssay) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow949(study: ArcStudy) -> ArcStudy:
            new_study: ArcStudy = study.Copy()
            new_study.AddRegisteredAssay(assay)
            return new_study

        return _arrow949

    def InitRegisteredAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcStudy = self
        assay: ArcAssay = ArcAssay(assay_identifier)
        this.AddRegisteredAssay(assay)
        return assay

    @staticmethod
    def init_registered_assay(assay_identifier: str) -> Callable[[ArcStudy], tuple[ArcStudy, ArcAssay]]:
        def _arrow950(study: ArcStudy) -> tuple[ArcStudy, ArcAssay]:
            copy: ArcStudy = study.Copy()
            return (copy, copy.InitRegisteredAssay(assay_identifier))

        return _arrow950

    def RegisterAssay(self, assay_identifier: str) -> None:
        this: ArcStudy = self
        class ObjectExpr952:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow951(x: str, y: str) -> bool:
                    return x == y

                return _arrow951

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr952()):
            raise Exception(("Assay `" + assay_identifier) + "` is already registered on the study.")

        (this.RegisteredAssayIdentifiers.append(assay_identifier))

    @staticmethod
    def register_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow953(study: ArcStudy) -> ArcStudy:
            copy: ArcStudy = study.Copy()
            copy.RegisterAssay(assay_identifier)
            return copy

        return _arrow953

    def DeregisterAssay(self, assay_identifier: str) -> None:
        this: ArcStudy = self
        class ObjectExpr955:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow954(x: str, y: str) -> bool:
                    return x == y

                return _arrow954

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        ignore(remove_in_place(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr955()))

    @staticmethod
    def deregister_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow956(study: ArcStudy) -> ArcStudy:
            copy: ArcStudy = study.Copy()
            copy.DeregisterAssay(assay_identifier)
            return copy

        return _arrow956

    def GetRegisteredAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcStudy = self
        class ObjectExpr958:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow957(x: str, y: str) -> bool:
                    return x == y

                return _arrow957

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if not contains(assay_identifier, this.RegisteredAssayIdentifiers, ObjectExpr958()):
            raise Exception(("Assay `" + assay_identifier) + "` is not registered on the study.")

        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        return inv.GetAssay(assay_identifier)

    @staticmethod
    def get_registered_assay(assay_identifier: str) -> Callable[[ArcStudy], ArcAssay]:
        def _arrow959(study: ArcStudy) -> ArcAssay:
            copy: ArcStudy = study.Copy()
            return copy.GetRegisteredAssay(assay_identifier)

        return _arrow959

    @staticmethod
    def get_registered_assays(__unit: None=None) -> Callable[[ArcStudy], Array[ArcAssay]]:
        def _arrow960(study: ArcStudy) -> Array[ArcAssay]:
            copy: ArcStudy = study.Copy()
            return copy.RegisteredAssays

        return _arrow960

    def GetRegisteredAssaysOrIdentifier(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcStudy = self
        match_value: ArcInvestigation | None = this.Investigation
        if match_value is None:
            def f_1(identifier_1: str) -> ArcAssay:
                return ArcAssay.init(identifier_1)

            return ResizeArray_map(f_1, this.RegisteredAssayIdentifiers)

        else: 
            i: ArcInvestigation = match_value
            def f(identifier: str) -> ArcAssay:
                match_value_1: ArcAssay | None = i.TryGetAssay(identifier)
                if match_value_1 is None:
                    return ArcAssay.init(identifier)

                else: 
                    return match_value_1


            return ResizeArray_map(f, this.RegisteredAssayIdentifiers)


    @staticmethod
    def get_registered_assays_or_identifier(__unit: None=None) -> Callable[[ArcStudy], Array[ArcAssay]]:
        def _arrow961(study: ArcStudy) -> Array[ArcAssay]:
            copy: ArcStudy = study.Copy()
            return copy.GetRegisteredAssaysOrIdentifier()

        return _arrow961

    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow962(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.AddTable(table, index)
            return c

        return _arrow962

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow963(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow963

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcStudy], tuple[ArcStudy, ArcTable]]:
        def _arrow964(study: ArcStudy) -> tuple[ArcStudy, ArcTable]:
            c: ArcStudy = study.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow964

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow965(study: ArcStudy) -> ArcStudy:
            c: ArcStudy = study.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow965

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcStudy], ArcTable]:
        def _arrow967(study: ArcStudy) -> ArcTable:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetTableAt(index)

        return _arrow967

    @staticmethod
    def get_table(name: str) -> Callable[[ArcStudy], ArcTable]:
        def _arrow968(study: ArcStudy) -> ArcTable:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetTable(name)

        return _arrow968

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow969(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateTableAt(index, table)
            return new_assay

        return _arrow969

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow970(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateTable(name, table)
            return new_assay

        return _arrow970

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow971(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.SetTableAt(index, table)
            return new_assay

        return _arrow971

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow973(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.SetTable(name, table)
            return new_assay

        return _arrow973

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow974(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveTableAt(index)
            return new_assay

        return _arrow974

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow975(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveTable(name)
            return new_assay

        return _arrow975

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow976(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.MapTableAt(index, update_fun)
            return new_assay

        return _arrow976

    @staticmethod
    def map_table(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow979(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.MapTable(name, update_fun)
            return new_assay

        return _arrow979

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow980(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RenameTableAt(index, new_name)
            return new_assay

        return _arrow980

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow981(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RenameTable(name, new_name)
            return new_assay

        return _arrow981

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow982(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_assay

        return _arrow982

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow983(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_assay

        return _arrow983

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow984(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumnAt(table_index, column_index)
            return new_assay

        return _arrow984

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow985(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumn(table_name, column_index)
            return new_assay

        return _arrow985

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow986(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateColumnAt(table_index, column_index, header, cells)
            return new_assay

        return _arrow986

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow987(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateColumn(table_name, column_index, header, cells)
            return new_assay

        return _arrow987

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcStudy], CompositeColumn]:
        def _arrow988(study: ArcStudy) -> CompositeColumn:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetColumnAt(table_index, column_index)

        return _arrow988

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcStudy], CompositeColumn]:
        def _arrow989(study: ArcStudy) -> CompositeColumn:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetColumn(table_name, column_index)

        return _arrow989

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow990(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddRowAt(table_index, cells, row_index)
            return new_assay

        return _arrow990

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow991(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.AddRow(table_name, cells, row_index)
            return new_assay

        return _arrow991

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow992(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveColumnAt(table_index, row_index)
            return new_assay

        return _arrow992

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow993(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.RemoveRow(table_name, row_index)
            return new_assay

        return _arrow993

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow994(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateRowAt(table_index, row_index, cells)
            return new_assay

        return _arrow994

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcStudy], ArcStudy]:
        def _arrow995(study: ArcStudy) -> ArcStudy:
            new_assay: ArcStudy = study.Copy()
            new_assay.UpdateRow(table_name, row_index, cells)
            return new_assay

        return _arrow995

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcStudy], Array[CompositeCell]]:
        def _arrow996(study: ArcStudy) -> Array[CompositeCell]:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetRowAt(table_index, row_index)

        return _arrow996

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcStudy], Array[CompositeCell]]:
        def _arrow997(study: ArcStudy) -> Array[CompositeCell]:
            new_assay: ArcStudy = study.Copy()
            return new_assay.GetRow(table_name, row_index)

        return _arrow997

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcStudy = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcStudy = self
        this.Investigation = None

    def Copy(self, copy_investigation_ref: bool | None=None) -> ArcStudy:
        this: ArcStudy = self
        copy_investigation_ref_1: bool = default_arg(copy_investigation_ref, False)
        next_tables: Array[ArcTable] = []
        next_assay_identifiers: Array[str] = list(this.RegisteredAssayIdentifiers)
        enumerator: Any = get_enumerator(this.Tables)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                table: ArcTable = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                copy: ArcTable = table.Copy()
                (next_tables.append(copy))

        finally: 
            dispose(enumerator)

        def f(c: Comment) -> Comment:
            return c.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f, this.Comments)
        def f_1(c_1: Person) -> Person:
            return c_1.Copy()

        next_contacts: Array[Person] = ResizeArray_map(f_1, this.Contacts)
        def f_2(c_2: Publication) -> Publication:
            return c_2.Copy()

        next_publications: Array[Publication] = ResizeArray_map(f_2, this.Publications)
        def f_3(c_3: OntologyAnnotation) -> OntologyAnnotation:
            return c_3.Copy()

        next_study_design_descriptors: Array[OntologyAnnotation] = ResizeArray_map(f_3, this.StudyDesignDescriptors)
        next_data_map: DataMap | None = map(DataMap__Copy, this.DataMap)
        study: ArcStudy
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        submission_date: str | None = this.SubmissionDate
        public_release_date: str | None = this.PublicReleaseDate
        study = ArcStudy.make(identifier, title, description, submission_date, public_release_date, next_publications, next_contacts, next_study_design_descriptors, next_tables, next_data_map, next_assay_identifiers, next_comments)
        if copy_investigation_ref_1:
            study.Investigation = this.Investigation

        return study

    def UpdateReferenceByStudyFile(self, study: ArcStudy, only_replace_existing: bool | None=None, keep_unused_ref_tables: bool | None=None) -> None:
        this: ArcStudy = self
        update_always: bool = not default_arg(only_replace_existing, False)
        if True if (study.Title is not None) else update_always:
            this.Title = study.Title

        if True if (study.Description is not None) else update_always:
            this.Description = study.Description

        if True if (study.SubmissionDate is not None) else update_always:
            this.SubmissionDate = study.SubmissionDate

        if True if (study.PublicReleaseDate is not None) else update_always:
            this.PublicReleaseDate = study.PublicReleaseDate

        if True if (len(study.Publications) != 0) else update_always:
            this.Publications = study.Publications

        if True if (len(study.Contacts) != 0) else update_always:
            this.Contacts = study.Contacts

        if True if (len(study.StudyDesignDescriptors) != 0) else update_always:
            this.StudyDesignDescriptors = study.StudyDesignDescriptors

        if True if (len(study.Tables) != 0) else update_always:
            tables: ArcTables = ArcTables.update_reference_tables_by_sheets(ArcTables(this.Tables), ArcTables(study.Tables), keep_unused_ref_tables)
            this.Tables = tables.Tables

        this.DataMap = study.DataMap
        if True if (len(study.RegisteredAssayIdentifiers) != 0) else update_always:
            this.RegisteredAssayIdentifiers = study.RegisteredAssayIdentifiers

        if True if (len(study.Comments) != 0) else update_always:
            this.Comments = study.Comments


    def StructurallyEquals(self, other: ArcStudy) -> bool:
        this: ArcStudy = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow1000(__unit: None=None) -> bool:
            a: IEnumerable_1[Publication] = this.Publications
            b: IEnumerable_1[Publication] = other.Publications
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow999(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow998(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow998, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow999))) if (length(a) == length(b)) else False

        def _arrow1003(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Contacts
            b_1: IEnumerable_1[Person] = other.Contacts
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow1002(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1001(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow1001, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow1002))) if (length(a_1) == length(b_1)) else False

        def _arrow1006(__unit: None=None) -> bool:
            a_2: IEnumerable_1[OntologyAnnotation] = this.StudyDesignDescriptors
            b_2: IEnumerable_1[OntologyAnnotation] = other.StudyDesignDescriptors
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow1005(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1004(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow1004, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow1005))) if (length(a_2) == length(b_2)) else False

        def _arrow1009(__unit: None=None) -> bool:
            a_3: IEnumerable_1[ArcTable] = this.Tables
            b_3: IEnumerable_1[ArcTable] = other.Tables
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow1008(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1007(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow1007, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow1008))) if (length(a_3) == length(b_3)) else False

        def _arrow1012(__unit: None=None) -> bool:
            a_4: IEnumerable_1[str] = this.RegisteredAssayIdentifiers
            b_4: IEnumerable_1[str] = other.RegisteredAssayIdentifiers
            def folder_4(acc_4: bool, e_4: bool) -> bool:
                if acc_4:
                    return e_4

                else: 
                    return False


            def _arrow1011(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1010(i_5: int) -> bool:
                    return item(i_5, a_4) == item(i_5, b_4)

                return map_1(_arrow1010, range_big_int(0, 1, length(a_4) - 1))

            return fold(folder_4, True, to_list(delay(_arrow1011))) if (length(a_4) == length(b_4)) else False

        def _arrow1015(__unit: None=None) -> bool:
            a_5: IEnumerable_1[Comment] = this.Comments
            b_5: IEnumerable_1[Comment] = other.Comments
            def folder_5(acc_5: bool, e_5: bool) -> bool:
                if acc_5:
                    return e_5

                else: 
                    return False


            def _arrow1014(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1013(i_6: int) -> bool:
                    return equals(item(i_6, a_5), item(i_6, b_5))

                return map_1(_arrow1013, range_big_int(0, 1, length(a_5) - 1))

            return fold(folder_5, True, to_list(delay(_arrow1014))) if (length(a_5) == length(b_5)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.SubmissionDate, other.SubmissionDate), equals(this.PublicReleaseDate, other.PublicReleaseDate), equals(this.DataMap, other.DataMap), _arrow1000(), _arrow1003(), _arrow1006(), _arrow1009(), _arrow1012(), _arrow1015()]))

    def ReferenceEquals(self, other: ArcStudy) -> bool:
        this: ArcStudy = self
        return this is other

    def __str__(self, __unit: None=None) -> str:
        this: ArcStudy = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: str | None = this.SubmissionDate
        arg_4: str | None = this.PublicReleaseDate
        arg_5: Array[Publication] = this.Publications
        arg_6: Array[Person] = this.Contacts
        arg_7: Array[OntologyAnnotation] = this.StudyDesignDescriptors
        arg_8: Array[ArcTable] = this.Tables
        arg_9: Array[str] = this.RegisteredAssayIdentifiers
        arg_10: Array[Comment] = this.Comments
        return to_text(printf("ArcStudy {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    SubmissionDate = %A,\r\n    PublicReleaseDate = %A,\r\n    Publications = %A,\r\n    Contacts = %A,\r\n    StudyDesignDescriptors = %A,\r\n    Tables = %A,\r\n    RegisteredAssayIdentifiers = %A,\r\n    Comments = %A,\r\n}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcStudy = self
        return this.StructurallyEquals(other) if isinstance(other, ArcStudy) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcStudy = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_option(this.DataMap), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.StudyDesignDescriptors), box_hash_seq(this.Tables), box_hash_seq(this.RegisteredAssayIdentifiers), box_hash_seq(this.Comments)])

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcStudy = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.StudyDesignDescriptors), box_hash_seq(this.Tables), box_hash_seq(this.RegisteredAssayIdentifiers), box_hash_seq(this.Comments)])


ArcStudy_reflection = _expr1017

def ArcStudy__ctor_64321D5B(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, study_design_descriptors: Array[OntologyAnnotation] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, registered_assay_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None) -> ArcStudy:
    return ArcStudy(identifier, title, description, submission_date, public_release_date, publications, contacts, study_design_descriptors, tables, datamap, registered_assay_identifiers, comments)


def _expr1019() -> TypeInfo:
    return class_type("ARCtrl.ArcWorkflow", None, ArcWorkflow)


class ArcWorkflow:
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        def _arrow1018(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_00401151: str = _arrow1018()
        self.investigation: ArcInvestigation | None = None
        self.title_00401156: str | None = title
        self.description_00401157: str | None = description
        self.sub_workflow_identifiers_00401158: Array[str] = default_arg(sub_workflow_identifiers, [])
        self.workflow_type_00401159: OntologyAnnotation | None = workflow_type
        self.uri_00401160: str | None = uri
        self.version_00401161: str | None = version
        self.parameters_00401162: Array[ProtocolParameter] = default_arg(parameters, [])
        self.components_00401163: Array[Component] = default_arg(components, [])
        self.data_map: DataMap | None = datamap
        self.contacts_00401165: Array[Person] = default_arg(contacts, [])
        self.comments_00401166: Array[Comment] = default_arg(comments, [])
        self.static_hash: int = 0

    def __str__(self, __unit: None=None) -> str:
        this: ArcWorkflow = self
        arg: str = ArcWorkflow__get_Identifier(this)
        arg_1: str | None = ArcWorkflow__get_Title(this)
        arg_2: str | None = ArcWorkflow__get_Description(this)
        arg_3: OntologyAnnotation | None = ArcWorkflow__get_WorkflowType(this)
        arg_4: str | None = ArcWorkflow__get_URI(this)
        arg_5: str | None = ArcWorkflow__get_Version(this)
        arg_6: Array[str] = ArcWorkflow__get_SubWorkflowIdentifiers(this)
        arg_7: Array[ProtocolParameter] = ArcWorkflow__get_Parameters(this)
        arg_8: Array[Component] = ArcWorkflow__get_Components(this)
        arg_9: DataMap | None = ArcWorkflow__get_DataMap(this)
        arg_10: Array[Person] = ArcWorkflow__get_Contacts(this)
        arg_11: Array[Comment] = ArcWorkflow__get_Comments(this)
        return to_text(printf("ArcWorkflow {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    WorkflowType = %A,\r\n    URI = %A,\r\n    Version = %A,\r\n    SubWorkflowIdentifiers = %A,\r\n    Parameters = %A,\r\n    Components = %A,\r\n    DataMap = %A,\r\n    Contacts = %A,\r\n    Comments = %A}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)(arg_11)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcWorkflow = self
        return ArcWorkflow__StructurallyEquals_Z1C75CB0E(this, other) if isinstance(other, ArcWorkflow) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcWorkflow = self
        return box_hash_array([ArcWorkflow__get_Identifier(this), box_hash_option(ArcWorkflow__get_Title(this)), box_hash_option(ArcWorkflow__get_Description(this)), box_hash_option(ArcWorkflow__get_WorkflowType(this)), box_hash_option(ArcWorkflow__get_URI(this)), box_hash_option(ArcWorkflow__get_Version(this)), box_hash_seq(ArcWorkflow__get_SubWorkflowIdentifiers(this)), box_hash_seq(ArcWorkflow__get_Parameters(this)), box_hash_seq(ArcWorkflow__get_Components(this)), box_hash_option(ArcWorkflow__get_DataMap(this)), box_hash_seq(ArcWorkflow__get_Contacts(this)), box_hash_seq(ArcWorkflow__get_Comments(this))])


ArcWorkflow_reflection = _expr1019

def ArcWorkflow__ctor_Z3BB02240(identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcWorkflow:
    return ArcWorkflow(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)


def _expr1075() -> TypeInfo:
    return class_type("ARCtrl.ArcRun", None, ArcRun, ArcTables_reflection())


class ArcRun(ArcTables):
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> None:
        super().__init__(default_arg(tables, []))
        performers_1: Array[Person] = default_arg(performers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        workflow_identifiers_1: Array[str] = default_arg(workflow_identifiers, [])
        def _arrow1074(__unit: None=None) -> str:
            identifier_1: str = identifier.strip()
            check_valid_characters(identifier_1)
            return identifier_1

        self.identifier_00401447: str = _arrow1074()
        self.title_00401451: str | None = title
        self.description_00401452: str | None = description
        self.investigation: ArcInvestigation | None = None
        self.measurement_type_00401454: OntologyAnnotation | None = measurement_type
        self.technology_type_00401455: OntologyAnnotation | None = technology_type
        self.technology_platform_00401456: OntologyAnnotation | None = technology_platform
        self.workflow_identifiers_00401457_002D1: Array[str] = workflow_identifiers_1
        self.data_map: DataMap | None = datamap
        self.performers_00401459_002D1: Array[Person] = performers_1
        self.comments_00401460_002D1: Array[Comment] = comments_1
        self.static_hash: int = 0

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcRun = self
        return this.identifier_00401447

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcRun = self
        this.identifier_00401447 = i

    @property
    def Investigation(self, __unit: None=None) -> ArcInvestigation | None:
        this: ArcRun = self
        return this.investigation

    @Investigation.setter
    def Investigation(self, i: ArcInvestigation | None=None) -> None:
        this: ArcRun = self
        this.investigation = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcRun = self
        return this.title_00401451

    @Title.setter
    def Title(self, t: str | None=None) -> None:
        this: ArcRun = self
        this.title_00401451 = t

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcRun = self
        return this.description_00401452

    @Description.setter
    def Description(self, d: str | None=None) -> None:
        this: ArcRun = self
        this.description_00401452 = d

    @property
    def MeasurementType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.measurement_type_00401454

    @MeasurementType.setter
    def MeasurementType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.measurement_type_00401454 = n

    @property
    def TechnologyType(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.technology_type_00401455

    @TechnologyType.setter
    def TechnologyType(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.technology_type_00401455 = n

    @property
    def TechnologyPlatform(self, __unit: None=None) -> OntologyAnnotation | None:
        this: ArcRun = self
        return this.technology_platform_00401456

    @TechnologyPlatform.setter
    def TechnologyPlatform(self, n: OntologyAnnotation | None=None) -> None:
        this: ArcRun = self
        this.technology_platform_00401456 = n

    @property
    def WorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcRun = self
        return this.workflow_identifiers_00401457_002D1

    @WorkflowIdentifiers.setter
    def WorkflowIdentifiers(self, w: Array[str]) -> None:
        this: ArcRun = self
        this.workflow_identifiers_00401457_002D1 = w

    @property
    def DataMap(self, __unit: None=None) -> DataMap | None:
        this: ArcRun = self
        return this.data_map

    @DataMap.setter
    def DataMap(self, n: DataMap | None=None) -> None:
        this: ArcRun = self
        this.data_map = n

    @property
    def Performers(self, __unit: None=None) -> Array[Person]:
        this: ArcRun = self
        return this.performers_00401459_002D1

    @Performers.setter
    def Performers(self, n: Array[Person]) -> None:
        this: ArcRun = self
        this.performers_00401459_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcRun = self
        return this.comments_00401460_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcRun = self
        this.comments_00401460_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcRun = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcRun = self
        this.static_hash = h or 0

    @staticmethod
    def init(identifier: str) -> ArcRun:
        return ArcRun(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcRun:
        return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, measurement_type: OntologyAnnotation | None, technology_type: OntologyAnnotation | None, technology_platform: OntologyAnnotation | None, workflow_identifiers: Array[str], tables: Array[ArcTable], datamap: DataMap | None, performers: Array[Person], comments: Array[Comment]) -> ArcRun:
        return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)

    @staticmethod
    def FileName() -> str:
        return "isa.run.xlsx"

    @property
    def WorkflowIdentifierCount(self, __unit: None=None) -> int:
        this: ArcRun = self
        return len(this.WorkflowIdentifiers)

    @property
    def WorkflowCount(self, __unit: None=None) -> int:
        this: ArcRun = self
        return len(this.Workflows)

    @property
    def Workflows(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcRun = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def chooser(workflow_identifier: str) -> ArcWorkflow | None:
            return inv.TryGetWorkflow(workflow_identifier)

        return list(choose(chooser, this.WorkflowIdentifiers))

    @property
    def VacantWorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcRun = self
        inv: ArcInvestigation
        investigation: ArcInvestigation | None = this.Investigation
        if investigation is not None:
            inv = investigation

        else: 
            raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

        def predicate(arg: str) -> bool:
            return not inv.ContainsWorkflow(arg)

        return list(filter(predicate, this.WorkflowIdentifiers))

    @staticmethod
    def add_table(table: ArcTable, index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1020(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.AddTable(table, index)
            return c

        return _arrow1020

    @staticmethod
    def add_tables(tables: IEnumerable_1[ArcTable], index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1021(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.AddTables(tables, index)
            return c

        return _arrow1021

    @staticmethod
    def init_table(table_name: str, index: int | None=None) -> Callable[[ArcRun], tuple[ArcRun, ArcTable]]:
        def _arrow1022(run: ArcRun) -> tuple[ArcRun, ArcTable]:
            c: ArcRun = run.Copy()
            return (c, c.InitTable(table_name, index))

        return _arrow1022

    @staticmethod
    def init_tables(table_names: IEnumerable_1[str], index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1023(run: ArcRun) -> ArcRun:
            c: ArcRun = run.Copy()
            c.InitTables(table_names, index)
            return c

        return _arrow1023

    @staticmethod
    def get_table_at(index: int) -> Callable[[ArcRun], ArcTable]:
        def _arrow1024(run: ArcRun) -> ArcTable:
            new_run: ArcRun = run.Copy()
            return new_run.GetTableAt(index)

        return _arrow1024

    @staticmethod
    def get_table(name: str) -> Callable[[ArcRun], ArcTable]:
        def _arrow1025(run: ArcRun) -> ArcTable:
            new_run: ArcRun = run.Copy()
            return new_run.GetTable(name)

        return _arrow1025

    @staticmethod
    def update_table_at(index: int, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow1026(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateTableAt(index, table)
            return new_run

        return _arrow1026

    @staticmethod
    def update_table(name: str, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow1027(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateTable(name, table)
            return new_run

        return _arrow1027

    @staticmethod
    def set_table_at(index: int, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow1028(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.SetTableAt(index, table)
            return new_run

        return _arrow1028

    @staticmethod
    def set_table(name: str, table: ArcTable) -> Callable[[ArcRun], ArcRun]:
        def _arrow1029(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.SetTable(name, table)
            return new_run

        return _arrow1029

    @staticmethod
    def remove_table_at(index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow1030(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveTableAt(index)
            return new_run

        return _arrow1030

    @staticmethod
    def remove_table(name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow1031(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveTable(name)
            return new_run

        return _arrow1031

    @staticmethod
    def map_table_at(index: int, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcRun], ArcRun]:
        def _arrow1032(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.MapTableAt(index, update_fun)
            return new_run

        return _arrow1032

    @staticmethod
    def update_table(name: str, update_fun: Callable[[ArcTable], None]) -> Callable[[ArcRun], ArcRun]:
        def _arrow1033(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.MapTable(name, update_fun)
            return new_run

        return _arrow1033

    @staticmethod
    def rename_table_at(index: int, new_name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow1034(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RenameTableAt(index, new_name)
            return new_run

        return _arrow1034

    @staticmethod
    def rename_table(name: str, new_name: str) -> Callable[[ArcRun], ArcRun]:
        def _arrow1035(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RenameTable(name, new_name)
            return new_run

        return _arrow1035

    @staticmethod
    def add_column_at(table_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1036(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddColumnAt(table_index, header, cells, column_index, force_replace)
            return new_run

        return _arrow1036

    @staticmethod
    def add_column(table_name: str, header: CompositeHeader, cells: Array[CompositeCell] | None=None, column_index: int | None=None, force_replace: bool | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1037(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddColumn(table_name, header, cells, column_index, force_replace)
            return new_run

        return _arrow1037

    @staticmethod
    def remove_column_at(table_index: int, column_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow1038(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumnAt(table_index, column_index)
            return new_run

        return _arrow1038

    @staticmethod
    def remove_column(table_name: str, column_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow1039(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumn(table_name, column_index)
            return new_run

        return _arrow1039

    @staticmethod
    def update_column_at(table_index: int, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1040(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateColumnAt(table_index, column_index, header, cells)
            return new_run

        return _arrow1040

    @staticmethod
    def update_column(table_name: str, column_index: int, header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1041(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateColumn(table_name, column_index, header, cells)
            return new_run

        return _arrow1041

    @staticmethod
    def get_column_at(table_index: int, column_index: int) -> Callable[[ArcRun], CompositeColumn]:
        def _arrow1042(run: ArcRun) -> CompositeColumn:
            new_run: ArcRun = run.Copy()
            return new_run.GetColumnAt(table_index, column_index)

        return _arrow1042

    @staticmethod
    def get_column(table_name: str, column_index: int) -> Callable[[ArcRun], CompositeColumn]:
        def _arrow1043(run: ArcRun) -> CompositeColumn:
            new_run: ArcRun = run.Copy()
            return new_run.GetColumn(table_name, column_index)

        return _arrow1043

    @staticmethod
    def add_row_at(table_index: int, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1044(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddRowAt(table_index, cells, row_index)
            return new_run

        return _arrow1044

    @staticmethod
    def add_row(table_name: str, cells: Array[CompositeCell] | None=None, row_index: int | None=None) -> Callable[[ArcRun], ArcRun]:
        def _arrow1045(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.AddRow(table_name, cells, row_index)
            return new_run

        return _arrow1045

    @staticmethod
    def remove_row_at(table_index: int, row_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow1046(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveColumnAt(table_index, row_index)
            return new_run

        return _arrow1046

    @staticmethod
    def remove_row(table_name: str, row_index: int) -> Callable[[ArcRun], ArcRun]:
        def _arrow1047(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.RemoveRow(table_name, row_index)
            return new_run

        return _arrow1047

    @staticmethod
    def update_row_at(table_index: int, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcRun], ArcRun]:
        def _arrow1048(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateRowAt(table_index, row_index, cells)
            return new_run

        return _arrow1048

    @staticmethod
    def update_row(table_name: str, row_index: int, cells: Array[CompositeCell]) -> Callable[[ArcRun], ArcRun]:
        def _arrow1049(run: ArcRun) -> ArcRun:
            new_run: ArcRun = run.Copy()
            new_run.UpdateRow(table_name, row_index, cells)
            return new_run

        return _arrow1049

    @staticmethod
    def get_row_at(table_index: int, row_index: int) -> Callable[[ArcRun], Array[CompositeCell]]:
        def _arrow1050(run: ArcRun) -> Array[CompositeCell]:
            new_run: ArcRun = run.Copy()
            return new_run.GetRowAt(table_index, row_index)

        return _arrow1050

    @staticmethod
    def get_row(table_name: str, row_index: int) -> Callable[[ArcRun], Array[CompositeCell]]:
        def _arrow1051(run: ArcRun) -> Array[CompositeCell]:
            new_run: ArcRun = run.Copy()
            return new_run.GetRow(table_name, row_index)

        return _arrow1051

    @staticmethod
    def set_performers(performers: Array[Person], run: ArcRun) -> ArcRun:
        run.Performers = performers
        return run

    def Copy(self, __unit: None=None) -> ArcRun:
        this: ArcRun = self
        def f(c: ArcTable) -> ArcTable:
            return c.Copy()

        next_tables: Array[ArcTable] = ResizeArray_map(f, this.Tables)
        def f_1(c_1: Comment) -> Comment:
            return c_1.Copy()

        next_comments: Array[Comment] = ResizeArray_map(f_1, this.Comments)
        next_data_map: DataMap | None = map(DataMap__Copy, this.DataMap)
        def f_2(c_2: Person) -> Person:
            return c_2.Copy()

        next_performers: Array[Person] = ResizeArray_map(f_2, this.Performers)
        def f_3(c_3: str) -> str:
            return c_3

        next_workflow_identifiers: Array[str] = ResizeArray_map(f_3, this.WorkflowIdentifiers)
        identifier: str = this.Identifier
        title: str | None = this.Title
        description: str | None = this.Description
        measurement_type: OntologyAnnotation | None = this.MeasurementType
        technology_type: OntologyAnnotation | None = this.TechnologyType
        technology_platform: OntologyAnnotation | None = this.TechnologyPlatform
        return ArcRun.make(identifier, title, description, measurement_type, technology_type, technology_platform, next_workflow_identifiers, next_tables, next_data_map, next_performers, next_comments)

    def UpdateBy(self, run: ArcRun, only_replace_existing: bool | None=None, append_sequences: bool | None=None) -> None:
        this: ArcRun = self
        only_replace_existing_1: bool = default_arg(only_replace_existing, False)
        append_sequences_1: bool = default_arg(append_sequences, False)
        update_always: bool = not only_replace_existing_1
        if True if (run.Title is not None) else update_always:
            this.Title = run.Title

        if True if (run.Description is not None) else update_always:
            this.Description = run.Description

        if True if (run.MeasurementType is not None) else update_always:
            this.MeasurementType = run.MeasurementType

        if True if (run.TechnologyType is not None) else update_always:
            this.TechnologyType = run.TechnologyType

        if True if (run.TechnologyPlatform is not None) else update_always:
            this.TechnologyPlatform = run.TechnologyPlatform

        if True if (len(run.WorkflowIdentifiers) != 0) else update_always:
            s: Array[str]
            origin: Array[str] = this.WorkflowIdentifiers
            next_1: Array[str] = run.WorkflowIdentifiers
            if not append_sequences_1:
                def f(x: str) -> str:
                    return x

                s = ResizeArray_map(f, next_1)

            else: 
                combined: Array[str] = []
                enumerator: Any = get_enumerator(origin)
                try: 
                    while enumerator.System_Collections_IEnumerator_MoveNext():
                        e: str = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1053:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow1052(x_1: str, y: str) -> bool:
                                    return x_1 == y

                                return _arrow1052

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains_1(e, combined, ObjectExpr1053()):
                            (combined.append(e))


                finally: 
                    dispose(enumerator)

                enumerator_1: Any = get_enumerator(next_1)
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        e_1: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1055:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow1054(x_2: str, y_1: str) -> bool:
                                    return x_2 == y_1

                                return _arrow1054

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains_1(e_1, combined, ObjectExpr1055()):
                            (combined.append(e_1))


                finally: 
                    dispose(enumerator_1)

                s = combined

            this.WorkflowIdentifiers = s

        if True if (run.DataMap is not None) else update_always:
            this.DataMap = run.DataMap

        if True if (len(run.Tables) != 0) else update_always:
            s_1: Array[ArcTable]
            origin_1: Array[ArcTable] = this.Tables
            next_1_1: Array[ArcTable] = run.Tables
            if not append_sequences_1:
                def f_1(x_3: ArcTable) -> ArcTable:
                    return x_3

                s_1 = ResizeArray_map(f_1, next_1_1)

            else: 
                combined_1: Array[ArcTable] = []
                enumerator_2: Any = get_enumerator(origin_1)
                try: 
                    while enumerator_2.System_Collections_IEnumerator_MoveNext():
                        e_2: ArcTable = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1056:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_2, combined_1, ObjectExpr1056()):
                            (combined_1.append(e_2))


                finally: 
                    dispose(enumerator_2)

                enumerator_1_1: Any = get_enumerator(next_1_1)
                try: 
                    while enumerator_1_1.System_Collections_IEnumerator_MoveNext():
                        e_1_1: ArcTable = enumerator_1_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1057:
                            @property
                            def Equals(self) -> Callable[[ArcTable, ArcTable], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[ArcTable], int]:
                                return safe_hash

                        if not contains_1(e_1_1, combined_1, ObjectExpr1057()):
                            (combined_1.append(e_1_1))


                finally: 
                    dispose(enumerator_1_1)

                s_1 = combined_1

            this.Tables = s_1

        if True if (len(run.Performers) != 0) else update_always:
            s_2: Array[Person]
            origin_2: Array[Person] = this.Performers
            next_1_2: Array[Person] = run.Performers
            if not append_sequences_1:
                def f_2(x_6: Person) -> Person:
                    return x_6

                s_2 = ResizeArray_map(f_2, next_1_2)

            else: 
                combined_2: Array[Person] = []
                enumerator_3: Any = get_enumerator(origin_2)
                try: 
                    while enumerator_3.System_Collections_IEnumerator_MoveNext():
                        e_3: Person = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1058:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_3, combined_2, ObjectExpr1058()):
                            (combined_2.append(e_3))


                finally: 
                    dispose(enumerator_3)

                enumerator_1_2: Any = get_enumerator(next_1_2)
                try: 
                    while enumerator_1_2.System_Collections_IEnumerator_MoveNext():
                        e_1_2: Person = enumerator_1_2.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1059:
                            @property
                            def Equals(self) -> Callable[[Person, Person], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Person], int]:
                                return safe_hash

                        if not contains_1(e_1_2, combined_2, ObjectExpr1059()):
                            (combined_2.append(e_1_2))


                finally: 
                    dispose(enumerator_1_2)

                s_2 = combined_2

            this.Performers = s_2

        if True if (len(run.Comments) != 0) else update_always:
            s_3: Array[Comment]
            origin_3: Array[Comment] = this.Comments
            next_1_3: Array[Comment] = run.Comments
            if not append_sequences_1:
                def f_3(x_9: Comment) -> Comment:
                    return x_9

                s_3 = ResizeArray_map(f_3, next_1_3)

            else: 
                combined_3: Array[Comment] = []
                enumerator_4: Any = get_enumerator(origin_3)
                try: 
                    while enumerator_4.System_Collections_IEnumerator_MoveNext():
                        e_4: Comment = enumerator_4.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1060:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_4, combined_3, ObjectExpr1060()):
                            (combined_3.append(e_4))


                finally: 
                    dispose(enumerator_4)

                enumerator_1_3: Any = get_enumerator(next_1_3)
                try: 
                    while enumerator_1_3.System_Collections_IEnumerator_MoveNext():
                        e_1_3: Comment = enumerator_1_3.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1061:
                            @property
                            def Equals(self) -> Callable[[Comment, Comment], bool]:
                                return equals

                            @property
                            def GetHashCode(self) -> Callable[[Comment], int]:
                                return safe_hash

                        if not contains_1(e_1_3, combined_3, ObjectExpr1061()):
                            (combined_3.append(e_1_3))


                finally: 
                    dispose(enumerator_1_3)

                s_3 = combined_3

            this.Comments = s_3


    def __str__(self, __unit: None=None) -> str:
        this: ArcRun = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: OntologyAnnotation | None = this.MeasurementType
        arg_4: OntologyAnnotation | None = this.TechnologyType
        arg_5: OntologyAnnotation | None = this.TechnologyPlatform
        arg_6: Array[str] = this.WorkflowIdentifiers
        arg_7: DataMap | None = this.DataMap
        arg_8: Array[ArcTable] = this.Tables
        arg_9: Array[Person] = this.Performers
        arg_10: Array[Comment] = this.Comments
        return to_text(printf("ArcRun({\r\n    Identifier = \"%s\",\r\n    Title = %A,\r\n    Description = %A,\r\n    MeasurementType = %A,\r\n    TechnologyType = %A,\r\n    TechnologyPlatform = %A,\r\n    WorkflowIdentifiers = %A,\r\n    DataMap = %A,\r\n    Tables = %A,\r\n    Performers = %A,\r\n    Comments = %A\r\n})"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)

    def AddToInvestigation(self, investigation: ArcInvestigation) -> None:
        this: ArcRun = self
        this.Investigation = investigation

    def RemoveFromInvestigation(self, __unit: None=None) -> None:
        this: ArcRun = self
        this.Investigation = None

    def StructurallyEquals(self, other: ArcRun) -> bool:
        this: ArcRun = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow1064(__unit: None=None) -> bool:
            a: IEnumerable_1[str] = this.WorkflowIdentifiers
            b: IEnumerable_1[str] = other.WorkflowIdentifiers
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow1063(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1062(i_1: int) -> bool:
                    return item(i_1, a) == item(i_1, b)

                return map_1(_arrow1062, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow1063))) if (length(a) == length(b)) else False

        def _arrow1067(__unit: None=None) -> bool:
            a_1: IEnumerable_1[ArcTable] = this.Tables
            b_1: IEnumerable_1[ArcTable] = other.Tables
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow1066(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1065(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow1065, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow1066))) if (length(a_1) == length(b_1)) else False

        def _arrow1070(__unit: None=None) -> bool:
            a_2: IEnumerable_1[Person] = this.Performers
            b_2: IEnumerable_1[Person] = other.Performers
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow1069(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1068(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow1068, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow1069))) if (length(a_2) == length(b_2)) else False

        def _arrow1073(__unit: None=None) -> bool:
            a_3: IEnumerable_1[Comment] = this.Comments
            b_3: IEnumerable_1[Comment] = other.Comments
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow1072(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1071(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow1071, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow1072))) if (length(a_3) == length(b_3)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.MeasurementType, other.MeasurementType), equals(this.TechnologyType, other.TechnologyType), equals(this.TechnologyPlatform, other.TechnologyPlatform), _arrow1064(), equals(this.DataMap, other.DataMap), _arrow1067(), _arrow1070(), _arrow1073()]))

    def ReferenceEquals(self, other: ArcRun) -> bool:
        this: ArcRun = self
        return this is other

    def __eq__(self, other: Any=None) -> bool:
        this: ArcRun = self
        return this.StructurallyEquals(other) if isinstance(other, ArcRun) else False

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcRun = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_seq(this.WorkflowIdentifiers), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcRun = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.MeasurementType), box_hash_option(this.TechnologyType), box_hash_option(this.TechnologyPlatform), box_hash_option(this.DataMap), box_hash_seq(this.WorkflowIdentifiers), box_hash_seq(this.Tables), box_hash_seq(this.Performers), box_hash_seq(this.Comments)])


ArcRun_reflection = _expr1075

def ArcRun__ctor_Z38E7054B(identifier: str, title: str | None=None, description: str | None=None, measurement_type: OntologyAnnotation | None=None, technology_type: OntologyAnnotation | None=None, technology_platform: OntologyAnnotation | None=None, workflow_identifiers: Array[str] | None=None, tables: Array[ArcTable] | None=None, datamap: DataMap | None=None, performers: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcRun:
    return ArcRun(identifier, title, description, measurement_type, technology_type, technology_platform, workflow_identifiers, tables, datamap, performers, comments)


def _expr1207() -> TypeInfo:
    return class_type("ARCtrl.ArcInvestigation", None, ArcInvestigation)


class ArcInvestigation:
    def __init__(self, identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> None:
        this: FSharpRef[ArcInvestigation] = FSharpRef(None)
        this.contents = self
        ontology_source_references_1: Array[OntologySourceReference] = default_arg(ontology_source_references, [])
        publications_1: Array[Publication] = default_arg(publications, [])
        contacts_1: Array[Person] = default_arg(contacts, [])
        assays_1: Array[ArcAssay]
        ass: Array[ArcAssay] = default_arg(assays, [])
        enumerator: Any = get_enumerator(ass)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                a.Investigation = this.contents

        finally: 
            dispose(enumerator)

        assays_1 = ass
        studies_1: Array[ArcStudy]
        sss: Array[ArcStudy] = default_arg(studies, [])
        enumerator_1: Any = get_enumerator(sss)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                s.Investigation = this.contents

        finally: 
            dispose(enumerator_1)

        studies_1 = sss
        workflows_1: Array[ArcWorkflow]
        wss: Array[ArcWorkflow] = default_arg(workflows, [])
        enumerator_2: Any = get_enumerator(wss)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                ArcWorkflow__set_Investigation_Z1E102E3E(enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current(), this.contents)

        finally: 
            dispose(enumerator_2)

        workflows_1 = wss
        runs_1: Array[ArcRun]
        rss: Array[ArcRun] = default_arg(runs, [])
        enumerator_3: Any = get_enumerator(rss)
        try: 
            while enumerator_3.System_Collections_IEnumerator_MoveNext():
                r: ArcRun = enumerator_3.System_Collections_Generic_IEnumerator_1_get_Current()
                r.Investigation = this.contents

        finally: 
            dispose(enumerator_3)

        runs_1 = rss
        registered_study_identifiers_1: Array[str] = default_arg(registered_study_identifiers, [])
        comments_1: Array[Comment] = default_arg(comments, [])
        remarks_1: Array[Remark] = default_arg(remarks, [])
        self.identifier_00401928: str = identifier
        self.title_00401929: str | None = title
        self.description_00401930: str | None = description
        self.submission_date_00401931: str | None = submission_date
        self.public_release_date_00401932: str | None = public_release_date
        self.ontology_source_references_00401933_002D1: Array[OntologySourceReference] = ontology_source_references_1
        self.publications_00401934_002D1: Array[Publication] = publications_1
        self.contacts_00401935_002D1: Array[Person] = contacts_1
        self.assays_00401936_002D1: Array[ArcAssay] = assays_1
        self.studies_00401937_002D1: Array[ArcStudy] = studies_1
        self.workflows_00401938_002D1: Array[ArcWorkflow] = workflows_1
        self.runs_00401939_002D1: Array[ArcRun] = runs_1
        self.registered_study_identifiers_00401940_002D1: Array[str] = registered_study_identifiers_1
        self.comments_00401941_002D1: Array[Comment] = comments_1
        self.remarks_00401942_002D1: Array[Remark] = remarks_1
        self.static_hash: int = 0
        self.init_00401899: int = 1

    @property
    def Identifier(self, __unit: None=None) -> str:
        this: ArcInvestigation = self
        return this.identifier_00401928

    @Identifier.setter
    def Identifier(self, i: str) -> None:
        this: ArcInvestigation = self
        this.identifier_00401928 = i

    @property
    def Title(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.title_00401929

    @Title.setter
    def Title(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.title_00401929 = n

    @property
    def Description(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.description_00401930

    @Description.setter
    def Description(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.description_00401930 = n

    @property
    def SubmissionDate(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.submission_date_00401931

    @SubmissionDate.setter
    def SubmissionDate(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.submission_date_00401931 = n

    @property
    def PublicReleaseDate(self, __unit: None=None) -> str | None:
        this: ArcInvestigation = self
        return this.public_release_date_00401932

    @PublicReleaseDate.setter
    def PublicReleaseDate(self, n: str | None=None) -> None:
        this: ArcInvestigation = self
        this.public_release_date_00401932 = n

    @property
    def OntologySourceReferences(self, __unit: None=None) -> Array[OntologySourceReference]:
        this: ArcInvestigation = self
        return this.ontology_source_references_00401933_002D1

    @OntologySourceReferences.setter
    def OntologySourceReferences(self, n: Array[OntologySourceReference]) -> None:
        this: ArcInvestigation = self
        this.ontology_source_references_00401933_002D1 = n

    @property
    def Publications(self, __unit: None=None) -> Array[Publication]:
        this: ArcInvestigation = self
        return this.publications_00401934_002D1

    @Publications.setter
    def Publications(self, n: Array[Publication]) -> None:
        this: ArcInvestigation = self
        this.publications_00401934_002D1 = n

    @property
    def Contacts(self, __unit: None=None) -> Array[Person]:
        this: ArcInvestigation = self
        return this.contacts_00401935_002D1

    @Contacts.setter
    def Contacts(self, n: Array[Person]) -> None:
        this: ArcInvestigation = self
        this.contacts_00401935_002D1 = n

    @property
    def Assays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcInvestigation = self
        return this.assays_00401936_002D1

    @Assays.setter
    def Assays(self, n: Array[ArcAssay]) -> None:
        this: ArcInvestigation = self
        this.assays_00401936_002D1 = n

    @property
    def Studies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        return this.studies_00401937_002D1

    @Studies.setter
    def Studies(self, n: Array[ArcStudy]) -> None:
        this: ArcInvestigation = self
        this.studies_00401937_002D1 = n

    @property
    def Workflows(self, __unit: None=None) -> Array[ArcWorkflow]:
        this: ArcInvestigation = self
        return this.workflows_00401938_002D1

    @Workflows.setter
    def Workflows(self, n: Array[ArcWorkflow]) -> None:
        this: ArcInvestigation = self
        this.workflows_00401938_002D1 = n

    @property
    def Runs(self, __unit: None=None) -> Array[ArcRun]:
        this: ArcInvestigation = self
        return this.runs_00401939_002D1

    @Runs.setter
    def Runs(self, n: Array[ArcRun]) -> None:
        this: ArcInvestigation = self
        this.runs_00401939_002D1 = n

    @property
    def RegisteredStudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        return this.registered_study_identifiers_00401940_002D1

    @RegisteredStudyIdentifiers.setter
    def RegisteredStudyIdentifiers(self, n: Array[str]) -> None:
        this: ArcInvestigation = self
        this.registered_study_identifiers_00401940_002D1 = n

    @property
    def Comments(self, __unit: None=None) -> Array[Comment]:
        this: ArcInvestigation = self
        return this.comments_00401941_002D1

    @Comments.setter
    def Comments(self, n: Array[Comment]) -> None:
        this: ArcInvestigation = self
        this.comments_00401941_002D1 = n

    @property
    def Remarks(self, __unit: None=None) -> Array[Remark]:
        this: ArcInvestigation = self
        return this.remarks_00401942_002D1

    @Remarks.setter
    def Remarks(self, n: Array[Remark]) -> None:
        this: ArcInvestigation = self
        this.remarks_00401942_002D1 = n

    @property
    def StaticHash(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return this.static_hash

    @StaticHash.setter
    def StaticHash(self, h: int) -> None:
        this: ArcInvestigation = self
        this.static_hash = h or 0

    @staticmethod
    def FileName() -> str:
        return "isa.investigation.xlsx"

    @staticmethod
    def init(identifier: str) -> ArcInvestigation:
        return ArcInvestigation(identifier)

    @staticmethod
    def create(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> ArcInvestigation:
        return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)

    @staticmethod
    def make(identifier: str, title: str | None, description: str | None, submission_date: str | None, public_release_date: str | None, ontology_source_references: Array[OntologySourceReference], publications: Array[Publication], contacts: Array[Person], assays: Array[ArcAssay], studies: Array[ArcStudy], workflows: Array[ArcWorkflow], runs: Array[ArcRun], registered_study_identifiers: Array[str], comments: Array[Comment], remarks: Array[Remark]) -> ArcInvestigation:
        return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)

    @property
    def AssayCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Assays)

    @property
    def AssayIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcAssay) -> str:
            return x.Identifier

        return list(map_1(mapping, this.Assays))

    @property
    def UnregisteredAssays(self, __unit: None=None) -> Array[ArcAssay]:
        this: ArcInvestigation = self
        def f(a: ArcAssay) -> bool:
            def predicate(s: ArcStudy, a: Any=a) -> bool:
                def _arrow1076(i: str, s: Any=s) -> bool:
                    return i == a.Identifier

                return exists(_arrow1076, s.RegisteredAssayIdentifiers)

            return not exists(predicate, this.RegisteredStudies)

        return ResizeArray_filter(f, this.Assays)

    def AddAssay(self, assay: ArcAssay, register_in: Array[ArcStudy] | None=None) -> None:
        this: ArcInvestigation = self
        assay_ident: str = assay.Identifier
        def predicate(x_1: str) -> bool:
            return x_1 == assay_ident

        def mapping(x: ArcAssay) -> str:
            return x.Identifier

        match_value: int | None = try_find_index(predicate, map_1(mapping, this.Assays))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident) + ", as assay names must be unique and assay at index ") + str(match_value)) + " has the same name.")

        assay.Investigation = this
        (this.Assays.append(assay))
        if register_in is not None:
            enumerator: Any = get_enumerator(value_5(register_in))
            try: 
                while enumerator.System_Collections_IEnumerator_MoveNext():
                    study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                    study.RegisterAssay(assay.Identifier)

            finally: 
                dispose(enumerator)



    @staticmethod
    def add_assay(assay: ArcAssay, register_in: Array[ArcStudy] | None=None) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1077(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.AddAssay(assay, register_in)
            return new_investigation

        return _arrow1077

    def InitAssay(self, assay_identifier: str, register_in: Array[ArcStudy] | None=None) -> ArcAssay:
        this: ArcInvestigation = self
        assay: ArcAssay = ArcAssay(assay_identifier)
        this.AddAssay(assay, register_in)
        return assay

    @staticmethod
    def init_assay(assay_identifier: str, register_in: Array[ArcStudy] | None=None) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow1078(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.InitAssay(assay_identifier, register_in)

        return _arrow1078

    def DeleteAssayAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Assays.pop(index)

    @staticmethod
    def delete_assay_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1079(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.DeleteAssayAt(index)
            return new_investigation

        return _arrow1079

    def DeleteAssay(self, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.DeleteAssayAt(index)

    @staticmethod
    def delete_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1080(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.DeleteAssay(assay_identifier)
            return new_inv

        return _arrow1080

    def RemoveAssayAt(self, index: int) -> None:
        this: ArcInvestigation = self
        ident: str = this.GetAssayAt(index).Identifier
        this.Assays.pop(index)
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                study.DeregisterAssay(ident)

        finally: 
            dispose(enumerator)


    @staticmethod
    def remove_assay_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1081(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.RemoveAssayAt(index)
            return new_investigation

        return _arrow1081

    def RemoveAssay(self, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.RemoveAssayAt(index)

    @staticmethod
    def remove_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1082(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RemoveAssay(assay_identifier)
            return new_inv

        return _arrow1082

    def RenameAssay(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(a: ArcAssay) -> None:
            if a.Identifier == old_identifier:
                a.Identifier = new_identifier


        iterate(action, this.Assays)
        def action_1(s: ArcStudy) -> None:
            def predicate(ai: str, s: Any=s) -> bool:
                return ai == old_identifier

            index: int | None = try_find_index(predicate, s.RegisteredAssayIdentifiers)
            if index is not None:
                index_1: int = index or 0
                s.RegisteredAssayIdentifiers[index_1] = new_identifier


        iterate(action_1, this.Studies)

    @staticmethod
    def rename_assay(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1083(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameAssay(old_identifier, new_identifier)
            return new_inv

        return _arrow1083

    def SetAssayAt(self, index: int, assay: ArcAssay) -> None:
        this: ArcInvestigation = self
        assay_ident: str = assay.Identifier
        def predicate(x: str) -> bool:
            return x == assay_ident

        def mapping(a: ArcAssay) -> str:
            return a.Identifier

        match_value: int | None = try_find_index(predicate, map_1(mapping, remove_at(index, this.Assays)))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident) + ", as assay names must be unique and assay at index ") + str(match_value)) + " has the same name.")

        assay.Investigation = this
        this.Assays[index] = assay
        this.DeregisterMissingAssays()

    @staticmethod
    def set_assay_at(index: int, assay: ArcAssay) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1084(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.SetAssayAt(index, assay)
            return new_investigation

        return _arrow1084

    def SetAssay(self, assay_identifier: str, assay: ArcAssay) -> None:
        this: ArcInvestigation = self
        index: int = this.GetAssayIndex(assay_identifier) or 0
        this.SetAssayAt(index, assay)

    @staticmethod
    def set_assay(assay_identifier: str, assay: ArcAssay) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1085(inv: ArcInvestigation) -> ArcInvestigation:
            new_investigation: ArcInvestigation = inv.Copy()
            new_investigation.SetAssay(assay_identifier, assay)
            return new_investigation

        return _arrow1085

    def GetAssayIndex(self, assay_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow1086(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        index: int = find_index(_arrow1086, this.Assays) or 0
        if index == -1:
            raise Exception(("Unable to find assay with specified identifier \'" + assay_identifier) + "\'!")

        return index

    @staticmethod
    def get_assay_index(assay_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow1087(inv: ArcInvestigation) -> int:
            return inv.GetAssayIndex(assay_identifier)

        return _arrow1087

    def GetAssayAt(self, index: int) -> ArcAssay:
        this: ArcInvestigation = self
        return this.Assays[index]

    @staticmethod
    def get_assay_at(index: int) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow1088(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.GetAssayAt(index)

        return _arrow1088

    def GetAssay(self, assay_identifier: str) -> ArcAssay:
        this: ArcInvestigation = self
        match_value: ArcAssay | None = this.TryGetAssay(assay_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier(assay_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcAssay]:
        def _arrow1089(inv: ArcInvestigation) -> ArcAssay:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.GetAssay(assay_identifier)

        return _arrow1089

    def TryGetAssay(self, assay_identifier: str) -> ArcAssay | None:
        this: ArcInvestigation = self
        def _arrow1090(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        return try_find(_arrow1090, this.Assays)

    @staticmethod
    def try_get_assay(assay_identifier: str) -> Callable[[ArcInvestigation], ArcAssay | None]:
        def _arrow1091(inv: ArcInvestigation) -> ArcAssay | None:
            new_investigation: ArcInvestigation = inv.Copy()
            return new_investigation.TryGetAssay(assay_identifier)

        return _arrow1091

    def ContainsAssay(self, assay_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(a: ArcAssay) -> bool:
            return a.Identifier == assay_identifier

        return exists(predicate, this.Assays)

    @staticmethod
    def contains_assay(assay_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow1092(inv: ArcInvestigation) -> bool:
            return inv.ContainsAssay(assay_identifier)

        return _arrow1092

    @property
    def RegisteredStudyIdentifierCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.RegisteredStudyIdentifiers)

    @property
    def RegisteredStudies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        def f(identifier: str) -> ArcStudy | None:
            return this.TryGetStudy(identifier)

        return ResizeArray_choose(f, this.RegisteredStudyIdentifiers)

    @property
    def RegisteredStudyCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.RegisteredStudies)

    @property
    def VacantStudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def f(arg: str) -> bool:
            return not this.ContainsStudy(arg)

        return ResizeArray_filter(f, this.RegisteredStudyIdentifiers)

    @property
    def StudyCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Studies)

    @property
    def StudyIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcStudy) -> str:
            return x.Identifier

        return to_array(map_1(mapping, this.Studies))

    @property
    def UnregisteredStudies(self, __unit: None=None) -> Array[ArcStudy]:
        this: ArcInvestigation = self
        def f(s: ArcStudy) -> bool:
            def _arrow1095(__unit: None=None, s: Any=s) -> bool:
                source: Array[str] = this.RegisteredStudyIdentifiers
                def _arrow1094(__unit: None=None) -> Callable[[str], bool]:
                    x: str = s.Identifier
                    def _arrow1093(y: str) -> bool:
                        return x == y

                    return _arrow1093

                return exists(_arrow1094(), source)

            return not _arrow1095()

        return ResizeArray_filter(f, this.Studies)

    def AddStudy(self, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        study_1: ArcStudy = study
        def predicate(x: ArcStudy) -> bool:
            return x.Identifier == study_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Studies)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create study with name " + study_1.Identifier) + ", as study names must be unique and study at index ") + str(match_value)) + " has the same name.")

        study.Investigation = this
        (this.Studies.append(study))

    @staticmethod
    def add_study(study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1096(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddStudy(study)
            return copy

        return _arrow1096

    def InitStudy(self, study_identifier: str) -> ArcStudy:
        this: ArcInvestigation = self
        study: ArcStudy = ArcStudy.init(study_identifier)
        this.AddStudy(study)
        return study

    @staticmethod
    def init_study(study_identifier: str) -> Callable[[ArcInvestigation], tuple[ArcInvestigation, ArcStudy]]:
        def _arrow1097(inv: ArcInvestigation) -> tuple[ArcInvestigation, ArcStudy]:
            copy: ArcInvestigation = inv.Copy()
            return (copy, copy.InitStudy(study_identifier))

        return _arrow1097

    def RegisterStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        study_ident: str = study_identifier
        def predicate(x: str) -> bool:
            return x == study_ident

        match_value: str | None = try_find(predicate, this.StudyIdentifiers)
        if match_value is not None:
            pass

        else: 
            raise Exception(("The given study with identifier \'" + study_ident) + "\' must be added to Investigation before it can be registered.")

        study_ident_1: str = study_identifier
        class ObjectExpr1099:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow1098(x_1: str, y: str) -> bool:
                    return x_1 == y

                return _arrow1098

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        if contains(study_ident_1, this.RegisteredStudyIdentifiers, ObjectExpr1099()):
            raise Exception(("Study with identifier \'" + study_ident_1) + "\' is already registered!")

        (this.RegisteredStudyIdentifiers.append(study_identifier))

    @staticmethod
    def register_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1100(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterStudy(study_identifier)
            return copy

        return _arrow1100

    def AddRegisteredStudy(self, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        this.AddStudy(study)
        this.RegisterStudy(study.Identifier)

    @staticmethod
    def add_registered_study(study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1101(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            study_1: ArcStudy = study.Copy()
            copy.AddRegisteredStudy(study_1)
            return copy

        return _arrow1101

    def DeleteStudyAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Studies.pop(index)

    @staticmethod
    def delete_study_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1102(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeleteStudyAt(index)
            return copy

        return _arrow1102

    def DeleteStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow1103(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        index: int = find_index(_arrow1103, this.Studies) or 0
        this.DeleteStudyAt(index)

    @staticmethod
    def delete_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1104(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeleteStudy(study_identifier)
            return copy

        return _arrow1104

    def RemoveStudyAt(self, index: int) -> None:
        this: ArcInvestigation = self
        ident: str = this.GetStudyAt(index).Identifier
        this.Studies.pop(index)
        this.DeregisterStudy(ident)

    @staticmethod
    def remove_study_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1105(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RemoveStudyAt(index)
            return new_inv

        return _arrow1105

    def RemoveStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.RemoveStudyAt(index)

    @staticmethod
    def remove_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1106(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RemoveStudy(study_identifier)
            return copy

        return _arrow1106

    def RenameStudy(self, old_identifier: str, new_identifier: str) -> None:
        this: ArcInvestigation = self
        def action(s: ArcStudy) -> None:
            if s.Identifier == old_identifier:
                s.Identifier = new_identifier


        iterate(action, this.Studies)
        def predicate(si: str) -> bool:
            return si == old_identifier

        index: int | None = try_find_index(predicate, this.RegisteredStudyIdentifiers)
        if index is not None:
            index_1: int = index or 0
            this.RegisteredStudyIdentifiers[index_1] = new_identifier


    @staticmethod
    def rename_study(old_identifier: str, new_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1107(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.RenameStudy(old_identifier, new_identifier)
            return new_inv

        return _arrow1107

    def SetStudyAt(self, index: int, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        study_1: ArcStudy = study
        def predicate(x: ArcStudy) -> bool:
            return x.Identifier == study_1.Identifier

        match_value: int | None = try_find_index(predicate, remove_at(index, this.Studies))
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create study with name " + study_1.Identifier) + ", as study names must be unique and study at index ") + str(match_value)) + " has the same name.")

        study.Investigation = this
        this.Studies[index] = study

    @staticmethod
    def set_study_at(index: int, study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1108(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.SetStudyAt(index, study)
            return new_inv

        return _arrow1108

    def SetStudy(self, study_identifier: str, study: ArcStudy) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.SetStudyAt(index, study)

    @staticmethod
    def set_study(study_identifier: str, study: ArcStudy) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1109(inv: ArcInvestigation) -> ArcInvestigation:
            new_inv: ArcInvestigation = inv.Copy()
            new_inv.SetStudy(study_identifier, study)
            return new_inv

        return _arrow1109

    def GetStudyIndex(self, study_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow1110(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        index: int = find_index(_arrow1110, this.Studies) or 0
        if index == -1:
            raise Exception(("Unable to find study with specified identifier \'" + study_identifier) + "\'!")

        return index

    @staticmethod
    def get_study_index(study_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow1111(inv: ArcInvestigation) -> int:
            return inv.GetStudyIndex(study_identifier)

        return _arrow1111

    def GetStudyAt(self, index: int) -> ArcStudy:
        this: ArcInvestigation = self
        return this.Studies[index]

    @staticmethod
    def get_study_at(index: int) -> Callable[[ArcInvestigation], ArcStudy]:
        def _arrow1112(inv: ArcInvestigation) -> ArcStudy:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.GetStudyAt(index)

        return _arrow1112

    def GetStudy(self, study_identifier: str) -> ArcStudy:
        this: ArcInvestigation = self
        match_value: ArcStudy | None = this.TryGetStudy(study_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier(study_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcStudy]:
        def _arrow1113(inv: ArcInvestigation) -> ArcStudy:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.GetStudy(study_identifier)

        return _arrow1113

    def TryGetStudy(self, study_identifier: str) -> ArcStudy | None:
        this: ArcInvestigation = self
        def predicate(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        return try_find(predicate, this.Studies)

    @staticmethod
    def try_get_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcStudy | None]:
        def _arrow1114(inv: ArcInvestigation) -> ArcStudy | None:
            new_inv: ArcInvestigation = inv.Copy()
            return new_inv.TryGetStudy(study_identifier)

        return _arrow1114

    def ContainsStudy(self, study_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(s: ArcStudy) -> bool:
            return s.Identifier == study_identifier

        return exists(predicate, this.Studies)

    @staticmethod
    def contains_study(study_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow1115(inv: ArcInvestigation) -> bool:
            return inv.ContainsStudy(study_identifier)

        return _arrow1115

    def RegisterAssayAt(self, study_index: int, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        study: ArcStudy = this.GetStudyAt(study_index)
        def predicate(x: str) -> bool:
            return x == assay_identifier

        def mapping(a: ArcAssay) -> str:
            return a.Identifier

        match_value: str | None = try_find(predicate, map_1(mapping, this.Assays))
        if match_value is not None:
            pass

        else: 
            raise Exception("The given assay must be added to Investigation before it can be registered.")

        assay_ident_1: str = assay_identifier
        def predicate_1(x_1: str) -> bool:
            return x_1 == assay_ident_1

        match_value_1: int | None = try_find_index(predicate_1, study.RegisteredAssayIdentifiers)
        if match_value_1 is None:
            pass

        else: 
            raise Exception(((("Cannot create assay with name " + assay_ident_1) + ", as assay names must be unique and assay at index ") + str(match_value_1)) + " has the same name.")

        study.RegisterAssay(assay_identifier)

    @staticmethod
    def register_assay_at(study_index: int, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1116(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterAssayAt(study_index, assay_identifier)
            return copy

        return _arrow1116

    def RegisterAssay(self, study_identifier: str, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.RegisterAssayAt(index, assay_identifier)

    @staticmethod
    def register_assay(study_identifier: str, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1117(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.RegisterAssay(study_identifier, assay_identifier)
            return copy

        return _arrow1117

    def DeregisterAssayAt(self, study_index: int, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        study: ArcStudy = this.GetStudyAt(study_index)
        study.DeregisterAssay(assay_identifier)

    @staticmethod
    def deregister_assay_at(study_index: int, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1118(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterAssayAt(study_index, assay_identifier)
            return copy

        return _arrow1118

    def DeregisterAssay(self, study_identifier: str, assay_identifier: str) -> None:
        this: ArcInvestigation = self
        index: int = this.GetStudyIndex(study_identifier) or 0
        this.DeregisterAssayAt(index, assay_identifier)

    @staticmethod
    def deregister_assay(study_identifier: str, assay_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1119(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterAssay(study_identifier, assay_identifier)
            return copy

        return _arrow1119

    def DeregisterStudy(self, study_identifier: str) -> None:
        this: ArcInvestigation = self
        class ObjectExpr1121:
            @property
            def Equals(self) -> Callable[[str, str], bool]:
                def _arrow1120(x: str, y: str) -> bool:
                    return x == y

                return _arrow1120

            @property
            def GetHashCode(self) -> Callable[[str], int]:
                return string_hash

        ignore(remove_in_place(study_identifier, this.RegisteredStudyIdentifiers, ObjectExpr1121()))

    @staticmethod
    def deregister_study(study_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1122(i: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = i.Copy()
            copy.DeregisterStudy(study_identifier)
            return copy

        return _arrow1122

    @property
    def WorkflowCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Workflows)

    @property
    def WorkflowIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        return to_array(map_1(ArcWorkflow__get_Identifier, this.Workflows))

    def GetWorkflowIndex(self, workflow_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow1123(w: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(w) == workflow_identifier

        index: int = find_index(_arrow1123, this.Workflows) or 0
        if index == -1:
            raise Exception(("Unable to find workflow with specified identifier \'" + workflow_identifier) + "\'!")

        return index

    @staticmethod
    def get_workflow_index(workflow_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow1124(inv: ArcInvestigation) -> int:
            return inv.GetWorkflowIndex(workflow_identifier)

        return _arrow1124

    def AddWorkflow(self, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        workflow_1: ArcWorkflow = workflow
        def predicate(x: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(x) == ArcWorkflow__get_Identifier(workflow_1)

        match_value: int | None = try_find_index(predicate, this.Workflows)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create workflow with name " + ArcWorkflow__get_Identifier(workflow_1)) + ", as workflow names must be unique and workflow at index ") + str(match_value)) + " has the same name.")

        ArcWorkflow__set_Investigation_Z1E102E3E(workflow, this)
        (this.Workflows.append(workflow))

    @staticmethod
    def add_workflow(workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1125(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddWorkflow(workflow)
            return copy

        return _arrow1125

    def InitWorkflow(self, workflow_identifier: str) -> ArcWorkflow:
        this: ArcInvestigation = self
        workflow: ArcWorkflow = ArcWorkflow_init_Z721C83C5(workflow_identifier)
        this.AddWorkflow(workflow)
        return workflow

    @staticmethod
    def init_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow1126(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.InitWorkflow(workflow_identifier)

        return _arrow1126

    def DeleteWorkflowAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Workflows.pop(index)

    @staticmethod
    def delete_workflow_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1128(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteWorkflowAt(index)
            return copy

        return _arrow1128

    def DeleteWorkflow(self, workflow_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow1129(w: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(w) == workflow_identifier

        index: int = find_index(_arrow1129, this.Workflows) or 0
        this.DeleteWorkflowAt(index)

    @staticmethod
    def delete_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1130(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteWorkflow(workflow_identifier)
            return copy

        return _arrow1130

    def GetWorkflowAt(self, index: int) -> ArcWorkflow:
        this: ArcInvestigation = self
        return this.Workflows[index]

    @staticmethod
    def get_workflow_at(index: int) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow1131(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetWorkflowAt(index)

        return _arrow1131

    def GetWorkflow(self, workflow_identifier: str) -> ArcWorkflow:
        this: ArcInvestigation = self
        match_value: ArcWorkflow | None = this.TryGetWorkflow(workflow_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier(workflow_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow]:
        def _arrow1134(inv: ArcInvestigation) -> ArcWorkflow:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetWorkflow(workflow_identifier)

        return _arrow1134

    def TryGetWorkflow(self, workflow_identifier: str) -> ArcWorkflow | None:
        this: ArcInvestigation = self
        def predicate(w: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(w) == workflow_identifier

        return try_find(predicate, this.Workflows)

    @staticmethod
    def try_get_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], ArcWorkflow | None]:
        def _arrow1135(inv: ArcInvestigation) -> ArcWorkflow | None:
            copy: ArcInvestigation = inv.Copy()
            return copy.TryGetWorkflow(workflow_identifier)

        return _arrow1135

    def ContainsWorkflow(self, workflow_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(w: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(w) == workflow_identifier

        return exists(predicate, this.Workflows)

    @staticmethod
    def contains_workflow(workflow_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow1136(inv: ArcInvestigation) -> bool:
            return inv.ContainsWorkflow(workflow_identifier)

        return _arrow1136

    def SetWorkflowAt(self, index: int, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        workflow_1: ArcWorkflow = workflow
        def predicate(x: ArcWorkflow) -> bool:
            return ArcWorkflow__get_Identifier(x) == ArcWorkflow__get_Identifier(workflow_1)

        match_value: int | None = try_find_index(predicate, this.Workflows)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create workflow with name " + ArcWorkflow__get_Identifier(workflow_1)) + ", as workflow names must be unique and workflow at index ") + str(match_value)) + " has the same name.")

        ArcWorkflow__set_Investigation_Z1E102E3E(workflow, this)
        this.Workflows[index] = workflow

    def SetWorkflow(self, workflow_identifier: str, workflow: ArcWorkflow) -> None:
        this: ArcInvestigation = self
        index: int = this.GetWorkflowIndex(workflow_identifier) or 0
        this.SetWorkflowAt(index, workflow)

    @staticmethod
    def set_workflow(workflow_identifier: str, workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1137(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetWorkflow(workflow_identifier, workflow)
            return copy

        return _arrow1137

    @staticmethod
    def set_workflow_at(index: int, workflow: ArcWorkflow) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1138(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetWorkflowAt(index, workflow)
            return copy

        return _arrow1138

    @property
    def RunCount(self, __unit: None=None) -> int:
        this: ArcInvestigation = self
        return len(this.Runs)

    @property
    def RunIdentifiers(self, __unit: None=None) -> Array[str]:
        this: ArcInvestigation = self
        def mapping(x: ArcRun) -> str:
            return x.Identifier

        return to_array(map_1(mapping, this.Runs))

    def GetRunIndex(self, run_identifier: str) -> int:
        this: ArcInvestigation = self
        def _arrow1139(r: ArcRun) -> bool:
            return r.Identifier == run_identifier

        index: int = find_index(_arrow1139, this.Runs) or 0
        if index == -1:
            raise Exception(("Unable to find run with specified identifier \'" + run_identifier) + "\'!")

        return index

    @staticmethod
    def get_run_index(run_identifier: str) -> Callable[[ArcInvestigation], int]:
        def _arrow1140(inv: ArcInvestigation) -> int:
            return inv.GetRunIndex(run_identifier)

        return _arrow1140

    def AddRun(self, run: ArcRun) -> None:
        this: ArcInvestigation = self
        run_1: ArcRun = run
        def predicate(x: ArcRun) -> bool:
            return x.Identifier == run_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Runs)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create run with name " + run_1.Identifier) + ", as run names must be unique and run at index ") + str(match_value)) + " has the same name.")

        run.Investigation = this
        (this.Runs.append(run))

    @staticmethod
    def add_run(run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1141(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.AddRun(run)
            return copy

        return _arrow1141

    def InitRun(self, run_identifier: str) -> ArcRun:
        this: ArcInvestigation = self
        run: ArcRun = ArcRun.init(run_identifier)
        this.AddRun(run)
        return run

    @staticmethod
    def init_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow1155(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.InitRun(run_identifier)

        return _arrow1155

    def DeleteRunAt(self, index: int) -> None:
        this: ArcInvestigation = self
        this.Runs.pop(index)

    @staticmethod
    def delete_run_at(index: int) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1156(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteRunAt(index)
            return copy

        return _arrow1156

    def DeleteRun(self, run_identifier: str) -> None:
        this: ArcInvestigation = self
        def _arrow1157(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        index: int = find_index(_arrow1157, this.Runs) or 0
        this.DeleteRunAt(index)

    @staticmethod
    def delete_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1158(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeleteRun(run_identifier)
            return copy

        return _arrow1158

    def GetRunAt(self, index: int) -> ArcRun:
        this: ArcInvestigation = self
        return this.Runs[index]

    @staticmethod
    def get_run_at(index: int) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow1159(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetRunAt(index)

        return _arrow1159

    def GetRun(self, run_identifier: str) -> ArcRun:
        this: ArcInvestigation = self
        match_value: ArcRun | None = this.TryGetRun(run_identifier)
        if match_value is None:
            raise Exception(ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier(run_identifier, this.Identifier))

        else: 
            return match_value


    @staticmethod
    def get_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun]:
        def _arrow1160(inv: ArcInvestigation) -> ArcRun:
            copy: ArcInvestigation = inv.Copy()
            return copy.GetRun(run_identifier)

        return _arrow1160

    def TryGetRun(self, run_identifier: str) -> ArcRun | None:
        this: ArcInvestigation = self
        def predicate(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        return try_find(predicate, this.Runs)

    @staticmethod
    def try_get_run(run_identifier: str) -> Callable[[ArcInvestigation], ArcRun | None]:
        def _arrow1161(inv: ArcInvestigation) -> ArcRun | None:
            copy: ArcInvestigation = inv.Copy()
            return copy.TryGetRun(run_identifier)

        return _arrow1161

    def ContainsRun(self, run_identifier: str) -> bool:
        this: ArcInvestigation = self
        def predicate(w: ArcRun) -> bool:
            return w.Identifier == run_identifier

        return exists(predicate, this.Runs)

    @staticmethod
    def contains_run(run_identifier: str) -> Callable[[ArcInvestigation], bool]:
        def _arrow1162(inv: ArcInvestigation) -> bool:
            return inv.ContainsRun(run_identifier)

        return _arrow1162

    def SetRunAt(self, index: int, run: ArcRun) -> None:
        this: ArcInvestigation = self
        run_1: ArcRun = run
        def predicate(x: ArcRun) -> bool:
            return x.Identifier == run_1.Identifier

        match_value: int | None = try_find_index(predicate, this.Runs)
        if match_value is None:
            pass

        else: 
            raise Exception(((("Cannot create run with name " + run_1.Identifier) + ", as run names must be unique and run at index ") + str(match_value)) + " has the same name.")

        run.Investigation = this
        this.Runs[index] = run

    def SetRun(self, run_identifier: str, run: ArcRun) -> None:
        this: ArcInvestigation = self
        index: int = this.GetRunIndex(run_identifier) or 0
        this.SetRunAt(index, run)

    @staticmethod
    def set_run_at(index: int, run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1163(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetRunAt(index, run)
            return copy

        return _arrow1163

    @staticmethod
    def set_run(run_identifier: str, run: ArcRun) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1164(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.SetRun(run_identifier, run)
            return copy

        return _arrow1164

    def GetAllPersons(self, __unit: None=None) -> Array[Person]:
        this: ArcInvestigation = self
        persons: Array[Person] = []
        enumerator: Any = get_enumerator(this.Assays)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(a.Performers, persons)

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Studies)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(s.Contacts, persons)

        finally: 
            dispose(enumerator_1)

        add_range_in_place(this.Contacts, persons)
        class ObjectExpr1165:
            @property
            def Equals(self) -> Callable[[Person, Person], bool]:
                return equals

            @property
            def GetHashCode(self) -> Callable[[Person], int]:
                return safe_hash

        return Array_distinct(list(persons), ObjectExpr1165())

    def GetAllPublications(self, __unit: None=None) -> Array[Publication]:
        this: ArcInvestigation = self
        pubs: Array[Publication] = []
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                s: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                add_range_in_place(s.Publications, pubs)

        finally: 
            dispose(enumerator)

        add_range_in_place(this.Publications, pubs)
        class ObjectExpr1166:
            @property
            def Equals(self) -> Callable[[Publication, Publication], bool]:
                return equals

            @property
            def GetHashCode(self) -> Callable[[Publication], int]:
                return safe_hash

        return Array_distinct(list(pubs), ObjectExpr1166())

    def DeregisterMissingAssays(self, __unit: None=None) -> None:
        this: ArcInvestigation = self
        inv: ArcInvestigation = this
        existing_assays: Array[str] = inv.AssayIdentifiers
        enumerator: Any = get_enumerator(inv.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                enumerator_1: Any = get_enumerator(list(study.RegisteredAssayIdentifiers))
                try: 
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        registered_assay: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        class ObjectExpr1168:
                            @property
                            def Equals(self) -> Callable[[str, str], bool]:
                                def _arrow1167(x: str, y: str) -> bool:
                                    return x == y

                                return _arrow1167

                            @property
                            def GetHashCode(self) -> Callable[[str], int]:
                                return string_hash

                        if not contains(registered_assay, existing_assays, ObjectExpr1168()):
                            value_1: None = study.DeregisterAssay(registered_assay)
                            ignore(None)


                finally: 
                    dispose(enumerator_1)


        finally: 
            dispose(enumerator)


    @staticmethod
    def deregister_missing_assays(__unit: None=None) -> Callable[[ArcInvestigation], ArcInvestigation]:
        def _arrow1169(inv: ArcInvestigation) -> ArcInvestigation:
            copy: ArcInvestigation = inv.Copy()
            copy.DeregisterMissingAssays()
            return copy

        return _arrow1169

    def UpdateIOTypeByEntityID(self, __unit: None=None) -> None:
        this: ArcInvestigation = self
        def _arrow1175(__unit: None=None) -> IEnumerable_1[ArcTable]:
            def _arrow1170(study: ArcStudy) -> IEnumerable_1[ArcTable]:
                return study.Tables

            def _arrow1174(__unit: None=None) -> IEnumerable_1[ArcTable]:
                def _arrow1171(assay: ArcAssay) -> IEnumerable_1[ArcTable]:
                    return assay.Tables

                def _arrow1173(__unit: None=None) -> IEnumerable_1[ArcTable]:
                    def _arrow1172(run: ArcRun) -> IEnumerable_1[ArcTable]:
                        return run.Tables

                    return collect(_arrow1172, this.Runs)

                return append_4(collect(_arrow1171, this.Assays), delay(_arrow1173))

            return append_4(collect(_arrow1170, this.Studies), delay(_arrow1174))

        io_map: Any = ArcTablesAux_getIOMap(list(to_list(delay(_arrow1175))))
        enumerator: Any = get_enumerator(this.Studies)
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                study_1: ArcStudy = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, study_1.Tables)

        finally: 
            dispose(enumerator)

        enumerator_1: Any = get_enumerator(this.Assays)
        try: 
            while enumerator_1.System_Collections_IEnumerator_MoveNext():
                assay_1: ArcAssay = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, assay_1.Tables)

        finally: 
            dispose(enumerator_1)

        enumerator_2: Any = get_enumerator(this.Runs)
        try: 
            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                run_1: ArcRun = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                ArcTablesAux_applyIOMap(io_map, run_1.Tables)

        finally: 
            dispose(enumerator_2)


    def Copy(self, __unit: None=None) -> ArcInvestigation:
        this: ArcInvestigation = self
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
        return ArcInvestigation(this.Identifier, this.Title, this.Description, this.SubmissionDate, this.PublicReleaseDate, next_ontology_source_references, next_publications, next_contacts, next_assays, next_studies, next_workflows, next_runs, next_study_identifiers, next_comments, next_remarks)

    def StructurallyEquals(self, other: ArcInvestigation) -> bool:
        this: ArcInvestigation = self
        def predicate(x: bool) -> bool:
            return x == True

        def _arrow1178(__unit: None=None) -> bool:
            a: IEnumerable_1[Publication] = this.Publications
            b: IEnumerable_1[Publication] = other.Publications
            def folder(acc: bool, e: bool) -> bool:
                if acc:
                    return e

                else: 
                    return False


            def _arrow1177(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1176(i_1: int) -> bool:
                    return equals(item(i_1, a), item(i_1, b))

                return map_1(_arrow1176, range_big_int(0, 1, length(a) - 1))

            return fold(folder, True, to_list(delay(_arrow1177))) if (length(a) == length(b)) else False

        def _arrow1181(__unit: None=None) -> bool:
            a_1: IEnumerable_1[Person] = this.Contacts
            b_1: IEnumerable_1[Person] = other.Contacts
            def folder_1(acc_1: bool, e_1: bool) -> bool:
                if acc_1:
                    return e_1

                else: 
                    return False


            def _arrow1180(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1179(i_2: int) -> bool:
                    return equals(item(i_2, a_1), item(i_2, b_1))

                return map_1(_arrow1179, range_big_int(0, 1, length(a_1) - 1))

            return fold(folder_1, True, to_list(delay(_arrow1180))) if (length(a_1) == length(b_1)) else False

        def _arrow1184(__unit: None=None) -> bool:
            a_2: IEnumerable_1[OntologySourceReference] = this.OntologySourceReferences
            b_2: IEnumerable_1[OntologySourceReference] = other.OntologySourceReferences
            def folder_2(acc_2: bool, e_2: bool) -> bool:
                if acc_2:
                    return e_2

                else: 
                    return False


            def _arrow1183(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1182(i_3: int) -> bool:
                    return equals(item(i_3, a_2), item(i_3, b_2))

                return map_1(_arrow1182, range_big_int(0, 1, length(a_2) - 1))

            return fold(folder_2, True, to_list(delay(_arrow1183))) if (length(a_2) == length(b_2)) else False

        def _arrow1187(__unit: None=None) -> bool:
            a_3: IEnumerable_1[ArcAssay] = this.Assays
            b_3: IEnumerable_1[ArcAssay] = other.Assays
            def folder_3(acc_3: bool, e_3: bool) -> bool:
                if acc_3:
                    return e_3

                else: 
                    return False


            def _arrow1186(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1185(i_4: int) -> bool:
                    return equals(item(i_4, a_3), item(i_4, b_3))

                return map_1(_arrow1185, range_big_int(0, 1, length(a_3) - 1))

            return fold(folder_3, True, to_list(delay(_arrow1186))) if (length(a_3) == length(b_3)) else False

        def _arrow1190(__unit: None=None) -> bool:
            a_4: IEnumerable_1[ArcStudy] = this.Studies
            b_4: IEnumerable_1[ArcStudy] = other.Studies
            def folder_4(acc_4: bool, e_4: bool) -> bool:
                if acc_4:
                    return e_4

                else: 
                    return False


            def _arrow1189(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1188(i_5: int) -> bool:
                    return equals(item(i_5, a_4), item(i_5, b_4))

                return map_1(_arrow1188, range_big_int(0, 1, length(a_4) - 1))

            return fold(folder_4, True, to_list(delay(_arrow1189))) if (length(a_4) == length(b_4)) else False

        def _arrow1193(__unit: None=None) -> bool:
            a_5: IEnumerable_1[ArcWorkflow] = this.Workflows
            b_5: IEnumerable_1[ArcWorkflow] = other.Workflows
            def folder_5(acc_5: bool, e_5: bool) -> bool:
                if acc_5:
                    return e_5

                else: 
                    return False


            def _arrow1192(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1191(i_6: int) -> bool:
                    return equals(item(i_6, a_5), item(i_6, b_5))

                return map_1(_arrow1191, range_big_int(0, 1, length(a_5) - 1))

            return fold(folder_5, True, to_list(delay(_arrow1192))) if (length(a_5) == length(b_5)) else False

        def _arrow1196(__unit: None=None) -> bool:
            a_6: IEnumerable_1[ArcRun] = this.Runs
            b_6: IEnumerable_1[ArcRun] = other.Runs
            def folder_6(acc_6: bool, e_6: bool) -> bool:
                if acc_6:
                    return e_6

                else: 
                    return False


            def _arrow1195(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1194(i_7: int) -> bool:
                    return equals(item(i_7, a_6), item(i_7, b_6))

                return map_1(_arrow1194, range_big_int(0, 1, length(a_6) - 1))

            return fold(folder_6, True, to_list(delay(_arrow1195))) if (length(a_6) == length(b_6)) else False

        def _arrow1199(__unit: None=None) -> bool:
            a_7: IEnumerable_1[str] = this.RegisteredStudyIdentifiers
            b_7: IEnumerable_1[str] = other.RegisteredStudyIdentifiers
            def folder_7(acc_7: bool, e_7: bool) -> bool:
                if acc_7:
                    return e_7

                else: 
                    return False


            def _arrow1198(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1197(i_8: int) -> bool:
                    return item(i_8, a_7) == item(i_8, b_7)

                return map_1(_arrow1197, range_big_int(0, 1, length(a_7) - 1))

            return fold(folder_7, True, to_list(delay(_arrow1198))) if (length(a_7) == length(b_7)) else False

        def _arrow1202(__unit: None=None) -> bool:
            a_8: IEnumerable_1[Comment] = this.Comments
            b_8: IEnumerable_1[Comment] = other.Comments
            def folder_8(acc_8: bool, e_8: bool) -> bool:
                if acc_8:
                    return e_8

                else: 
                    return False


            def _arrow1201(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1200(i_9: int) -> bool:
                    return equals(item(i_9, a_8), item(i_9, b_8))

                return map_1(_arrow1200, range_big_int(0, 1, length(a_8) - 1))

            return fold(folder_8, True, to_list(delay(_arrow1201))) if (length(a_8) == length(b_8)) else False

        def _arrow1205(__unit: None=None) -> bool:
            a_9: IEnumerable_1[Remark] = this.Remarks
            b_9: IEnumerable_1[Remark] = other.Remarks
            def folder_9(acc_9: bool, e_9: bool) -> bool:
                if acc_9:
                    return e_9

                else: 
                    return False


            def _arrow1204(__unit: None=None) -> IEnumerable_1[bool]:
                def _arrow1203(i_10: int) -> bool:
                    return equals(item(i_10, a_9), item(i_10, b_9))

                return map_1(_arrow1203, range_big_int(0, 1, length(a_9) - 1))

            return fold(folder_9, True, to_list(delay(_arrow1204))) if (length(a_9) == length(b_9)) else False

        return for_all(predicate, to_enumerable([this.Identifier == other.Identifier, equals(this.Title, other.Title), equals(this.Description, other.Description), equals(this.SubmissionDate, other.SubmissionDate), equals(this.PublicReleaseDate, other.PublicReleaseDate), _arrow1178(), _arrow1181(), _arrow1184(), _arrow1187(), _arrow1190(), _arrow1193(), _arrow1196(), _arrow1199(), _arrow1202(), _arrow1205()]))

    def ReferenceEquals(self, other: ArcInvestigation) -> bool:
        this: ArcInvestigation = self
        return this is other

    def __str__(self, __unit: None=None) -> str:
        this: ArcInvestigation = self
        arg: str = this.Identifier
        arg_1: str | None = this.Title
        arg_2: str | None = this.Description
        arg_3: str | None = this.SubmissionDate
        arg_4: str | None = this.PublicReleaseDate
        arg_5: Array[OntologySourceReference] = this.OntologySourceReferences
        arg_6: Array[Publication] = this.Publications
        arg_7: Array[Person] = this.Contacts
        arg_8: Array[ArcAssay] = this.Assays
        arg_9: Array[ArcStudy] = this.Studies
        arg_10: Array[ArcWorkflow] = this.Workflows
        arg_11: Array[ArcRun] = this.Runs
        arg_12: Array[str] = this.RegisteredStudyIdentifiers
        arg_13: Array[Comment] = this.Comments
        arg_14: Array[Remark] = this.Remarks
        return to_text(printf("ArcInvestigation {\r\n    Identifier = %A,\r\n    Title = %A,\r\n    Description = %A,\r\n    SubmissionDate = %A,\r\n    PublicReleaseDate = %A,\r\n    OntologySourceReferences = %A,\r\n    Publications = %A,\r\n    Contacts = %A,\r\n    Assays = %A,\r\n    Studies = %A,\r\n    Workflows = %A,\r\n    Runs = %A,\r\n    RegisteredStudyIdentifiers = %A,\r\n    Comments = %A,\r\n    Remarks = %A,\r\n}"))(arg)(arg_1)(arg_2)(arg_3)(arg_4)(arg_5)(arg_6)(arg_7)(arg_8)(arg_9)(arg_10)(arg_11)(arg_12)(arg_13)(arg_14)

    def __eq__(self, other: Any=None) -> bool:
        this: ArcInvestigation = self
        return this.StructurallyEquals(other) if isinstance(other, ArcInvestigation) else False

    def __hash__(self, __unit: None=None) -> Any:
        this: ArcInvestigation = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.OntologySourceReferences), box_hash_seq(this.Assays), box_hash_seq(this.Studies), box_hash_seq(this.Workflows), box_hash_seq(this.Runs), box_hash_seq(this.RegisteredStudyIdentifiers), box_hash_seq(this.Comments), box_hash_seq(this.Remarks)])

    def GetLightHashCode(self, __unit: None=None) -> Any:
        this: ArcInvestigation = self
        return box_hash_array([this.Identifier, box_hash_option(this.Title), box_hash_option(this.Description), box_hash_option(this.SubmissionDate), box_hash_option(this.PublicReleaseDate), box_hash_seq(this.Publications), box_hash_seq(this.Contacts), box_hash_seq(this.OntologySourceReferences), box_hash_seq(this.RegisteredStudyIdentifiers), box_hash_seq(this.Comments), box_hash_seq(this.Remarks)])


ArcInvestigation_reflection = _expr1207

def ArcInvestigation__ctor_Z67823F6C(identifier: str, title: str | None=None, description: str | None=None, submission_date: str | None=None, public_release_date: str | None=None, ontology_source_references: Array[OntologySourceReference] | None=None, publications: Array[Publication] | None=None, contacts: Array[Person] | None=None, assays: Array[ArcAssay] | None=None, studies: Array[ArcStudy] | None=None, workflows: Array[ArcWorkflow] | None=None, runs: Array[ArcRun] | None=None, registered_study_identifiers: Array[str] | None=None, comments: Array[Comment] | None=None, remarks: Array[Remark] | None=None) -> ArcInvestigation:
    return ArcInvestigation(identifier, title, description, submission_date, public_release_date, ontology_source_references, publications, contacts, assays, studies, workflows, runs, registered_study_identifiers, comments, remarks)


def ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier(assay_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find assay with identifier \'" + str(assay_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier(study_identifer: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find study with identifier \'" + str(study_identifer)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier(workflow_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find workflow with identifier \'" + str(workflow_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier(run_identifier: Any, investigation_identifier: Any) -> str:
    return ((("Error. Unable to find run with identifier \'" + str(run_identifier)) + "\' in investigation ") + str(investigation_identifier)) + "."


def ArcWorkflow__get_Identifier(this: ArcWorkflow) -> str:
    return this.identifier_00401151


def ArcWorkflow__set_Identifier_Z721C83C5(this: ArcWorkflow, i: str) -> None:
    this.identifier_00401151 = i


def ArcWorkflow__get_Investigation(this: ArcWorkflow) -> ArcInvestigation | None:
    return this.investigation


def ArcWorkflow__set_Investigation_Z1E102E3E(this: ArcWorkflow, a: ArcInvestigation | None=None) -> None:
    this.investigation = a


def ArcWorkflow__get_Title(this: ArcWorkflow) -> str | None:
    return this.title_00401156


def ArcWorkflow__set_Title_6DFDD678(this: ArcWorkflow, t: str | None=None) -> None:
    this.title_00401156 = t


def ArcWorkflow__get_Description(this: ArcWorkflow) -> str | None:
    return this.description_00401157


def ArcWorkflow__set_Description_6DFDD678(this: ArcWorkflow, d: str | None=None) -> None:
    this.description_00401157 = d


def ArcWorkflow__get_SubWorkflowIdentifiers(this: ArcWorkflow) -> Array[str]:
    return this.sub_workflow_identifiers_00401158


def ArcWorkflow__set_SubWorkflowIdentifiers_70A00D82(this: ArcWorkflow, s: Array[str]) -> None:
    this.sub_workflow_identifiers_00401158 = s


def ArcWorkflow__get_WorkflowType(this: ArcWorkflow) -> OntologyAnnotation | None:
    return this.workflow_type_00401159


def ArcWorkflow__set_WorkflowType_279AAFF2(this: ArcWorkflow, w: OntologyAnnotation | None=None) -> None:
    this.workflow_type_00401159 = w


def ArcWorkflow__get_URI(this: ArcWorkflow) -> str | None:
    return this.uri_00401160


def ArcWorkflow__set_URI_6DFDD678(this: ArcWorkflow, u: str | None=None) -> None:
    this.uri_00401160 = u


def ArcWorkflow__get_Version(this: ArcWorkflow) -> str | None:
    return this.version_00401161


def ArcWorkflow__set_Version_6DFDD678(this: ArcWorkflow, v: str | None=None) -> None:
    this.version_00401161 = v


def ArcWorkflow__get_Parameters(this: ArcWorkflow) -> Array[ProtocolParameter]:
    return this.parameters_00401162


def ArcWorkflow__set_Parameters_10749ED2(this: ArcWorkflow, p: Array[ProtocolParameter]) -> None:
    this.parameters_00401162 = p


def ArcWorkflow__get_Components(this: ArcWorkflow) -> Array[Component]:
    return this.components_00401163


def ArcWorkflow__set_Components_Z3A507DDE(this: ArcWorkflow, c: Array[Component]) -> None:
    this.components_00401163 = c


def ArcWorkflow__get_DataMap(this: ArcWorkflow) -> DataMap | None:
    return this.data_map


def ArcWorkflow__set_DataMap_51F1E59E(this: ArcWorkflow, dm: DataMap | None=None) -> None:
    this.data_map = dm


def ArcWorkflow__get_Contacts(this: ArcWorkflow) -> Array[Person]:
    return this.contacts_00401165


def ArcWorkflow__set_Contacts_Z7E0D1CA3(this: ArcWorkflow, c: Array[Person]) -> None:
    this.contacts_00401165 = c


def ArcWorkflow__get_Comments(this: ArcWorkflow) -> Array[Comment]:
    return this.comments_00401166


def ArcWorkflow__set_Comments_149C14BB(this: ArcWorkflow, c: Array[Comment]) -> None:
    this.comments_00401166 = c


def ArcWorkflow__get_StaticHash(this: ArcWorkflow) -> int:
    return this.static_hash


def ArcWorkflow__set_StaticHash_Z524259A4(this: ArcWorkflow, s: int) -> None:
    this.static_hash = s or 0


def ArcWorkflow_init_Z721C83C5(identifier: str) -> ArcWorkflow:
    return ArcWorkflow__ctor_Z3BB02240(identifier)


def ArcWorkflow_create_Z3BB02240(identifier: str, title: str | None=None, description: str | None=None, workflow_type: OntologyAnnotation | None=None, uri: str | None=None, version: str | None=None, sub_workflow_identifiers: Array[str] | None=None, parameters: Array[ProtocolParameter] | None=None, components: Array[Component] | None=None, datamap: DataMap | None=None, contacts: Array[Person] | None=None, comments: Array[Comment] | None=None) -> ArcWorkflow:
    return ArcWorkflow__ctor_Z3BB02240(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)


def ArcWorkflow_make(identifier: str, title: str | None, description: str | None, workflow_type: OntologyAnnotation | None, uri: str | None, version: str | None, sub_workflow_identifiers: Array[str], parameters: Array[ProtocolParameter], components: Array[Component], datamap: DataMap | None, contacts: Array[Person], comments: Array[Comment]) -> ArcWorkflow:
    return ArcWorkflow__ctor_Z3BB02240(identifier, title, description, workflow_type, uri, version, sub_workflow_identifiers, parameters, components, datamap, contacts, comments)


def ArcWorkflow_get_FileName(__unit: None=None) -> str:
    return "isa.run.xlsx"


def ArcWorkflow__get_SubWorkflowIdentifiersCount(this: ArcWorkflow) -> int:
    return len(ArcWorkflow__get_SubWorkflowIdentifiers(this))


def ArcWorkflow__get_SubWorkflowCount(this: ArcWorkflow) -> int:
    return len(ArcWorkflow__get_SubWorkflows(this))


def ArcWorkflow__get_SubWorkflows(this: ArcWorkflow) -> Array[ArcWorkflow]:
    inv: ArcInvestigation
    investigation: ArcInvestigation | None = ArcWorkflow__get_Investigation(this)
    if investigation is not None:
        inv = investigation

    else: 
        raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

    def chooser(workflow_identifier: str, this: Any=this) -> ArcWorkflow | None:
        return inv.TryGetWorkflow(workflow_identifier)

    return list(choose(chooser, ArcWorkflow__get_SubWorkflowIdentifiers(this)))


def ArcWorkflow__get_VacantSubWorkflowIdentifiers(this: ArcWorkflow) -> Array[str]:
    inv: ArcInvestigation
    investigation: ArcInvestigation | None = ArcWorkflow__get_Investigation(this)
    if investigation is not None:
        inv = investigation

    else: 
        raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

    def predicate(arg: str, this: Any=this) -> bool:
        return not inv.ContainsWorkflow(arg)

    return list(filter(predicate, ArcWorkflow__get_SubWorkflowIdentifiers(this)))


def ArcWorkflow__AddSubWorkflow_Z1C75CB0E(this: ArcWorkflow, sub_workflow: ArcWorkflow) -> None:
    inv: ArcInvestigation
    investigation: ArcInvestigation | None = ArcWorkflow__get_Investigation(this)
    if investigation is not None:
        inv = investigation

    else: 
        raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

    inv.AddWorkflow(sub_workflow)


def ArcWorkflow_addSubWorkflow_Z1C75CB0E(sub_workflow: ArcWorkflow) -> Callable[[ArcWorkflow], ArcWorkflow]:
    def _arrow1210(workflow: ArcWorkflow, sub_workflow: Any=sub_workflow) -> ArcWorkflow:
        new_workflow: ArcWorkflow = ArcWorkflow__Copy_6FCE9E49(workflow)
        ArcWorkflow__AddSubWorkflow_Z1C75CB0E(new_workflow, sub_workflow)
        return new_workflow

    return _arrow1210


def ArcWorkflow__InitSubWorkflow_Z721C83C5(this: ArcWorkflow, sub_workflow_identifier: str) -> ArcWorkflow:
    sub_workflow: ArcWorkflow = ArcWorkflow__ctor_Z3BB02240(sub_workflow_identifier)
    ArcWorkflow__AddSubWorkflow_Z1C75CB0E(this, sub_workflow)
    return sub_workflow


def ArcWorkflow_initSubWorkflow_Z721C83C5(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], tuple[ArcWorkflow, ArcWorkflow]]:
    def _arrow1211(workflow: ArcWorkflow, sub_workflow_identifier: Any=sub_workflow_identifier) -> tuple[ArcWorkflow, ArcWorkflow]:
        copy: ArcWorkflow = ArcWorkflow__Copy_6FCE9E49(workflow)
        return (copy, ArcWorkflow__InitSubWorkflow_Z721C83C5(copy, sub_workflow_identifier))

    return _arrow1211


def ArcWorkflow__RegisterSubWorkflow_Z721C83C5(this: ArcWorkflow, sub_workflow_identifier: str) -> None:
    class ObjectExpr1213:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1212(x: str, y: str) -> bool:
                return x == y

            return _arrow1212

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    if contains(sub_workflow_identifier, ArcWorkflow__get_SubWorkflowIdentifiers(this), ObjectExpr1213()):
        raise Exception(("SubWorkflow `" + sub_workflow_identifier) + "` is already registered on the workflow.")

    (ArcWorkflow__get_SubWorkflowIdentifiers(this).append(sub_workflow_identifier))


def ArcWorkflow_registerSubWorkflow_Z721C83C5(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
    def _arrow1214(workflow: ArcWorkflow, sub_workflow_identifier: Any=sub_workflow_identifier) -> ArcWorkflow:
        copy: ArcWorkflow = ArcWorkflow__Copy_6FCE9E49(workflow)
        ArcWorkflow__RegisterSubWorkflow_Z721C83C5(copy, sub_workflow_identifier)
        return copy

    return _arrow1214


def ArcWorkflow__DeregisterSubWorkflow_Z721C83C5(this: ArcWorkflow, sub_workflow_identifier: str) -> None:
    class ObjectExpr1216:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1215(x: str, y: str) -> bool:
                return x == y

            return _arrow1215

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    ignore(remove_in_place(sub_workflow_identifier, ArcWorkflow__get_SubWorkflowIdentifiers(this), ObjectExpr1216()))


def ArcWorkflow_deregisterSubWorkflow_Z721C83C5(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
    def _arrow1217(workflow: ArcWorkflow, sub_workflow_identifier: Any=sub_workflow_identifier) -> ArcWorkflow:
        copy: ArcWorkflow = ArcWorkflow__Copy_6FCE9E49(workflow)
        ArcWorkflow__DeregisterSubWorkflow_Z721C83C5(copy, sub_workflow_identifier)
        return copy

    return _arrow1217


def ArcWorkflow__GetRegisteredSubWorkflow_Z721C83C5(this: ArcWorkflow, sub_workflow_identifier: str) -> ArcWorkflow:
    class ObjectExpr1219:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1218(x: str, y: str) -> bool:
                return x == y

            return _arrow1218

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    if not contains(sub_workflow_identifier, ArcWorkflow__get_SubWorkflowIdentifiers(this), ObjectExpr1219()):
        raise Exception(("SubWorkflow `" + sub_workflow_identifier) + "` is not registered on the workflow.")

    inv: ArcInvestigation
    investigation: ArcInvestigation | None = ArcWorkflow__get_Investigation(this)
    if investigation is not None:
        inv = investigation

    else: 
        raise Exception("Cannot execute this function. Object is not part of ArcInvestigation.")

    return inv.GetWorkflow(sub_workflow_identifier)


def ArcWorkflow_getRegisteredSubWorkflow_Z721C83C5(sub_workflow_identifier: str) -> Callable[[ArcWorkflow], ArcWorkflow]:
    def _arrow1220(workflow: ArcWorkflow, sub_workflow_identifier: Any=sub_workflow_identifier) -> ArcWorkflow:
        return ArcWorkflow__GetRegisteredSubWorkflow_Z721C83C5(ArcWorkflow__Copy_6FCE9E49(workflow), sub_workflow_identifier)

    return _arrow1220


def ArcWorkflow_getRegisteredSubWorkflows(__unit: None=None) -> Callable[[ArcWorkflow], Array[ArcWorkflow]]:
    def _arrow1221(workflow: ArcWorkflow) -> Array[ArcWorkflow]:
        return ArcWorkflow__get_SubWorkflows(ArcWorkflow__Copy_6FCE9E49(workflow))

    return _arrow1221


def ArcWorkflow__GetRegisteredSubWorkflowsOrIdentifier(this: ArcWorkflow) -> Array[ArcWorkflow]:
    match_value: ArcInvestigation | None = ArcWorkflow__get_Investigation(this)
    if match_value is None:
        def f_1(identifier_1: str, this: Any=this) -> ArcWorkflow:
            return ArcWorkflow_init_Z721C83C5(identifier_1)

        return ResizeArray_map(f_1, ArcWorkflow__get_SubWorkflowIdentifiers(this))

    else: 
        i: ArcInvestigation = match_value
        def f(identifier: str, this: Any=this) -> ArcWorkflow:
            match_value_1: ArcWorkflow | None = i.TryGetWorkflow(identifier)
            if match_value_1 is None:
                return ArcWorkflow_init_Z721C83C5(identifier)

            else: 
                return match_value_1


        return ResizeArray_map(f, ArcWorkflow__get_SubWorkflowIdentifiers(this))



def ArcWorkflow_getRegisteredSubWorkflowsOrIdentifier(__unit: None=None) -> Callable[[ArcWorkflow], Array[ArcWorkflow]]:
    def _arrow1222(workflow: ArcWorkflow) -> Array[ArcWorkflow]:
        return ArcWorkflow__GetRegisteredSubWorkflowsOrIdentifier(ArcWorkflow__Copy_6FCE9E49(workflow))

    return _arrow1222


def ArcWorkflow__Copy_6FCE9E49(this: ArcWorkflow, copy_investigation_ref: bool | None=None) -> ArcWorkflow:
    copy_investigation_ref_1: bool = default_arg(copy_investigation_ref, False)
    def mapping(w: OntologyAnnotation, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> OntologyAnnotation:
        return w.Copy()

    next_work_flow_type: OntologyAnnotation | None = map(mapping, ArcWorkflow__get_WorkflowType(this))
    next_sub_workflow_identifiers: Array[str] = list(ArcWorkflow__get_SubWorkflowIdentifiers(this))
    def f(x: ProtocolParameter, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> ProtocolParameter:
        return x

    next_parameters: Array[ProtocolParameter] = ResizeArray_map(f, ArcWorkflow__get_Parameters(this))
    def f_1(x_1: Component, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> Component:
        return x_1

    next_components: Array[Component] = ResizeArray_map(f_1, ArcWorkflow__get_Components(this))
    def mapping_1(d: DataMap, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> DataMap:
        return DataMap__Copy(d)

    next_data_map: DataMap | None = map(mapping_1, ArcWorkflow__get_DataMap(this))
    def f_2(c: Person, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> Person:
        return c.Copy()

    next_contacts: Array[Person] = ResizeArray_map(f_2, ArcWorkflow__get_Contacts(this))
    def f_3(c_1: Comment, this: Any=this, copy_investigation_ref: Any=copy_investigation_ref) -> Comment:
        return c_1.Copy()

    next_comments: Array[Comment] = ResizeArray_map(f_3, ArcWorkflow__get_Comments(this))
    workflow: ArcWorkflow = ArcWorkflow_make(ArcWorkflow__get_Identifier(this), ArcWorkflow__get_Title(this), ArcWorkflow__get_Description(this), next_work_flow_type, ArcWorkflow__get_URI(this), ArcWorkflow__get_Version(this), next_sub_workflow_identifiers, next_parameters, next_components, next_data_map, next_contacts, next_comments)
    if copy_investigation_ref_1:
        ArcWorkflow__set_Investigation_Z1E102E3E(workflow, ArcWorkflow__get_Investigation(this))

    return workflow


def ArcWorkflow__StructurallyEquals_Z1C75CB0E(this: ArcWorkflow, other: ArcWorkflow) -> bool:
    def predicate(x: bool, this: Any=this, other: Any=other) -> bool:
        return x == True

    def _arrow1225(__unit: None=None, this: Any=this, other: Any=other) -> bool:
        a: IEnumerable_1[str] = ArcWorkflow__get_SubWorkflowIdentifiers(this)
        b: IEnumerable_1[str] = ArcWorkflow__get_SubWorkflowIdentifiers(other)
        def folder(acc: bool, e: bool) -> bool:
            if acc:
                return e

            else: 
                return False


        def _arrow1224(__unit: None=None) -> IEnumerable_1[bool]:
            def _arrow1223(i_1: int) -> bool:
                return item(i_1, a) == item(i_1, b)

            return map_1(_arrow1223, range_big_int(0, 1, length(a) - 1))

        return fold(folder, True, to_list(delay(_arrow1224))) if (length(a) == length(b)) else False

    def _arrow1228(__unit: None=None, this: Any=this, other: Any=other) -> bool:
        a_1: IEnumerable_1[ProtocolParameter] = ArcWorkflow__get_Parameters(this)
        b_1: IEnumerable_1[ProtocolParameter] = ArcWorkflow__get_Parameters(other)
        def folder_1(acc_1: bool, e_1: bool) -> bool:
            if acc_1:
                return e_1

            else: 
                return False


        def _arrow1227(__unit: None=None) -> IEnumerable_1[bool]:
            def _arrow1226(i_2: int) -> bool:
                return equals(item(i_2, a_1), item(i_2, b_1))

            return map_1(_arrow1226, range_big_int(0, 1, length(a_1) - 1))

        return fold(folder_1, True, to_list(delay(_arrow1227))) if (length(a_1) == length(b_1)) else False

    def _arrow1231(__unit: None=None, this: Any=this, other: Any=other) -> bool:
        a_2: IEnumerable_1[Component] = ArcWorkflow__get_Components(this)
        b_2: IEnumerable_1[Component] = ArcWorkflow__get_Components(other)
        def folder_2(acc_2: bool, e_2: bool) -> bool:
            if acc_2:
                return e_2

            else: 
                return False


        def _arrow1230(__unit: None=None) -> IEnumerable_1[bool]:
            def _arrow1229(i_3: int) -> bool:
                return equals(item(i_3, a_2), item(i_3, b_2))

            return map_1(_arrow1229, range_big_int(0, 1, length(a_2) - 1))

        return fold(folder_2, True, to_list(delay(_arrow1230))) if (length(a_2) == length(b_2)) else False

    def _arrow1234(__unit: None=None, this: Any=this, other: Any=other) -> bool:
        a_3: IEnumerable_1[Person] = ArcWorkflow__get_Contacts(this)
        b_3: IEnumerable_1[Person] = ArcWorkflow__get_Contacts(other)
        def folder_3(acc_3: bool, e_3: bool) -> bool:
            if acc_3:
                return e_3

            else: 
                return False


        def _arrow1233(__unit: None=None) -> IEnumerable_1[bool]:
            def _arrow1232(i_4: int) -> bool:
                return equals(item(i_4, a_3), item(i_4, b_3))

            return map_1(_arrow1232, range_big_int(0, 1, length(a_3) - 1))

        return fold(folder_3, True, to_list(delay(_arrow1233))) if (length(a_3) == length(b_3)) else False

    def _arrow1237(__unit: None=None, this: Any=this, other: Any=other) -> bool:
        a_4: IEnumerable_1[Comment] = ArcWorkflow__get_Comments(this)
        b_4: IEnumerable_1[Comment] = ArcWorkflow__get_Comments(other)
        def folder_4(acc_4: bool, e_4: bool) -> bool:
            if acc_4:
                return e_4

            else: 
                return False


        def _arrow1236(__unit: None=None) -> IEnumerable_1[bool]:
            def _arrow1235(i_5: int) -> bool:
                return equals(item(i_5, a_4), item(i_5, b_4))

            return map_1(_arrow1235, range_big_int(0, 1, length(a_4) - 1))

        return fold(folder_4, True, to_list(delay(_arrow1236))) if (length(a_4) == length(b_4)) else False

    return for_all(predicate, to_enumerable([ArcWorkflow__get_Identifier(this) == ArcWorkflow__get_Identifier(other), equals(ArcWorkflow__get_Title(this), ArcWorkflow__get_Title(other)), equals(ArcWorkflow__get_Description(this), ArcWorkflow__get_Description(other)), equals(ArcWorkflow__get_WorkflowType(this), ArcWorkflow__get_WorkflowType(other)), equals(ArcWorkflow__get_URI(this), ArcWorkflow__get_URI(other)), equals(ArcWorkflow__get_Version(this), ArcWorkflow__get_Version(other)), _arrow1225(), _arrow1228(), _arrow1231(), equals(ArcWorkflow__get_DataMap(this), ArcWorkflow__get_DataMap(other)), _arrow1234(), _arrow1237()]))


def ArcWorkflow__ReferenceEquals_1680536E(this: ArcWorkflow, other: ArcStudy) -> bool:
    return this is other


def ArcWorkflow__GetLightHashCode(this: ArcWorkflow) -> Any:
    return box_hash_array([ArcWorkflow__get_Identifier(this), box_hash_option(ArcWorkflow__get_Title(this)), box_hash_option(ArcWorkflow__get_Description(this)), box_hash_option(ArcWorkflow__get_WorkflowType(this)), box_hash_option(ArcWorkflow__get_URI(this)), box_hash_option(ArcWorkflow__get_Version(this)), box_hash_seq(ArcWorkflow__get_SubWorkflowIdentifiers(this)), box_hash_seq(ArcWorkflow__get_Parameters(this)), box_hash_seq(ArcWorkflow__get_Components(this)), box_hash_seq(ArcWorkflow__get_Contacts(this)), box_hash_seq(ArcWorkflow__get_Comments(this))])


__all__ = ["ArcAssay_reflection", "ArcStudy_reflection", "ArcWorkflow_reflection", "ArcRun_reflection", "ArcInvestigation_reflection", "ArcTypesAux_ErrorMsgs_unableToFindAssayIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindStudyIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindWorkflowIdentifier", "ArcTypesAux_ErrorMsgs_unableToFindRunIdentifier", "ArcWorkflow__get_Identifier", "ArcWorkflow__set_Identifier_Z721C83C5", "ArcWorkflow__get_Investigation", "ArcWorkflow__set_Investigation_Z1E102E3E", "ArcWorkflow__get_Title", "ArcWorkflow__set_Title_6DFDD678", "ArcWorkflow__get_Description", "ArcWorkflow__set_Description_6DFDD678", "ArcWorkflow__get_SubWorkflowIdentifiers", "ArcWorkflow__set_SubWorkflowIdentifiers_70A00D82", "ArcWorkflow__get_WorkflowType", "ArcWorkflow__set_WorkflowType_279AAFF2", "ArcWorkflow__get_URI", "ArcWorkflow__set_URI_6DFDD678", "ArcWorkflow__get_Version", "ArcWorkflow__set_Version_6DFDD678", "ArcWorkflow__get_Parameters", "ArcWorkflow__set_Parameters_10749ED2", "ArcWorkflow__get_Components", "ArcWorkflow__set_Components_Z3A507DDE", "ArcWorkflow__get_DataMap", "ArcWorkflow__set_DataMap_51F1E59E", "ArcWorkflow__get_Contacts", "ArcWorkflow__set_Contacts_Z7E0D1CA3", "ArcWorkflow__get_Comments", "ArcWorkflow__set_Comments_149C14BB", "ArcWorkflow__get_StaticHash", "ArcWorkflow__set_StaticHash_Z524259A4", "ArcWorkflow_init_Z721C83C5", "ArcWorkflow_create_Z3BB02240", "ArcWorkflow_make", "ArcWorkflow_get_FileName", "ArcWorkflow__get_SubWorkflowIdentifiersCount", "ArcWorkflow__get_SubWorkflowCount", "ArcWorkflow__get_SubWorkflows", "ArcWorkflow__get_VacantSubWorkflowIdentifiers", "ArcWorkflow__AddSubWorkflow_Z1C75CB0E", "ArcWorkflow_addSubWorkflow_Z1C75CB0E", "ArcWorkflow__InitSubWorkflow_Z721C83C5", "ArcWorkflow_initSubWorkflow_Z721C83C5", "ArcWorkflow__RegisterSubWorkflow_Z721C83C5", "ArcWorkflow_registerSubWorkflow_Z721C83C5", "ArcWorkflow__DeregisterSubWorkflow_Z721C83C5", "ArcWorkflow_deregisterSubWorkflow_Z721C83C5", "ArcWorkflow__GetRegisteredSubWorkflow_Z721C83C5", "ArcWorkflow_getRegisteredSubWorkflow_Z721C83C5", "ArcWorkflow_getRegisteredSubWorkflows", "ArcWorkflow__GetRegisteredSubWorkflowsOrIdentifier", "ArcWorkflow_getRegisteredSubWorkflowsOrIdentifier", "ArcWorkflow__Copy_6FCE9E49", "ArcWorkflow__StructurallyEquals_Z1C75CB0E", "ArcWorkflow__ReferenceEquals_1680536E", "ArcWorkflow__GetLightHashCode"]

