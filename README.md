# Datathon-Leaderboard

Creates a server to update DS3 Datathon Leaderboard using Kaggle Leaderboard

**Requirement**: Python 3.12 or above

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

4. Replace the `KAGGLE_USERNAME` and `KAGGLE_KEY` with those from the Kaggle

5. Replace the `MONGO_URI` if you have MongoDB running elsewhere

6. Install the packages listed in the `requirements.txt`:

    **Non VS Code**

    ```bash
        pip install -r requirements.txt
    ```

    **VS Code**

    **Requirement**: VS Code Python Interpreter be set to Virtual Environment `ds3-env`:
    Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)

    1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
    2. Search for `Tasks: Run Task` and select it.
    3. Search for `Install Packages` and select it.
    4. VS Code will automatically install all the packages and close the shell.

## Start Dev Server

### **Non VS Code**

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

### **VS Code**

**Requirement**: VS Code Python Interpreter be set to Virtual Environment `ds3-env`:
Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)

1. Open the Command Palette using `Ctrl+Shift+P` or `Cmd+Shift+P`.
2. Search for `Tasks: Run Task` and select it.
3. Search for `Dev Server` and select it.
4. VS Code will start the Dev Server automatically.
