import pandas as pd
import bleach
from data.etl import Feeder
from api_model import CommentModel


class CommentFeeder(Feeder):
    def __init__(self, comment: CommentModel):
        super().__init__({}, comment.activity_id)
        self.comment = comment
        self.schema = 'param'
        print(self.activity_id)

    def process(self):
        sanitized_comment = self._sanitize_comment(self.comment.comment_text)
        data = {
                'activity_id': self.activity_id,
                'user_id': self.comment.user_id,
                'comment': sanitized_comment
        }
        self.tables = {'comment': pd.DataFrame([data])}

    def _sanitize_comment(self, text):
        return bleach.clean(text)
