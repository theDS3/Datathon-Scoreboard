
from zipfile import ZipFile
from kaggle.api.kaggle_api_extended import KaggleApi
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from pytz import timezone

import os
from shutil import rmtree
import pandas as pd
import certifi

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

class Request(BaseModel):
    competitions: list[str]
    numOfTeams: int = 40

app = FastAPI()

ZIP_PATH = os.path.join(os.getcwd(), "zip")
CSV_PATH = os.path.join(os.getcwd(), "csv")

def download_competitions(competitions: list[str]):
    """ Downloads *.zip files containing leaderboard information from multiple competitions

    Args:
        competitions (list[str]): Competition IDs on Kaggle
    """

    # Initialize and authenticate with Kaggle Public API
    kaggle = KaggleApi()
    kaggle.authenticate()

    # Download zip files
    for comp in competitions:
        kaggle.competition_leaderboard_download(competition=comp, path=ZIP_PATH)

def extract_competitions():
    """ Extracts leaderboard information into *.csv from the *.zip files
    """

    for item in os.listdir(ZIP_PATH):
        if item.endswith(".zip"):
            file_path = os.path.join(ZIP_PATH, item)
            with ZipFile(file_path, "r") as zf:
                target_path = os.path.join("csv", os.path.splitext(item)[0] + ".csv")
                source_path = zf.namelist()[0]
                zf.getinfo(source_path).filename = target_path
                zf.extract(source_path)

def score_metric(df: pd.DataFrame) -> pd.DataFrame:
    """ Combines individual competition scores

    Args:
        df (pd.DataFrame): DataFrame containing individual competition scores

    Returns:
        pd.DataFrame: Contains the combined score
    """

    # Assumes all datasets are using the balanced_accuracy metric
    return df.sum(axis = 1, skipna = True)*100

def process_competitions(size: int, coll: Collection) -> list:
    """ Process the leaderboard data from multiple competitions

    Args:
        size (int): Maximum entries for the leaderboard. Defaults according to Request.
        coll (Collection):  Collection that contains the leaderboard snapshots.

    Returns:
        list: Contains the name of the team and cumulative score
    """

    df = pd.DataFrame()
    for item in os.listdir(CSV_PATH):
        if item.endswith(".csv"):
            file_path = os.path.join(CSV_PATH, item)
            df_comp = pd.read_csv(file_path)
            df_comp = df_comp.filter(["TeamName", "Score", "SubmissionCount"])
            df_comp.columns = ["Name", "Score-" + item, "Count-" + item]
            df = df_comp if df.empty  else pd.merge(df, df_comp, on = ["Name"], how = "outer")

    # create filters
    score_filter = []
    attempt_filter = []
    for item in os.listdir(CSV_PATH):
        if item.endswith(".csv"):
            score_filter.append("Score-" + item)
            attempt_filter.append("Count-" + item)
    
    # remove downloaded files
    rmtree(ZIP_PATH)
    rmtree(CSV_PATH)

    # aggregate attempts and compute score
    df["Attempts"] = df.filter(attempt_filter).sum(axis = 1, skipna = True)
    df["Score"] = score_metric(df.filter(score_filter))

    # sort
    df.sort_values(by = ["Score", "Attempts"], inplace = True, ascending = [False, True])
    df.reset_index(inplace = True, drop = True)

    # round
    df["Score"] = df["Score"].round(5)

    # Format to array
    curr_standings = []
    for _, row in df.head(size).iterrows():
        curr_standings.append({"name": row["Name"], "score": row["Score"], "numAttempts": (row["Attempts"]), "delta": "-"})

    # compute delta if feasible
    if (coll.count_documents({}) > 0):
        prev_standings = coll.find_one(sort=[("timestamp", -1)])
        for i in range(len(curr_standings)):
            team_name = curr_standings[i]["name"]
            prev_standing = next((team for team in prev_standings["data"] if team["name"] == team_name), None)
            if prev_standing:
                delta = prev_standings["data"].index(prev_standing) - i
                if (delta < 0):
                    curr_standings[i]["delta"] = str(delta)
                elif (delta > 0):
                    curr_standings[i]["delta"] = "+" + str(delta)

    return curr_standings

@app.post("/" , status_code=status.HTTP_201_CREATED)
def update_leaderboard(request: Request):
    """ Updates Leaderboard with new scores

    Args:
        request (Request): JSON Request Body

    Raises:
        HTTPException: Missing Competition IDs

    Returns:
        JSON: Returns the message 'OK' if successfully else an Error
    """

    # Initialize and authenticate
    client = MongoClient(os.getenv('MONGO_URI'), tlsCAFile=certifi.where())
    db = client[os.getenv("MONGO_DB")]

    if request.competitions:
        download_competitions(request.competitions)
        extract_competitions()

        db.leaderboard.insert_one(
            {
                "type": "public",
                "timestamp": datetime.now(timezone('Canada/Eastern')).strftime('%b %d %Y %I:%M:%S %p'),
                "data": process_competitions(size = request.numOfTeams, coll = db.leaderboard)
            }
        )

        # Return an HTTP response
        return {"message": 'OK'}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition IDs not provided")
