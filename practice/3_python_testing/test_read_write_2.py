"""
Write tests for 2_python_part_2/task_read_write_2.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""

import os
import sys

FOLDER = '2_python_part_2'
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), FOLDER))


def test_read_write_2(tmpdir):
    from task_read_write_2 import read_write_2 as func
    p = tmpdir.mkdir(FOLDER)
    file1 = p.join('file1.txt')
    file2 = p.join('file2.txt')
    func(file1=file1, file2=file2)
    assert os.path.exists(path=file1)
    assert os.path.exists(path=file2)
    set1 = file1.read()
    set2 = file2.read()
    assert len(set1) != 0
    assert len(set2) != 0
    assert set1.split('\n') == set2.split(',')[::-1]
