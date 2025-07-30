import os

import botocore.config
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import CONNECTION_TYPE_ATHENA

from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.athena.athena_config import Config
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.athena.connection_transformer import get_athena_connection
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.sagemaker_database_session_manager import SageMakerDatabaseSessionManager
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.utils.common_utils import get_athena_gamma_endpoint

USER_AGENT_SUFFIX = "sagemaker_unified_studio_connection_magic"
botocore_config = botocore.config.Config(user_agent_extra=USER_AGENT_SUFFIX)

class AthenaSession(SageMakerDatabaseSessionManager):
    def __init__(self, connection_name: str):
        self.connection_details = get_athena_connection(connection_name, self.get_logger())
        super().__init__(connection_name)
        self.config = Config()

    def get_connection_parameter(self):
        # https://github.com/laughingman7743/PyAthena/blob/master/pyathena/connection.py#L49
        # https://code.amazon.com/packages/SMUnoSQLExecution/blobs/178ea494faca9f65a20d64e1358713c0f59eb381/--/src/amazon_sagemaker_sql_execution/athena/models.py#L41
        connection_properties: dict = {"work_group": self.connection_details.work_group,
                                       "connection_type": CONNECTION_TYPE_ATHENA,
                                       "profile_name": self.connection_details.connection_id,
                                       "region_name": self.connection_details.region}
        if self.config.catalog_name:
            connection_properties["catalog_name"] = self.config.catalog_name
        if self.config.schema_name:
            connection_properties["schema_name"] = self.config.schema_name
        connection_properties["config"] = botocore_config
        if os.getenv("AWS_STAGE", None) == "GAMMA":
            connection_properties["endpoint_url"] = get_athena_gamma_endpoint(self.connection_details.region)
        return connection_properties