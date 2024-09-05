import bcrypt
from utils.exception import UserTaken, EmailTaken
from data.tables import UserCRUD


def auth_user(username, password):
    db_user = UserCRUD('postgresql://leo:postgres@localhost:5432/sporting')
    user = db_user.get_user(username)
    if not user:
        return
    hashed = user.password
    if bcrypt.checkpw(password.encode(), hashed.encode()):
        return user.user_id


def create_user(username, password, email):
    db_user = UserCRUD('postgresql://leo:postgres@localhost:5432/sporting')
    u_exist, e_exist = db_user.check_user_exist(username, email)
    if u_exist:
        raise UserTaken('Username already taken')
    elif e_exist:
        raise EmailTaken('Email already taken')
    else:
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db_user.add_user(username, password.decode(), email)
    return auth_user(username, password.decode())
