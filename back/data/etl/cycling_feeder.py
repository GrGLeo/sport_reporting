from back.data.etl import Feeder


class CyclingFeeder(Feeder):
    def __init__(self, tables, id, user_id):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'cycling'

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

    def _process_records(self):
        records = self.tables["record_running"]
        records['enhanced_altitude'] = 0

        cols = {
            'timestamp': 'timestamp',
            'distance': 'distance',
            'heart_rate': 'hr',
            'cadence': 'cadence',
            'power': 'power',
            'speed': 'speed',
            'enhanced_altitude': 'altitude'
        }

        records.rename(
                cols,
                axis=1,
                inplace=True
        )
        records = records[cols.values()]
        records['speed'] = (records['speed'] * 3600) / 1000
        records['norm_power'] = records['power'].rolling(window=30).mean()
        records['norm_power'] = records['norm_power'] ** 4
        records['norm_power'] = records['norm_power'].rolling(window=30, min_periods=1).mean()
        records['norm_power'] = records['norm_power'] ** 0.25
        records['norm_power'] = records['norm_power'].round()
        return records

    def _process_laps(self):
        pass
