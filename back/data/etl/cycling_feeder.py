from datetime import time

import pandas as pd

from data.etl.activity_feeder import ActivityFeeder
from utils.utilities import assign_zone, seconds_to_time

pd.options.mode.copy_on_write = True


class CyclingFeeder(ActivityFeeder):
    def __init__(self, tables, activity_id, user_id):
        super().__init__(tables, activity_id, user_id)
        self.schema = "cycling"

    def _process_records(self):
        records = self.tables["record_cycling"]
        records["enhanced_altitude"] = 0

        cols = {
            "timestamp": "timestamp",
            "distance": "distance",
            "heart_rate": "hr",
            "cadence": "cadence",
            "power": "power",
            "speed": "speed",
            "enhanced_altitude": "altitude",
        }

        # Handling missing altitude on indoor wkt
        try:
            records.drop("altitude", axis=1, inplace=True)
        except KeyError:
            pass

        records.rename(cols, axis=1, inplace=True)
        if "heart_rate" not in records.columns:
            records["hr"] = None

        records = records[cols.values()]

        # get the associated zone
        zones = self.get("param.cycling_zone", user_id=self.user_id)
        zones = zones.drop(columns="user_id")
        zones = zones.iloc[0].to_dict()
        records["zone"] = records["power"].apply(lambda x: assign_zone(x, zones))
        records["record_id"] = records.index
        records["speed"] = (records["speed"] * 3600) / 1000

        # calculate the Normalized Power
        records["norm_power"] = records["power"].rolling(window=30).mean()
        records["norm_power"] = records["norm_power"] ** 4
        records["norm_power"] = records["norm_power"].expanding(min_periods=1).mean()
        records["norm_power"] = records["norm_power"] ** 0.25
        records["norm_power"] = records["norm_power"].round()
        return records

    def _process_laps(self):
        laps = self.tables["lap_cycling"]
        laps["lap_id"] = laps.index
        cols = {
            "lap_id": "lap_id",
            "total_timer_time": "timer",
            "total_distance": "distance",
            "avg_heart_rate": "hr",
            "avg_speed": "speed",
            "avg_cadence": "cadence",
            "avg_power": "power",
            "normalized_power": "norm_power",
        }

        laps.rename(cols, axis=1, inplace=True)
        if "avg_heart_rate" not in laps.columns:
            laps["hr"] = None

        laps = laps[cols.values()]
        laps["timer"] = laps["timer"].apply(lambda x: seconds_to_time(int(x)))
        laps["speed"] = (laps["speed"] * 3600) / 1000
        return laps

    def _get_wkt_syn(self):
        syn = pd.DataFrame(index=range(1))
        records = self.records
        syn["date"] = records["timestamp"].iloc[0]
        duration = len(records)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        time_duration = time(hour=hours, minute=minutes, second=seconds)
        syn["duration"] = time_duration
        syn["avg_cadence"] = records["cadence"].mean()
        if "hr" in records.columns:
            syn["avg_hr"] = records["hr"].mean()
        else:
            syn["avg_hr"] = None
        syn["avg_speed"] = records["speed"].mean()

        # Calculate workout TSS
        threshold = self.get("param.user_threshold", user_id=self.user_id)
        threshold.sort_values("date", ascending=False)
        ftp = threshold["ftp"].iloc[0]
        np = records["norm_power"].iloc[-1]
        tss = (duration * np * (np / ftp)) / (ftp * 3600) * 100
        syn["tss"] = tss

        # Calculate the time spent in zone
        zones = records.groupby("zone").size().reset_index(name="count")
        zones["count"] = zones["count"].astype(int)
        zones = zones.pivot_table(
            index=None, columns="zone", values="count", fill_value=0
        )
        zones = zones.reset_index(drop=True)
        syn = pd.concat([syn, zones], axis=1)
        #
        distance = records["distance"].iloc[-1]
        syn["distance"] = distance
        return syn
