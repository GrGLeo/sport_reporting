from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from back.api_model import PostCommentModel, RpeModel
from back.utils.logger import logger
from back.endpoints.db_query import conn
from back.data.etl.comment_feeder import CommentFeeder


activity_router = APIRouter(prefix="/activity")


def authorize_user():
    pass


@activity_router.post("/post_comment/")
async def post_comment(comment: PostCommentModel, user_id: int = Depends(authorize_user)):
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


@activity_router.post("/post_rpe/")
async def post_rpe(rpe: RpeModel, user_id: int = Depends(authorize_user)):
    activity = rpe.activity_id
    sport = rpe.sport
    rpe = rpe.rpe
    query = text(f"update {sport}.syn set rpe=:rpe  where activity_id = :activity_id and user_id=:user_id")
    params = {"activity_id": activity, "rpe": rpe, "user_id": user_id}
    with conn.connect() as connection:
        result = connection.execute(query, params)
        connection.commit()
    return {"status": "ok", "updated_rows": result.rowcount}


@activity_router.get("/{activity_id}/get_rpe/")
async def get_rpe(activity_id: int, sport: str):
    query = text(f"select rpe from {sport}.syn where activity_id = :activity_id")
    params = {'activity_id': activity_id}
    with conn.connect() as connection:
        result = connection.execute(query, params)
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        return {"data": rows}
