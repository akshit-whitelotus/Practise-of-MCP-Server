from pathlib import Path
import subprocess

PROJECT_ROOT=Path(__file__).resolve().parent.parent
TEST_TIMEOUT=120

def run_tests() -> str:
    """
    Run the project's pytest test suite and return a readable test report.
    
    Only pytest is executed; arbitary shell commands are not accepted.
    
    """

    try:
        result=subprocess.run(
            ["python","-m","pytest"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT
        )
    except FileNotFoundError:
        return (
            "TEST REPORT\n"
            "============\n\n"
            "Status: ERROR\n\n"
            "Python executable was not found."
        )

    except subprocess.TimeoutExpired as exc:
        output=""

        if exc.stdout:
            output += str(exc.stdout)
        if exc.stderr:
            output += str(exc.stderr)

        return(
            "TEST REPORT\n"
            "===========\n\n"
            "Status: TIMEOUT\n\n"
            f"Pytest exceeded the {TEST_TIMEOUT}- second timeout.\n\n"
            "OUTPUT\n"
            "-------\n"
            f"{output.strip()}"
        )
    except OSError as exc:
        return(
            "TEST REPORT\n"
            "===========\n\n"
            "Status: ERROR\n\n"
            f"Could not execute pytest: {exc}"
        )

    stdout=result.stdout.strip()
    stderr=result.stderr.strip()

    status_map={
        0: "PASSED",
        1: "FAILED",
        2: "INTERRUPTED",
        3: "PYTEST ERROR",
        4: "USAGE ERROR",
        5: "NO TESTS FOUND"
    }
    status=status_map.get(
        result.returncode,
        "UNKNOWN ERROR"
    )
    report_parts=[
        "TEST_REPORT",
        "===========",
        "",
        f"Status: {status}",
        f"Exit code: {result.returncode}"
    ]

    if stdout:
        report_parts.extend(
            [
                "",
                "PYTEST OUTPUT",
                "-------------",
                stdout
            ]
        )
    if stderr:
        report_parts.extend(
            [
                "",
                "PYTEST ERRORS",
                "-------------",
                stderr
            ]
        )

    if not stderr and not stdout :
        report_parts.extend(
            [
                "",
                "No pytest output was produced"
            ]
        )
    
    return "\n".join(report_parts)