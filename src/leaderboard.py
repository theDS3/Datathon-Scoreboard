from typing import TypedDict
from pymongo import MongoClient
from argparse import ArgumentParser
from dotenv import dotenv_values
from tabulate import tabulate

from numpy.random import randint, uniform
from pandas import DataFrame

from shared import (
    ROOT_FOLDER_PATH,
    MAX_NUM_OF_TEAMS,
    DECIMALS,
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
    raise RuntimeError("Missing .env file")

parser = ArgumentParser(
    prog="leaderboard.py",
    description="Add Leaderboard Entry",
    epilog="Update Datathon Leaderboard",
)

subparsers = parser.add_subparsers(dest="command")

# Seed command
seed_parser = subparsers.add_parser("seed", help="Generate Mock Standings")
seed_parser.add_argument(
    "num_of_teams",
    metavar="teams-size",
    type=int,
    nargs="?",
    default=MAX_NUM_OF_TEAMS,
    help=f"Seed value (default: {MAX_NUM_OF_TEAMS})",
)

# Show command
show_parser = subparsers.add_parser("show", help="Display the latest Standing")
show_parser.add_argument(
    "type",
    metavar="type",
    type=str,
    choices={"public", "private", "final"},
    help="Leaderboard Entry Type",
)

# Publish command
publish_parser = subparsers.add_parser("publish", help="Publish the latest Standing")
publish_parser.add_argument(
    "type",
    metavar="type",
    type=str,
    choices={"public", "private", "final"},
    help="Leaderboard Entry Type",
)

args = parser.parse_args()

client = MongoClient(config.get("MONGO_URI"))
db = client.get_database(config.get("MONGO_DB"))
leaderboard_col = db.get_collection("leaderboard")

if args.command == "seed":
    name = list(map(lambda x: f"Team-{x}", range(1, args.num_of_teams + 1)))
    attempts = randint(low=1, high=40, size=args.num_of_teams)

    score = lambda high=100: uniform(low=0, high=high, size=(args.num_of_teams, 3)).sum(
        axis=1
    )
    delta = lambda: list(
        map(
            lambda x: "-" if x == 0 else f"+{x}" if x > 0 else x,
            randint(-12, 12, size=args.num_of_teams),
        )
    )

    for leaderboard_type in ["public", "private", "final"]:
        df = DataFrame(
            {
                "name": name,
                "score": score(100 if leaderboard_type != "final" else 94),
                "attempts": attempts,
                "delta": delta(),
            }
        )

        if leaderboard_type == "final":
            df = df.assign(
                bonus=uniform(0.1, 2.0, size=args.num_of_teams)
                ** randint(1, 4, size=args.num_of_teams)
            )
            df = df.assign(finalScore=df["bonus"] * df["score"])

            df.sort_values(
                by=["finalScore", "score", "attempts"],
                inplace=True,
                ascending=[False, False, True],
            )
            df["bonus"] = df["bonus"].astype(float).round(DECIMALS)
            df["score"] = df["score"].astype(float).round(DECIMALS)
            df["finalScore"] = df["finalScore"].astype(float).round(DECIMALS)
        else:
            df.sort_values(
                by=["score", "attempts"], inplace=True, ascending=[False, True]
            )
            df["score"] = df["score"].astype(float).round(DECIMALS)

        update_leaderboard(df.to_dict("records"), leaderboard_type, leaderboard_col)
        print(f"Added Mock Entry for {leaderboard_type.capitalize()} Leaderboard on {db.name} Database")

elif args.command in ['show', 'publish']:

    PRIVATE_PATH = f"{ROOT_FOLDER_PATH}/private"

    csv_files = get_abs_file_paths(PRIVATE_PATH, ".csv")
    df = process_csv(csv_files)
    standings = process_competitions(df, args.type, leaderboard_col)

    if len(standings) == 0:
        if args.type != 'public':
            raise ValueError(f"Review the CSV files in {PRIVATE_PATH}")
        else:
            raise ValueError(f"Review the Competition on Kaggle")

    print(f"Latest Standing for {args.type.capitalize()} Leaderboard")
    headers = [x.capitalize() for x in standings[0].keys()]
    rows = [x.values() for x in standings]
    print(tabulate(rows, headers, tablefmt="mixed_outline", numalign='left'))

    if args.command == 'publish':
        update_leaderboard(standings, args.type, leaderboard_col)
        print(f"Updated {args.type.capitalize()} Leaderboard on {db.name} Database")

client.close()
