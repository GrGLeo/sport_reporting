import psycopg2
from psycopg2 import OperationalError
from sqlalchemy import create_engine


def create_connection():
    # TODO: don't hardcode that!
    db_name = "sporting"
    db_user = "leo"
    db_password = "postgres"
    db_host = "127.0.0.1"
    db_port = "5432"

    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Connection to PostgreSQL DB successful")
        return connection

    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None


def create_session():
    pg_connection = create_connection()

    if pg_connection:
        engine = create_engine(
            'postgresql+psycopg2://',
            creator=lambda: pg_connection
        )

        return engine
