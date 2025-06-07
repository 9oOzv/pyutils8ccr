from pathlib import Path

def readfile(file: Path | str) -> str:
    """
    Read the content of a file.

    Args:
        file: The path to the file to read.
    """
    file = Path(file)
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()
