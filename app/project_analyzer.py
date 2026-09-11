
from pathlib import Path
import ast

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def analyze_project_file(file_path: str) -> str:
    """Analyze a Python project file for structure and MCP components."""

    try:
        requested_path = Path(file_path)

        # --------------------------------------------------------
        # Security: reject absolute paths
        # --------------------------------------------------------
        if requested_path.is_absolute():
            return "Error: absolute paths are not allowed."

        # --------------------------------------------------------
        # Resolve the requested file
        # --------------------------------------------------------
        project_root = PROJECT_ROOT.resolve()
        project_file = (project_root / requested_path).resolve()

        # --------------------------------------------------------
        # Security: prevent ../ path traversal
        # --------------------------------------------------------
        try:
            project_file.relative_to(project_root)
        except ValueError:
            return "Error: path is outside the project directory."

        # --------------------------------------------------------
        # Validate file
        # --------------------------------------------------------
        if not project_file.exists():
            return f"Error: file not found: {file_path}"

        if not project_file.is_file():
            return f"Error: path is not a file: {file_path}"

        if project_file.suffix != ".py":
            return "Error: only Python files are supported."

        # --------------------------------------------------------
        # Read source
        # --------------------------------------------------------
        try:
            source = project_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "Error: file is not valid UTF-8 text."
        except OSError as exc:
            return f"Error reading file: {exc}"

        # --------------------------------------------------------
        # Parse Python source
        # --------------------------------------------------------
        try:
            tree = ast.parse(
                source,
                filename=str(project_file),
            )
        except SyntaxError as exc:
            return (
                "Python syntax error:\n"
                f"Line: {exc.lineno}\n"
                f"Column: {exc.offset}\n"
                f"Message: {exc.msg}"
            )

        # --------------------------------------------------------
        # Collect information
        # --------------------------------------------------------
        imports: list[str] = []
        functions: list[str] = []
        classes: list[str] = []

        mcp_tools: list[str] = []
        mcp_resources: list[str] = []
        mcp_prompts: list[str] = []

        todos: list[str] = []

        # --------------------------------------------------------
        # AST analysis
        # --------------------------------------------------------
        for node in ast.walk(tree):

            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""

                for alias in node.names:
                    if module:
                        imports.append(
                            f"{module}.{alias.name}"
                        )
                    else:
                        imports.append(alias.name)

            # Functions
            elif isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                functions.append(node.name)

                for decorator in node.decorator_list:
                    decorator_name = _get_decorator_name(decorator)

                    if decorator_name == "mcp.tool":
                        mcp_tools.append(node.name)

                    elif decorator_name == "mcp.resource":
                        mcp_resources.append(node.name)

                    elif decorator_name == "mcp.prompt":
                        mcp_prompts.append(node.name)

            # Classes
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        # --------------------------------------------------------
        # TODO / FIXME detection
        # --------------------------------------------------------
        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):
            stripped = line.strip()

            if "TODO" in stripped or "FIXME" in stripped:
                todos.append(
                    f"line {line_number}: {stripped}"
                )

        # --------------------------------------------------------
        # Build report
        # --------------------------------------------------------
        relative_path = project_file.relative_to(project_root)

        report: list[str] = [
            "PROJECT FILE ANALYSIS",
            "=====================",
            "",
            f"File: {relative_path}",
            f"Lines: {len(source.splitlines())}",
            "",
            "Imports:",
        ]

        if imports:
            for item in sorted(set(imports)):
                report.append(f"- {item}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "Functions:",
            ]
        )

        if functions:
            for name in functions:
                report.append(f"- {name}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "Classes:",
            ]
        )

        if classes:
            for name in classes:
                report.append(f"- {name}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "MCP Tools:",
            ]
        )

        if mcp_tools:
            for name in mcp_tools:
                report.append(f"- {name}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "MCP Resources:",
            ]
        )

        if mcp_resources:
            for name in mcp_resources:
                report.append(f"- {name}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "MCP Prompts:",
            ]
        )

        if mcp_prompts:
            for name in mcp_prompts:
                report.append(f"- {name}")
        else:
            report.append("- None")

        report.extend(
            [
                "",
                "TODO / FIXME:",
            ]
        )

        if todos:
            for item in todos:
                report.append(f"- {item}")
        else:
            report.append("- None")

        return "\n".join(report)

    except Exception as exc:
        # Do not let an internal analyzer exception become
        # the generic "Error executing tool" message.
        return (
            "Project analyzer failed.\n"
            f"Error type: {type(exc).__name__}\n"
            f"Error: {exc}"
        )


def _get_decorator_name(node: ast.AST) -> str:
    """Return a dotted decorator name such as mcp.tool."""

    # @tool
    if isinstance(node, ast.Name):
        return node.id

    # @mcp.tool
    if isinstance(node, ast.Attribute):
        parts: list[str] = []

        current: ast.AST = node

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))

    # @mcp.tool()
    # @mcp.resource(...)
    # @mcp.prompt()
    if isinstance(node, ast.Call):
        return _get_decorator_name(node.func)

    return ""

