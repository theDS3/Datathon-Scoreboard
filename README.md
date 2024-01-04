# Datathon-Leaderboard

Creates a server to update DS3 Datathon Leaderboard using Kaggle Leaderboard

## Local Setup

1. Create a virtual environment using `virtualenv`

    ```bash
    virtualenv <env-name>
    ```

2. Start the virtual environment


    ```bash
    source <env-name>/bin/activate
    ```

3. Install the packages listed in the `requirements.txt`

    ```bash
    pip install -r requirements.txt
    ```

3. Copy the `.env.example` to `.env`

    ```bash
    cp .env.example .env
    ```

4. Replace the `KAGGLE_USERNAME` and `KAGGLE_KEY` with those from the Kaggle and optionally replace the `MONGO_URI` if you have the database running elsewhere

5. Run the following command export these environmental variables and verify if they exist in the output

    ```bash
    export $(cat .env | xargs) && env
    ```

6. Run the server using this command

    ```bash
    uvicorn main:app --reload
    ```