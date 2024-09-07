import pandas as pd
import bleach
from data.etl.feeder import Feeder


class CommentFeeder(Feeder):
    def __init__(self, tables, id, user_id, put: bool = True):
        super().__init__(tables, id)
        self.user_id = user_id
        self.schema = 'param'
        self._sanitize_comment()

        if put:
            df_comment = self.to_df()
            self.completion = self.put(df_comment, "comment")

    def to_df(self):
        return pd.DataFrame([self.tables])

    def _sanitize_comment(self):
        return bleach.clean(self.tables["comment"])
