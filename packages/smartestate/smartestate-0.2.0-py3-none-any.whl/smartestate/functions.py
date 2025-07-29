def tuple_list_has_key(tuple_list, key):
    for tupl in tuple_list:
        if key in tupl:
            return True
    return False
