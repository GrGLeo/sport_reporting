from datetime import timedelta
import pandas as pd


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


class User:
    def __init__(self, user_id, conn):
        self.user_id = user_id
        self.conn = conn

    def _get_activity(self, table, wkt_id=None):
        query = f"""
            SELECT *
            FROM {table}
            WHERE user_id = :user_id
            """
        params = {'table': table, 'user_id': self.user_id}
        if wkt_id:
            query += 'activity_id = :wkt_id'
            params['activity_id'] = wkt_id
        return self.conn.query(query, params=params)

    def get_calendar(self):
        syn_run = self._get_activity('running.syn')
        syn_run = self._prep_calendar(syn_run, 'run')
        syn_cycling = self._get_activity('cycling.syn')
        syn_cycling = self._prep_calendar(syn_cycling, 'cyling')
        total = pd.concat([syn_run, syn_cycling], axis=0)
        return total

    def get_events(self):
        query = """
        SELECT date, name, sport, priority
        FROM param.events
        WHERE user_id = :user_id
        ORDER BY priority
        """
        params = {"user_id": self.user_id}
        return self.conn.query(query, params=params)

    def get_threshold(self):
        pass

    def _prep_calendar(self, data, sport):
        cols = ['activity_id', 'date', 'duration']
        data = data[cols]
        data['title'] = sport
        data['end'] = data.apply(lambda row: row['date'] + time_to_timedelta(row['duration']), axis=1)
        return data
