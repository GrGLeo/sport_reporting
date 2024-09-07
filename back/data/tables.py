from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Column, Integer, Float, Time, DateTime, String
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = {'schema': 'settings'}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String)
    password = Column(String)
    email = Column(String)


class LoginAttempts(Base):
    __tablename__ = "login_attempts"
    __table_args__ = {'schema': 'settings'}

    username = Column(String, primary_key=True)
    attempts = Column(Integer, nullable=False, default=0)
    last_attempts = Column(DateTime)


class Comments(Base):
    __tablename__ = "activity_comments"
    __table_args__ = {'schema': 'param'}

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer)
    user_id = Column(Integer)
    comment = Column(String)


class WorkoutRun(Base):
    __tablename__ = "workout"
    __table_args__ = {'schema': 'running'}

    user_id = Column(Integer, primary_key=True)
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
    __tablename__ = "lap"
    __table_args__ = {'schema': 'running'}

    user_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, primary_key=True)
    lap_id = Column(Integer, primary_key=True)
    timer = Column(Time)
    distance = Column(Float)
    hr = Column(Integer)
    cadence = Column(Integer)
    pace = Column(Float)


class SynRun(Base):
    __tablename__ = "syn"
    __table_args__ = {'schema': 'running'}

    user_id = Column(Integer, primary_key=True)
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

    user_id = Column("Integer", primary_key=True)
    swim = Column(Float)
    run_pace = Column(Float)
    ftp = Column(Integer)
    date = Column(DateTime)


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

    def get_user(self, username: str) -> Optional[UserInfo]:
        session = self.get_session()
        user = session.query(UserInfo).filter_by(user=username).first()
        return user

    def query_login_attempts(self, username):
        session = self.get_session()
        return session, session.query(LoginAttempts).filter_by(username=username).first()

    def record_failed_attempt(self, username):
        session, result = self.query_login_attempts(username)
        if result:
            if datetime.now() - result.last_attempts > timedelta(minutes=5):
                result.attempts = 0
            result.attempts += 1
            result.last_attempts = datetime.now()
            session.commit()
            attempt = result.attempts

        else:
            attempt = 1
            new_attempt = LoginAttempts(
                username=username,
                attempts=attempt,
                last_attempts=datetime.now()
            )
            session.add(new_attempt)
            session.commit()
        session.close()
        return attempt

    def verify_locked(self, username):
        session, result = self.query_login_attempts(username)

        if result:
            if datetime.now() - result.last_attempts <= timedelta(minutes=5) and result.attempts >= 5:
                return True
        else:
            False

    def reset_attempts(self, username):
        session, result = self.query_login_attempts(username)

        if result:
            session.delete(result)
            session.close()
