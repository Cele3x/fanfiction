from datetime import datetime
from dateutil import parser
from parser import ParserError
from typing import Union
import re


# merge two dictionaries and replace None and empty values if available
def merge_dict(dict_old: dict, dict_new: dict) -> dict:
    result = {**dict_old, **dict_new}  # append keys and values from dict_new
    for k, v in result.items():
        if k in dict_new and (v is None and dict_new[k] is not None) or (v == '' and dict_new[k] != ''):
            result[k] = dict_new[k]
    return result


# try to convert string to integer
def str_to_int(string_value: str) -> Union[int, str]:
    try:
        return int(string_value)
    except ValueError:
        print('String could not be converted to integer: ' + string_value)
        return string_value


# format datetime from string
def get_datetime(datetime_string: str) -> Union[datetime, str]:
    try:
        datetime_string = re.sub(r'[^\d.:]', ' ', datetime_string)  # replace everything except numbers, ':' and '.' characters with spaces
        datetime_string = re.sub(r'\s{2,}', ' ', datetime_string)  # replace multiple spaces with single space
        return parser.parse(datetime_string)
    except AttributeError:
        print('Passed item is not a String')
        return datetime_string
    except (ValueError, ParserError):
        print('Datetime string could not be parsed: ' + datetime_string)
        return datetime_string


# format date from string
def get_date(date_string: str) -> Union[datetime, str]:
    try:
        date_string = re.sub(r'[^\d.]', ' ', date_string)  # replace everything except numbers, ':' and '.' characters with spaces
        date_string = re.sub(r'\s{2,}', ' ', date_string)  # replace multiple spaces with single space
        return parser.parse(date_string)
    except (AttributeError, TypeError):
        print('Passed item is not a String')
        print(date_string)
        return date_string
    except (ValueError, ParserError):
        print('Datetime string could not be parsed: ' + date_string)
        return date_string
