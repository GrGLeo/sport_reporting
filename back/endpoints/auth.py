import os
import bcrypt
from datetime import timedelta, datetime
import jwt
from fastapi import APIRouter, HTTPException, status
from back.utils.exception import UserTaken, EmailTaken, UnknownUser, FailedAttempt, UserLocked
from back.data.tables import UserCRUD
from back.api_model import UserModel, LoginModel
from back.utils.logger import logger


router = APIRouter()

DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")
SECRET = os.getenv("SECRET", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


@router.post("/login")
async def login(login_data: LoginModel):
    try:
        logger.info(f'User: {login_data.username} login attempt')
        user_id = auth_user(login_data.username, login_data.password)
        data = {"user_id": user_id}
        return {"access_token": create_jwt(data), "token_type": "Bearer"}
    except UnknownUser as e:
        logger.warning(f'User: {login_data.username} {e}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserLocked as e:
        logger.warning(f'User: {login_data.username} {e}')
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(e))
    except FailedAttempt as e:
        logger.warning(f'User: {login_data.username} {e}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    logger.info(f'User: {login_data.username} login successfull')


@router.post("/create_user")
async def create_new_user(new_user: UserModel):
    try:
        token = create_user(new_user.username, new_user.password, new_user.email)
    except (UserTaken, EmailTaken) as e:
        raise HTTPException(status_code=401, detail=f'{e}')
    return {"token": token}


def auth_user(username, password):
    db_user = UserCRUD(f'postgresql://{DB_URL}')
    user = db_user.get_user(username)
    if not user:
        raise UnknownUser()
    # check if user locked out
    if not db_user.verify_locked(username):
        hashed = user.password
        if bcrypt.checkpw(password.encode(), hashed.encode()):
            # erase from login attempts table
            db_user.reset_attempts(username)
            return user.user_id
        else:
            attempts = db_user.record_failed_attempt(username)
            remaining = 6 - attempts
            raise FailedAttempt(f"Invalid password, {remaining} attempts")
    else:
        raise UserLocked()


def create_user(username, password, email):
    db_user = UserCRUD(f'postgresql://{DB_URL}')
    u_exist, e_exist = db_user.check_user_exist(username, email)
    if u_exist:
        raise UserTaken('Username already taken')
    elif e_exist:
        raise EmailTaken('Email already taken')
    else:
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db_user.add_user(username, password.decode(), email)
        # change logic: need to log after creating the user
        return True
        # return auth_user(username, password.decode())


def create_jwt(data: dict, expire: timedelta = timedelta(hours=1)):
    expire_delta = datetime.now() + expire
    data["exp"] = expire_delta
    return jwt.encode(data, SECRET, algorithm=ALGORITHM)


def decode_jwt(token: str):
    if len(token.split(".")) != 3:
        print(token)
        raise HTTPException(status_code=401, detail="Invalid JWT token structure")

    payload = jwt.decode(token, SECRET, [ALGORITHM])
    return payload["user_id"]
