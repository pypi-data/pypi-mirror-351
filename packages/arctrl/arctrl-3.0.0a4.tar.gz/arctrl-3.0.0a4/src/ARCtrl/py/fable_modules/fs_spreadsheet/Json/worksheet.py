from __future__ import annotations
from typing import (Any, TypeVar)
from ...fable_library.option import default_arg
from ...fable_library.range import range_big_int
from ...fable_library.seq import (to_list, delay, map, collect, singleton, append, is_empty, empty, iterate)
from ...fable_library.util import (IEnumerable_1, ignore)
from ...thoth_json_core.decode import (object, IRequiredGetter, string, seq as seq_1, IOptionalGetter, IGetters)
from ...thoth_json_core.encode import seq
from ...thoth_json_core.types import (IEncodable, IEncoderHelpers_1, Decoder_1)
from ..Cells.fs_cell import FsCell
from ..Cells.fs_cells_collection import FsCellsCollection__TryGetCell_Z37302880
from ..fs_column import FsColumn
from ..fs_row import FsRow
from ..fs_worksheet import FsWorksheet
from ..Tables.fs_table import FsTable
from .column import (encode_no_numbers as encode_no_numbers_1, encode as encode_2, decode as decode_2)
from .row import (encode_no_numbers, encode, decode as decode_1)
from .table import (encode as encode_1, decode)

__A_ = TypeVar("__A_")

def encode_rows(no_numbering: bool, sheet: FsWorksheet) -> IEncodable:
    sheet.RescanRows()
    def _arrow321(__unit: None=None, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEnumerable_1[IEncodable]:
        def _arrow320(r: int) -> IEncodable:
            def _arrow319(__unit: None=None) -> IEnumerable_1[FsCell]:
                def _arrow318(c: int) -> IEnumerable_1[FsCell]:
                    match_value: FsCell | None = FsCellsCollection__TryGetCell_Z37302880(sheet.CellCollection, r, c)
                    return singleton(FsCell("")) if (match_value is None) else singleton(match_value)

                return collect(_arrow318, range_big_int(1, 1, sheet.MaxColumnIndex))

            return encode_no_numbers(to_list(delay(_arrow319)))

        return map(_arrow320, range_big_int(1, 1, sheet.MaxRowIndex))

    def mapping(row_1: FsRow, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEncodable:
        return encode(row_1)

    j_rows: IEncodable = seq(to_list(delay(_arrow321))) if no_numbering else seq(map(mapping, sheet.Rows))
    def _arrow326(__unit: None=None, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEnumerable_1[tuple[str, IEncodable]]:
        def _arrow323(__unit: None=None) -> IEncodable:
            value: str = sheet.Name
            class ObjectExpr322(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value)

            return ObjectExpr322()

        def _arrow325(__unit: None=None) -> IEnumerable_1[tuple[str, IEncodable]]:
            def _arrow324(__unit: None=None) -> IEnumerable_1[tuple[str, IEncodable]]:
                return singleton(("rows", j_rows))

            return append(singleton(("tables", seq(map(encode_1, sheet.Tables)))) if (not is_empty(sheet.Tables)) else empty(), delay(_arrow324))

        return append(singleton(("name", _arrow323())), delay(_arrow325))

    values_1: IEnumerable_1[tuple[str, IEncodable]] = to_list(delay(_arrow326))
    class ObjectExpr327(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], no_numbering: Any=no_numbering, sheet: Any=sheet) -> Any:
            def mapping_2(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_1))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping_2, values_1)
            return helpers_1.encode_object(arg)

    return ObjectExpr327()


def _arrow329(builder: IGetters) -> FsWorksheet:
    row_index: int = 0
    n: str
    object_arg: IRequiredGetter = builder.Required
    n = object_arg.Field("name", string)
    ts: IEnumerable_1[FsTable] | None
    arg_3: Decoder_1[IEnumerable_1[FsTable]] = seq_1(decode)
    object_arg_1: IOptionalGetter = builder.Optional
    ts = object_arg_1.Field("tables", arg_3)
    def _arrow328(__unit: None=None) -> IEnumerable_1[tuple[int | None, IEnumerable_1[FsCell]]] | None:
        arg_5: Decoder_1[IEnumerable_1[tuple[int | None, IEnumerable_1[FsCell]]]] = seq_1(decode_1)
        object_arg_2: IOptionalGetter = builder.Optional
        return object_arg_2.Field("rows", arg_5)

    rs: IEnumerable_1[tuple[int | None, IEnumerable_1[FsCell]]] = default_arg(_arrow328(), empty())
    sheet: FsWorksheet = FsWorksheet(n)
    def action_1(tupled_arg: tuple[int | None, IEnumerable_1[FsCell]]) -> None:
        nonlocal row_index
        row_i: int | None = tupled_arg[0]
        col_index: int = 0
        row_i_1: int = ((row_index + 1) if (row_i is None) else row_i) or 0
        row_index = row_i_1 or 0
        r: FsRow = sheet.Row(row_i_1)
        def action(cell: FsCell, tupled_arg: Any=tupled_arg) -> None:
            nonlocal col_index
            col_i: int
            match_value: int = cell.ColumnNumber or 0
            col_i = (col_index + 1) if (match_value == 0) else match_value
            col_index = col_i or 0
            c: FsCell = r.Item(col_i)
            c.Value = cell.Value
            c.DataType = cell.DataType

        iterate(action, tupled_arg[1])

    iterate(action_1, rs)
    if ts is None:
        pass

    else: 
        def action_2(t: FsTable) -> None:
            ignore(sheet.AddTable(t))

        iterate(action_2, ts)

    return sheet


