import pandas as pd
from data.etl import Feeder
from api_model import ThresholdModel


class ThresholdFeeder(Feeder):
    def __init__(self, threshold: ThresholdModel, user_id):
        self.schema = 'param'
        self.threshold = threshold
        self.user_id = user_id
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
        zone = {
            'recovery': round(vma * 0.55, 2),
            'endurance': round(vma * 0.65, 2),
            'tempo': round(vma * 0.80, 2),
            'threshold': round(vma * 0.90, 2),
            'vo2max': round(vma * 1.2, 2),
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
