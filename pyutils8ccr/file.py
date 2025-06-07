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

def writefile(file: Path | str, content: str) -> None:
    """
    Write content to a file.

    Args:
        file: The path to the file to write.
        content: The content to write to the file.
    """
    file = Path(file)
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
