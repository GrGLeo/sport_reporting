import os
import jwt
import random
import string
from fastapi import HTTPException, Request

from datetime import time, timedelta


def speed_to_pace(speed, ms=True):
    if speed == 0:
        return float("inf")
    if ms:
        pace = (1000 / (speed * 60))
    else:
        pace = 60 / speed
    minutes = int(pace)
    seconds = int(round((pace - minutes) * 60))
    return round(minutes + (seconds / 100), 2)


def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


def assign_zone(power, zones):
    if power <= zones['recovery']:
        return 'recovery'
    elif power <= zones['endurance']:
        return 'endurance'
    elif power <= zones['tempo']:
        return 'tempo'
    elif power <= zones['threshold']:
        return 'threshold'
    elif power <= zones['vo2max']:
        return 'vo2max'
    else:
        return 'vo2max'


def authorize_user(requests: Request) -> int:
    SECRET = os.getenv("SECRET", "secret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    authorization = requests.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    if len(token.split(".")) != 3:
        raise HTTPException(status_code=401, detail="Invalid JWT token structure.")

    try:
        payload = jwt.decode(token, SECRET, [ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user_id missing.")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def generate_custom_id(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

