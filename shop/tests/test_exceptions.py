from shop.exceptions import UnhandledValueError


def test_create_unhandled_value_error():
    value = 'some_data'
    try:
        raise UnhandledValueError(value)
    except UnhandledValueError as e:
        assert e.message == f'Unhandled value: {value} ({type(value).__name__})'
