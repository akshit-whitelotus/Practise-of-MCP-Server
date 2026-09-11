from pathlib import Path

PROJECT_ROOT=Path(__file__).resolve().parent.parent

ALLOWED_EXTENSIONS={
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css"
}

IGNORED_DIRECTORIES={
    ".venv",
    ".git",
    "__pycache__"
}

def search_code(query:str) -> str:
    if not query.strip():
        return "Query cannot be empty"
    query=query.lower()

    matches:list[str] =[]

    for file_path in PROJECT_ROOT.rglob("*"):
        if any(
            ignored in file_path.parts

            for ignored in IGNORED_DIRECTORIES
        ):
            continue
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:
            content=file_path.read_text(
                encoding="utf-8"
            )
        except (UnicodeDecodeError,OSError):
            continue

        for linenumber,line in enumerate(
            content.splitlines(),
            start=1
        ):
            if query in line.lower():
                relative_path=file_path.relative_to(PROJECT_ROOT)
                matches.append(
                    f"{relative_path}:{linenumber}: {line.strip()}"
                )
    if not matches:
        return f"No matches for {query}"

    return "\n".join(matches)