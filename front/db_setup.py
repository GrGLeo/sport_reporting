import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Float, Time, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base


DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(f'postgresql://{DB_URL}')
Session = sessionmaker(bind=engine)
session = Session()


Base = declarative_base()


class WorkoutRun(Base):
    __tablename__ = "workout_running"

    activity_id = Column(Integer, primary_key=True)
    record_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    lat = Column(Float)
    lon = Column(Float)
    hr = Column(Integer)
    cadence = Column(Integer)
    pace = Column(Float)
    altitude = Column(Integer)


class LapRun(Base):
    __tablename__ = "lap_running"

    activity_id = Column(Integer, primary_key=True)
    lap_id = Column(Integer, primary_key=True)
    timer = Column(Time)
    distance = Column(Float)
    hr = Column(Integer)
    cadence = Column(Integer)
    pace = Column(Float)


class Threshold(Base):
    __tablename__ = "threshold"

    id = Column(Integer, primary_key=True, autoincrement=True)
    swim = Column(Float)
    ftp = Column(Integer)
    run_pace = Column(Float)
    date = Column(DateTime)


Base.metadata.create_all(engine)
