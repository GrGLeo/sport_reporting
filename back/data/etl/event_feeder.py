from data.etl import Feeder
from api_model import EventModel
import pandas as pd


class EventFeeder(Feeder):
    def __init__(self, event: EventModel, user_id: int):
        self.user_id = user_id
        self.event = event.model_dump()
        super().__init__({}, None)
        self.schema = 'param'

    def process(self):
        data = pd.DataFrame([self.event])
        self.tables_processed = {'events': data}
