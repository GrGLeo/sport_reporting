from pydantic import BaseModel, FutureDate
from datetime import date

class LoginModel(BaseModel):
    username: str
    password: str


class UserModel(BaseModel):
    username: str
    password: str
    email: str


class CommentModel(BaseModel):
    activity_id: int
    user_id: int
    comment_text: str


class EventModel(BaseModel):
    user_id: int
    date: FutureDate
    name: str
    sport: str
    priority: str


class ThresholdModel(BaseModel):
    user_id: int
    date: date
    swim: int
    ftp: int
    vma: float
