from sqlalchemy import Column, Integer, Float, Time, DateTime, String
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class DataBase:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.Session()


class UserCRUD(DataBase):
    def __init__(self, db_url: str):
        super().__init__(db_url)

    def add_user(self, username: str, password: str, email: str):
        session = self.get_session()
        new_user = UserInfo(user=username, password=password, email=email)
        session.add(new_user)
        session.commit()
        session.close()

    def check_user_exist(self, username: str, email: str) -> tuple[bool, bool]:
        session = self.get_session()
        # Check if the username is taken
        username_taken = session.query(UserInfo).filter_by(user=username).first() is not None
        # Check if the email is taken
        email_taken = session.query(UserInfo).filter_by(email=email).first() is not None
        session.close()
        return (username_taken, email_taken)

    def get_password(self, username):
        session = self.get_session()
        password = session.query(UserInfo).filter_by(user=username).first()
        return password.password


class UserInfo(Base):
    __tablename__ = "user_info"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String)
    password = Column(String)
    email = Column(String)


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
