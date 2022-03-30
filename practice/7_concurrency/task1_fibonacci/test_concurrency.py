from template import OUTPUT_DIR, RESULT_FILE, func1, func2
from random import randint
import os
import re


class TestConcurrency:
    array = [randint(1000, 100000) for _ in range(1000)]

    @staticmethod
    def clean_dirs():
        for file in os.listdir(OUTPUT_DIR):
            os.remove(f'{OUTPUT_DIR}/{file}')

    def test_func_1(self):
        self.clean_dirs()
        func1(array=self.array)

        fls = [int(re.findall(r'\d+', file)[0]) for file in os.listdir(OUTPUT_DIR)]
        array = list(set(self.array))
        assert sorted(fls) == sorted(array)

    def test_func_2(self):
        func2(result_file=RESULT_FILE)

        assert os.path.isfile(RESULT_FILE)
        array = list(set(self.array))
        with open(RESULT_FILE) as f:
            assert len(array) + 1 == len(f.readlines())
        self.clean_dirs()
