import tempfile
import itertools
import glob
import os
import re

import xlrd

from vpo1.vpo1_structure import (VPO1Row, VPO1SheetHeader, VPO1Sheet, VPO1)

try:
    import requests
    import pyunpack
except:
    pass

def unpack_cell(cell):
    # TODO: apply normalization, stripping str's, etc -- right here
    return cell.value if cell.ctype != 0 else None

def unpack_row(row):
    return map(unpack_cell, row)

def read_vpo1(filename):
    xls = xlrd.open_workbook(filename)
    vpo1 = dict((s.name, list(map(VPO1Row,
                                  map(unpack_row, s.get_rows()))))
                for s in xls.sheets())
    vpo1 = VPO1(vpo1)
    return vpo1


class VPO1Set:
    # TODO: clean up
    def _init_deep_inspect(self, path):
        self.files = (
            glob.glob(os.path.join(path, 'СВОД_ВПО1*.xls'))
            + glob.glob(os.path.join(path, 'Своды ВПО-1*/*/*.xls')))
        self.file_to_i = dict((f, i) for i, f in enumerate(self.files))
        self.file_to_traits = list()
        for f in self.files:
            # TODO: use iterables, not lists; read only header; don't create pd.DataFrame yet;
            # NB: splitting names would've been faster but I'm rather hesitant to bind to them
            #     as they might be unstable;
            vpo1 = read_vpo1(f).pages[0].header
            # TODO: namedtuple
            self.file_to_traits.append(dict((field, getattr(vpo1, field)) for field in VPO1SheetHeader.DESC))
    def _init_name_inspect(self, path):
        for root, dirs, files in os.walk(path):
            files = ((split(f) for split in [self.split_name_country, self.split_name_region])
                     for f in files)
            files = (itertools.islice((splitted for splitted in f if splitted is not None), 0, 1)
                     for f in files)
            files = itertools.chain.from_iterable(files)
            files = list(files)
            for filename, traits in files:
                self.files.append(os.path.join(root, filename))
                self.file_to_traits.append(traits)
    @staticmethod
    def split_name_country(s):
        PAT_COUNTRY = re.compile(r'СВОД_ВПО1_(?P<funded_by>[А-Я]+)_(?P<time_involvement>[А-Яа-я\s-]+)\.xls')
        m = PAT_COUNTRY.match(s)
        if not m:
            return None
        return (s, dict(region='Russia',
                    funded_by=m.group('funded_by'),
                    time_involvement=m.group('time_involvement')))
    @staticmethod
    def split_name_region(s):
        PAT_REGION = re.compile(r'(?P<region>[а-яА-Я\s-]+)_(?P<funded_by>[А-Я]+)_(?P<time_involvement>[а-яА-Я\s-]+)\.xls')
        m = PAT_REGION.match(s)
        if not m:
            return None
        return (s, dict(m.groupdict()))
    def __init__(self, path, deep=False):
        self.files = []
        self.file_to_traits = []
        if deep:
            self._init_deep_inspect(path)
        else:
            self._init_name_inspect(path)
        VPO1SET_TRAITS = ['region', 'funded_by', 'time_involvement']
        for field in VPO1SET_TRAITS:
            setattr(self, field + 's', list(set(map(lambda x: x[field], self.file_to_traits))))
                    
                
    def get_vpo1(self, region, funded_by, time_involvement):
        # TODO: something faster than linear search
        return read_vpo1(next(x for x, traits in zip(self.files, self.file_to_traits)
            if region == traits['region']
            and funded_by == traits['funded_by']
            and time_involvement == traits['time_involvement']))

    

# def download(year, output_path):
#     URL_TEMPLATE = 'https://minobrnauki.gov.ru/common/upload/download/VPO_1_{year}.rar'
#     url = URL_TEMPLATE.format(year=year)
