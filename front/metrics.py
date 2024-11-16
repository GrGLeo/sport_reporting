import pandas as pd


def calculate_metric(df: pd.DataFrame, col: str, days: int) -> pd.DataFrame:
    for i in range(len(df)):
        if i == 0:
            df.loc[i, col] = 0 + (df.loc[i, 'tss'] - 0) / days
        else:
            df.loc[i, col] = df.loc[i - 1, col] + (df.loc[i, 'tss'] - df.loc[i - 1, col]) / days

    return df


def calculate_ctl(df: pd.DataFrame) -> pd.DataFrame:
    ctl_days = 42
    df['ctl'] = 0.

    return calculate_metric(df, 'ctl', ctl_days)


def calculate_atl(df: pd.DataFrame) -> pd.DataFrame:
    atl_days = 7
    df['atl'] = 0.

    return calculate_metric(df, 'atl', atl_days)


def calculate_form(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(len(df)):
        if i == 0:
            df['form'] = 0.
        else:
            df.loc[i, 'form'] = df.loc[i - 1, 'ctl'] - df.loc[i - 1, 'atl']

    return df


def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
    df = calculate_form(calculate_atl(calculate_ctl(df)))
    return df
