import datetime


def time_to_seconds(t):
    h = t.total_seconds() // 3600
    m = (t.total_seconds() % 3600) // 60
    s = t.total_seconds() % 60
    time = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(time)


def time_to_timedelta(t):
    hours = t.total_seconds() // 3600
    minutes = (t.total_seconds() % 3600) // 60
    seconds = t.total_seconds() % 60
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


def get_color(rpe):
    if rpe >= 1 and rpe <= 3:
        return "green"
    elif rpe >= 4 and rpe <= 6:
        return "yellow"
    elif rpe >= 7 and rpe <= 8:
        return "orange"
    elif rpe >= 9 and rpe <= 10:
        return "red"
    else:
        return "black"
