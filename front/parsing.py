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


if __name__ == "__main__":
    df = fit_parsing('bike.fit')
    power = df.power
    power = power.rolling(window=30).mean()
    power = power ** 4
    power = power.mean()
    np = power ** 0.25

    print(np)
    print(df.info())
