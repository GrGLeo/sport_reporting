from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fitparse import FitFile
import pandas as pd
from sqlalchemy import create_engine
from data.etl.running_feeder import RunningFeeder
from data.etl.comment_feeder import CommentFeeder
from data.etl.event_feeder import EventFeeder
from data.etl.cycling_feeder import CyclingFeeder
from data.tables import Base
from data.utils import create_schema
from api_model import LoginModel, UserModel, CommentModel, EventModel
from utils.exception import UserTaken, EmailTaken, UnknownUser, FailedAttempt, UserLocked
from utils.data_handler import get_data
from auth import auth_user, create_user


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    DATABASE_URL = "postgresql://leo:postgres@localhost:5432/sporting"
    engine = create_engine(DATABASE_URL)
    create_schema(engine, ['settings'])
    Base.metadata.create_all(bind=engine)
    print("All tables are created or verified!")


@app.post("/uploadfile/")
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Form(...)
):
    contents = await file.read()
    fitfile = FitFile(contents)
    records = get_data(fitfile, 'record')
    laps = get_data(fitfile, 'lap')
    activity = get_data(fitfile, 'session')[0]['sport']
    activity_id = int(records[0]["timestamp"].timestamp())

    wkt = {
        f"record_{activity}": pd.DataFrame(records),
        f"lap_{activity}": pd.DataFrame(laps)
    }

    if activity == "running":
        feeder = RunningFeeder(wkt, activity_id, int(user_id))
        feeder.process()
        completion = feeder.put()
    elif activity == "cycling":
        feeder = CyclingFeeder(wkt, activity, int(user_id))
        feeder.process
        completion = feeder.put()
    return {
        "data": completion,
            }


@app.post("/post_comment")
async def post_comment(comment: CommentModel):
    if len(comment.comment_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment can not be empty")

    try:
        comment_feeder = CommentFeeder(comment)
        comment_feeder.process()
        comment_feeder.put()
    except Exception as e:
        print(e)
        pass


@app.post("/post_event")
async def post_event(event: EventModel):
    event_feeder = EventFeeder(event)
    event_feeder.process()
    event_feeder.put()


@app.post("/login")
async def login(login_data: LoginModel):
    try:
        token = auth_user(login_data.username, login_data.password)
    except (UnknownUser, UserLocked, FailedAttempt) as e:
        raise HTTPException(status_code=401, detail=f'{e}')

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": token}


@app.post("/create_user")
async def create_new_user(new_user: UserModel):
    try:
        token = create_user(new_user.username, new_user.password, new_user.email)
    except (UserTaken, EmailTaken) as e:
        raise HTTPException(status_code=401, detail=f'{e}')
    return {"token": token}
