from back.data.etl import Feeder
from abc import abstractmethod
import pandas as pd


class ActivityFeeder(Feeder):
    def __init__(self, tables, activity_id, user_id):
        self.user_id = user_id
        super().__init__(tables, activity_id)
        self._records = None
        self._laps = None
        self._syn = None

    @property
    def records(self) -> pd.DataFrame:
        if self._records is None:
            self._records = self._process_records()
        return self._records

    @property
    def laps(self) -> pd.DataFrame:
        if self._laps is None:
            self._laps = self._process_laps()
        return self._laps

    @property
    def syn(self) -> pd.DataFrame:
        if self._syn is None:
            self._syn = self._get_wkt_syn()
        return self._syn

    def process(self) -> None:
        self.tables_processed = {
                'workout': self.records,
                'lap': self.laps,
                'syn': self.syn
        }

    @abstractmethod
    def _process_records(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def _process_laps(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_wkt_syn(self) -> pd.DataFrame:
        pass
