import json

import pandas as pd
from kywy.client.kawa_decorators import KawaScriptParameter

from .kawa_loader_callback import LoaderCallback
from ..server.kawa_directory_manager import KawaDirectoryManager


class PythonMetaDataLoaderCallback(LoaderCallback):
    def __init__(self,
                 job_id: str,
                 kawa_directory_manager: KawaDirectoryManager):
        self.job_id = job_id
        self.kawa_directory_manager: KawaDirectoryManager = kawa_directory_manager

    def retrieve_data(self) -> pd.DataFrame:
        raise Exception('retrieve_data should not be used with PythonMetaDataLoaderCallback')

    def load(self, df: pd.DataFrame):
        raise Exception('load should not be used with PythonMetaDataLoaderCallback')

    def dump_metadata(self, to_dump):
        j = json.dumps(to_dump, default=self.kawa_script_parameter_encoder)
        self.kawa_directory_manager.write_json_metadata(self.job_id, j)

    @staticmethod
    def kawa_script_parameter_encoder(obj):
        if isinstance(obj, KawaScriptParameter):
            return {
                "name": obj.name,
                "type": obj.type,
                "default": obj.default,
                "description": obj.description,
                "values": obj.values,
            }
        raise TypeError(f"Type {type(obj)} not serializable")
