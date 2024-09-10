import pandas as pd
import numpy as np
from datetime import time
from data.etl import Feeder
pd.options.mode.copy_on_write = True


class RunningFeeder(Feeder):
    def __init__(self, tables, id, user_id):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'running'

    def process(self):
        self.tables = {
                'workout': self.records,
                'lap': self.laps,
                'syn': self.syn
        }

    @property
    def records(self):
        return self._process_records()

    @property
    def laps(self):
        return self._process_laps()

    @property
    def syn(self):
        return self._get_wkt_syn()

    def _process_laps(self) -> str:
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

        return laps

    def _process_records(self):
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
        return records

    def _get_wkt_syn(self):
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
        return syn


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
