from sqlalchemy import text


def create_schema(engine, schemas):
    with engine.connect() as connection:
        for schema in schemas:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            print(f"{schema} created")
