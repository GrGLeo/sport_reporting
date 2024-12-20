from pydantic import BaseModel, FutureDate
from typing import Optional
from datetime import date


class LoginModel(BaseModel):
    username: str
    password: str


class UserModel(BaseModel):
    username: str
    password: str
    email: str


class PostCommentModel(BaseModel):
    activity_id: int
    comment_text: str


class RpeModel(BaseModel):
    activity_id: int
    sport: str
    rpe: int


class EventModel(BaseModel):
    date: FutureDate
    name: str
    sport: str
    priority: str


class ThresholdModel(BaseModel):
    date: date
    swim: int
    ftp: int
    vma: float


class FuturWktModel(BaseModel):
    name: str
    date: date
    sport: str
    data: dict


class GenerateWktModel(BaseModel):
    target: str
    date: date
    sport: str


class QueryModel(BaseModel):
    table: str
    select: str
    wkt_id: Optional[int] = None
    order: Optional[str] = None
    limit: Optional[int] = None
