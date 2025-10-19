from typing import Iterable
from pathlib import Path
import json
from pydantic import BaseModel
from ruamel.yaml import YAML


class ConfigBase(BaseModel):

    @classmethod
    def from_file(cls, filepaths: Iterable[Path] | Path):
        filepaths = (
            filepaths
            if isinstance(filepaths, Iterable)
            else [filepaths]
        )
        data = {}
        for filepath in filepaths:
            if not filepath.exists():
                continue
            with open(filepath, "r") as f:
                if filepath.suffix in [".yaml", ".yml"]:
                    yaml = YAML(typ='safe')
                    data = {
                        **data,
                        **yaml.load(filepath)
                    }
                elif filepath.suffix == ".json":
                    data = {
                        **data,
                        **json.load(f)
                    }
                else:
                    raise ValueError(
                        f"Unsupported config file format: {filepath.suffix}"
                    )
        self = cls.model_validate(data)
        return self
