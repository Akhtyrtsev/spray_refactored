def to_boolean(value):
    if value == 'true':
        return True
    elif value == 'false':
        return False
    elif value == 'null':
        return None
    else:
        return value