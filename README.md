# Datathon-Leaderboard

Creates a server to update DS3 Datathon Leaderboard using Kaggle Leaderboard

## Local Setup

1. Create a Virtual Environment using `virtualenv`:
    ```bash
    virtualenv env
    ```

2. Start the Virtual Environment:
    ```bash
    source env/bin/activate
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

    **Requirement**: VS Code Python Interpreter be set to Virtual Environment `env`: Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)  for more info

    1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
    2. Search for `Tasks: Run Task` and select it.
    3. Search for `Install Packages` and select it.
    4. VS Code will automatically install all the packages and close the shell.


## Start Dev Server

### **NON-VSCODE**

1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
2. Search for `Tasks: Run Task` and select it.
3. Search for `Dev Server` and select it.
4. VS Code will start the Dev Server automatically.

### **VSCODE**


**Requirement**: VS Code Python Interpreter be set to Virtual Environment `env`: Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)  for more info


1. Export the Environmental Variables to the shell:
    ```bash
    export $(cat .env | xargs)
    ```

2. Verify if the Environmental Variables exist in the shell:
    ```bash
    env
    ```

3. Run the Dev Server:
    ```bash
    uvicorn main:app --reload --env-file .env
    ```