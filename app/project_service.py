from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_project_files() -> list[str]:
    """Return Python source files in the project"""

    files=[]

    for path in PROJECT_ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue

        relative_path=path.relative_to(PROJECT_ROOT)
        files.append(str(relative_path))

    return sorted(files)


def find_todos() -> list[str]:
    """Find TODO comments in python files."""

    results=[]

    for path in PROJECT_ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue

        try:
            lines=path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError,OSError):
            continue

        relative_path=path.relative_to(PROJECT_ROOT)

        for line_number,line in enumerate(lines,start=1):
            if "TODO" in line:
                results.append(
                    f"{relative_path}:{line_number}: {line.strip()}"
                )

    return results

def get_git_status() -> str:
    """Returns a git status..."""
    result= subprocess.run(
        ["git","status","--short","--branch"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        check=False
    )

    if result.returncode !=0:
        return f"Git Error: {result.stderr.strip()}"

    return result.stdout.strip()


def get_project_health() -> str:
    """Generate a project health report."""

    python_files=get_project_files()
    todos=find_todos()
    git_status=get_git_status()

    modified_files=[]
    untracked_files=[]

    for line in git_status.splitlines():
        if line.startswith("??"):
            untracked_files.append(line[3:].strip())
        elif line.startswith(" M") or line.startswith("M "):
            modified_files.append(line[3:].strip())

    report=[]
    report.append("PROJECT HEALTH REPORT")
    report.append("=" * 40)

    report.append("")
    report.append("Python")
    report.append(f" Python files: {len(python_files)}")

    report.append("")
    report.append("Git")
    report.append(
        f" Modified files: {len(modified_files)}"
    )
    report.append(
        f" Untracked files: {len(untracked_files)}"
    )

    if modified_files:
        report.append(" Modified: ")
        for file in modified_files:
            report.append(f"    -{file}")

    if untracked_files:
        report.append(" Untracked: ")
        for file in untracked_files:
            report.append(f"     -{file}")

    report.append("")
    report.append("TODO's")
    report.append(f" FOUND: {len(todos)}")

    if todos:
        for todo in todos:
            report.append(f"     -{todo}")

    report.append("")
    report.append("Project Files")

    for file in python_files:
        report.append(f"    -{file}")

    return "\n".join(report)