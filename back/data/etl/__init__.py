from abc import ABC, abstractmethod
import pandas as pd
from back.data.connexion import DatabaseConnection
from back.utils.logger import ConsoleLogger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class Feeder(ABC):
    def __init__(self, tables: dict[pd.DataFrame], activity_id: int = None):
        self.tables = tables
        self.activity_id = activity_id
        self.logger = ConsoleLogger(f'{self.__class__.__name__} User: {self.user_id}')

    def compute(self) -> None:
        self._step(self.process, 'Processing')
        self._step(self.put, 'Writting')

    def _step(self, func: callable, message: str) -> None:
        self.logger.info(f'{message.upper()}...')
        func()
        self.logger.info(f'{message.upper()} done')

    @abstractmethod
    def process(self):
        pass

    def get(self, table: str, **kwargs) -> pd.DataFrame:
        with DatabaseConnection() as engine:
            query = f"select * from {table}"

            if kwargs:
                conditions = " AND ".join([f"{k} = %s" for k in kwargs])
                query += f" WHERE {conditions}"
            params = tuple(kwargs.values())

            return pd.read_sql(query, engine, params=params)

    def put(self) -> str:
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

    def drop(self, tables: list[str]) -> None:
        with DatabaseConnection() as engine:
            for table in tables:
                drop_query = f"""
                DELETE {self.schema}.{table}
                """
                if self.user_id:
                    drop_query += f" WHERE user_id = {self.user_id}"
                if self.activity_id:
                    drop_query += f" AND activity_id = {self.activity_id}"
                engine.execute(drop_query)
