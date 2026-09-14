from pathlib import Path
import fileinput
log_path = r"C:\Users\Vedant\PythonProjects\LogAnalyser\NASA_access_log_Aug95_small_test"

for line in fileinput.input(files = log_path):
    line_list = line.split(" ")
    line_space = ""

    # Delete 1 and 2 ('-' and '-')
    line_list.pop(1)
    line_list.pop(1)

    # Conatenate 3 and 4 (The new 1 and 2) with a space - becoming 1
    concatenate = line_list[1] + " " + line_list[2]
    line_list.pop(1)
    line_list.pop(1)
    line_list.insert(1, concatenate)

    # Conatenate 5, 6 and 7 (The new 2, 3 and 4) with spaces in between, becoming 2
    concatenate = line_list[2] + " " + line_list[3] + " " + line_list[4]
    line_list.pop(2)
    line_list.pop(2)
    line_list.pop(2)
    line_list.insert(2, concatenate)

    # Leave 8 and 9 (3 and 4) as is
    for column in line_list:
        line_space += column + " "

    space_pos = len(line_space) - 2
    line = line_space[:space_pos]

    print(line)