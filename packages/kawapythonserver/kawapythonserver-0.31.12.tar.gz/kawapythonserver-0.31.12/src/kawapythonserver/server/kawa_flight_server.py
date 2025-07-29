import concurrent.futures
import json
import logging
import threading
import traceback
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.flight
import pyarrow.parquet

from .interpreter_error import InterpreterError
from .jobs.job_executor_2 import KawaJobExecutorBatched
from .jobs.job_manager_client import JobManagerClient
from .kawa_directory_manager import KawaDirectoryManager
from ..server.jobs.job_executor import KawaJobExecutor
from ..server.jobs.job_runner import JobRunner
from .kawa_log_manager import KawaLogManager, get_kawa_logger
from .. import __version__


class KawaFlightServer(pa.flight.FlightServerBase):
    MAX_OLD_JOB = 12 * 3600
    CHECK_OLD_JOB_INTERVAL = 3600

    def __init__(self,
                 dict_logging_config,
                 job_logging_level,
                 job_logging_formatter,
                 pex_executable_path: str,
                 script_runner_path: str,
                 location=None,
                 working_directory: Path = None,
                 tls_certificates=None,
                 aes_key=None,
                 kawa_url=None,
                 **kwargs):
        super(KawaFlightServer, self).__init__(location=location, tls_certificates=tls_certificates, **kwargs)
        self._location = location
        self._aes_key = aes_key
        self.kawa_url = kawa_url
        self.executor: concurrent.futures.ProcessPoolExecutor = concurrent.futures.ProcessPoolExecutor()

        self.directory_manager: KawaDirectoryManager = KawaDirectoryManager(working_directory)
        self.log_manager: KawaLogManager = KawaLogManager(
            dict_logging_config,
            job_logging_level,
            logging.Formatter(job_logging_formatter)
        )
        self.kawa_job_runner: JobRunner = JobRunner(self.directory_manager,
                                                    pex_executable_path,
                                                    script_runner_path,
                                                    self._aes_key,
                                                    self.kawa_url)
        self.python_job_manager_client = JobManagerClient(self.kawa_url, self._aes_key)

        self.kawa_job_executor: KawaJobExecutorBatched = KawaJobExecutorBatched(self.python_job_manager_client,
                                                                                self.kawa_job_runner,
                                                                                self.directory_manager)
        self.remove_old_jobs()

        get_kawa_logger().info('KAWA Python automation server started at location: %s', self._location)

    def _make_flight_info(self, job_id):
        schema = pa.parquet.read_schema(self.directory_manager.dataset_path(job_id))
        metadata = pa.parquet.read_metadata(self.directory_manager.dataset_path(job_id))
        descriptor = pa.flight.FlightDescriptor.for_path(
            job_id.encode('utf-8')
        )
        endpoints = [pa.flight.FlightEndpoint(job_id, [self._location])]
        return pyarrow.flight.FlightInfo(schema,
                                         descriptor,
                                         endpoints,
                                         metadata.num_rows,
                                         metadata.serialized_size)

    def list_flights(self, context, criteria):
        raise InterpreterError('Not supported')

    def get_flight_info(self, context, descriptor):
        return self._make_flight_info(descriptor.path[0].decode('utf-8'))

    def do_put(self, context, descriptor, reader, writer):
        job_id = descriptor.path[0].decode('utf-8')
        data_table = reader.read_all()
        get_kawa_logger().info('Upload dataset for job: %s', job_id)
        self.directory_manager.write_table(job_id, data_table)

    def do_get(self, context, ticket):
        job_id = ticket.ticket.decode('utf-8')
        get_kawa_logger().info('Download dataset for job: %s', job_id)
        return pa.flight.RecordBatchStream(self.directory_manager.read_table(job_id))

    def list_actions(self, context):
        return [
            ('run_script', 'Queue an automation script for execution.'),
            ('restart_script', 'Restart an already uploaded script.'),
            ('script_metadata', 'Get automation script metadata (parameters, outputs).'),
            ('health', 'Check server health.'),
            ('etl_preview', 'Load a preview of the output of the script')
        ]

    def do_action(self, context, action):
        try:
            get_kawa_logger().debug('action.type: %s', action.type)
            if action.type == 'script_metadata':
                return self.json_to_array_of_one_flight_result(self.action_metadata(action))
            elif action.type == 'health':
                j = f'"status":"OK", "version": "{__version__}"'
                return self.json_to_array_of_one_flight_result('{' + j + '}')
            elif action.type == 'etl_preview':
                return self.json_to_array_of_one_flight_result(self.action_etl_preview(action))
            else:
                raise NotImplementedError
        except Exception as err:
            traceback.print_exception(err)
            raise err

    def action_etl_preview(self, action):
        job_id = None
        try:
            json_action_payload = self.parse_action_payload(action)
            job_id = json_action_payload['job']
            self.kawa_job_runner.run_job(job_id, json_action_payload)
            etl_preview_json = self.directory_manager.read_json_etl_preview(job_id)
            return EtlPreviewResult(etl_preview_json, '').to_json()
        except Exception as err:
            get_kawa_logger().error(f'Error when getting etl preview: {err}')
            res = EtlPreviewResult('', str(err)).to_json()
            return res
        finally:
            if job_id:
                self.directory_manager.remove_etl_preview(job_id)

    def action_metadata(self, action):
        job_id = None
        try:
            json_action_payload = self.parse_action_payload(action)
            job_id = json_action_payload['job']
            self.kawa_job_runner.run_job(job_id, json_action_payload)
            metadata = self.directory_manager.read_json_metadata(job_id)
            return MetadataResult(metadata, '').to_json()
        except Exception as err:
            get_kawa_logger().error(f'Error when getting metadata: {err}')
            res = MetadataResult('', str(err)).to_json()
            return res
        finally:
            if job_id:
                self.directory_manager.remove_metadata(job_id)

    def remove_old_jobs(self):
        get_kawa_logger().info(f'Start removing the old jobs, with max old job: {self.MAX_OLD_JOB}')
        self.directory_manager.remove_files_older_than(self.MAX_OLD_JOB)
        threading.Timer(self.CHECK_OLD_JOB_INTERVAL, self.remove_old_jobs).start()
        get_kawa_logger().info(f'End removing the old jobs')

    @staticmethod
    def json_to_array_of_one_flight_result(json_result: str):
        flight_result = pyarrow.flight.Result(pyarrow.py_buffer(json_result.encode('utf-8')))
        return [flight_result]

    @staticmethod
    def parse_action_payload(action: pyarrow.flight.Action):
        return json.loads(action.body.to_pybytes().decode('utf-8'))


@dataclass
class EtlPreviewResult:
    result: str
    error: str

    def to_json(self):
        return json.dumps(self.__dict__)


@dataclass
class MetadataResult:
    result: str
    error: str

    def to_json(self):
        return json.dumps(self.__dict__)
