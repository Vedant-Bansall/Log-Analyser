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
db_cursor.execute('DELETE FROM logs')

for line in fileinput.input(files = log_path):
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
        break

db.commit()

df = pd.read_sql_query("SELECT * FROM logs", db)
print(df.shape)

# Timestamp Graphs
# Time Format: DD/MMM/YYYY:HH:MM:SS
format = "%d/%b/%Y:%H:%M:%S %z"
time_stamp_column = pd.to_datetime(df["timestamp"], format=format)

# Graph 1
hours = time_stamp_column.dt.hour
hours_group  = hours.groupby(hours)
hours_group.size().plot(kind="bar")
plt.xlabel("Hour of day")
plt.ylabel("Requests")
plt.title("Requests per hour")
plt.show()

# Graph 2
hourly_buckets = time_stamp_column.dt.floor('h')
hourly_buckets_group = hourly_buckets.groupby(hourly_buckets)
hourly_buckets_group.size().plot(kind="line")
plt.xlabel("Month")
plt.ylabel("Requests")
plt.title("Requests in a month")
plt.show()

# Top Requested Content Graph
requests_split = df["request"].str.split(expand=True)
contents = requests_split[1]
days_floor = time_stamp_column.dt.floor('D')

combined = pd.DataFrame({"day": days_floor, "path": contents})

all_counts = contents.value_counts()
requests = all_counts.index
requests = requests[:5]

filteration = combined[combined["path"].isin(requests)]

day_path = filteration.groupby(["day", "path"]).size()

df_unstack = day_path.unstack()

df_unstack.plot(kind="line")
plt.legend()
plt.xlabel("Dates")
plt.ylabel("Amount of Requests")
plt.title("Most Requested items")
plt.show()

# Status Code Graphs
df["reply_code"] = df["reply_code"].astype(str)
first_dig = df["reply_code"].str[0]
first_dig += "xx"
first_counts = first_dig.value_counts()
first_counts.plot(kind="pie")
plt.title("All status codes as pie chart")
plt.show()