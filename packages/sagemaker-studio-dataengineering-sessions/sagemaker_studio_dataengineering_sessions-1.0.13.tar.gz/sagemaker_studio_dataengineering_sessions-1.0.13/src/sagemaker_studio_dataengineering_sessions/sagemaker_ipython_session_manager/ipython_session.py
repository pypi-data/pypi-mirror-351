import logging
import uuid

from IPython import get_ipython
from IPython.core.error import UsageError
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.base_connection import BaseConnection
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.base_session_manager import BaseSessionManager
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import Language, PROJECT_S3_PATH
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.exceptions import \
    LanguageNotSupportedException
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.sagemaker_toolkit_utils import \
    SageMakerToolkitUtils
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.s3_manager.s3_variable_manager import S3VariableManager
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.utils.profile.aws_profile_helper import \
    set_aws_profile_and_region, reset_aws_profile_and_region


class IpythonSession(BaseSessionManager):
    logger = logging.getLogger(__name__)

    def __init__(self, connection_name: str):
        connection_id = SageMakerToolkitUtils.get_connection_id_from_connection_name(connection_name)
        connection_detail = SageMakerToolkitUtils.get_connection_detail_from_id(connection_id)
        self.connection_details = BaseConnection(
            connection_name=connection_name,
            connection_id=connection_id,
            region=connection_detail["physicalEndpoints"][0]["awsLocation"]["awsRegion"]
        )
        super().__init__()
        self.connection_name = connection_name
        self.s3_variable_manager_name = None

    def create_session(self):
        # Jupyter Lab session is always available
        pass

    def run_cell(self, cell="", language=Language.python):
        if language != Language.python:
            raise LanguageNotSupportedException(f"Language {language.name} not supported for Local Python")
        try:
            self._set_aws_profile_and_region()
            get_ipython().run_cell(cell)
        finally:
            reset_aws_profile_and_region()

    def run_statement(self, cell="", language=Language.python, mode="exec", *kwargs):
        if language != Language.python:
            raise LanguageNotSupportedException(f"Language {language.name} not supported for Local Python")
        try:
            self._set_aws_profile_and_region()
            if mode == "exec":
                return get_ipython().ex(cell)
            elif mode == "eval":
                return get_ipython().ev(cell)
        finally:
            reset_aws_profile_and_region()

    def stop_session(self):
        # Jupyter Lab session is always available
        pass

    def is_session_connectable(self) -> bool:
        # Jupyter Lab session is always available
        return True

    def _configure_core(self, cell: str):
        # Jupyter lab session doesn't support _configure_core
        raise NotImplementedError('configure magic is not by Local Python')

    def get_s3_store(self):
        if self.s3_variable_manager_name is None:
            try:
                s3_variable_manager_name = "_s3_variable_manager_" + uuid.uuid4().hex
                s3_variable_manager = S3VariableManager(project_s3_path=PROJECT_S3_PATH)
                get_ipython().user_ns[s3_variable_manager_name] = s3_variable_manager
                self.s3_variable_manager_name = s3_variable_manager_name
            except Exception as e:
                self.logger.error(f"Could not create s3 store handler: {e}")
                raise UsageError(f"Could not create s3 store handler: {e}")

        return self.s3_variable_manager_name

    def _set_aws_profile_and_region(self):
        set_aws_profile_and_region(self.connection_details.connection_id, self.connection_details.region)
