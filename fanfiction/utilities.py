# merge two dictionaries and replace None and empty values if available
def merge_dict(d1, d2):
    result = {**d2, **d1}  # append keys and values from d2
    for k, v in result.items():
        if k in d2 and (v is None and d2[k] is not None) or (v == '' and d2[k] != ''):
            result[k] = d2[k]
    return result
