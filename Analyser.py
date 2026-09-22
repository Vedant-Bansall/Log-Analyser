import argparse
import fileinput
import re
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

# Argparsing
parser = argparse.ArgumentParser(description="A simple log scanner using python!")
parser.add_argument("--log", "-l", help="Run the log analyser with requested log", default=r"C:\Users\Vedant\PythonProjects\LogAnalyser\NASA_access_log_Aug95")
args = parser.parse_args()

# Get Log Path
log_path = args.log

# SQL Database
db_path = r"C:\Users\Vedant\PythonProjects\LogAnalyser\LogData.db"
db = sqlite3.connect(db_path)
db_cursor = db.cursor()
db_cursor.execute('CREATE TABLE IF NOT EXISTS logs (host TEXT, timestamp TEXT, request TEXT, reply_code TEXT, reply_bytes TEXT)')
db_cursor.execute('DELETE FROM logs')

# Regexing to break the request up
for line in fileinput.input(files = log_path):  # noqa: SIM115
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

    except:  # noqa: E722
        print(fileinput.lineno())
        break

db.commit()

df = pd.read_sql_query("SELECT * FROM logs", db)

# Timestamp Graphs
# Time Format: DD/MMM/YYYY:HH:MM:SS
format = "%d/%b/%Y:%H:%M:%S %z"
time_stamp_column = pd.to_datetime(df["timestamp"], format=format)

# Requests per hour Graph
hours = time_stamp_column.dt.hour
hours_group  = hours.groupby(hours)
hours_group.size().plot(kind="bar")
plt.xlabel("Hour of day")
plt.ylabel("Requests")
plt.title("Requests per hour")
plt.show()

# Requests in a month Graph
hourly_buckets = time_stamp_column.dt.floor('h')
hourly_buckets_group = hourly_buckets.groupby(hourly_buckets)
hourly_size = hourly_buckets_group.size().plot(kind="line")
plt.xlabel("Month")
plt.ylabel("Requests")
plt.title("Requests in a month")
plt.show()

# Top Requested Content Graph
requests_split = df["request"].str.split(expand=True)
contents = requests_split[1]
days_floor = time_stamp_column.dt.floor('D')

combined_df = pd.DataFrame({"day": days_floor, "path": contents})

all_counts = contents.value_counts()
requests = all_counts.index
requests = requests[:5]

filteration = combined_df[combined_df["path"].isin(requests)]

day_path = filteration.groupby(["day", "path"]).size()

df_unstack = day_path.unstack()

df_unstack.plot(kind="line")
plt.legend()
plt.xlabel("Dates")
plt.ylabel("Amount of Requests")
plt.title("Most Requested items")
plt.show()

# Status Code Graphs
# Status Code Breakdown Graph
df["reply_code"] = df["reply_code"].astype(str)
first_dig = df["reply_code"].str[0]
fxx = first_dig + "xx"
first_counts = fxx.value_counts()
first_counts.plot(kind="pie")
plt.title("All status codes as pie chart")
plt.show()

# Top 5 Errors Graph
error_df = pd.DataFrame({"error_path": contents, "error_code": first_dig, "error_day": days_floor})
code_filtered = error_df[error_df["error_code"].isin(['4', '5'])]
error_path_counts = code_filtered["error_path"].value_counts()

top_five = error_path_counts.index
top_five = top_five[:5]

error_path_counts.head(5).plot(kind="bar")
plt.xlabel("Error Requests")
plt.ylabel("Amount of Errors")
plt.title("Top 5 Errors Graph")
plt.show()

# Errors Over Time Graph
day_error = code_filtered.groupby(["error_day", "error_code"]).size()
de_df_unstack = day_error.unstack()
 
de_df_unstack.plot(kind="line")
plt.xlabel("Dates")
plt.ylabel("Errors")
plt.title("Errors over time")
plt.show()

# Possible Outage Scanner
hourly_counts = hourly_buckets_group.size()
hourly_df = hourly_counts.reset_index(name="count")
outage_df = pd.DataFrame({"hour": hourly_counts.index.hour, "values": hourly_counts.values, "outage_ts": hourly_df["timestamp"]})
hour = outage_df.groupby("hour")["values"]
hourly_mean = hour.mean()
threshold = hourly_mean / 2
outage_df["threshold"] = outage_df["hour"].map(threshold)
outage_df["is_outage"] = outage_df["values"] < outage_df["threshold"]
outages = outage_df[outage_df["is_outage"]]
print("Possible outages at:\n", outages["outage_ts"])