#!/usr/bin/env python
import json
import os
import sys
from typing import Callable
from itertools import islice
from logging import (
    getLogger,
    StreamHandler,
    Formatter,
    DEBUG,
    INFO,
    LogRecord
)
from pathlib import Path


class Encoder(json.JSONEncoder):
    def __init__(
        self,
        *args,
        max_depth: int | None = None,
        max_str_len: int | None = None,
        max_dict_items: int | None = None,
        max_list_items: int | None = None,
        placeholder: str = '...',
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.max_depth = max_depth
        self.max_str_len = max_str_len
        self.max_dict_items = max_dict_items
        self.max_list_items = max_list_items
        self.placeholder = placeholder

    def limit(self, obj, depth: int = 0):
        if isinstance(obj, str):
            if self.max_str_len is not None and len(obj) > self.max_str_len:
                cut = self.max_str_len - len(self.placeholder)
                return obj[:cut] + self.placeholder
            else:
                return obj
        if (
            isinstance(obj, int)
            or isinstance(obj, float)
            or isinstance(obj, bool)
            or obj is None
        ):
            return obj
        if isinstance(obj, dict):
            if depth == self.max_depth:
                return { self.placeholder: self.placeholder }
            too_many_items = (
                self.max_dict_items is not None
                and len(obj) > self.max_dict_items
            )
            if too_many_items:
                cut = self.max_dict_items - 1
                new = {
                    k: self.limit(v, depth + 1)
                    for k, v in islice(obj.items(), cut)
                }
                new[self.placeholder] = self.placeholder
                return new
            else:
                return {
                    k: self.limit(v, depth + 1)
                    for k, v in obj.items()
                }
        if isinstance(obj, list) or isinstance(obj, tuple):
            if depth == self.max_depth:
                return [self.placeholder]
            too_many_items = (
                self.max_list_items is not None
                and len(obj) > self.max_list_items
            )
            if too_many_items:
                cut = self.max_list_items - 1
                limited = (
                    self.limit(v, depth + 1)
                    for v in obj[:cut]
                )
                return [
                    *limited,
                    self.placeholder
                ]
            else:
                return [
                    self.limit(v, depth + 1)
                    for v in obj
                ]
        return self.limit(
            self.default(obj),
            depth
        )

    def encode(self, obj):
        return super().encode(
            self.limit(obj)
        )


class JSONFormatter(Formatter):

    def __init__(
        self,
        max_depth: int = 5,
        max_str_len: int = 512,
        max_dict_items: int = 64,
        max_list_items: int = 64,
        placeholder: str = '...',
        default: Callable = str
    ):
        super().__init__()
        self.placeholder = placeholder
        self.default = default
        self.encoder = Encoder(
            max_depth=max_depth,
            max_dict_items=max_dict_items,
            max_list_items=max_list_items,
            max_str_len=max_str_len,
            placeholder=placeholder,
            default=default
        )

    def _format(self, record: LogRecord, message: str):
        return self.encoder.encode(
            {
                'timestamp': record.created,
                'level': record.levelname,
                'message': message,
                'funcName': record.funcName,
                'lineno': record.lineno,
                'pathname': record.pathname,
                'module': record.module,
            }
        )

    def format(self, record: LogRecord):
        try:
            if isinstance(record.msg, str):
                message = record.getMessage()
            else:
                message = record.msg
            return self._format(record, message)
        except Exception:
            try:
                return self._format(
                    record,
                    super().format(record)
                )
            except Exception:
                return json.dumps('INVALID LOG MESSAGE')


def _pretty_print():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            data = json.loads(line)
            json.dump(
                data,
                sys.stderr,
                indent=2
            )
        except json.JSONDecodeError:
            print(line, end='')


def _create_logger():
    script_path = Path(sys.argv[0])
    name = (
        script_path.stem
        or 'app'
    )
    log = getLogger(name)
    env = os.environ
    level = (
        DEBUG if env.get('DEBUG')
        else INFO
    )
    log.setLevel(level)
    handler = StreamHandler(sys.stderr)
    handler.setFormatter(JSONFormatter())
    log.addHandler(handler)
    return log


if __name__ == '__main__':
    _pretty_print()
else:
    log = _create_logger()
