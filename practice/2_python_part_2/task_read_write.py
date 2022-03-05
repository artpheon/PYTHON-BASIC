"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "23")
    file_2.txt (content: "78")
    file_3.txt (content: "3")

    Output:

    result.txt(content: "23, 78, 3")
"""


def read_write_values(fnum=20, fdir='files', result='result.txt'):
    with open(result, 'w') as result:
        for i in range(1, fnum + 1):
            with open(f'{fdir}/file_{i}.txt', 'r') as f:
                for line in f.readlines():
                    result.write(line.strip())
                    if i == fnum:
                        result.write('\n')
                    else:
                        result.write(', ')


if __name__ == '__main__':
    read_write_values()
