import pytest

from shop.tools import is_all_elements_exist_in_list


@pytest.mark.parametrize('list_1, list_2, expected', [
    pytest.param([1, 2, 5, 6], [1, 2, 5, 6], True, id='All correct all'),
    pytest.param([1, 2], [1, 2, 5, 6], True, id='All correct not all'),
    pytest.param([1, 2, 457], [1, 2, 5, 6], False, id='Not all correct'),
    pytest.param([234, 4567], [1, 2, 5, 6], False, id='All incorrect'),
    pytest.param([234, 4567], [], False, id='Empty check list'),
    pytest.param([], [32, 3], True, id='Empty to check list'),
    pytest.param([], [], True, id='Two empty lists'),
])
def test_existence_of_one_list_in_another(list_1: list, list_2: list, expected):
    assert is_all_elements_exist_in_list(list_1, list_2) == expected
