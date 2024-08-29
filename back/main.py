from fastapi import FastAPI, File, UploadFile
from fitparse import FitFile


app = FastAPI()


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    fitfile = FitFile(contents)

    records = []

    for record in fitfile.get_messages('record'):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value
        records.append(record_data)

    return {"data": records}
