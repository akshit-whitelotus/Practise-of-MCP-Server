from mcp.server.mcpserver import MCPServer

from app.student_service import (
    create_student,
    get_student,
    list_students,
    delete_student,
)

from app.code_search import search_code
from app.git_service import get_git_status

mcp = MCPServer(
    name="Practice MCP Server",
    version="1.0.0",
)


# ============================================================
# Calculator Tools
# ============================================================

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def substract_numbers(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


# ============================================================
# Student Tools
# ============================================================

@mcp.tool()
def create_student_tool(
    student_id: str,
    name: str,
    email: str,
    role: str,
) -> dict:
    """Create a new student."""
    return create_student(
        student_id,
        name,
        email,
        role,
    )


@mcp.tool()
def get_student_tool(student_id: str) -> dict:
    """Get a student by ID."""
    return get_student(student_id)


@mcp.tool()
def list_students_tool() -> list[dict]:
    """Return all students."""
    return list_students()


@mcp.tool()
def delete_student_tool(student_id: str) -> dict:
    """Delete a student by id."""
    return delete_student(student_id)


# ============================================================
# Code Search Tool
# ============================================================

@mcp.tool()
def search_code_tool(query: str) -> str:
    """Search source code files for a text query."""
    return search_code(query)


# ============================================================
# Student Resource
# ============================================================

@mcp.resource(
    "students://list",
    name="resource_students",
    description="List all students",
    mime_type="text/plain",
)
def resource_students() -> str:
    """Return the current list of students."""

    students = list_students()

    if not students:
        return "No students found."

    return "\n".join(
        f"{student['id']} - "
        f"{student['name']} - "
        f"{student['email']} - "
        f"{student['role']}"
        for student in students
    )


# ============================================================
# Student Prompt
# ============================================================

@mcp.prompt()
def student_analysis(student_name: str) -> str:
    """Create a prompt for analyzing a student's information."""

    return f"""
Analyze the following student:

Student Name: {student_name}

Please provide:
1. A brief profile
2. Possible technical strengths
3. Areas of improvement
4. Recommended next steps
"""

# ============================================================
# Git status check
# ============================================================

@mcp.tool()
def get_git_status_tool() -> str:
    """Return the current git repository status"""
    return get_git_status()


if __name__ == "__main__":
    mcp.run()