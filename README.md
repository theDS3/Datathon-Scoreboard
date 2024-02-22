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

6. Update `kaggle` in [requirements.txt](https://github.com/theDS3/Datathon-Leaderboard/blob/29fa60133147bd99534644b3ff8807e0c1021ce9/requirements.txt#L19)

    - Update the Raw GitHub Link to the wheel file path **OR**
    - Run the below command with `VERSION_NUMBER` inserted from the wheel file

        ```bash
        sed -i 's/-\([0-9]\.\)\{2\}[0-9]\{1,2\}-/-VERSION_NUMBER-/g' requirements.txt
        ```

7. Merge new changes to `main` branch

## Build Image

As part of deploying the service, we create a docker image and push it to [DockerHub](https://hub.docker.com/r/devds3/leaderboard)

The image can be built either locally or via the recommended method of using
[Github Actions](https://github.com/theDS3/Datathon-Leaderboard/actions/workflows/build.yml).
To build it manually, follow the below steps:

1. Create a `requirements.txt` which describes the specific packages used

    ```bash
    PIPENV_DONT_LOAD_ENV=1 pipenv requirements > requirements.txt
    ```

2. Create the Docker Image, provided a specific tag using SemVer.

    ```bash
    docker build -t devds3/leaderboard:$(git rev-parse HEAD) .
    ```

3. Test the Image

4. Push Image to DockerHub and remove `requirements.txt`

## Update Non-Public Leaderboard

To push `private` and `final` standings, you will be making use the
[leaderboard.py](https://github.com/theDS3/Datathon-Leaderboard/tree/main/src/leaderboard.py).
Read the below subsections for requirements.

```bash
usage: leaderboard.py [-h] [-p] type

Create Private & Final Leaderboard Entry

positional arguments:
  type           Leaderboard Entry Type

options:
  -h, --help     show this help message and exit
  -p, --publish  Publish the latest standing

Update Datathon Leaderboard
```

### For Private Leaderboard

#### Folder Structure

```txt
data
├── private
│   ├── *.csv
```

#### Steps

1. Create a folder called `private` inside folder `data` to contain multiple CSV
2. Download from Kaggle the Private Leaderboard CSV's and place it here
3. Each of these CSV require the following headers: `Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames`
4. To view the latest standings:

    ```bash
    python src/leaderboard.py private
    ```

5. To publish the latest standings:

    ```bash
    python src/leaderboard.py private --publish
    ```

### For Final Leaderboard

#### Folder Structure

```txt
data
├── final
│   ├── mapping.csv
│   ├── bonus
│   │   ├── *.csv
├── private
│   ├── *.csv
```

#### Steps

1. Create a folder called `private` inside folder `data` to contain multiple CSV
2. Download from Kaggle the Private Leaderboard CSV's and place it here
3. Each of these CSV require the following headers: `Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames`
4. Create a folder called `bonus` inside folder `data/final` to contain multiple
CSV
5. Load each CSV containing the attendance of participants at in-person events
6. Each of these CSV require the following headers: `Email`
7. Create a file called `mapping.csv` with the following headers:
`Email,Team,Team Size`

    - It is a mapping that contains all participants and the teams they belong to

8. To view the latest standings:

    ```bash
    python src/leaderboard.py final
    ```

9. To publish the latest standings:

    ```bash
    python src/leaderboard.py final --publish
    ```
