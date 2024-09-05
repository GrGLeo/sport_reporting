from fastapi import FastAPI, File, UploadFile, HTTPException
from fitparse import FitFile
import pandas as pd
from data.etl import Running_Feeder
from api_model import LoginModel, UserModel
from auth import auth_user, create_user


app = FastAPI()


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    fitfile = FitFile(contents)

    records = get_data(fitfile, 'record')
    laps = get_data(fitfile, 'lap')
    activity = get_data(fitfile, 'sport')[0]['sport']
    activity_id = int(records[0]["timestamp"].timestamp())

    wkt = {
        f"record_{activity}": pd.DataFrame(records),
        f"lap_{activity}": pd.DataFrame(laps)
    }

    if activity == "running":
        feeder = Running_Feeder(wkt, activity_id)
        completion = feeder.process_laps()
        feeder.process_records()
        feeder.get_wkt_syn()
        completion = "haha"
    return {
        "data": completion,
            }


@app.post("/login")
async def login(login_data: LoginModel):
    token = auth_user(login_data.username, login_data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": token}


def get_data(fitfile, field):
    field_data = []
    for line in fitfile.get_messages(field):
        line_data = {}
        for data in line:
            line_data[data.name] = data.value
        field_data.append(line_data)
    return field_data


@app.post("/create_user")
async def create_new_user(new_user: UserModel):
    print('hello')
    try:
        create_user(new_user.username, new_user.password, new_user.email)
    except Exception as e:
        raise HTTPException(status_code=401, detail=e)
