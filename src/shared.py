from typing import TypedDict, NotRequired, Literal
from pymongo.collection import Collection

from datetime import datetime
from pytz import timezone
from pandas import DataFrame, read_csv, merge

import os

type LeaderboardType = Literal["public", "private", "final"]


class LeaderboardEntry(TypedDict):
    name: str
    score: float
    numAttempts: int
    delta: str
    bonus: NotRequired[float]
    finalScore: NotRequired[float]


# Maximum number of teams to be displayed
MAX_NUM_OF_TEAMS = 40

# Maximum decimal places for rounding
DECIMALS = 5

# Root Folder
ROOT_FOLDER_PATH = "data"


def get_abs_file_paths(
    dir_path: str, file_ext: Literal[".csv", ".zip"], is_sorted=False
) -> list[str]:
    """Retrieve Absolute File Paths from `dir_path` with certain `file_ext`

    Args:
        dir_path (str): Relative/Absolute Directory Path
        file_ext (Literal[.csv, .zip]): Specific File Extensions
        is_sorted (bool, optional): Orders by File Basename. Defaults to False.

    Raises:
        ValueError: `DirectoryDoesNotExist`

    Returns:
        list[str]: Absolute File Paths for specific File Extensions
    """

    # Verify if `dir_path` is an absolute or relative path
    # Converts `dir_path` if its an relative path
    abs_dir_path = (
        os.path.join(os.getcwd(), dir_path) if not os.path.isabs(dir_path) else dir_path
    )

    # Checks if the `abs_dir_path` exists
    if not os.path.isdir(abs_dir_path):
        raise ValueError(f"DirectoryDoesNotExist: {abs_dir_path}")

    # Finds and Filters all files in the `abs_dir_path` with extension of `file_ext`
    files = [
        os.path.join(abs_dir_path, file)
        for file in os.listdir(abs_dir_path)
        if file.endswith(file_ext)
    ]

    return files if not is_sorted else sorted(files)


def process_csv(csv_file_paths: list[str]) -> DataFrame:
    """Extract leaderboard information from *.csv

    Args:
        csv_file_paths (list[str]): File Path for *.csv files

    Raises:
        ValueError: `InvalidFile`

    Returns:
        DataFrame: Kaggle API Data with Scores and Counts for each Team from all competitions
    """

    df = DataFrame()
    for csv_file_path in csv_file_paths:
        # Read the CSV files and filter specific columns
        df_comp = read_csv(csv_file_path).filter(
            ["TeamName", "Score", "SubmissionCount"]
        )

        # Check if the file has the correct extension
        competition_name, file_ext = os.path.splitext(os.path.basename(csv_file_path))
        if file_ext != ".csv":
            raise ValueError(f"InvalidFile: {csv_file_path}")

        # Rename the columns
        df_comp.columns = [
            "name",
            f"score-{competition_name}",
            f"count-{competition_name}",
        ]

        # Join the multiple csv from
        df = df_comp if df.empty else merge(df, df_comp, on=["name"], how="outer")

    return df


