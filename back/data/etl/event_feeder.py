from back.data.etl import Feeder
from back.api_model import EventModel
import pandas as pd


class EventFeeder(Feeder):
    def __init__(self, event: EventModel):
        self.user_id = event.user_id
        self.event = event.model_dump()
        super().__init__({}, None)
        self.schema = 'param'

    def process(self):
        data = pd.DataFrame([self.event])
        self.tables_processed = {'events': data}
