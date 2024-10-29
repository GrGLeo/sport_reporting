from fastapi import APIRouter, HTTPException, Header
from back.api_model import CommentModel
from back.endpoints.auth import retrieve_user_id
from back.utils.logger import logger
from back.data.etl.comment_feeder import CommentFeeder


comment_router = APIRouter(prefix="/comments")


@comment_router.post("/post_comment/")
async def post_comment(comment: CommentModel, authorization: str = Header(None)):
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


@comment_router.get("/get_comment")
async def get_comment():
    pass
