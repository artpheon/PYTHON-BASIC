"""
Write tests for classes in 2_python_part_2/task_classes.py (Homework, Teacher, Student).
Check if all methods working correctly.
Also check corner-cases, for example if homework number of days is negative.
"""

import sys
import os
import pytest
from datetime import datetime

FOLDER = '2_python_part_2'
NAME1 = 'Dmitry'
NAME2 = 'Vlad'
LNAME1 = 'Orlyakov'
LNAME2 = 'Popov'
DESC1 = 'Learn functions'
DESC2 = 'Create 2 simple classes'
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), FOLDER))


@pytest.fixture()
def test_task():
    from task_classes import Homework, Student, Teacher
    return {'homework': Homework, 'student': Student, 'teacher': Teacher}


class TestClasses:
    def test_class_teacher(self, test_task):
        Teacher = test_task['teacher']

        teacher = Teacher(NAME1, LNAME1)
        assert teacher.first_name == NAME1
        assert teacher.last_name == LNAME1
        hwork = teacher.create_homework(DESC1, 10)
        assert hwork.text == DESC1

    def test_class_student(self, test_task):
        Student = test_task['student']
        Homework = test_task['homework']

        student = Student(NAME2, LNAME2)
        assert student.first_name == NAME2
        assert student.last_name == LNAME2

        hwork = Homework(DESC1, 5)
        assert student.do_homework(hwork) == hwork
        hwork = Homework(DESC1, 0)
        assert student.do_homework(hwork) is None

    def test_class_homework(self, test_task):
        Homework = test_task['homework']
        hwork = Homework(DESC2, 0)
        assert hwork.created.date() == datetime.now().date()
        assert hwork.deadline.total_seconds() == 0.0
        assert hwork.text == DESC2

        hwork = Homework(DESC1, 5)
        assert hwork.created.date() == datetime.now().date()
        assert hwork.deadline.total_seconds() == 432000.0
        assert hwork.text == DESC1

        with pytest.raises(ValueError):
            invalid_homework = Homework(DESC1, -1)
            assert invalid_homework is None
