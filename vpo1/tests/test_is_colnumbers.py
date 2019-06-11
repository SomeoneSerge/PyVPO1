import pytest
from vpo1.vpo1_structure import is_colnumbers_row


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

