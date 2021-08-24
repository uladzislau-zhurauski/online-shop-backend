def is_all_elements_exist_in_list(list_to_check, check_list):
    return all(item in check_list for item in list_to_check)
