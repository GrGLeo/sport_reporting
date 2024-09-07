from pydantic import BaseModel, constr, validator


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
    #comment_text: constr(min_length=1, max_length=300)

    #@validator('comment_text')
    #def no_empty_comment(cls, v):
    #    if not v.strip():
    #        raise ValueError("Comment cannot be empty or only whitespace")
