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
