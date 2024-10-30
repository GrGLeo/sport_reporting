import pandas as pd
import bleach
from back.data.etl import Feeder
from back.api_model import PostCommentModel


class CommentFeeder(Feeder):
    def __init__(self, comment: PostCommentModel, user_id: int):
        self.user_id = user_id
        self.text = comment.comment_text
        self.schema = 'param'
        super().__init__({}, comment.activity_id)

    def process(self):
        sanitized_comment = self._sanitize_comment(self.text)
        data = {
                'comment': sanitized_comment
        }
        self.tables_processed = {'activity_comments': pd.DataFrame([data])}

    def _sanitize_comment(self, text):
        return bleach.clean(text)
