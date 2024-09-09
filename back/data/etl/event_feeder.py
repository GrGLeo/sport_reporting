from data.etl import Feeder


class EventFeeder(Feeder):
    def __init__(self, tables: dict, user_id, id=None):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'param'

    def process(self):
        print(self.tables)
        pass
