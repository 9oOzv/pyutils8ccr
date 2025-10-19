from ruamel.yaml import YAML
from functools import cache
import sys
from typing import IO
from pathlib import Path


@cache
def _yaml():
    yaml = YAML(typ='safe')
    yaml.default_flow_style = False
    yaml.default_style = ''

    def block_literal_str_representer(dumper, data):
        style = (
            '|' if
            '\n' in data
            or len(data) > 32
            else ''
        )
        return dumper.represent_scalar(
            'tag:yaml.org,2002:str',
            data,
            style=style
        )
    yaml.representer.add_representer(str, block_literal_str_representer)
    return yaml


def dump(data, output: IO = sys.stdout):
    print(_yaml().dump(data, output))


def dumps(data) -> str:
    from io import StringIO
    stream = StringIO()
    _yaml().dump(data, stream)
    return stream.getvalue()


def load(file: Path | str):
    with open(file, 'r') as f:
        return _yaml().load(f)


def loads(s: str):
    from io import StringIO
    stream = StringIO(s)
    return _yaml().load(stream)
