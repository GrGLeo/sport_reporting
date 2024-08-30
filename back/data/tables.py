from sqlalchemy import Column, Integer, Float, Time, DateTime
from sqlalchemy.ext.declarative import declarative_base


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
