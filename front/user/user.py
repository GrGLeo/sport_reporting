import os
from datetime import timedelta, datetime
import requests
import pandas as pd
from utils import time_to_timedelta, time_to_seconds


class User:
    API = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000")

    GET_TABLE_QUERY = """
        SELECT *
        FROM {table}
        WHERE user_id = :user_id
    """
    GET_EVENTS_QUERY = """
        SELECT date, name, sport, priority
        FROM param.events
        WHERE user_id = :user_id
        ORDER BY priority
    """

    def __init__(self, token, conn):
        self.token = token
        self.conn = conn

    def get_calendar(self) -> pd.DataFrame:
        syn_run = self._get_query('running.syn')
        if not syn_run.empty:
            syn_run = self._prep_calendar(syn_run, 'running')
        syn_cycling = self._get_query('cycling.syn')
        if not syn_cycling.empty:
            syn_cycling = self._prep_calendar(syn_cycling, 'cycling')
        return pd.concat([syn_run, syn_cycling], axis=0)

    def get_planned_wkt(self) -> pd.DataFrame:
        ftr_wkt = self._get_query('planning.workout')
        return ftr_wkt

    def get_analysis(self, schema: str, wkt_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_laps = self._get_query(f'{schema}.lap', wkt_id=wkt_id).drop(['activity_id', 'user_id', 'lap_id'], axis=1)
        df_laps['distance'] = (df_laps['distance'] / 1000).round(2)

        df_zones = self._get_query(f'{schema}.syn', wkt_id=wkt_id)
        duration = time_to_seconds(df_zones.iloc[0]['duration'])
        df_zones = df_zones[['recovery', 'endurance', 'tempo', 'threshold', 'vo2max']]
        for col in df_zones.columns:
            df_zones[col] = round(df_zones[col] / duration * 100, 2)

        df_records = self._get_query(f'{schema}.workout', wkt_id=wkt_id)

        return df_laps, df_zones, df_records

    def get_events(self) -> pd.DataFrame:
        return self._get_query("param.events", select="date, name, sport, priority", order_by="priority")

    def get_full_workouts(self) -> pd.DataFrame:
        syn_run = self._get_query('running.syn')
        syn_run['sport'] = 'running'
        syn_cycling = self._get_query('cycling.syn')
        syn_cycling['sport'] = 'cycling'
        total = pd.concat([syn_run, syn_cycling], axis=0)

        total = self._process_duration(total)
        date_range = pd.date_range(start=datetime.today() - timedelta(days=92), end=datetime.today())
        date_range = date_range.strftime('%Y-%m-%d')
        df = pd.DataFrame({'date': date_range})

        return df.merge(total, on='date', how='left')

    def get_threshold(self, past: bool = False) -> pd.DataFrame:
        limit = 2 if past else 1
        return self._get_query('param.user_threshold', order_by='date DESC', limit=limit)

    def update_threshold(self, threshold: dict) -> None:
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{self.API}/threshold/", json=threshold, headers=headers)
        response.raise_for_status()

    def push_programmed_wkt(self, wkt_date, sport, wkt, name):
        full_data = {}
        full_data['user_id'] = self.user_id
        full_data['name'] = name
        full_data['date'] = wkt_date.strftime('%Y-%m-%d')
        full_data['sport'] = sport
        full_data['data'] = wkt
        response = requests.post(f"{self.API}/push_program_wkt/", json=full_data)
        response.raise_for_status()
        return True

    def get_programmed_wkt(self, activity_id):
        res = self._get_query('planning.workout', wkt_id=activity_id)
        return res

    def get_zones(self) -> tuple[pd.DataFrame]:
        run_zone = self._get_zone('run_zone')
        cycling_zone = self._get_zone('cycling_zone')
        return (cycling_zone, run_zone)

    def _get_zone(self, sport: str) -> pd.DataFrame:
        return self._get_query(f'param.{sport}')

    def _get_query(self, table: str, select: str = "*", wkt_id: int = None, order_by: str = None, limit: int = None) -> pd.DataFrame:
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "table": str(table),
            "select": "*",
        }

        if wkt_id:
            params['wkt_id'] = wkt_id
        if order_by:
            params['order'] = order_by
        if limit:
            params['limit'] = str(limit)

        response = requests.get(f"{self.API}/query/simple_query/", headers=headers, json=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data["data"])
            for col in df.columns:
                dt_ = ["date", "timestamp", "duration", "timer"]
                if col in dt_:
                    df[col] = pd.to_datetime(df[col])
            return df

    def _prep_calendar(self, data: pd.DataFrame, sport: str) -> pd.DataFrame:
        cols = ['activity_id', 'date', 'duration']
        data = data[cols]
        data['title'] = sport
        data['end'] = data.apply(lambda row: row['date'] + time_to_timedelta(row['duration']), axis=1)
        return data

    def _process_duration(self, total: pd.DataFrame) -> pd.DataFrame:
        total['week'] = total['date'].dt.isocalendar().week
        total['hour'] = total['duration'].apply(lambda x: x.hour)
        total['minute'] = total['duration'].apply(lambda x: x.minute)
        total['duration'] = total['hour'] * 60 + total['minute']
        total['date'] = total['date'].dt.strftime('%Y-%m-%d')
        return total
