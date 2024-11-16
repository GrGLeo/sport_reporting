import os
from fastapi import APIRouter, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from back.endpoints.auth import authorize_user
from back.utils.query import Query
from back.api_model import QueryModel


db_router = APIRouter(prefix="/query")
DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")


conn = create_engine("postgresql://" + DB_URL)
Session = sessionmaker(conn)
session = Session()


@db_router.get("/simple_query/")
async def simple_query(param: QueryModel, user_id: int = Depends(authorize_user)):
    query = Query(user_id, conn)
    param = {k: v for k, v in param.model_dump().items() if v is not None}
    data = query.get_query(**param)
    return data
