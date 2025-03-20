from pathlib import Path
import os
import shlex
import json
from ruamel.yaml import YAML
from tempfile import TemporaryDirectory


yaml = YAML(typ=['safe', 'rt', 'string'])


def get_editor() -> Path:
    """
    Get the user preferred editor

    Returns:
        Path to the editor binary

    Raises:
        Exception: If no editor is found
    """
    if 'VISUAL' in os.environ:
        return Path(os.environ['VISUAL'])
    elif 'EDITOR' in os.environ:
        return Path(os.environ['EDITOR'])
    if os.system('which editor') == 0:
        return Path('editor')
    if os.system('which vim') == 0:
        return Path('vim')
    if os.system('which vi') == 0:
        return Path('vi')
    if os.system('which nano') == 0:
        return Path('nano')
    else:
        raise Exception('No editor found')


def edit(
    text: str,
    filename: str = 'text.txt'
) -> str:
    """
    Edit a string in the user preferred editor

    Args:
        string: The string to edit

    Returns:
        The edited string

    Raises:
        Exception: If the editor fails
    """
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        path.write_text(text)
        editor = get_editor()
        command = shlex.join([str(editor), str(path)])
        ret = os.system(command)
        if ret != 0:
            raise Exception('Editor failed')
        return path.read_text()

def edit_as_yaml(
    data: dict,
    filename: str = 'data.yaml'
) -> dict:
    """
    Edit a dictionary as yaml in the user preferred editor

    Args:
        data: The dictionary to edit

    Returns:
        The edited dictionary

    Raises:
        Exception: If the editor fails
    """
    text = yaml.dumps(data)
    text = edit(text, filename)
    return yaml.load(text)

def edit_as_json(
    data: dict,
    filename: str = 'data.json'
) -> dict:
    """
    Edit a dictionary as json in the user preferred editor

    Args:
        data: The dictionary to edit

    Returns:
        The edited dictionary

    Raises:
        Exception: If the editor fails
    """
    text = json.dumps(data, indent=2)
    text = edit(text, filename)
    return json.loads(text)
