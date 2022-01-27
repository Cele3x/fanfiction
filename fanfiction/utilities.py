from datetime import datetime
from dateutil import parser
from parser import ParserError
from typing import Union
import re


# merge two dictionaries and replace None and empty values if available
def merge_dict(d1, d2):
    result = {**d2, **d1}  # append keys and values from d2
    for k, v in result.items():
        if k in d2 and (v is None and d2[k] is not None) or (v == '' and d2[k] != ''):
            result[k] = d2[k]
    return result


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
    except AttributeError:
        print('Passed item is not a String')
        return date_string
    except (ValueError, ParserError):
        print('Datetime string could not be parsed: ' + date_string)
        return date_string
