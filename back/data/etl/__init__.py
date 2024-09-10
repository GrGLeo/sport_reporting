from data.connexion import DatabaseConnection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class Feeder:
    def __init__(self, tables: dict, activity_id: int = None):
        self.tables = tables
        self.user_id = None
        self.activity_id = activity_id

    def put(self):
        with DatabaseConnection() as engine:
            for table_name, table in self.tables.items():
                if self.user_id:
                    table['activity_id'] = self.user_id
                if self.activity_id:
                    table['activity_id'] = self.activity_id
                try:
                    table.to_sql(
                        table_name,
                        schema=self.schema,
                        con=engine,
                        if_exists='append',
                        index=False
                    )
                    print(f'Inserted {len(table)} rows')
                    return "Upload completed"
                except IntegrityError:
                    return "Activity already uploaded"
                except SQLAlchemyError as e:
                    # Generic SQL error handling
                    print(f"An error occurred: {e}")
                    return "An error occurred during the upload"
