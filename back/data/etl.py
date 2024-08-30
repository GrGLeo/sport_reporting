import pandas as pd
from sqlalchemy import inspect
from datetime import time
from data.tables import Base
from data.connexion import create_connection, create_session
pd.options.mode.copy_on_write = True


class Feeder:
    def __init__(self, tables: dict, id: int):
        self.tables = tables
        self.id = id
        self.connection = create_connection()
        self.engine = create_session()
        self._create_tables()

    def _create_tables(self):
        inspector = inspect(self.engine)
        Base.metadata.bind = self.engine
        created_tables = inspector.get_table_names()
        for table in self.tables:
            if table not in created_tables:
                Base.metadata.create_all(self.engine)
                print(f"Created table {table}")


class Running_Feeder(Feeder):
    def __init__(self, tables, id):
        super().__init__(tables, id)

    def process_laps(self):
        laps = self.tables["lap_running"]
        cols = {
            'message_index': 'lap_id',
            'total_timer_time': 'timer',
            'total_distance': 'distance',
            'avg_heart_rate': 'hr',
            'avg_running_cadence': 'cadence'
        }
        laps.rename(
            cols,
            axis=1,
            inplace=True
        )
        laps = laps[cols.values()]
        laps['activity_id'] = self.id
        laps['pace'] = laps['distance'] / laps['timer']
        laps['pace'] = laps['pace'].apply(speed_to_pace)
        laps['timer'] = laps['timer'].apply(lambda x: seconds_to_time(int(x)))
        laps.to_sql('lap_running', con=self.engine, if_exists='append', index=False)
        print(f'Inserted {len(laps)} rows')


def speed_to_pace(speed):
    if speed == 0:
        return float("inf")
    pace = (1000 / (speed * 60))
    return round(pace, 2)


def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)
