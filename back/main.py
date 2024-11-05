import os
import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, status, Header
from fitparse import FitFile
import pandas as pd
from sqlalchemy import create_engine
from back.endpoints.auth import router, decode_jwt
from back.endpoints.db_query import db_router
from back.endpoints.comments import activity_router
from back.data.etl.running_feeder import RunningFeeder
from back.data.etl.event_feeder import EventFeeder
from back.data.etl.cycling_feeder import CyclingFeeder
from back.data.etl.threshold_feeder import ThresholdFeeder
from back.data.etl.futur_wkt_feeder import FuturWorkoutFeeder
from back.data.tables import Base
from back.utils.data_handler import get_data
from back.fit.fit_writer import WorkoutWriter
from back.api_model import (
    EventModel,
    ThresholdModel,
    FuturWktModel
)


DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")
app = FastAPI()
app.include_router(router)
app.include_router(db_router)
app.include_router(activity_router)


@app.on_event("startup")
async def startup_event():
    MAX_RETRIES = 10
    WAIT_TIME = 2
    DATABASE_URL = f"postgresql://{DB_URL}"
    engine = create_engine(DATABASE_URL)

    for attempt in range(MAX_RETRIES):
        try:
            Base.metadata.create_all(bind=engine)
            print("All tables are created or verified!")
            break
        except OperationalError:
            print(f"Database connection failed, retrying in {WAIT_TIME} seconds...")
            time.sleep(WAIT_TIME)
    else:
        print(f"Failed to connect to Database after {MAX_RETRIES} attemps.")


@app.post("/uploadfile/")
async def upload_file(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.split(" ")[1]
    user_id = decode_jwt(token)

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
        feeder.compute()
    elif activity == "cycling":
        feeder = CyclingFeeder(wkt, activity_id, int(user_id))
        feeder.compute()
    if feeder.complete:
        return {
            "data": "Uploading successfull",
        }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occured while uploading activity')


@app.post("/post_event")
async def post_event(event: EventModel, authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.split(" ")[1]
    user_id = decode_jwt(token)
    event_feeder = EventFeeder(event, user_id)
    event_feeder.compute()


@app.post("/threshold")
async def update_threshold(threshold: ThresholdModel, authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.split(" ")[1]
    user_id = decode_jwt(token)
    threshold_feeder = ThresholdFeeder(threshold, user_id)
    threshold_feeder.compute()


@app.post("/push_program_wkt")
async def save_program_wkt(futur_wkt: FuturWktModel, authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.split(" ")[1]
    user_id = decode_jwt(token)
    ftr_wkt_feeder = FuturWorkoutFeeder(futur_wkt, user_id)
    ftr_wkt_feeder.compute()
    wkt_writer = WorkoutWriter(futur_wkt, user_id)
    wkt_writer.write_workout()

import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
