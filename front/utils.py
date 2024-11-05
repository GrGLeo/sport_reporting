import datetime


def time_to_seconds(t):
    h, m, s = t.hour, t.minute, t.second
    time = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(time)


def time_to_timedelta(t):
    return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


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
