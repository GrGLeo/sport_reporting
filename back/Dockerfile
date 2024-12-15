FROM python:3.12-slim

WORKDIR /app

COPY . ./back

WORKDIR /app/back

RUN pip install .

RUN pip install -r requirements.txt

RUN mkdir -p /app/back/workout

EXPOSE 12345/udp

CMD ["python", "main.py"]
# CMD ["uvicorn", "back.main:app", "--host", "0.0.0.0", "--port", "8000"]

