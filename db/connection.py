import psycopg
from sqlalchemy import create_engine

DB_NAME = "transport"
DB_HOST = "127.0.0.1"
DB_PORT = 5433
DB_USER = "postgres"
DB_PASSWORD = "postgres"


def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


engine = create_engine(
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)