# coding: utf-8

__author__ = 'Junki Ishida'

from ._compat import str_types, int_types, int_or_float_types, raise_with_inner, PY2
from .exceptions import FormatError
from decimal import Decimal
from datetime import datetime, date

try:
    import dateutil.parser
except ImportError:
    pass


def str_to_str(value):
    if isinstance(value, str_types):
        return value
    raise FormatError()


def str_to_unicode(value):
    if isinstance(value, str_types):
        if PY2 and isinstance(value, bytes):
            value = value.decode()
        return value
    raise FormatError()


def str_or_none_to_str(value):
    if value is None:
        return ''
    if isinstance(value, str_types):
        return value
    raise FormatError()


def str_or_none_to_unicode(value):
    if value is None:
        value = ''
    if isinstance(value, str_types):
        if PY2 and isinstance(value, bytes):
            value = value.decode()
        return value
    raise FormatError()


def str_to_int(value):
    if isinstance(value, str_types):
        return int(value)
    raise FormatError()


def str_to_float(value):
    if isinstance(value, str_types):
        return float(value)
    raise FormatError()


def str_to_decimal(value):
    if isinstance(value, str_types):
        return Decimal(value)
    raise FormatError()


def str_to_bool(value):
    if isinstance(value, str_types):
        value = value.lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
    raise FormatError()


def int_to_str(value):
    if isinstance(value, int_types):
        return str(value)
    raise FormatError()


def int_to_int(value):
    if isinstance(value, int_types):
        return value
    raise FormatError()


def float_to_float(value):
    if isinstance(value, float):
        return value
    raise FormatError()


def int_or_float_to_float(value):
    if isinstance(value, int_types):
        return float(value)
    if isinstance(value, float):
        return value
    raise FormatError()


def int_or_float_to_str(value):
    if isinstance(value, int_or_float_types):
        return str(value)
    raise FormatError()


def float_to_decimal(value):
    if isinstance(value, float):
        return Decimal(str(float))
    raise FormatError()


def int_or_float_to_decimal(value):
    if isinstance(value, int_types):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(float))
    raise FormatError()


def bool_to_str(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    raise FormatError()


def bool_to_bool(value):
    if isinstance(value, bool):
        return value
    raise FormatError()


def decimal_to_str(value):
    if isinstance(value, Decimal):
        return str(value)
    raise FormatError()


def str_to_datetime(value, format, timezone, flexible):
    if not isinstance(value, str_types):
        raise FormatError()
    try:
        if flexible:
            result = dateutil.parser.parse(value)
        else:
            result = datetime.strptime(value, format)
        if timezone:
            return result.astimezone(timezone)
    except ValueError as e:
        raise_with_inner(FormatError, e)
    return result


def datetime_to_str(value, format, timezone, flexible):
    if not isinstance(value, datetime):
        raise FormatError()
    if timezone:
        try:
            value = value.astimezone(timezone)
        except ValueError as e:
            raise_with_inner(FormatError, e)
    return value.strftime(format)


def str_to_date(value, format):
    if not isinstance(value, str_types):
        raise FormatError()
    try:
        dt = datetime.strptime(value, format)
    except ValueError as e:
        raise_with_inner(FormatError, e)
    return date(dt.year, dt.month, dt.day)


def date_to_str(value, format):
    if not isinstance(value, date):
        raise FormatError()
    return value.strftime(format)


def str_to_enum(value, values):
    if value not in values:
        raise FormatError()
    return value


def enum_to_str(value, values):
    if value not in values:
        raise FormatError()
    return value
