from app.server import add_numbers,substract_numbers,multiply_numbers

def test_add_numbers():
    assert add_numbers(10,5) == 15

def test_substract_numbers():
    assert substract_numbers(10,5) == 5

def test_multiply_numbers():
    assert multiply_numbers(10,5) == 50

def test_add_negative_numbers():
    assert add_numbers(-10,5) == -5

def test_multiply_by_zero():
    assert multiply_numbers(100,0) == 0