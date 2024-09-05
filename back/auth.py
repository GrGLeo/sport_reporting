import bcrypt
from data.tables import UserCRUD


def auth_user(username, password):
    db_user = UserCRUD('postgresql://leo:postgres@localhost:5432/sporting')
    hashed = db_user.get_password(username)
    print(hashed)
    if bcrypt.checkpw(password.encode(), hashed.encode()):
        return 'yes'


def create_user(username, password, email):
    db_user = UserCRUD('postgresql://leo:postgres@localhost:5432/sporting')
    u_exist, e_exist = db_user.check_user_exist(username, email)
    if u_exist:
        # create exception
        return Exception
    elif e_exist:
        raise Exception
    else:
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        db_user.add_user(username, password.decode(), email)
    return auth_user(username, password.decode())
