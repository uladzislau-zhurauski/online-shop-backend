def are_all_elements_in_list(list_to_check, check_list):
    return all(item in check_list for item in list_to_check)


def create_unhandled_value_error(value):
    return ValueError(f'Unhandled value: {value} ({type(value).__name__})')
