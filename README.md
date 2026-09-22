# Log Analyser
This is a simple Log analyser. It would analyse the logs of a server, app, etc and will create a file explaining what has happened. It can/will tell you about brute-force hacking possibilities, anomalies, and whatever i can think to add. If you use this, enjoy!

## How it works
Use the argparsing of --log to and add you log path.

This script will analyse each log, parse it and add it to an SQLite Table. Pandas will then analyse each line and plot a few graphs. These include:
- Requests per hour Graph
- Requests in a month Graph
- Top Requested Content Graph
- Status Code Breakdown Graph
- Top 5 Errors Graph
- Errors Over Time Graph
- This last one isn't a graph but a print of possible detected outages.

## Note
In the paths, please change User to your user/match the paths to your paths if you do not use the argparse.

The log I used to test this is the NASA access logs of August 1995. These were CLF logs.

### Contact me
If you would like to contact me, contact me via [discord](https://discord.com/users/1092881580453802064)