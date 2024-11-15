FROM python:3.12-slim

WORKDIR /app

COPY . /app/back

RUN pip install /app/back

RUN pip install -r /app/back/requirements.txt

RUN mkdir -p /app/back/workout

CMD ["uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]

