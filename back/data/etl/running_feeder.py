import pandas as pd
import numpy as np
from datetime import time
from data.connexion import create_connection, create_session
from sqlalchemy.exc import IntegrityError
pd.options.mode.copy_on_write = True


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


class Running_Feeder(Feeder):
    def __init__(self, tables, id, user_id):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'running'

    def process_laps(self) -> str:
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
        laps['pace'] = laps['distance'] / laps['timer']
        laps['pace'] = laps['pace'].apply(speed_to_pace)
        laps['timer'] = laps['timer'].apply(lambda x: seconds_to_time(int(x)))
        print(laps.head())

        completion = self.put(laps, 'lap')
        return completion

    def process_records(self):
        records = self.tables["record_running"]
        cols = {
            'timestamp': 'timestamp',
            'distance': 'distance',
            'position_lat': 'lat',
            'position_long': 'lon',
            'heart_rate': 'hr',
            'cadence': 'cadence',
            'enhanced_speed': 'pace',
            'enhanced_altitude': 'altitude'
        }

        records.rename(
                cols,
                axis=1,
                inplace=True
        )
        records = records[cols.values()]
        records['record_id'] = records.index
        records['pace'] = records['pace'].apply(speed_to_pace)
        records['pace'] = records['pace'].rolling(window=5).mean()
        records['pace'] = np.where(records['pace'] > 12, 10, records['pace'])
        records['pace'] = records['pace'].round(2)
        self.records = records
        self.put(records, 'workout')

    def get_wkt_syn(self):
        syn = pd.DataFrame(index=range(1))
        syn['date'] = self.records['timestamp'].iloc[0]
        duration = len(self.records)
        hours = duration//3600
        minutes = (duration % 3600)//60
        seconds = duration % 60
        duration = time(hour=hours, minute=minutes, second=seconds)
        syn['duration'] = duration
        syn['avg_hr'] = self.records['hr'].mean()
        syn['avg_pace'] = self.records['pace'].mean().round(2)
        syn['avg_cadence'] = self.records['cadence'].mean()
        distance = self.records['distance'].iloc[-1]
        syn['distance'] = distance
        syn['tss'] = int((distance / 1609) * 10)
        self.put(syn, 'syn')


def speed_to_pace(speed):
    if speed == 0:
        return float("inf")
    pace = (1000 / (speed * 60))
    minutes = int(pace)
    seconds = int(round((pace - minutes) * 60))
    return round(minutes + (seconds / 100), 2)


def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)
