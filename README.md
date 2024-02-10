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

    - The `kaggle` package that is being used is a custom build version by `theDS3`.
      Read [below](#custom-kaggle-api)

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

## Custom Kaggle API

When we try to use the official Kaggle API to pull data that is required to compute
the Public Leaderboard, we encounter the following
[bug](https://github.com/Kaggle/kaggle-api/issues/513#issuecomment-1874634876).
The custom [wheels](https://github.com/theDS3/Datathon-Leaderboard/tree/main/wheels)
implements the following [change](https://github.com/Kaggle/kaggle-api/pull/514/files#diff-c3a1002ee9fd03076fec2d10f81b0f1307e3ad16821c6915e38a05f213efefdc).

### Wheel Build

If a new version of Kaggle is released, and the above bug has not been fixed,
then follow these steps here to update Kaggle API.

1. To build the wheel, it requires the [build](https://pypi.org/project/build/) package

    ```bash
    pip install --upgrade build
    ```

2. Download the build [files](https://pypi.org/project/kaggle/#files) related to
the latest version of the API

3. Implement the [change](https://github.com/Kaggle/kaggle-api/pull/514/files#diff-c3a1002ee9fd03076fec2d10f81b0f1307e3ad16821c6915e38a05f213efefdc)

4. Build the wheel

    ```bash
    python -m build --wheel
    ```

5. Move the wheel file from `dist` folder to the `wheels` folder inside
[Datathon-Leaderboard/wheels](https://github.com/theDS3/Datathon-Leaderboard/tree/main/wheels)

6. Update kaggle in [requirements.txt](https://github.com/theDS3/Datathon-Leaderboard/blob/961d4b6994f3f068802c20e3847fe0a0f560c973/requirements.txt#L19)
for the latest wheel

7. Merge new changes to `main` branch
