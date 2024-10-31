from fastapi import APIRouter, HTTPException, Header
from sqlalchemy import text
from back.api_model import PostCommentModel, RpeModel
from back.endpoints.auth import retrieve_user_id
from back.utils.logger import logger
from back.endpoints.db_query import conn
from back.data.etl.comment_feeder import CommentFeeder


activity_router = APIRouter(prefix="/activity")


@activity_router.post("/post_comment/")
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


@activity_router.get("/get_comments/")
async def get_comment(activity_id):
    query = text(f'select comment from param.activity_comments where activity_id = {activity_id} order by comment_id')
    params = {'activity_id': activity_id}
    with conn.connect() as connection:
        result = connection.execute(query, params)
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        return {"data": rows}


@activity_router.post("/upsert_rpe/")
async def upsert_rpe(rpe: RpeModel, authorization: str = Header(None)):
    user_id = retrieve_user_id(authorization)
    activity = RpeModel.activity_id
    sport = RpeModel.sport


@activity_router.get("/{activity_id}/get_rpe/")
async def get_rpe(activity_id: int, sport: str):
    query = text(f"select rpe from {sport}.syn where activity_id = {activity_id}")
    with conn.connect() as connection:
        result = connection.execute(query)
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        return {"data": rows}
