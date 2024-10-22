import os
import bcrypt
from back.utils.exception import UserTaken, EmailTaken, UnknownUser, FailedAttempt, UserLocked
from back.data.tables import UserCRUD


DB_URL = os.getenv("DATABASE_URL", "leo:postgres@localhost:5432/sporting")


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
    print(u_exist, e_exist)
    if u_exist:
        raise UserTaken('Username already taken')
    elif e_exist:
        raise EmailTaken('Email already taken')
    else:
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db_user.add_user(username, password.decode(), email)
    return auth_user(username, password.decode())
