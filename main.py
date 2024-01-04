"""
Installation, Imports, Variables
"""
# might have to pip install on the cloud
# pip install kaggle
# pip install pandas
# pip install pymongo

import os
from zipfile import ZipFile
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import pymongo
import datetime

# set up environment variables (now we don't need kaggle.json)
os.environ["KAGGLE_USERNAME"] = ""
os.environ["KAGGLE_KEY"] = ""

# Initialize and authenticate
api = KaggleApi()
api.authenticate()

competitions = ["llm-detect-ai-generated-text", "blood-vessel-segmentation", "UBC-OCEAN"]
zip_path = os.path.join(os.getcwd(), "raw")

"""
Fetch leaderboards via Kaggle API
"""

# Download zip files
for comp in competitions:
    api.competition_leaderboard_download(competition=comp, path=zip_path, quiet=True)

# Extract csv

for item in os.listdir(zip_path):
    if item.endswith(".zip"):
        file_path = os.path.join(zip_path, item)
        with ZipFile(file_path, "r") as zf:
            target_path = os.path.join("CSV", os.path.splitext(item)[0] + ".csv")
            source_path = zf.namelist()[0]
            zf.getinfo(source_path).filename = target_path
            zf.extract(source_path)

"""
Compute combined score
"""

# Read and combine csv's (assumes team names within each comp are unique and consistent across all comps)
csv_path = os.path.join(os.getcwd(), "CSV")
df = pd.DataFrame()
for item in os.listdir(csv_path):
    if item.endswith(".csv"):
        file_path = os.path.join(csv_path, item)
        df_comp = pd.read_csv(file_path)
        df_comp = df_comp.filter(["TeamName", "Score"])
        df_comp.columns = ["Name", "Score-"+item]
        if (df.empty):
            df = df_comp
        else:
            df = pd.merge(df, df_comp, on = ["Name"], how = "outer")

# compute combined score (placeholder)
df["Score"] = df.drop(columns=["Name"]).sum(axis=1, skipna=True)
df["Score"] = df["Score"].round(5)
df.sort_values(by=['Score'], inplace=True, ascending=False)
df = df.reset_index()

"""
Export to Atlas
"""

# Format to array
data = []
for index, row in df.iterrows():
    data.append({"Team": row["Name"], "Score": row["Score"]})

# Send to cloud
ATLAS_ENDPT = ""
client = pymongo.MongoClient(ATLAS_ENDPT)
db = client['dev']
col = db['leaderboard']
col.delete_many({})
mydict = {"time": datetime.datetime.now(), "data": data}
col.insert_one(mydict)