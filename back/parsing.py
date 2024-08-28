import pandas as pd
from fitparse import FitFile


def fit_parsing(file: str) -> pd.DataFrame:
    fitfile = FitFile(file)
    records = []

    for record in fitfile.get_messages('record'):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value
        records.append(record_data)

    df = pd.DataFrame(records)
    return df


df = fit_parsing('run.fit')
print(df.tail())
print(df.columns)