decode_rows: Decoder_1[FsWorksheet] = object(_arrow329)

def encode_columns(no_numbering: bool, sheet: FsWorksheet) -> IEncodable:
    sheet.RescanRows()
    def _arrow333(__unit: None=None, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEnumerable_1[IEncodable]:
        def _arrow332(c: int) -> IEncodable:
            def _arrow331(__unit: None=None) -> IEnumerable_1[FsCell]:
                def _arrow330(r: int) -> IEnumerable_1[FsCell]:
                    match_value: FsCell | None = FsCellsCollection__TryGetCell_Z37302880(sheet.CellCollection, r, c)
                    return singleton(FsCell("")) if (match_value is None) else singleton(match_value)

                return collect(_arrow330, range_big_int(1, 1, sheet.MaxRowIndex))

            return encode_no_numbers_1(to_list(delay(_arrow331)))

        return map(_arrow332, range_big_int(1, 1, sheet.MaxColumnIndex))

    def mapping(col_1: FsColumn, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEncodable:
        return encode_2(col_1)

    j_columns: IEncodable = seq(to_list(delay(_arrow333))) if no_numbering else seq(map(mapping, sheet.Columns))
    def _arrow338(__unit: None=None, no_numbering: Any=no_numbering, sheet: Any=sheet) -> IEnumerable_1[tuple[str, IEncodable]]:
        def _arrow335(__unit: None=None) -> IEncodable:
            value: str = sheet.Name
            class ObjectExpr334(IEncodable):
                def Encode(self, helpers: IEncoderHelpers_1[Any]) -> Any:
                    return helpers.encode_string(value)

            return ObjectExpr334()

        def _arrow337(__unit: None=None) -> IEnumerable_1[tuple[str, IEncodable]]:
            def _arrow336(__unit: None=None) -> IEnumerable_1[tuple[str, IEncodable]]:
                return singleton(("columns", j_columns))

            return append(singleton(("tables", seq(map(encode_1, sheet.Tables)))) if (not is_empty(sheet.Tables)) else empty(), delay(_arrow336))

        return append(singleton(("name", _arrow335())), delay(_arrow337))

    values_1: IEnumerable_1[tuple[str, IEncodable]] = to_list(delay(_arrow338))
    class ObjectExpr339(IEncodable):
        def Encode(self, helpers_1: IEncoderHelpers_1[Any], no_numbering: Any=no_numbering, sheet: Any=sheet) -> Any:
            def mapping_2(tupled_arg: tuple[str, IEncodable]) -> tuple[str, __A_]:
                return (tupled_arg[0], tupled_arg[1].Encode(helpers_1))

            arg: IEnumerable_1[tuple[str, __A_]] = map(mapping_2, values_1)
            return helpers_1.encode_object(arg)

    return ObjectExpr339()


def _arrow340(builder: IGetters) -> FsWorksheet:
    col_index: int = 0
    n: str
    object_arg: IRequiredGetter = builder.Required
    n = object_arg.Field("name", string)
    ts: IEnumerable_1[FsTable] | None
    arg_3: Decoder_1[IEnumerable_1[FsTable]] = seq_1(decode)
    object_arg_1: IOptionalGetter = builder.Optional
    ts = object_arg_1.Field("tables", arg_3)
    cs: IEnumerable_1[tuple[int | None, IEnumerable_1[FsCell]]]
    arg_5: Decoder_1[IEnumerable_1[tuple[int | None, IEnumerable_1[FsCell]]]] = seq_1(decode_2)
    object_arg_2: IRequiredGetter = builder.Required
    cs = object_arg_2.Field("columns", arg_5)
    sheet: FsWorksheet = FsWorksheet(n)
    def action_1(tupled_arg: tuple[int | None, IEnumerable_1[FsCell]]) -> None:
        nonlocal col_index
        col_i: int | None = tupled_arg[0]
        row_index: int = 0
        col_i_1: int = ((col_index + 1) if (col_i is None) else col_i) or 0
        col_index = col_i_1 or 0
        col: FsColumn = sheet.Column(col_i_1)
        def action(cell: FsCell, tupled_arg: Any=tupled_arg) -> None:
            nonlocal row_index
            row_i: int
            match_value: int = cell.RowNumber or 0
            row_i = (row_index + 1) if (match_value == 0) else match_value
            row_index = row_i or 0
            c: FsCell = col.Item(row_index)
            c.Value = cell.Value
            c.DataType = cell.DataType

        iterate(action, tupled_arg[1])

    iterate(action_1, cs)
    if ts is None:
        pass

    else: 
        def action_2(t: FsTable) -> None:
            ignore(sheet.AddTable(t))

        iterate(action_2, ts)

    return sheet


decode_columns: Decoder_1[FsWorksheet] = object(_arrow340)

__all__ = ["encode_rows", "decode_rows", "encode_columns", "decode_columns"]

