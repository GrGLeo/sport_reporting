import datetime


def time_to_seconds(t):
    h, m, s = t.hour, t.minute, t.second
    time = datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    return int(time)


def time_to_timedelta(t):
    return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
