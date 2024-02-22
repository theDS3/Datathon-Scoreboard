from typing import TypedDict
from pymongo import MongoClient
from argparse import ArgumentParser
from dotenv import dotenv_values
from tabulate import tabulate

from shared import (
    ROOT_PATH,
    get_abs_file_paths,
    process_csv,
    process_competitions,
    update_leaderboard,
)


class Secrets(TypedDict):
    MONGO_URI: str
    MONGO_DB: str


config: Secrets = dotenv_values(".env")

if len(config) == 0:
    raise RuntimeError('Missing .env file')

parser = ArgumentParser(
    prog="leaderboard.py",
    description="Create Private & Final Leaderboard Entry",
    epilog="Update Datathon Leaderboard",
)

parser.add_argument(
    "type",
    metavar="type",
    type=str,
    help="Leaderboard Entry Type",
    choices={"private", "final"},
)

parser.add_argument(
    "-p",
    "--publish",
    help="Publish the latest standing",
    action="store_true",
    default=False,
)

args = parser.parse_args()

PRIVATE_PATH = f"{ROOT_PATH}/private"

client = MongoClient(config.get("MONGO_URI"))
db = client.get_database(config.get("MONGO_DB"))
leaderboard_col = db.get_collection("leaderboard")

csv_files = get_abs_file_paths(PRIVATE_PATH, ".csv")
df = process_csv(csv_files)
standings = process_competitions(df, args.type, leaderboard_col)

if len(standings) == 0:
    raise ValueError(f"Review the CSV files in {PRIVATE_PATH}")


print(f"Latest Standing for {args.type.capitalize()} Leaderboard")
headers = [x.capitalize() for x in standings[0].keys()]
rows = [x.values() for x in standings]
print(tabulate(rows, headers, tablefmt="mixed_outline", numalign='left'))

if args.publish:
    update_leaderboard(standings, args.type, leaderboard_col)
    print(f"Updated {args.type.capitalize()} Leaderboard on {db} Database")

client.close()
