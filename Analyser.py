import fileinput
import sqlite3
import re
import pandas as pd
import matplotlib.pyplot as plt

# Get Log Path
log_path = r"C:\Users\Vedant\PythonProjects\LogAnalyser\NASA_access_log_Aug95"

# SQL Database
db_path = r"C:\Users\Vedant\PythonProjects\LogAnalyser\LogData.db"
db = sqlite3.connect(db_path)
db_cursor = db.cursor()
db_cursor.execute('CREATE TABLE IF NOT EXISTS logs (host TEXT, timestamp TEXT, request TEXT, reply_code TEXT, reply_bytes TEXT)')

for line in fileinput.input(files = log_path):
    # Previous Seperation Method... It didnt work due to varying types of logs
    '''line_list = line.split(" ")

    # Delete 1 and 2 ("-" and "-")
    line_list.pop(1)
    line_list.pop(1)

    # Conatenate 3 and 4 (The new 1 and 2) with a space - becoming 1, strip []
    concatenate = line_list[1] + " " + line_list[2]
    line_list.pop(1)
    line_list.pop(1)
    concatenate = concatenate.lstrip("[")
    concatenate = concatenate.rstrip("]")
    line_list.insert(1, concatenate)

    # Conatenate 5, 6 and 7 (The new 2, 3 and 4) with spaces in between, becoming 2
    concatenate = line_list[2] + " " + line_list[3] + " " + line_list[4]
    line_list.pop(2)
    line_list.pop(2)
    line_list.pop(2)
    line_list.insert(2, concatenate)
    
    # Leave 8 and 9 (3 and 4) as is
    '''

    # New Seperation Method (Regex)
    try:
        host = re.match(r"(\S+)", line)
        host = host.group(1)

        timestamp = re.search(r"\[(.+?)\]", line)
        timestamp = timestamp.group(1)

        request = re.search(r"\"(.+?)\"", line)
        request = request.group(1)

        status_code = re.search(r"\" (\d+)", line)
        status_code = status_code.group(1)

        bytes_count = re.search(r"\" (?:\d+) (\d+|-)", line)
        bytes_count = bytes_count.group(1)

        regexed_line = [host, timestamp, request, status_code, bytes_count]

        # Add Everything to table
        db_cursor.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?)", regexed_line)

    except:
        print(fileinput.lineno())

db.commit()

data_frame = pd.read_sql_query("SELECT * FROM logs", db)

# Time Format: DD/MMM/YYYY:HH:MM:SS
format = "%d/%b/%Y:%H:%M:%S %z"
time_stamp_column = pd.to_datetime(data_frame["timestamp"], format=format)

hours = time_stamp_column.dt.hour

hours_group  = hours.groupby(hours)
hours_group.size().plot(kind="bar")
plt.xlabel("Hour of day")
plt.ylabel("Requests")
plt.title("Requests per hour")
plt.show()