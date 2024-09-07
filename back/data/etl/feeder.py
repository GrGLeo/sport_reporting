from data.connexion import create_connection, create_session
from sqlalchemy.exc import IntegrityError


class Feeder:
    def __init__(self, tables: dict, id: int):
        self.tables = tables
        self.id = id
        self.connection = create_connection()
        self.engine = create_session()

    def put(self, table, table_name):
        table['user_id'] = self.user_id
        table['activity_id'] = self.id

        try:
            table.to_sql(
                table_name,
                schema=self.schema,
                con=self.engine,
                if_exists='append',
                index=False
            )
            print(f'Inserted {len(table)} rows')
            return "Upload completed"

        except IntegrityError:
            return "Activity already uploaded"
