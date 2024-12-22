#!/usr/bin/env python
from tomlkit.toml_file import TOMLFile
from tomlkit import TOMLDocument
import re

toml_file = "pyproject.toml"


class SemVer:
    def __init__(self, version: str):
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            raise ValueError(f"Invalid version format: `{version}`")
        self.major, self.minor, self.patch = version.split(".")

    def next_minor(self):
        return f"{self.major}.{int(self.minor) + 1}.0"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def increment_toml_version() -> None:
    print(f"Incrementing package minor version in {toml_file}")
    f = TOMLFile(toml_file)
    doc = f.read()
    current = SemVer(
        doc["project"]["version"]
    )
    print(
        f'Current version: {current}'
    )
    new = current.next_minor()
    print(
        f'New version: {new}'
    )
    doc["project"]["version"] = str(new)
    f.write(doc)
    print(
        f'{toml_file} updated'
    )


def git_amend() -> None:
    print("Amending git commit")
    import subprocess
    subprocess.run(
        ["git", "add", toml_file]
    )
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit"]
    )
    print("Git commit amended")


if __name__ == "__main__":
    increment_toml_version()
    git_amend()
