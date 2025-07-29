from dataclasses import dataclass
from typing import cast

import pyarrow as pa

from kywy.client.kawa_client import KawaClient

from ..scripts.kawa_loader_callback import LoaderCallback
from ..scripts.kawa_python_datasource_loader_callback import PythonDatasourceLoaderCallback
from ..scripts.kawa_python_datasource_preview_loader_callback import PythonDatasourcePreviewCallback
from ..scripts.kawa_python_metadata_callback import PythonMetaDataLoaderCallback
from ..scripts.kawa_secrets import KawaSecrets


@dataclass
class ScriptRunnerInputs:
    script_runner_path: str
    pex_file_path: str
    job_id: str
    module: str
    job_log_file: str
    secrets: KawaSecrets
    repo_path: str
    kawa_client: KawaClient
    callback: LoaderCallback
    arrow_table: pa.Table
    kawa_meta_data: dict
    script_parameters_values_dict: dict

    def needs_defined_outputs(self) -> bool:
        return self.callback is not None

    def is_preview(self) -> bool:
        return self.callback is not None and isinstance(self.callback, PythonDatasourcePreviewCallback)

    def is_datasource_script(self) -> bool:
        return self.callback is not None and isinstance(self.callback, PythonDatasourceLoaderCallback)

    def is_incremental(self) -> bool:
        return self.is_datasource_script() and not cast(PythonDatasourceLoaderCallback, self.callback).reset_before_insert

    def is_metadata(self) -> bool:
        return self.callback is not None and isinstance(self.callback, PythonMetaDataLoaderCallback)
