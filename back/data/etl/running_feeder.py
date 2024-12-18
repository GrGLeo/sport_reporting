import pandas as pd
import numpy as np
from datetime import time
from data.etl.activity_feeder import ActivityFeeder
from utils.utilities import seconds_to_time, assign_zone
pd.options.mode.copy_on_write = True


class RunningFeeder(ActivityFeeder):
    def __init__(self, tables, activity_id, user_id):
        super().__init__(tables, activity_id, user_id)
        self.schema = 'running'

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
        laps['pace'] = round((laps['pace'] * 3600) / 1000, 2)
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
        records.ffill(inplace=True)
        # TODO: better outlier replacement
        # records['pace'] = records['pace'].rolling(window=5).mean()
        records['pace'] = (records['pace'] * 3600) / 1000
        records['pace'] = np.where(records['pace'] < 3, 3, records['pace'])
        records['pace'] = records['pace'].round(2)

        # get the associated zone
        zones = self.get('param.run_zone', user_id=self.user_id)
        zones = zones.drop(columns='user_id')
        zones = zones.iloc[0].to_dict()
        records['zone'] = records['pace'].apply(lambda x: assign_zone(x, zones))

        return records

    def _get_wkt_syn(self):
        syn = pd.DataFrame(index=range(1))
        records = self._process_records()
        syn['date'] = records['timestamp'].iloc[0]

        # Calculate the duration of the workout
        duration = len(self.records)
        hours = duration//3600
        minutes = (duration % 3600)//60
        seconds = duration % 60
        duration = time(hour=hours, minute=minutes, second=seconds)
        syn['duration'] = duration
        syn['avg_hr'] = self.records['hr'].mean()

        # Get the average for the metrics
        syn['avg_pace'] = round(self.records['pace'].mean(), 2)
        syn['avg_cadence'] = self.records['cadence'].mean()
        distance = self.records['distance'].iloc[-1]
        syn['distance'] = distance
        syn['tss'] = int((distance / 1609) * 10)

        # Calculate the time spent in zone
        zones = records.groupby('zone').size().reset_index(name='count')
        zones['count'] = zones['count'].astype(int)
        zones = zones.pivot_table(index=None, columns='zone', values='count', fill_value=0)
        zones = zones.reset_index(drop=True)
        syn = pd.concat([syn, zones], axis=1)
        return syn
