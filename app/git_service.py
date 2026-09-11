from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_git_command(*args:str) -> str:
    """Run a git command inside the project repository ."""
    try:
        result=subprocess.run(
            ["git",*args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
    except FileNotFoundError:
        return "Git executable was not found."
    except subprocess.TimeoutExpired:
        return "Git status Timed out"
    except OSError as exc:
        return f"Unable to execute git: {exc}"
    if result.returncode != 0:
        error=result.stderr.strip()
        if error:
            return f"Git error: {error}"

        return f"Git command failed with exit code {result.returncode}"

    return result.stdout.strip()

def get_git_status() -> str:
    """Returns the current Git repository status."""
    output=run_git_command(
        "status",
        "--short",
        "--branch"
    )
    if not output:
        return "Working tree is clean"
    return output

def get_git_diff() -> str:
    """Returns unstaged changes in the Git Repository."""
    output=run_git_command(
        "diff",
        "--"
    )
    if not output:
        return "No unstaged changes found"
    return output
