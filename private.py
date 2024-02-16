"""
This script compiles the leaderboard using the private leaderboard of the 
competitions. Hard-coded since it only needs to run once (locally) at the end
of the Datathon.
"""

from pymongo import MongoClient
from datetime import datetime
from pytz import timezone

import os
import pandas as pd

CSV_PATH = os.path.join(os.getcwd(), "private")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]

"""Merge the leaderboards"""
df = pd.DataFrame()
for item in os.listdir(CSV_PATH):
    if item.endswith(".csv"):
        df_private = pd.read_csv(os.path.join(CSV_PATH, item)).filter(
            ["TeamName", "Score", "SubmissionCount"]
        )
        df_private.columns = ["Name", f"Score{item[0:-24]}", f"Count{item[0:-24]}"]
        df = (
            df_private
            if df.empty
            else pd.merge(df, df_private, on=["Name"], how="outer")
        )

"""Combine leaderboards"""
# create filters
score_filter = list(filter(lambda x: x.startswith("Score"), list(df.columns)))
attempt_filter = list(filter(lambda x: x.startswith("Count"), list(df.columns)))

# aggregate attempts and compute score
df["Attempts"] = df.filter(attempt_filter).sum(axis=1, skipna=True)
df["Score"] = df.filter(score_filter).sum(axis=1, skipna=True) * 100

# sort
df.sort_values(by=["Score", "Attempts"], inplace=True, ascending=[False, True])
df.reset_index(inplace=True, drop=True)

# round
df["Score"] = df["Score"].astype(float).round(5)

# Format to array
curr_standings = []
for _, row in df.iterrows():
    curr_standings.append(
        {
            "name": row["Name"],
            "score": row["Score"],
            "numAttempts": row["Attempts"],
            "delta": "-",
        }
    )

# Calculate Deltas
if db.leaderboard.count_documents({}) > 0:
    prev_standings = db.leaderboard.find_one(
        {"type": "public"}, sort=[("timestamp", -1)]
    )
    for i in range(len(curr_standings)):
        team_name = curr_standings[i]["name"]
        prev_standing = next(
            (team for team in prev_standings["data"] if team["name"] == team_name), None
        )
        if prev_standing:
            delta = prev_standings["data"].index(prev_standing) - i
            if delta < 0:
                curr_standings[i]["delta"] = str(delta)
            elif delta > 0:
                curr_standings[i]["delta"] = "+" + str(delta)


db.leaderboard.insert_one(
    {
        "type": "private",
        "timestamp": datetime.now(timezone("Canada/Eastern")).strftime(
            "%b %d %Y %I:%M:%S %p"
        ),
        "data": curr_standings,
    }
)
