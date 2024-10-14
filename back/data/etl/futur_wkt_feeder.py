import json
from back.data.etl import Feeder
from back.api_model import FuturWktModel
import pandas as pd


class FuturWorkoutFeeder(Feeder):
    def __init__(self, futur_wkt: FuturWktModel):
        self.user_id = futur_wkt.user_id
        self.futur_wkt = futur_wkt.model_dump()
        super().__init__({}, None)
        self.schema = 'planning'

    def process(self):
        data = pd.DataFrame([self.futur_wkt])
        data['data'] = data['data'].apply(json.dumps)
        self.tables_processed = {'workout': data}
