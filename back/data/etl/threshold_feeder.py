import pandas as pd
from back.data.etl import Feeder
from back.api_model import ThresholdModel
from back.utils.utilities import speed_to_pace


class ThresholdFeeder(Feeder):
    def __init__(self, threshold: ThresholdModel):
        self.user_id = threshold.user_id
        self.schema = 'param'
        self.threshold = threshold
        super().__init__({})

    def process(self):
        self.tables_processed = {
                'user_threshold': self.process_threshold(),
                'cycling_zone': self.process_bike_zone(),
                'run_zone': self.process_run_zone()
        }

    def process_threshold(self):
        threshold = self.threshold.dict()
        threshold['vma'] *= 0.90
        return pd.DataFrame([threshold])

    def process_run_zone(self):
        vma = self.threshold.vma
        threshold_pace = speed_to_pace(vma, ms=False) / 0.85
        print(threshold_pace)
        zone = {
            'recovery': threshold_pace / 0.85,
            'endurance': threshold_pace / 0.89,
            'tempo': threshold_pace / 0.95,
            'threshold': threshold_pace / 1.,
            'vo2max': threshold_pace / 1.1,
        }
        return pd.DataFrame([zone])

    def process_bike_zone(self):
        ftp = self.threshold.ftp
        zone = {
            'recovery': int(ftp * 0.55),
            'endurance': int(ftp * 0.75),
            'tempo': int(ftp * 0.90),
            'threshold': int(ftp * 1.05),
            'vo2max': int(ftp * 1.20),
        }

        return pd.DataFrame([zone])
