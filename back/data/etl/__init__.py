from back.data.connexion import DatabaseConnection
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class Feeder:
    def __init__(self, tables: dict, activity_id: int = None):
        self.tables = tables
        self.user_id = None
        self.activity_id = activity_id

    def compute(self):
        self._step(self.process, 'Processing')
        self._step(self.put, 'Writting')

    def _step(self, func: callable, message: str):
        print(message)
        func()

    def process(self):
        pass

    def put(self):
        with DatabaseConnection() as engine:
            for table_name, table in self.tables_processed.items():
                if self.user_id:
                    table['user_id'] = self.user_id
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
                except IntegrityError as e:
                    print(f"An error occurred: {e}")
                    return None
                except SQLAlchemyError as e:
                    # Generic SQL error handling
                    print(f"An error occurred: {e}")
                    return None
        return "Upload competed"
