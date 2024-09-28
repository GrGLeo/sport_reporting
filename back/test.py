import pandas as pd
from datetime import time
from utils.data_handler import get_data
from fitparse import FitFile


def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)


# fitfile = FitFile('bike.fit')
# df = get_data(fitfile, 'lap')
# laps = pd.DataFrame(df)
# laps['lap_id'] = laps.index
# cols = {
#     'total_timer_time': 'timer',
#     'total_distance': 'distance',
#     'avg_heart_rate': 'hr',
#     'avg_speed': 'speed',
#     'avg_cadence': 'cadence',
#     'avg_power': 'power',
#     'normalized_power': 'norm_power'
# }
# 
# laps.rename(
#     cols,
#     axis=1,
#     inplace=True
# )
# 
# 
# print(laps.columns)
# laps = laps[cols.values()]
# laps['timer'] = laps['timer'].apply(lambda x: seconds_to_time(int(x)))
# laps['speed'] = (laps['speed'] * 3600) / 1000
# 
# print(laps.tail())
# print(len(laps))
# 
test = pd.DataFrame({
                    'user_id': [1],
                    'recovery': [162],
                    'threshold': [310]
})
print(test)

print(test.iloc[0].to_dict())
test = pd.melt(test)
print(test)
