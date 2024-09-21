import pandas as pd
from back.data.connexion import DatabaseConnection
from back.utils.logger import ConsoleLogger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class Feeder:
    def __init__(self, tables: dict, activity_id: int = None):
        self.tables = tables
        self.activity_id = activity_id
        self.logger = ConsoleLogger(f'{self.__class__.__name__} User: {self.user_id}')

    def compute(self):
        self._step(self.process, 'Processing')
        self._step(self.put, 'Writting')

    def _step(self, func: callable, message: str):
        self.logger.info(f'{message.upper()}...')
        func()
        self.logger.info(f'{message.upper()} done')

    def process(self):
        pass

    def get(self, table, **kwargs):
        with DatabaseConnection() as engine:
            query = f"select * from {table}"

            if kwargs:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query += f" WHERE {conditions}"
            params = tuple(kwargs.values())

            return pd.read_sql(query, engine, params=params)

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
                    self.logger.info(f'INSERTING IN {self.schema}.{table_name}: {len(table)} rows')
                except IntegrityError as e:
                    self.logger.error(f"An error occurred: {e}")
                    return None
                except SQLAlchemyError as e:
                    self.logger.error(f"An error occurred: {e}")
                    return None
        return "Upload competed"
