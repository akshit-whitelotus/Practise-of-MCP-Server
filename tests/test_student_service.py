from app.student_service import create_student,get_student,list_students,delete_student

def test_create_student():
    student_id = "test-create-001"
    student=create_student(
        student_id,
        "Test Student",
        "test-create@example.com",
        "Backend Devloper"
    )
    assert student["id"] == student_id
    assert student["name"] == "Test Student"
    assert student["email"] == "test-create@example.com"
    assert student["role"] == "Backend Devloper"

    delete_student(student_id)
def test_get_student():
    student_id = "test-get-001"
    create_student(
        student_id,
        "Get Test Student",
        "test-get@example.com",
        "Python Developer"
    )
    student=get_student(student_id)

    assert student["id"] == student_id
    assert student["name"] == "Get Test Student"
    assert student["email"] == "test-get@example.com"
    assert student["role"] == "Python Developer"

    delete_student(student_id)

def test_list_students():
    student_id="test-list-001"
    create_student(
        student_id,
        "List Test Student",
        "test-list@example.com",
        "Backend Developer"
    )
    students=list_students()

    assert isinstance(students,list)
    assert any(
        student["id"] == student_id
        for student in students 
    )
    delete_student(student_id)

def test_delete_student():
    student_id="test-delete-001"
    create_student(
        student_id,
        "Delete Test Student",
        "test-delete@example.com",
        "Backend Developer"
    )
    deleted_student=delete_student(student_id)

    assert deleted_student["id"] == student_id
    students=list_students()

    assert not any(
        student["id"] == student_id
        for student in students
    )