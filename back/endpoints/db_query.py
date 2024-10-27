import os
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import create_engine
from back.endpoints.auth import decode_jwt
from back.utils.query import Query
from back.api_model import QueryModel


db_router = APIRouter(prefix="/query")
DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")


conn = create_engine("postgresql://" + DB_URL)


@db_router.get("/simple_query/")
async def simple_query(param: QueryModel, authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    table = param.table
    select = param.select
    token = authorization.split(" ")[1]
    user_id = decode_jwt(token)
    queryer = Query(table, select, user_id, conn)
    data = queryer.get_query()
    return data
