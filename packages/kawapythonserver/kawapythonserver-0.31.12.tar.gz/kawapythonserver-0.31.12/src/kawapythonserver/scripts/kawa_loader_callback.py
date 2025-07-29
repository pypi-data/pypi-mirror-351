import typing
from abc import ABC, abstractmethod

import pandas as pd


class LoaderCallback(ABC):

    @abstractmethod
    def load(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def retrieve_data(self) -> pd.DataFrame:
        pass

    def dump_metadata(self, to_dump):
        pass
