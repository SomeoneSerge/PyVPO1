import pytest
from vpo1.vpo1_structure import is_colnumbers_row, VPO1Row
from vpo1.vpo1_sm import SheetMachine


def test_is_colnumbers_row():
    # colnumbers row always begins with (1, 2) which correspond to varname column and rownumber column
    assert is_colnumbers_row([1, 2])
    assert not is_colnumbers_row([])
    assert not is_colnumbers_row([1])

    # colnumbers row consists of integer numbers
    assert is_colnumbers_row([1., 2., 3., 4.])
    assert is_colnumbers_row([1, 2, 30, 31])
    assert not is_colnumbers_row([1, 2, 3.14])
    assert not is_colnumbers_row([1, 2, 'name', 'price', 'whatever'])

def test_SheetMachine_valid_sheet():
    example_sheet = [
            ['Воронежская область', None, None],
            ['Государственные, Муниципальные', None, None],
            ['очная', None, None],
            ['2.1.2. Распределение численности студентов по курсам, направлениям подготовки и специальностям', None, None],
            ['Program', '№ строки', 'Всего'],
            [1, 2, 5],
            ['Математика', 1, 27]
            ]
    example_sheet = list(map(VPO1Row, example_sheet))
    events = list(SheetMachine().read_sheet(example_sheet))
    assert ('region', 'Воронежская область') in events
    assert ('funded_by', 'Государственные, Муниципальные') in events
    assert ('time_involvement', 'очная') in events
    assert next((True for event, payload in events if event=='section' and payload[0]=='2.1.2'))
    assert next((True for event, payload in events if event=='row' and payload['rowname'] == 'Математика'))
