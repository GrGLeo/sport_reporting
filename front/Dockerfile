FROM python:3.12-slim

WORKDIR /app

COPY . /app/front

RUN pip install /app/front

RUN pip install -r /app/front/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "front/streamlit_app.py"]
