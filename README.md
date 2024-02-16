# Datathon-Leaderboard

Creates a server to update DS3 Datathon Leaderboard using Kaggle Leaderboard

## Local Setup

1. Create a Virtual Environment using `virtualenv`:
    ```bash
    virtualenv ds3-env
    ```

2. Start the Virtual Environment:
    ```bash
    source ds3-env/bin/activate
    ```

3. Copy the `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```

4. Replace the `KAGGLE_USERNAME` and `KAGGLE_KEY` with those from the Kaggle and optionally replace the `MONGO_URI` if you have the database running elsewhere

5. Install the packages listed in the `requirements.txt`:

    ### **NON-VSCODE**

        pip install -r requirements.txt

    ### **VSCODE**

    **Requirement**: VS Code Python Interpreter be set to Virtual Environment `ds3-env`: Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)  for more info

    1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
    2. Search for `Tasks: Run Task` and select it.
    3. Search for `Install Packages` and select it.
    4. VS Code will automatically install all the packages and close the shell.


## Start Dev Server

### **NON-VSCODE**

1. Export the Environmental Variables to the shell:
    ```bash
    export $(cat .env | xargs)
    ```

2. Verify if the Environmental Variables exist in the shell:
    ```bash
    env
    ```

3. Start the Virtual Environment:
    ```bash
    source ds3-env/bin/activate
    ```

4. Run the Dev Server:
    ```bash
    uvicorn main:app --reload --env-file .env
    ```

### **VSCODE**

**Requirement**: VS Code Python Interpreter be set to Virtual Environment `ds3-env`: Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)  for more info


1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
2. Search for `Tasks: Run Task` and select it.
3. Search for `Dev Server` and select it.
4. VS Code will start the Dev Server automatically.


## Update Non-Public Leaderboard

### For Private Leaderboard

To make updates to the private leaderboard it requires the following:

1. Create a Folder called `private` to contain multiple CSV
2. Download from Kaggle the Private Leaderboard CSV's and place it here
3. Each of these CSV require the following headers:

    ```txt
    Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames
    ```

Use the following command to run the commands:

```bash
export $(cat .env | xargs)
python private.py
```
### For Final Leaderboard

To make updates to the final leaderboard it requires the following:

1. Create a Folder called `private` to contain multiple CSV
2. Download from Kaggle the Private Leaderboard CSV's and place it here
3. Each of these CSV require the following headers:

    ```txt
    Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames
    ```

4. Create a Folder called `bonus` to contain multiple CSV
5. Load each CSV containing the attendance of participants at in-person events
6. Each of these CSV require the following headers:

    ```txt
    Email
    ```

7. Create a file called `mapping.csv` with the following headers: `Email,Team,Team Size`

    - It is a mapping that contains all participants and the teams they belong to

Use the following command to run the commands:

```bash
export $(cat .env | xargs)
python final.py
```
