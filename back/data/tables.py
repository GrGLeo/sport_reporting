from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, Float, Time, DateTime, String, Date, JSON
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Comments(Base):
    __tablename__ = "activity_comments"
    __table_args__ = {'schema': 'param'}

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer)
    user_id = Column(Integer)
    comment = Column(String)


class Events(Base):
    __tablename__ = "events"
    __table_args__ = {'schema': 'param'}

    user_id = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)
    name = Column(String)
    sport = Column(String)
    priority = Column(String)


class FuturWorkout(Base):
    __tablename__ = "workout"
    __table_args__ = {"schema": "planning"}

    activity_id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    date = Column(Date)
    name = Column(String)
    sport = Column(String)
    data = Column(JSON)


class Workout(Base):
    __abstract__ = True
    __tablename__ = "workout"

    user_id = Column(Integer, primary_key=True)
    record_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    distance = Column(Float)
    hr = Column(Integer)
    cadence = Column(Integer)
    pace = Column(Float)
    altitude = Column(Integer)
    zone = Column(String)


class WorkoutRun(Workout):
    __table_args__ = {'schema': 'running'}

    lat = Column(Float)
    lon = Column(Float)
    pace = Column(Float)


class WorkoutCycling(Workout):
    __table_args__ = {'schema': 'cycling'}

    speed = Column(Float)
    power = Column(Integer)
    norm_power = Column(Integer)


class Lap(Base):
    __abstract__ = True
    __tablename__ = "lap"

    user_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, primary_key=True)
    lap_id = Column(Integer, primary_key=True)
    timer = Column(Time)
    distance = Column(Float)
    hr = Column(Integer)
    cadence = Column(Integer)


class LapRun(Lap):
    __table_args__ = {'schema': 'running'}

    pace = Column(Float)


class LapCycling(Lap):
    __table_args__ = {'schema': 'cycling'}

    speed = Column(Float)
    power = Column(Integer)
    norm_power = Column(Integer)


class Syn(Base):
    __abstract__ = True
    __tablename__ = "syn"

    user_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    duration = Column(Time)
    distance = Column(Float)
    avg_hr = Column(Integer)
    avg_cadence = Column(Integer)
    tss = Column(Integer)
    recovery = Column(Integer)
    endurance = Column(Integer)
    tempo = Column(Integer)
    threshold = Column(Integer)
    vo2max = Column(Integer)
    rpe = Column(Integer)


class SynRun(Syn):
    __table_args__ = {'schema': 'running'}

    avg_pace = Column(Float)


class SynCycling(Syn):
    __table_args__ = {'schema': 'cycling'}

    avg_speed = Column(Float)


class User(Base):
    __tablename__ = "user_threshold"
    __table_args__ = {'schema': 'param'}

    user_id = Column(Integer, primary_key=True)
    date = Column(DateTime, primary_key=True)
    swim = Column(Integer)
    vma = Column(Float)
    ftp = Column(Integer)


class Zone(Base):
    __abstract__ = True
    __table_args__ = {'schema': 'param'}

    user_id = Column(Integer, primary_key=True)
    recovery = Column(Integer)
    endurance = Column(Integer)
    tempo = Column(Integer)
    threshold = Column(Integer)
    vo2max = Column(Integer)


class CyclingZone(Zone):
    __tablename__ = 'cycling_zone'


class RunZone(Zone):
    __tablename__ = 'run_zone'

    recovery = Column(Float)
    endurance = Column(Float)
    tempo = Column(Float)
    threshold = Column(Float)
    vo2max = Column(Float)


class DataBase:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.Session()
