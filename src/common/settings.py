import os
from dotenv import load_dotenv


load_dotenv()


def get_sql_url():
    return "postgresql+{}://{}:{}@{}:{}/{}".format(
        os.getenv("POSTGRES_ENGINE"),
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_HOST"),
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_DB"),
    )
