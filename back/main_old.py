import os
import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from fitparse import FitFile
import pandas as pd
from sqlalchemy import create_engine
from endpoints.db_query import db_router
from endpoints.comments import activity_router
from data.etl.running_feeder import RunningFeeder
from data.etl.event_feeder import EventFeeder
from data.etl.cycling_feeder import CyclingFeeder
from data.etl.threshold_feeder import ThresholdFeeder
from data.etl.futur_wkt_feeder import FuturWorkoutFeeder
from data.tables import Base
from utils.data_handler import get_data
from fit.fit_writer import WorkoutWriter
from generator.generator import Generator
from utils.utilities import authorize_user, generate_custom_id
from api_model import (
    EventModel,
    ThresholdModel,
    FuturWktModel,
    GenerateWktModel
)


DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")
app = FastAPI()
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
    user_id: int = Depends(authorize_user)
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
        feeder = RunningFeeder(wkt, activity_id, user_id)
        feeder.compute()
    elif activity == "cycling":
        feeder = CyclingFeeder(wkt, activity_id, user_id)
        feeder.compute()
    if feeder.complete:
        return {
            "data": "Uploading successfull",
        }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occured while uploading activity')


@app.post("/workouts/")
async def save_program_wkt(futur_wkt: FuturWktModel, user_id: str = Depends(authorize_user)):
    ftr_wkt_feeder = FuturWorkoutFeeder(futur_wkt, user_id)
    ftr_wkt_feeder.compute()
    wkt_writer = WorkoutWriter(futur_wkt, user_id)
    wkt_writer.write_workout()


@app.post("/workouts/ai")
async def generate_wkt(generate_param: GenerateWktModel, user_id = Depends(authorize_user)):
    generator = Generator(generate_param.sport, generate_param.target, user_id)
    data = generator.generate_workout()
    name = generate_custom_id(5)
    model = FuturWktModel(name=name, date=generate_param.date, sport=generate_param.sport, data=data)
    ftr_wkt_feeder = FuturWorkoutFeeder(model, user_id)
    ftr_wkt_feeder.compute()
    wkt_writer = WorkoutWriter(model, user_id)
    wkt_writer.write_workout()


@app.get("/workouts/download/{name}")
async def download_workout(name: str, user_id: str = Depends(authorize_user)):
    path = f"/app/workout/{user_id}/{name}.fit"
    return FileResponse(
            path,
            media_type="application/octet-stream",
            filename=f"{name}.fit"
            )


@app.post("/post_event")
async def post_event(event: EventModel, user_id: str = Depends(authorize_user)):
    event_feeder = EventFeeder(event, user_id)
    event_feeder.compute()


@app.post("/threshold")
async def update_threshold(threshold: ThresholdModel, user_id: str = Depends(authorize_user)):
    threshold_feeder = ThresholdFeeder(threshold, user_id)
    threshold_feeder.compute()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
