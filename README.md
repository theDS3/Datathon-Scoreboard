# Datathon-Leaderboard

Creates a server to update DS3 Datathon Leaderboard using Kaggle Leaderboard

**Requirement**: Python 3.12 or above and [`pipenv`](https://pipenv.pypa.io/en/latest/)

## Getting Started

1. Create Virtual Environment and Install Packages:

    - The `kaggle` package that is being used is a custom build version by `theDS3`.
      Read [below](#custom-kaggle-api)

    ```bash
    pipenv install
    ```

2. Copy the `.env.example` to `.env`:

    ```bash
    cp .env.example .env
    ```

3. Replace the `KAGGLE_USERNAME` and `KAGGLE_KEY` with those from the Kaggle

4. Replace the `MONGO_URI` with the [MongoDB Atlas](https://www.mongodb.com/atlas)
   URI

5. **(Optional)** If you are using VS Code, please configure the Python Interpreter
    based on Virtual Environment. Read [here](https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters)

## Commands

All commands are run from the root of the project, from a terminal:

| Command              | Action                                         |
| -------------------- | ---------------------------------------------- |
| `pipenv install`     | Installs packages to virtual environment       |
| `pipenv run dev`     | Starts local dev server at `0.0.0.0:8000`      |
| `pipenv run start`   | Creates a production server at `0.0.0.0:8000`  |

Check the [`pipenv`](https://pipenv.pypa.io/en/latest/cli.html) docs for more commands

Checkout the [Wiki](https://github.com/theDS3/Datathon-Leaderboard/wiki) for details about build images and other topics
