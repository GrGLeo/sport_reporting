import pandas as pd
from back.data.etl import Feeder
from back.api_model import ThresholdModel


class ThresholdFeeder(Feeder):
    def __init__(self, threshold: ThresholdModel):
        self.user_id = threshold.user_id
        self.schema = 'param'
        self.threshold = threshold
        super().__init__({})

    def process(self):
        print(self.process_threshold())
        print(self.process_bike_zone())
        pass

    def process_threshold(self):
        threshold = self.threshold.dict()
        return pd.DataFrame([threshold])

    def process_run_zone(self):
        pass

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
