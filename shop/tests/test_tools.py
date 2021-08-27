import pytest

from shop.tools import are_all_elements_in_list, create_unhandled_value_error


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
    assert are_all_elements_in_list(list_1, list_2) == expected


def test_create_unhandled_value_error():
    value = 'some_data'
    actual_error = create_unhandled_value_error(value)
    expected_error = ValueError(f'Unhandled value: {value} ({type(value).__name__})')
    assert type(actual_error) is type(expected_error) and actual_error.args == expected_error.args
