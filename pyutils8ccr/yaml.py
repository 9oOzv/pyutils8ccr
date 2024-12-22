from ruamel.yaml import YAML
from functools import cache
import sys


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


def dump(data):
    print(_yaml().dump(data, sys.stdout))
