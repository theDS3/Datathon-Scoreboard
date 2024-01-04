
from zipfile import ZipFile
from kaggle.api.kaggle_api_extended import KaggleApi
from pymongo import MongoClient
from datetime import datetime
from pytz import timezone

import os
import pandas as pd

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

def process_competitions(size: int) -> list:
    """ Process the leaderboard data from multiple competitions

    Args:
        size (int, optional): Maximum entries for the leaderboard. Defaults to 40.

    Returns:
        list: Contains the name of the team and cumulative score
    """

    df = pd.DataFrame()
    for item in os.listdir(CSV_PATH):
        if item.endswith(".csv"):
            file_path = os.path.join(CSV_PATH, item)
            df_comp = pd.read_csv(file_path)
            df_comp = df_comp.filter(["TeamName", "Score"])
            df_comp.columns = ["Name", "Score-"+item]
            df = df_comp if df.empty  else pd.merge(df, df_comp, on = ["Name"], how = "outer")

    # compute combined score (placeholder)
    df["Score"] = df.drop(columns=["Name"]).sum(axis=1, skipna=True)
    df["Score"] = df["Score"].round(5)
    df.sort_values(by=['Score'], inplace=True, ascending=False)
    df = df.reset_index()

    # Format to array
    data = []
    for _, row in df.head(size).iterrows():
        data.append({"Team": row["Name"], "Score": row["Score"]})

    return data

@app.get("/" , status_code=status.HTTP_201_CREATED)
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
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client.dev

    if request.competitions:
        download_competitions(request.competitions)
        extract_competitions()

        db.leaderboard.insert_one(
            {
                "timestamp": datetime.now(timezone('Canada/Eastern')).strftime('%b %d %Y %I:%M %p'),
                "data": process_competitions(request.numOfTeams)
            }
        )

        # Return an HTTP response
        return {"message": 'OK'}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition IDs not provided")
