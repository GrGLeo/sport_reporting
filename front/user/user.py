from datetime import timedelta, datetime
import requests
import pandas as pd


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


class User:
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

    def __init__(self, user_id: int, conn):
        self.user_id = user_id
        self.conn = conn

    def get_calendar(self) -> pd.DataFrame:
        syn_run = self.__get_query('running.syn')
        syn_run = self.__prep_calendar(syn_run, 'running')
        syn_cycling = self.__get_query('cycling.syn')
        syn_cycling = self.__prep_calendar(syn_cycling, 'cycling')
        return pd.concat([syn_run, syn_cycling], axis=0)

    def get_analysis(self, schema: str, wkt_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_laps = self.__get_query(f'{schema}.lap', wkt_id).drop(['activity_id', 'user_id', 'lap_id'], axis=1)
        df_laps['distance'] = (df_laps['distance'] / 1000).round(2)

        df_records = self.__get_query(f'{schema}.workout', wkt_id)
        return df_laps, df_records

    def get_events(self) -> pd.DataFrame:
        params = {"user_id": self.user_id}
        return self.conn.query(self.GET_EVENTS_QUERY, params=params)

    def get_full_workouts(self) -> pd.DataFrame:
        syn_run = self.__get_query('running.syn')
        syn_cycling = self.__get_query('cycling.syn')
        total = pd.concat([syn_run, syn_cycling], axis=0)

        total = self._process_duration(total)
        date_range = pd.date_range(start=datetime.today() - timedelta(days=92), end=datetime.today())
        date_range = date_range.strftime('%Y-%m-%d')
        df = pd.DataFrame({'date': date_range})

        return df.merge(total, on='date', how='left')

    def get_threshold(self, past: bool = False) -> pd.DataFrame:
        limit = 2 if past else 1
        return self.__get_query('param.user_threshold', order_by='date DESC', limit=limit)

    def update_threshold(self, threshold: dict) -> None:
        threshold['user_id'] = self.user_id
        response = requests.post("http://127.0.0.1:8000/threshold/", json=threshold)
        response.raise_for_status()

    def get_zones(self) -> tuple[pd.DataFrame]:
        run_zone = self._get_zone('run_zone')
        cycling_zone = self._get_zone('cycling_zone')
        return (run_zone, cycling_zone)

    def _get_zone(self, sport: str) -> pd.DataFrame:
        return self.__get_query(f'param.{sport}')

    def __get_query(self, table: str, wkt_id: int = None, order_by: str = None, limit: int = None) -> pd.DataFrame:
        query = self.GET_TABLE_QUERY.format(table=table)
        params = {'user_id': self.user_id}

        if wkt_id:
            query += ' AND activity_id = :wkt_id'
            params['wkt_id'] = int(wkt_id)

        if order_by:
            query += f' ORDER BY {order_by}'

        if limit:
            query += f' LIMIT {limit}'

        query += ';'
        print(query)
        return self.conn.query(query, params=params)

    def __prep_calendar(self, data: pd.DataFrame, sport: str) -> pd.DataFrame:
        cols = ['activity_id', 'date', 'duration']
        data = data[cols]
        data['title'] = sport
        data['end'] = data.apply(lambda row: row['date'] + time_to_timedelta(row['duration']), axis=1)
        return data

    def _process_duration(self, total: pd.DataFrame) -> pd.DataFrame:
        total['week'] = total['date'].dt.isocalendar().week
        total['hour'] = total['duration'].apply(lambda x: x.hour)
        total['minute'] = total['duration'].apply(lambda x: x.minute)
        total['second'] = total['duration'].apply(lambda x: x.second)
        total['duration'] = total['hour'] * 3600 + total['minute'] * 60 + total['second']
        total['date'] = total['date'].dt.strftime('%Y-%m-%d')
        return total