def process_competitions(
    df: DataFrame,
    leaderboard_type: LeaderboardType,
    coll: Collection,
    size=MAX_NUM_OF_TEAMS,
) -> list[LeaderboardEntry]:
    """Process the leaderboard data from multiple competitions

    Args:
        df (DataFrame): Kaggle API Data with Scores and Counts for each Team from all competitions.
        leaderboard_type (LeaderboardType): Specific mode of calculations
        coll (Collection):  Collection that contains the leaderboard snapshots.
        size (int, optional): Limits number of teams. Defaults to `MAX_NUM_OF_TEAMS`.

    Raises:
        ValueError: `InvalidCollection`
        ValueError: `FileDoesNotExist`

    Returns:
        list[LeaderboardEntry]: Contains the latest standings from multiple leaderboards per team
    """

    # Checks if all columns in df is Nan
    if df.isnull().values.all():
        return []

    # Verifies if reading the correct leaderboard collection
    if coll.name != "leaderboard":
        raise ValueError(f"InvalidCollection: ${coll.name}")

    # create filters
    score_filter = filter(lambda x: x.startswith("score-"), df.columns)
    attempt_filter = filter(lambda x: x.startswith("count-"), df.columns)

    # aggregate attempts and compute score
    df["score"] = df[score_filter].sum(axis=1, skipna=True) * 100
    df["attempts"] = df[attempt_filter].sum(axis=1, skipna=True)

    # leaderboard document entry
    curr_standings: list[LeaderboardEntry] = []

    # previous leaderboard standings to compare for delta calculations
    compare_leaderboard_type: LeaderboardType = "public"

    if leaderboard_type == "final":
        """Compute Bonuses

        assume we have a mapping.csv where each row has email, teamname, teamsize.
        for each event, compute team -> bonus mapping (default bonus = 1)
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
        multiply score with bonus to compute finalScore
        """

        # Create bonus column
        df["bonus"] = 1.0
        df.set_index("name", inplace=True)

        MAPPING_CSV = f"{ROOT_FOLDER_PATH}/final/mapping.csv"
        BONUS_PATH = f"{ROOT_FOLDER_PATH}/final/bonus"

        if not os.path.isfile(MAPPING_CSV):
            raise ValueError(f"FileDoesNotExist: {MAPPING_CSV}")

        # Get mapping
        df_mapping = read_csv(MAPPING_CSV)

        # Get a list of all CSV files in the folder
        csv_files = get_abs_file_paths(BONUS_PATH, ".csv")

        if len(csv_files) == 0:
            raise ValueError(f"FileDoesNotExist: {BONUS_PATH}/*.csv")

        # Iterate over each CSV file in the folder
        for csv_file in csv_files:

            # Load the CSV file into a dataframe
            df_attendance = read_csv(csv_file)

            # Subsetting attendance
            merged_df = merge(df_mapping, df_attendance, on="Email", how="inner")

            # Populating with 1's
            merged_df["Attendance"] = 1

            # Grouping by Team and Team Size, and aggregating attendance
            aggregate_attendance = (
                merged_df.groupby(["Team", "Team Size"])["Attendance"]
                .sum()
                .reset_index()
            )

            # Creating Partial Bonus column
            aggregate_attendance["Partial Bonus"] = (
                aggregate_attendance["Attendance"] / aggregate_attendance["Team Size"]
            )

            # Updating bonus column
            for _, row in aggregate_attendance.iterrows():
                df.loc[row["Team"], "bonus"] *= 1 + 0.06 * row["Partial Bonus"]

        # Calculate final score
        df["finalScore"] = df["score"] * df["bonus"]

        # sort
        df.sort_values(
            by=["finalScore", "score", "attempts"],
            inplace=True,
            ascending=[False, False, True],
        )
        df.reset_index(inplace=True, drop=False)

        # round
        df["bonus"] = df["bonus"].astype(float).round(DECIMALS)
        df["score"] = df["score"].astype(float).round(DECIMALS)
        df["finalScore"] = df["finalScore"].astype(float).round(DECIMALS)

        compare_leaderboard_type = "private"
        curr_standings = df[:size][
            ["name", "score", "attempts", "bonus", "finalScore"]
        ].to_dict("records")

    else:
        # sort
        df.sort_values(by=["score", "attempts"], inplace=True, ascending=[False, True])
        df.reset_index(inplace=True, drop=True)

        # round
        df["score"] = df["score"].astype(float).round(DECIMALS)

        curr_standings = df[:size][["name", "score", "attempts"]].to_dict("records")

    # checks if leaderboard has an older entry
    if coll.count_documents({"type": compare_leaderboard_type}) > 0:
        # pulling previous leaderboard standing
        prev_standings = coll.find_one(
            {"type": compare_leaderboard_type},
            {"data": True, "_id": False},
            sort=[("timestamp", -1)],
        )

        # calculates the delta between previous and current standings
        for idx, entry in enumerate(curr_standings):
            prev_standing = next(
                (
                    team
                    for team in prev_standings["data"]
                    if team["name"] == entry["name"]
                ),
                None,
            )
            if prev_standing:
                delta = prev_standings["data"].index(prev_standing) - idx
                if delta < 0:
                    entry["delta"] = str(delta)  # Decrease
                elif delta > 0:
                    entry["delta"] = "+" + str(delta)  # Increase
                else:
                    entry["delta"] = "-"  # No Change
            else:
                entry["delta"] = "-"

    return curr_standings


def update_leaderboard(
    data: list[LeaderboardEntry], leaderboard_type: LeaderboardType, coll: Collection
):
    """Insert new document into `leaderboard` collection

    Args:
        data (list[LeaderboardEntry]): New document to be added to the collection
        leaderboard_type (LeaderboardType): Specific type of document for a specific leaderboard
        coll (Collection):  Collection that contains the leaderboard snapshots.

    Raises:
        ValueError: `InvalidCollection`

    Returns:
        None
    """

    # verifies if reading the correct leaderboard collection
    if coll.name != "leaderboard":
        raise ValueError(f"InvalidCollection: ${coll.name}")

    coll.insert_one(
        {
            "type": leaderboard_type,
            "timestamp": datetime.now(timezone("Canada/Eastern")).strftime(
                "%b %d %Y %I:%M:%S %p"
            ),
            "data": data,
        }
    )
