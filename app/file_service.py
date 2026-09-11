from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent

class FileReadError(Exception):
    pass

def read_project_file(file_path:str) -> str:
    """Read a text file from project safely."""
    path=(PROJECT_PATH/file_path).resolve()

    try:
        path.relative_to(PROJECT_PATH)
    except ValueError:
        raise FileReadError("Access denied: file is outside the project")

    if not path.exists():
        raise FileReadError(f"File not found: {file_path}")
    if not path.is_file():
        raise FileReadError(f"Not a file: {file_path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise FileReadError(f"File is a not a UTF-8 text file : {file_path}")