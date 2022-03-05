"""
Write tests for 2_python_part_2/task_read_write.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""


import os
import sys

FOLDER = '2_python_part_2'
FILES = os.path.join(os.path.dirname(os.getcwd()), FOLDER, 'files')
FNUM = 20
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), FOLDER))


def test_read_write(tmpdir):
    from task_read_write import read_write_values as func
    p = tmpdir.mkdir(FOLDER).join('result.txt')
    func(fnum=FNUM, fdir=FILES, result=p)
    assert os.path.exists(path=p)
    data = p.read()
    assert len(data) != 0
    assert len(data.split(',')) == FNUM
