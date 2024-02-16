"""
This script compiles the leaderboard using the private leaderboard of the
competitions along with the bonus points awarded for attending events.
Hard-coded since it only needs to run once (locally) at the end
of the Datathon.
"""

from pymongo import MongoClient
from datetime import datetime
from pytz import timezone

import os
import pandas as pd

CSV_PATH = os.path.join(os.getcwd(), "private")
BONUS_PATH = os.path.join(os.getcwd(), "bonus")

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

"""Compute Bonuses

assume we have a mapping.csv where each row has email, teamname, teamsize.
for each event, compute team->bonus mapping (default bonus = 1)
    might be easier to create a dictionary object first {(name, bonus)} for every team on the leaderboard
    by doing df.iterrows.
    for each email in the event.csv, find corresponding teamname and teamsize from mapping.csv
    increment bonus by 0.06 / team_size
    create df_event, which has teamname and event_bonus (unique for each event)
merge all 4 mappings (by taking the product) EASY
    outer merge on teamname (make sure column name for bonuses in all 4 df_events are unique)
    create "bonus" by taking the prod of all 4 individual bonuses
update original df with bonuses
    just merge on team name
multiply score with bonus to compute FinalScore
"""

# Create bonus column
df["Bonus"] = 1.0
df.set_index("Name", inplace=True)

# Get mapping
df_mapping = pd.read_csv("mapping.csv")

# Get a list of all CSV files in the folder
csv_files = [file for file in os.listdir(BONUS_PATH) if file.endswith(".csv")]

# Iterate over each CSV file in the folder
for csv_file in csv_files:

    # Construct the full file path
    file_path = os.path.join(BONUS_PATH, csv_file)

    # Load the CSV file into a dataframe
    df_attendance = pd.read_csv(file_path)

    # Subsetting attendance
    merged_df = pd.merge(df_mapping, df_attendance, on="Email", how="inner")

    # Populating with 1's
    merged_df["Attendance"] = 1

    # Grouping by Team and Team Size, and aggregating attendance
    aggregate_attendance = (
        merged_df.groupby(["Team", "Team Size"])["Attendance"].sum().reset_index()
    )

    # Creating Partial Bonus column
    aggregate_attendance["Partial Bonus"] = (
        aggregate_attendance["Attendance"] / aggregate_attendance["Team Size"]
    )

    # Updating bonus column
    for _, row in aggregate_attendance.iterrows():
        df.loc[row["Team"], "Bonus"] *= 1 + 0.06 * row["Partial Bonus"]

# Calculate final score
df["FinalScore"] = df["Score"] * df["Bonus"]

# sort
df.sort_values(by=["FinalScore", "Score"], inplace=True, ascending=[False, False])
df.reset_index(inplace=True, drop=False)

# round
df["Bonus"] = df["Bonus"].astype(float).round(5)
df["Score"] = df["Score"].astype(float).round(5)
df["FinalScore"] = df["FinalScore"].astype(float).round(5)

# Format to array
curr_standings = []
for _, row in df.iterrows():
    curr_standings.append(
        {
            "name": row["Name"],
            "score": row["Score"],
            "numAttempts": row["Attempts"],
            "bonus": row["Bonus"],
            "finalScore": row["FinalScore"],
            "delta": "-",
        }
    )

# Calculate Deltas
if db.leaderboard.count_documents({}) > 0:
    prev_standings = db.leaderboard.find_one(
        {"type": "private"}, sort=[("timestamp", -1)]
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

"""Send Leaderboard to ATLAS"""
db.leaderboard.insert_one(
    {
        "type": "final",
        "timestamp": datetime.now(timezone("Canada/Eastern")).strftime(
            "%b %d %Y %I:%M:%S %p"
        ),
        "data": curr_standings,
    }
)
