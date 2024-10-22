import os
from sqlalchemy import create_engine


DB_URL = os.getenv("DATABASE_URL")


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.engine = None

    def __enter__(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{DB_URL}',
        )
        return self.engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
        if exc_type:
            print(f"Exception occurred: {exc_val}")  # You could also log this.
        # Return False to propagate the exception, True to suppress it
        return False
