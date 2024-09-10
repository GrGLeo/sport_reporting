from data.etl import Feeder
from api_model import EventModel
import pandas as pd


class EventFeeder(Feeder):
    def __init__(self, event: EventModel):
        super().__init__({}, None)
        self.user_id = event.user_id
        self.event = event.dict()
        self.schema = 'param'

    def process(self):
        data = pd.DataFrame([self.event])
        self.tales = {'events': data}
