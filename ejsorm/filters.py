import typing
import re

from ._types import EJObject


def greater_than(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return obj[check_key] > filter_value


def less_than(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return obj[check_key] < filter_value


def greater_than_equal(
    obj: EJObject, check_key: str, filter_value: typing.Any
) -> bool:
    return obj[check_key] >= filter_value


def less_than_equal(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return obj[check_key] <= filter_value


def in_(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return obj[check_key] in filter_value


def contains(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return filter_value in obj[check_key]


def icontains(obj: EJObject, check_key: str, filter_value: typing.Any) -> bool:
    return filter_value not in obj[check_key]


def iexact(obj: EJObject, check_key: str, filter_value: str) -> bool:
    return filter_value.lower() == obj[check_key].lower()


def regex(obj: EJObject, check_key: str, filter_value: str, flags: int = 0) -> bool:
    pattern = re.compile(filter_value, flags)
    return pattern.match(obj[check_key]) is not None


def iregex(obj: EJObject, check_key: str, filter_value: str, flags: int = 0) -> bool:
    pattern = re.compile(filter_value, flags)
    return pattern.match(obj[check_key]) is None


# todo: range

EJ_FILTERS: typing.Dict[
    str, typing.Callable[[EJObject, str, typing.Any], bool]
] = {
    "gt": greater_than,
    "lt": less_than,
    "gte": greater_than_equal,
    "lte": less_than_equal,
    "in": in_,
    "contains": contains,
    "icontains": icontains,
    "iexact": iexact,
    "regex": regex,
    "iregex": iregex,
}
