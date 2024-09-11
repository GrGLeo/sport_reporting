import pytest
from unittest.mock import patch, MagicMock
from back.data.etl.event_feeder import EventFeeder
from back.api_model import EventModel


@pytest.fixture
def event_model():
    # Fixture providing a sample EventModel object for tests
    return EventModel(
        user_id=1,
        date='2024-12-01',
        name='Test Event',
        sport='Running',
        priority='A'
    )


@patch('back.data.connexion.DatabaseConnection')
def test_event_feeder(mock_db_conn, event_model):
    # Arrange: Set up the mock database connection
    mock_engine = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_engine

    # Act: Create an instance of EventFeeder
    feeder = EventFeeder(event_model)
    feeder.process()

    # Assert: Check that the process method works as expected
    assert feeder.tables['events'] is not None
