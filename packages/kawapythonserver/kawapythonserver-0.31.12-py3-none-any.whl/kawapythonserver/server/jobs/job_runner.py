import glob
import os
import pickle
import subprocess
import time

from kywy.client.kawa_client import KawaClient

from ...scripts.kawa_python_column_loader_callback import PythonColumnLoaderCallback
from ...scripts.kawa_python_datasource_loader_callback import PythonDatasourceLoaderCallback
from ...scripts.kawa_python_datasource_preview_loader_callback import PythonDatasourcePreviewCallback
from ...scripts.kawa_python_metadata_callback import PythonMetaDataLoaderCallback
from ...scripts.kawa_tool_kit import build_kawa_toolkit_from_yaml_file
from ...server.clear_script_with_secrets import ClearScriptWithSecrets
from ...server.kawa_directory_manager import KawaDirectoryManager
from ...server.kawa_log_manager import get_kawa_logger
from ...server.kawa_pex_builder import KawaPexBuilder
from ...server.kawa_script_runner_inputs import ScriptRunnerInputs


class JobRunner:

    def __init__(self,
                 directory_manager: KawaDirectoryManager,
                 pex_executable_path: str,
                 script_runner_path: str,
                 aes_key: str,
                 kawa_url: str):
        self.directory_manager: KawaDirectoryManager = directory_manager
        self.logger = get_kawa_logger()
        self.pex_executable_path = pex_executable_path
        self.script_runner_path = script_runner_path
        self._aes_key = aes_key
        self.kawa_url = kawa_url

    def run_job(self,
                job_id: str,
                json_action_payload: dict):
        try:
            self.logger.info(f'Starting to run the job: {job_id}')

            encrypted_script_with_secrets = json_action_payload['script']

            clear_script_with_secrets = ClearScriptWithSecrets.decrypt(encrypted_script_with_secrets, self._aes_key)
            self.load_package_from_source_control(clear_script_with_secrets, job_id)
            module = self.extract_module_from_package_and_task(clear_script_with_secrets, job_id)
            pex_builder = KawaPexBuilder(self.pex_executable_path,
                                         f'{self.directory_manager.repo_path(job_id)}/requirements.txt',
                                         self.directory_manager.pex_path())
            pex_file_path = pex_builder.build_pex_if_necessary(job_id)

            is_automation_job = not (
                    'pythonPrivateJoinId' in json_action_payload or
                    'dataSourceId' in json_action_payload or
                    'isPreview' in json_action_payload or
                    'isMetadata' in json_action_payload)
            arrow_table = self.directory_manager.read_table(job_id) if is_automation_job else None

            kawa_client = self._create_kawa_client(json_action_payload, job_id, clear_script_with_secrets.api_key)
            callback = self._create_callback(json_action_payload, kawa_client, clear_script_with_secrets)

            script_parameters_values = json_action_payload.get('scriptParametersValues', [])
            script_parameters_dict = {p['scriptParameterName']: p['value']
                                      for p in script_parameters_values
                                      if p.get('value') is not None}

            inputs = ScriptRunnerInputs(
                self.script_runner_path,
                pex_file_path,
                job_id,
                module,
                self.directory_manager.log_path(job_id),
                clear_script_with_secrets.kawa_secrets,
                self.directory_manager.repo_path(job_id),
                kawa_client,
                callback,
                arrow_table,
                clear_script_with_secrets.meta_data,
                script_parameters_dict
            )

            self.execute_script_in_sub_process(inputs)
        except Exception as e:
            raise e
        finally:
            self.clean_files(job_id)

    def execute_script_in_sub_process(self, inputs: ScriptRunnerInputs):
        self.logger.info(f'Starting the sub process to run the script for jobId: {inputs.job_id}')
        start_time = time.time()
        error = ''
        try:
            my_env = os.environ.copy()
            my_env['PEX_EXTRA_SYS_PATH'] = os.pathsep.join([str(inputs.repo_path)])
            self.logger.info(f'PEX_EXTRA_SYS_PATH is {my_env["PEX_EXTRA_SYS_PATH"]}')
            sub = subprocess.run([
                inputs.pex_file_path, self.script_runner_path
            ],
                input=pickle.dumps(inputs),
                timeout=10*60,
                check=True,
                capture_output=True,
                env=my_env
            )
            execution_time = round(time.time() - start_time, 1)
            self.logger.info(f'''Logs from subprocess: 
                                 ###### SUB PROCESS LOGS START ######
                                 {sub.stdout.decode("unicode_escape")}
                                 ###### SUB PROCESS LOGS FINISH ######''')
            self.logger.info(f'Sub process ended in {execution_time}s')

        except FileNotFoundError as exc:
            error = f'Process failed because the executable could not be found.{exc}'
        except subprocess.CalledProcessError as exc:
            self.logger.info(exc.stdout.decode("unicode_escape"))
            error = f'Error when execution script: \n {exc.stderr.decode("unicode_escape")}'
        except subprocess.TimeoutExpired as exc:
            self.logger.info(exc.stdout.decode("unicode_escape"))
            error = f'Process timed out.\n{exc}'
        except Exception as exc:
            self.logger.info('Some weird exception occurred')

            error = f'Process failed.\n{exc}'
        finally:
            if error:
                self.logger.error(error)
                raise Exception(error)

    def clean_files(self, job_id):
        self.directory_manager.remove_job_working_files(job_id)
        self.directory_manager.remove_repo_files(job_id)

    def _create_kawa_client(self, action_payload, job_id, api_key) -> KawaClient:
        start = time.time()
        workspace_id = action_payload.get('workspaceId')
        if not api_key:
            return KawaClient(kawa_api_url=self.kawa_url)  # if key is not there we don't need the client
        kawa_client = KawaClient(kawa_api_url=self.kawa_url)
        kawa_client.set_api_key(api_key=api_key)
        kawa_client.set_active_workspace_id(workspace_id=workspace_id)
        exec_time = round(time.time() - start, 1)
        self.logger.info(f'KawaClient created in {exec_time}s for jobId: {job_id}')
        return kawa_client

    def _create_callback(self, action_payload,
                         kawa_client: KawaClient,
                         clear_script_with_secrets: ClearScriptWithSecrets):
        job_id = action_payload['job']

        if action_payload.get('isMetadata'):
            return PythonMetaDataLoaderCallback(job_id, self.directory_manager)

        if action_payload.get('pythonPrivateJoinId'):
            python_private_join_id = action_payload.get('pythonPrivateJoinId')
            dashboard_id = action_payload.get('dashboardId')
            application_id = action_payload.get('applicationId')
            return PythonColumnLoaderCallback(python_private_join_id,
                                              job_id,
                                              kawa_client,
                                              dashboard_id,
                                              application_id)
        if action_payload.get('dataSourceId'):
            datasource_id = action_payload.get('dataSourceId')
            reset_before_insert = action_payload.get('isFullRefresh')
            optimize_after_insert = action_payload.get('optimizeTableAfterInsert')
            return PythonDatasourceLoaderCallback(datasource_id=datasource_id,
                                                  reset_before_insert=reset_before_insert,
                                                  optimize_after_insert=optimize_after_insert,
                                                  job_id=job_id,
                                                  kawa_client=kawa_client)
        if action_payload.get('isPreview'):
            return PythonDatasourcePreviewCallback(job_id,
                                                   clear_script_with_secrets.meta_data,
                                                   self.directory_manager)

        return None

    def load_package_from_source_control(self,
                                         clear_script_with_secrets: ClearScriptWithSecrets,
                                         job_id: str):
        start_time = time.time()
        repo_path = self.directory_manager.repo_path(job_id)
        self.logger.info(f'Start loading repo from source control in {repo_path} for jobId: {job_id}')
        if clear_script_with_secrets.is_from_kawa_source_control():
            # in case of tool coming from kawa source control, we just load the content from ClearScriptWithSecrets
            # and copy it to the repo path
            os.mkdir(repo_path)
            with open(f'{repo_path}/kawa_managed_tool.py', 'w') as file:
                file.write(clear_script_with_secrets.content)
            with open(f'{repo_path}/requirements.txt', 'w') as file:
                file.write(clear_script_with_secrets.requirements)
        else:
            command = 'git clone -b {branch} --single-branch https://oauth2:{token}@{repo_rul} {repo_path}'.format(
                branch=clear_script_with_secrets.branch,
                token=clear_script_with_secrets.repo_key,
                repo_rul=clear_script_with_secrets.repo_url.replace('https://', ''),
                repo_path=repo_path
            )
            os.system(command)
        t = round(time.time() - start_time, 1)
        self.logger.info(f'End loading repo in {t}s from source control for jobId: {job_id}')

    def extract_module_from_package_and_task(self,
                                             clear_script_wit_secrets: ClearScriptWithSecrets,
                                             job_id: str) -> str:
        if clear_script_wit_secrets.is_from_kawa_source_control():
            return 'kawa_managed_tool'
        toolkit_name, tool_name = clear_script_wit_secrets.toolkit, clear_script_wit_secrets.tool
        repo_path = self.directory_manager.repo_path(job_id)
        files = glob.glob(f'{repo_path}/**/kawa-toolkit.yaml', recursive=True)
        kawa_toolkits = [build_kawa_toolkit_from_yaml_file(repo_path, file) for file in files]
        for kawa_toolkit in kawa_toolkits:
            if kawa_toolkit.name != toolkit_name:
                continue
            for tool in kawa_toolkit.tools:
                if tool.name != tool_name:
                    continue
                self.logger.debug(f'MODULE TO USE: {tool.module} for jobId: {job_id}')
                return tool.module

        raise Exception(f'No module found in the repo for toolkit: {toolkit_name} and tool: {tool_name}')
