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


@pytest.fixture
def voronezh_parsed():
    sheet = [
            ['Воронежская область', None, None],
            ['Государственные, Муниципальные', None, None],
            ['очная', None, None],
            ['2.1.2. Распределение численности студентов по курсам, направлениям подготовки и специальностям', None, None],
            ['Program', '№ строки', 'Всего'],
            [1, 2, 5],
            ['Математика', 1, 27]
            ]
    sheet = list(map(VPO1Row, sheet))
    events =  list(SheetMachine().read_sheet(sheet))
    return events

def test_SheetMachine_region(voronezh_parsed):
    assert ('region', 'Воронежская область') in voronezh_parsed
def test_SheetMachine_funded_by(voronezh_parsed):
    assert ('funded_by', 'Государственные, Муниципальные') in voronezh_parsed
def test_SheetMachine_time_involvement(voronezh_parsed):
    assert ('time_involvement', 'очная') in voronezh_parsed
def test_SheetMachine_section(voronezh_parsed):
    assert next((
        True for event, section in voronezh_parsed
        if event=='section' and section.number=='2.1.2'))
def test_SheetMachine_df_row_exists(voronezh_parsed):
    assert next((
        True for event, payload in voronezh_parsed
        if event=='row' and payload.rowname == 'Математика'))
def test_SheetMachine_df_row_colindices(voronezh_parsed):
    mathrow = next((
        payload for event, payload in voronezh_parsed
        if event=='row' and payload.rowname == 'Математика'))
    assert mathrow.data == [(5, 27)]
