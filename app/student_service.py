from typing import Any

students:dict[str,dict[str,Any]] = {}



class StudentNotFoundException(Exception):
    pass

def create_student(
        student_id:str,
        name:str,
        email:str,
        role:str,
) -> dict[str,Any]:
    if student_id in students:
        raise ValueError("Student already exists")

    student={
        "id":student_id,
        "name":name,
        "email":email,
        "role":role
    }
    students[student_id]=student
    return student


def get_student(student_id:str) -> dict[str,Any]:
    student=students.get(student_id)

    if student is None:
        raise ValueError("Student not found")

    return student

def list_students() -> list[dict[str,Any]]:
    return list(students.values())


def delete_student(student_id:str) -> dict[str,Any]:
    student=students.pop(student_id,None)

    if student is None:
        raise ValueError("Student not found")

    return student