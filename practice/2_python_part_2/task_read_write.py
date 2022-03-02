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

if __name__ == '__main__':
    files = 20
    with open('result.txt', 'w') as result:
        for i in range(1, files + 1):
            with open(f'files/file_{i}.txt', 'r') as f:
                # using readlines() in case we have several lines with numbers. otherwise, would use read()
                for line in f.readlines():
                    result.write(line.strip())
                    if i == files:
                        result.write('\n')
                    else:
                        result.write(', ')
