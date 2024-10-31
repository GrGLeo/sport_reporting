from fastapi import APIRouter, HTTPException, Header
from sqlalchemy import text
from back.api_model import PostCommentModel
from back.endpoints.auth import retrieve_user_id
from back.utils.logger import logger
from back.endpoints.db_query import conn
from back.data.etl.comment_feeder import CommentFeeder


comment_router = APIRouter(prefix="/comments")


@comment_router.post("/post_comment/")
async def post_comment(comment: PostCommentModel, authorization: str = Header(None)):
    user_id = retrieve_user_id(authorization)
    if len(comment.comment_text.strip()) == 0:
        logger.warning("Empty comment")
        raise HTTPException(status_code=400, detail="Comment can not be empty")
    try:
        comment_feeder = CommentFeeder(comment, user_id)
        comment_feeder.compute()
    except Exception as e:
        logger.error(e)
        pass


@comment_router.get("/get_comments/")
async def get_comment(activity_id):
    query = text(f'select comment from param.activity_comments where activity_id = {activity_id} order by comment_id')
    params = {'activity_id': activity_id}
    with conn.connect() as connection:
        result = connection.execute(query, params)
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        return {"data": rows}
