from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_git_status() -> str:
    """Returns the current Git repository status."""
    try:
        result=subprocess.run(
            ["git","status","--short","--branch"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
    except FileNotFoundError:
        return "Git executable was not found on this system."
    except subprocess.TimeoutExpired:
        return "Git status Timed out"
    except OSError as exc:
        return f"Unable to execute git: {exc}"
    if result.returncode != 0:
        error=result.stderr.strip()
        if error:
            return f"Git error: {error}"

        return f"Git command failed with exit code {result.returncode}"

    output=result.stdout.strip()
    if not output:
        return "Working tree is clean"
    return output

