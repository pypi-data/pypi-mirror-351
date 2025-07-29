# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Callable, Mapping, Union

import isodate


# Some type conversion functions
def to_date(value: str) -> datetime.date:
    return isodate.parse_date(value)


def to_time(value: str) -> datetime.time:
    return isodate.parse_time(value)


def to_datetime(value: str) -> datetime.datetime:
    # We encountered situations where the T separator was replaces by a space
    # so make sure that is not the case
    value = value.replace(" ", "T")
    return isodate.parse_datetime(value)


def to_timedelta(value: str) -> datetime.timedelta:
    return isodate.parse_duration(value).tdelta


def to_bool(value: str) -> bool:
    return value in ["true", "1"]


def from_datetime(value: Union[str, datetime.datetime]) -> str:
    if isinstance(value, str):
        to_datetime(value)  # First make sure it is a datetime

    if isinstance(value, datetime.datetime):
        return value.isoformat()
    else:
        raise ValueError(
            "To create a proper string representation for a"
            " datetime, either a datetime.datetime or str has"
            " to be supplied!"
        )


def from_date(value: Union[str, datetime.date]) -> str:
    if isinstance(value, str):
        value = isodate.parse_date(value)

    if isinstance(value, datetime.date):
        return value.isoformat()
    else:
        raise ValueError(
            "To create a proper string representation for a date," " either a datetime.date or str has to be supplied!"
        )


def from_time(value: Union[datetime.time, str]) -> str:
    if isinstance(value, str):
        value = isodate.parse_time(value)

    if isinstance(value, datetime.time):
        return value.isoformat()
    else:
        raise ValueError(
            "To create a proper string representation for a time," " either a datetime.time or str has to be supplied!"
        )


def from_timedelta(value: Union[datetime.timedelta, str]) -> str:
    if isinstance(value, str):
        value = isodate.parse_duration(value)
    elif isinstance(value, datetime.timedelta):
        value = isodate.duration.Duration(days=value.days, seconds=value.seconds, microseconds=value.microseconds)

    if isinstance(value, isodate.duration.Duration):
        return isodate.duration_isoformat(value)
    else:
        raise ValueError(
            "To create a proper string representation for a duration,"
            " either a isodate.duration.Duration or str has to be supplied!"
        )


def from_bool(value: Union[str, bool]) -> str:
    if isinstance(value, str):
        if value in ["true", "false", "1", "0"]:
            return value
        else:
            raise ValueError("Value {} is not a valid string representation of a bool".format(value))
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        raise TypeError(
            "To create a proper string presentation for a bool," " either a bool or str has to be supplied!"
        )


def from_int(value: Union[str, float, int]) -> str:
    if not isinstance(value, int):
        value = int(value)
    return str(value)


def from_float(value: Union[str, float, int]) -> str:
    if not isinstance(value, float):
        value = float(value)
    return str(value)


# Here to be after all needed function definitions
TYPE_TO_MAP: Mapping[str, Callable[[str], Any]] = {
    "xs:anyURI": str,
    "xs:string": str,
    "xs:boolean": to_bool,
    "xs:integer": int,
    "xs:long": int,
    "xs:float": float,
    "xs:double": float,
    "xs:dateTime": to_datetime,
    "xs:time": to_time,
    "xs:date": to_date,
    "xs:duration": to_timedelta,
}

TYPE_FROM_MAP: Mapping[str, Callable[[Any], str]] = {
    "xs:anyURI": str,
    "xs:string": str,
    "xs:boolean": from_bool,
    "xs:integer": from_int,
    "xs:long": from_int,
    "xs:float": from_float,
    "xs:double": from_float,
    "xs:dateTime": from_datetime,
    "xs:time": from_time,
    "xs:date": from_date,
    "xs:duration": from_timedelta,
}

TYPE_TO_PYTHON = {
    "xs:anyURI": str,
    "xs:string": str,
    "xs:boolean": bool,
    "xs:integer": int,
    "xs:long": int,
    "xs:float": float,
    "xs:double": float,
    "xs:dateTime": datetime.datetime,
    "xs:time": datetime.time,
    "xs:date": datetime.date,
    "xs:duration": datetime.timedelta,
}


def convert_to(value: str, type_: str) -> Any:
    return TYPE_TO_MAP.get(type_, str)(value)


def convert_from(value: Any, type_: str) -> str:
    return TYPE_FROM_MAP[type_](value)
