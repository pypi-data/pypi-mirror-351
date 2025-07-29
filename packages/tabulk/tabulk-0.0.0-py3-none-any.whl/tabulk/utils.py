from __future__ import annotations

import json
import logging
import os
import sys
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from decimal import Decimal
from enum import Enum, Flag
from pathlib import Path
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo


def get_logger(obj: str|type|object):
    if isinstance(obj, str):
        name = obj
    else:
        if not isinstance(obj, type):
            obj = type(obj)
        name = obj.__module__ + '.' + obj.__qualname__

    try:
        from celery.utils.log import get_task_logger  # type: ignore (optional dependency)
        return get_task_logger(name)
    except ModuleNotFoundError:
        pass

    return logging.getLogger(name)


def parse_timezone(name: Literal['localtime','UTC']|str) -> tzinfo:
    if name == 'localtime':
        if sys.platform == 'win32':
            try:
                import tzlocal  # type: ignore (optional dependency)
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module 'tzlocal' is required on Windows to retrieve local timezone") from None
            return tzlocal.get_localzone()
        else:
            return ZoneInfo('localtime')
    elif name == 'UTC':
        return timezone.utc
    elif isinstance(name, str):
        if sys.platform == 'win32':
            try:
                import tzdata
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"Module 'tzdata' is required on Windows to parse timezone from string")
        return ZoneInfo(name)
    else:
        raise TypeError(f"name: {type(name).__name__}")


class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    
    Usage example: json.dumps(data, indent=4, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if o.tzinfo is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:12]
            return f'T{r}'
        elif isinstance(o, timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        else:
            try:
                from django.utils.functional import Promise  # type: ignore (optional dependency)
                if isinstance(o, Promise):
                    return str(o)
            except ModuleNotFoundError:
                pass

            if isinstance(o, (Enum,Flag)):
                return o.value
            elif isinstance(o, bytes):
                return str(o)
            else:
                return super().default(o)


def duration_iso_string(duration: timedelta):
    """
    Adapted from: django.utils.duration.duration_iso_string
    """
    if duration < timedelta(0):
        sign = "-"
        duration *= -1
    else:
        sign = ""

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = ".{:06d}".format(microseconds) if microseconds else ""
    return "{}P{}DT{:02d}H{:02d}M{:02d}{}S".format(
        sign, days, hours, minutes, seconds, ms
    )


def _get_duration_components(duration: timedelta):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds


class DelayedStr:
    @property
    def value(self) -> str|None:
        ...


def get_delayedstr_value(obj: str|DelayedStr|None) -> str|None:
    if isinstance(obj, str|None):
        return obj
    else:
        return obj.value


class Secret(DelayedStr):
    def __init__(self, name: str, default: type[SecretNotFound]|str|None = None):
        self.name = name
        self.default = default
        self._evaluated = False
        self._value = None
    
    @property
    def value(self) -> str|None:
        if not self._evaluated:
            self._value = get_secret_value(self.name, self.default)
            self._evaluated = True
        return self._value


class SecretNotFound(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Secret '{name}' not found")


def get_secret_value(name: str, default: type[SecretNotFound]|str|None = None) -> str|None:
    # Search in standard files
    name = name.lower()
    if (path := Path(f'/run/secrets/{name}')).exists(): # usefull in Docker containers
        return path.read_text(encoding='utf-8')
    elif (path := Path.cwd().joinpath(f'secrets/{name}')).exists(): # usefull during local development
        return path.read_text(encoding='utf-8')
    
    # Search in environment variables
    name = name.upper()
    if value := os.environ.get(name):
        return value
    elif file := os.environ.get(f'{name}_FILE'):
        if file.startswith('pass:'):
            raise NotImplementedError() #TODO
        else:
            return Path(file).read_text(encoding='utf-8')
    
    # Return default
    if isinstance(default, type):
        raise SecretNotFound(name)
    return default


def is_secret_defined(name: str):
    # Search in standard files
    name = name.lower()
    if Path(f'/run/secrets/{name}').exists(): # usefull in Docker containers
        return True
    elif Path.cwd().joinpath(f'secrets/{name}').exists(): # usefull during local development
        return True
    
    # Search in environment variables
    name = name.upper()
    if os.environ.get(name):
        return True
    elif os.environ.get(f'{name}_FILE'):
        return True
    
    # Return default
    return False
