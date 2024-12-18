import pytest
import pandas as pd
from datetime import datetime
from data.etl.running_feeder import RunningFeeder, speed_to_pace, seconds_to_time  # Adjust import based on your structure


@pytest.fixture
def mock_tables():
    return {
        "lap_running": pd.DataFrame({
            'message_index': [1, 2],
            'total_timer_time': [600, 500],
            'total_distance': [1000, 900],
            'avg_heart_rate': [140, 135],
            'avg_running_cadence': [90, 85]
        }),
        "record_running": pd.DataFrame({
            'timestamp': [datetime.now(), datetime.now()],
            'distance': [1000, 2000],
            'position_lat': [34.05, 34.06],
            'position_long': [-118.25, -118.24],
            'heart_rate': [150, 148],
            'cadence': [90, 92],
            'enhanced_speed': [3.0, 2.5],
            'enhanced_altitude': [500, 505]
        })
    }


def test_feeder_init(mock_tables):
    feeder = RunningFeeder(mock_tables, id=1, user_id=123)
    assert feeder.tables == mock_tables
    assert feeder.user_id == 123
    assert feeder.schema == 'running'


def test_process_laps(mock_tables):
    feeder = RunningFeeder(mock_tables, id=1, user_id=123)
    laps = feeder._process_laps()

    assert laps.shape[1] == 6  # Check if 6 columns (including pace and timer)
    assert 'pace' in laps.columns
    assert 'timer' in laps.columns


def test_process_records(mock_tables):
    feeder = RunningFeeder(mock_tables, id=1, user_id=123)
    records = feeder._process_records()

    assert records.shape[1] == 9  # Expected number of columns in records
    assert 'record_id' in records.columns
    assert 'pace' in records.columns
    assert records['pace'].notna().all()  # Pace should be calculated correctly


def test_wkt_syn(mock_tables):
    feeder = RunningFeeder(mock_tables, id=1, user_id=123)
    syn = feeder._get_wkt_syn()

    assert 'date' in syn.columns
    assert 'duration' in syn.columns
    assert 'avg_hr' in syn.columns
    assert syn['tss'].iloc[0] > 0  # Ensure Training Stress Score (tss) is calculated


def test_speed_to_pace():
    assert speed_to_pace(3.0) > 0  # Expect positive value for non-zero speed
    assert speed_to_pace(0) == float('inf')  # Expect inf for zero speed


def test_seconds_to_time():
    time = seconds_to_time(3661)
    assert time.hour == 1
    assert time.minute == 1
    assert time.second == 1
