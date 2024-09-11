import pytest
import pandas as pd
from back.api_model import CommentModel
from back.data.etl.comment_feeder import CommentFeeder


def test_sanitize_comment():
    comment = CommentModel(user_id=1, activity_id=1, comment_text= "<script>alert('hack');</script>")
    feeder = CommentFeeder(comment)

    sanitized = feeder._sanitize_comment(comment.comment_text)

    assert sanitized == "&lt;script&gt;alert('hack');&lt;/script&gt;"
    

def test_process_comment():
    comment = CommentModel(user_id=1, activity_id=1, comment_text="This is a test comment!")
    feeder = CommentFeeder(comment)

    feeder.process()

    assert 'comment' in feeder.tables  # Ensure the 'comment' table exists
    assert isinstance(feeder.tables['comment'], pd.DataFrame)
    assert feeder.tables['comment'].iloc[0]['comment'] == "This is a test comment!"
