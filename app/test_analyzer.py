from pathlib import Path
import re
import subprocess

from app.test_runner import PROJECT_ROOT, TEST_TIMEOUT


def analyze_test_failures() -> str:
    """
    Run pytest and analyze any test failures.

    Returns a readable diagnostic report.
    """

    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "-v",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
        )

    except subprocess.TimeoutExpired:
        return (
            "TEST FAILURE ANALYSIS\n"
            "=====================\n\n"
            "Status: TIMEOUT\n\n"
            f"Pytest exceeded the {TEST_TIMEOUT}-second timeout."
        )

    except OSError as exc:
        return (
            "TEST FAILURE ANALYSIS\n"
            "=====================\n\n"
            "Status: ERROR\n\n"
            f"Could not execute pytest: {exc}"
        )

    output = "\n".join(
        part
        for part in (
            result.stdout,
            result.stderr,
        )
        if part
    ).strip()

    if result.returncode == 0:
        return (
            "TEST FAILURE ANALYSIS\n"
            "=====================\n\n"
            "Status: PASSED\n\n"
            "All tests passed. No failures to analyze."
        )

    if result.returncode == 5:
        return (
            "TEST FAILURE ANALYSIS\n"
            "=====================\n\n"
            "Status: NO TESTS FOUND\n\n"
            "Pytest did not collect any tests."
        )

    failures = _extract_failures(output)

    report = [
        "TEST FAILURE ANALYSIS",
        "=====================",
        "",
        f"Status: FAILED",
        f"Exit code: {result.returncode}",
        "",
        f"Failures detected: {len(failures)}",
    ]

    if not failures:
        report.extend(
            [
                "",
                "Could not extract structured failure information.",
                "",
                "RAW PYTEST OUTPUT",
                "------------------",
                output,
            ]
        )

        return "\n".join(report)

    for index, failure in enumerate(failures, start=1):
        report.extend(
            [
                "",
                f"FAILURE #{index}",
                "------------",
                f"Test: {failure['test']}",
                f"File: {failure['file']}",
                f"Line: {failure['line']}",
                f"Exception: {failure['exception']}",
                "",
                "Traceback:",
                failure["traceback"],
                "",
                "Likely Cause:",
                _guess_cause(failure),
            ]
        )

    return "\n".join(report)


def _extract_failures(output: str) -> list[dict]:
    """
    Extract basic failure information from pytest output.
    """

    failures = []

    # Example:
    # tests/test_calculator.py::test_add_numbers FAILED
    test_pattern = re.compile(
        r"(?P<file>[\w./-]+\.py)::(?P<test>[^\s]+)\s+FAILED"
    )

    matches = list(test_pattern.finditer(output))

    for match in matches:
        test_name = match.group("test")
        file_path = match.group("file")

        line_number = _find_line_number(
            output,
            file_path,
        )

        exception = _find_exception(
            output,
            test_name,
        )

        traceback = _find_traceback(
            output,
            file_path,
            test_name,
        )

        failures.append(
            {
                "test": test_name,
                "file": file_path,
                "line": line_number,
                "exception": exception,
                "traceback": traceback,
            }
        )

    return failures


def _find_line_number(
    output: str,
    file_path: str,
) -> str:
    pattern = re.compile(
        rf"{re.escape(file_path)}:(\d+)"
    )

    match = pattern.search(output)

    if match:
        return match.group(1)

    return "Unknown"


def _find_exception(
    output: str,
    test_name: str,
) -> str:
    """
    Try to find the assertion/exception associated
    with a failing test.
    """

    pattern = re.compile(
        rf"{re.escape(test_name)}.*?"
        r"(?:E\s+)?"
        r"(?P<exception>[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure|Exit))"
        r"(?::\s*(?P<message>[^\n]+))?",
        re.DOTALL,
    )

    match = pattern.search(output)

    if match:
        exception = match.group("exception")
        message = match.group("message")

        if message:
            return f"{exception}: {message.strip()}"

        return exception

    # Fallback: inspect common pytest assertion output.
    assertion_pattern = re.compile(
        r"E\s+assert\s+(.+)"
    )

    match = assertion_pattern.search(output)

    if match:
        return f"AssertionError: assert {match.group(1).strip()}"

    return "Unknown"


def _find_traceback(
    output: str,
    file_path: str,
    test_name: str,
) -> str:
    """
    Extract a compact traceback section.
    """

    start_pattern = re.compile(
        rf"_{3,}\s+{re.escape(test_name)}\s+_{3,}"
    )

    start_match = start_pattern.search(output)

    if not start_match:
        return "Traceback unavailable."

    section = output[start_match.start():]

    # Stop at the next test failure section when possible.
    next_failure = re.search(
        r"\n_{3,}\s+.*?\s+_{3,}",
        section[len(start_match.group(0)):],
    )

    if next_failure:
        section = section[
            :len(start_match.group(0)) + next_failure.start()
        ]

    lines = section.strip().splitlines()

    # Keep the report manageable.
    return "\n".join(lines[-20:])


def _guess_cause(failure: dict) -> str:
    """
    Provide a basic deterministic diagnosis.

    This is intentionally rule-based for now.
    """

    exception = failure["exception"]

    if "AssertionError" in exception:
        return (
            "The actual value returned by the code does not "
            "match the value expected by the test."
        )

    if "TypeError" in exception:
        return (
            "The code likely received an argument with an "
            "unexpected type or an incorrect function signature."
        )

    if "KeyError" in exception:
        return (
            "The code attempted to access a dictionary key "
            "that does not exist."
        )

    if "AttributeError" in exception:
        return (
            "The code attempted to access an attribute or "
            "method that does not exist on the object."
        )

    if "ValueError" in exception:
        return (
            "The code received a value that is invalid for "
            "the operation being performed."
        )

    if "ImportError" in exception or "ModuleNotFoundError" in exception:
        return (
            "A required module or import could not be resolved."
        )

    return (
        "The test failed, but the current rule-based analyzer "
        "could not determine the specific cause."
    )