import itertools
import collections
import typing

import pandas as pd


class VPO1Error(Exception):
    pass

class VPO1Row:
    def __init__(self, cells):
        # consider, for `str`s:
        # cells = map(str.strip, cells)
        # cells = map(str.lower, cells)
        # plus multiple spaces, etc
        cells = list(cells)
        self.cells = cells
        self.atomic_to_full = [i if c is not None else None for i, c in enumerate(cells)]
        self.atomic_to_full[0] = 0
        self._n_cells = sum(map(lambda x: x is not None, self.atomic_to_full))
        for i, ref in enumerate(self.atomic_to_full):
            if ref is None:
                self.atomic_to_full[i] = self.atomic_to_full[i - 1]
        for ref in self.atomic_to_full:
            assert ref is not None
    @property
    def n_cells(self):
        # TODO: remove
        return self._n_cells
    @property
    def n_full_cells(self):
        return self._n_cells
    @property
    def n_atomic_cells(self):
        return len(self.cells)
    def clone(self):
        return VPO1Row(self.cells)
    def __getitem__(self, atomic_cell_id):
        cell_id = self.atomic_to_full[atomic_cell_id]
        return self.cells[cell_id]
    def __repr__(self):
        return repr(self.cells)
    def __len__(self):
        # TODO: return len(self.cells) for consistency with __getitem__
        return self.n_cells
    def __iter__(self):
        return (self[j] for j in range(self.n_cells))


class VPO1SheetHeader:
    DESC = ['region', 'funded_by', 'time_involvement', 'name', 'units']
    DESC = dict(((x, i) for i, x in enumerate(DESC)))
    def __init__(
            self,
            rows_traits: typing.List[VPO1Row],
            rows_tableheader: typing.List[VPO1Row],
            n_cols: int):
        
        if len(rows_traits) < len(VPO1SheetHeader.DESC):
            raise VPO1Error(
                'Expected at least {} rows in the header (for the traits) got {}'
                .format(len(rows, len(VPO1SheetHeader.DESC)))
            )
        if not isinstance(rows_traits[VPO1SheetHeader.DESC['units']][0], str):
            raise VPO1Error('Units of measurement misspecified')
        if not 'ОКЕИ' in rows_traits[VPO1SheetHeader.DESC['units']][0]:
            raise VPO1Error('Units of measurement misspecified')
        
        
        TRANSFORMS = collections.defaultdict(lambda: (lambda x: x))
        # TRANSFORMS['units'] = lambda x: x.replace(STARTSWITH_UNITS, '')
        for field, i in VPO1SheetHeader.DESC.items():
            transform = TRANSFORMS[field]
            setattr(self, field, transform(rows_traits[i][0]))
        
        def table_header_transform(x):
            if x is None:
                return ''
            return str(x)
        table_header = (
            (row[i] for row in rows_tableheader)
            for i in range(n_cols)
        )
        table_header = [' '.join(map(table_header_transform, col)) for col in table_header]
        self.table_header = table_header
        self.n_cols = n_cols
        
def vpo1_table(header: VPO1SheetHeader,
               rows: typing.List[VPO1Row]) -> pd.DataFrame:
    index = [row[0] for row in rows]
    cols = header.table_header[1: ]
    data = data=[[row[i] for i in range(1, header.n_cols)] for row in rows]
    df = pd.DataFrame(data=data,
                      index=index,
                      columns=cols)
    return df

def is_colnumbers_row(row):
    return (
            len(row) >= 2
            and row[0] == 1
            and row[1] == 2
            and all(
                isinstance(j, (int, float))
                and j == int(j)
                for j in row))

class VPO1Sheet:
    def __init__(self, rows: typing.List[VPO1Row]):
        cells_in_row = list(map(lambda r: r.n_cells, rows))
        n_cols = max(cells_in_row)
        try:
            end_sheet_traits = next(i for i, n_cells in enumerate(cells_in_row) if n_cells >= 2)
        except StopIteration:
            raise VPO1Error('Table header never begins')
        try:
            end_table_header = next(
                    i for i, row
                    in enumerate(rows[end_sheet_traits:], end_sheet_traits)
                    if is_colnumbers_row(row))
        except StopIteration:
            raise VPO1Error('Cannot find the row with column numbers that signifies end of table header')
        
        self.header = VPO1SheetHeader(rows[:end_sheet_traits], rows[end_sheet_traits:end_table_header], n_cols)
        self.table = vpo1_table(self.header, rows[end_table_header + 1: ])
        for field in VPO1SheetHeader.DESC:
            setattr(self, field, getattr(self.header, field))
    @staticmethod
    def try_yield_parsed(rows):
        try:
            yield VPO1Sheet(rows)
        except VPO1Error:
            pass

    
class VPO1:
    def __init__(self, sheets: typing.Dict[str, typing.List[VPO1Row]]):
        # sheets = map(lambda name, rows: zip([name], VPO1Sheet.try_yield_parsed(rows)), sheets.items())
        sheets = (list(zip([name], VPO1Sheet.try_yield_parsed(rows))) for name, rows in sheets.items())
        sheets = itertools.chain.from_iterable(sheets)
        sheets = list(sheets)
        self.names, self.sheets = [n for n, p in sheets], [p for n, p in sheets]
        if len(self.sheets) == 0:
            raise VPO1Error('No sheets could be parsed')
        page0 = self.sheets[0]
        self.region = page0.region
        self.time_involvement = page0.time_involvement
    @staticmethod
    def try_yield_parsed(sheets):
        try:
            yield VPO1(sheets)
        except VPO1Error:
            pass
