from sqlalchemy import Column, Integer, Float, Time, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class WorkoutRun(Base):
    __tablename__ = "workout_running"

    activity_id = Column(Integer, primary_key=True)
    record_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    distance = Column(Float)
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


class SynRun(Base):
    __tablename__ = "syn_running"

    activity_id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    duration = Column(Time)
    distance = Column(Float)
    avg_hr = Column(Integer)
    avg_cadence = Column(Integer)
    avg_pace = Column(Float)
    tss = Column(Integer)


class User(Base):
    __tablename__ = "user"

    id = Column("Integer", primary_key=True, autoincrement=True)
    swim = Column(Float)
    run_pace = Column(Float)
    ftp = Column(Integer)
    date = Column(DateTime)
