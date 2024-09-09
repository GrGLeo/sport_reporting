import pandas as pd
import bleach
from data.etl import Feeder


class CommentFeeder(Feeder):
    def __init__(self, tables, id, user_id, put: bool = True):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'param'

        print(self.process())
        if put:
            df_comment = self.process()
            print(df_comment)
            self.completion = self.put(df_comment, "comment")

    def process(self):
        self.tables["comment"] = self._sanitize_comment()
        return pd.DataFrame([self.tables])

    def _sanitize_comment(self):
        return bleach.clean(self.tables["comment"])
