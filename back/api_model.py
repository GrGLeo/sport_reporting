from pydantic import BaseModel, FutureDate


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
