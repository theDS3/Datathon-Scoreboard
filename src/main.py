from zipfile import ZipFile
from kaggle.api.kaggle_api_extended import KaggleApi
from pymongo import MongoClient

from os import getenv
from os.path import basename
from shutil import rmtree

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

from src.shared import (
    ROOT_FOLDER_PATH,
    MAX_NUM_OF_TEAMS,
    get_abs_file_paths,
    process_csv,
    process_competitions,
    update_leaderboard,
)

class Request(BaseModel):
    competitions: list[str]
    numOfTeams: int = MAX_NUM_OF_TEAMS


app = FastAPI()

PUBLIC_PATH = f"{ROOT_FOLDER_PATH}/public"

def download_competitions(competitions: list[str]) -> list[str]:
    """Downloads and Extracts leaderboard information from multiple competitions

    Args:
        competitions (list[str]): Competition IDs on Kaggle

    Returns:
        list(str): File Path for *.csv
    """

    # local paths for *.zip and *.csv files
    ZIP_PATH = f"{PUBLIC_PATH}/zip"
    CSV_PATH = f"{PUBLIC_PATH}/csv"

    # initialize and authenticate with Kaggle Public API
    kaggle = KaggleApi()
    kaggle.authenticate()

    # Download *.zip files
    for comp in competitions:
        kaggle.competition_leaderboard_download(competition=comp, path=ZIP_PATH)

    # extracts *.csv file from *.zip files
    zip_file_paths = get_abs_file_paths(ZIP_PATH, '.zip')
    csv_file_paths = []

    for zip_file_path in zip_file_paths:
        with ZipFile(zip_file_path, "r") as zf:
            target_path = f"{CSV_PATH}/{basename(zip_file_path).replace("zip", "csv")}"
            source_path = zf.namelist()[0]
            zf.getinfo(source_path).filename = target_path
            zf.extract(source_path)
            csv_file_paths.append(target_path)

    return csv_file_paths

@app.post("/public", status_code=status.HTTP_201_CREATED)
def update_public(request: Request):
    """Updates Public Leaderboard with new scores

    Args:
        request (Request): JSON Request Body

    Raises:
        HTTPException: Missing Competition IDs
        HTTPException: Internal Server Error

    Returns:
        JSON: Returns the message 'OK' if successfully else an Error
    """

    if request.competitions:
        try:
            # initialize and authenticate
            client = MongoClient(getenv("MONGO_URI"))
            db = client.get_database(getenv("MONGO_DB"))
            leaderboard_col = db.get_collection("leaderboard")

            csv_files = download_competitions(request.competitions)
            df = process_csv(csv_files)
            standings = process_competitions(df, "public", leaderboard_col, size=request.numOfTeams)

            # adds new entry to public leaderboard
            update_leaderboard(standings, "public", leaderboard_col)

            # closes db connection
            client.close()

            # removing files to prevent caching on cloud
            rmtree(PUBLIC_PATH)

            return {"message": "OK"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Competition IDs not provided"
    )
