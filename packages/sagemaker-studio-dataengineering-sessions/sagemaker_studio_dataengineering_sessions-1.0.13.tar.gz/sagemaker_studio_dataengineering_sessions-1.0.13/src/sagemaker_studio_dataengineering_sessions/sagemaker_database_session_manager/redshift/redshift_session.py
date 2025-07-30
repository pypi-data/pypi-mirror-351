import os

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import CONNECTION_TYPE_REDSHIFT

from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.redshift.redshift_config import Config
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.sagemaker_database_session_manager import SageMakerDatabaseSessionManager
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.redshift.connection_transformer import get_redshift_connection, \
    AUTH_TYPE_SECRET_MANAGER, get_redshift_connection_credentials
from sagemaker_studio_dataengineering_sessions.sagemaker_database_session_manager.utils.common_utils import get_redshift_serverless_gamma_endpoint, \
    get_redshift_gamma_endpoint

REDSHIFT_HOST_KEYWORD = "redshift.amazonaws"
REDSHIFT_DEV_HOST_KEYWORD = "redshift-dev.amazonaws"

class RedshiftSession(SageMakerDatabaseSessionManager):
    def __init__(self, connection_name: str):
        self.connection_details = get_redshift_connection(connection_name, self.get_logger())
        super().__init__(connection_name)
        self.config = Config()

    def get_connection_parameter(self) -> dict:
        # https://code.amazon.com/packages/SMUnoSQLExecution/blobs/178ea494faca9f65a20d64e1358713c0f59eb381/--/src/amazon_sagemaker_sql_execution/redshift/models.py#L37
        connection_properties: dict = {"host": self.connection_details.host,
                                       "database": self.connection_details.database,
                                       "port": self.connection_details.port,
                                       "connection_type": CONNECTION_TYPE_REDSHIFT,
                                       "region": self.connection_details.region}
        is_gamma = os.getenv("AWS_STAGE", None) == "GAMMA"
        gamma_endpoint = get_redshift_gamma_endpoint(self.connection_details.region)
        serverless_gamma_endpoint = get_redshift_serverless_gamma_endpoint(self.connection_details.region)
        if self.connection_details.auth_type == AUTH_TYPE_SECRET_MANAGER:
            username, password = get_redshift_connection_credentials(self.connection_details.connection_id)
            connection_properties["user"] = username
            connection_properties["password"] = password
            # for Redshift Cluster, cluster_identifier is required, which is not required for Redshift-Serverless
            # sample host:
            # RS Cluster: default-rs-cluster.cmlomtaja7gk.us-west-2.redshift.amazonaws.com
            # RS Workgroup: default-workgroup.123456789012.us-west-2.redshift-serverless.amazonaws.com
            if REDSHIFT_HOST_KEYWORD in self.connection_details.host or REDSHIFT_DEV_HOST_KEYWORD in self.connection_details.host:
                connection_properties["cluster_identifier"] = self.connection_details.host.split('.')[0]
                if is_gamma:
                    connection_properties["endpoint_url"] = gamma_endpoint
            else:
                connection_properties["serverless_work_group"] = self.connection_details.host.split('.')[0]
                if is_gamma:
                    connection_properties["endpoint_url"] = serverless_gamma_endpoint
        # At the time of this commit, the else logic would be FEDERATED
        # We set the default case to IAM mode
        # in case redshiftAuthType is missing from connection to be backward compatible
        else:
            # IAM authentication is set to be True.
            # We use an AWS profile which is created in SageMakerConnectionMagic
            # https://code.amazon.com/packages/SageMakerConnectionMagic/blobs/93998b3d11d8f65d7c6e52f0d04638d6862ad454/--/sagemaker_connection_magic/sagemaker_connection_magic.py#L187
            # The profile will fetch creds for default IAM connection
            connection_properties["iam"] = True
            connection_properties["profile"] = self.connection_details.connection_id
            # for Redshift Cluster, cluster_identifier is required, which is not required for Redshift-Serverless
            # sample host:
            # RS Cluster: default-rs-cluster.cmlomtaja7gk.us-west-2.redshift.amazonaws.com
            # RS Workgroup: default-workgroup.851725315372.us-west-2.redshift-serverless.amazonaws.com
            if REDSHIFT_HOST_KEYWORD in self.connection_details.host or REDSHIFT_DEV_HOST_KEYWORD in self.connection_details.host:
                connection_properties["cluster_identifier"] = self.connection_details.host.split('.')[0]
                # A special flag to instruct redshift_connector to use Redshift:GetClusterCredentialsWithIam API
                # Ref: https://github.com/aws/amazon-redshift-python-driver/blob/26fc02dd860a31daf31b92b4ccf1ef66a09f3cdf/redshift_connector/iam_helper.py#L84-L89
                connection_properties["group_federation"] = True
                if is_gamma:
                    connection_properties["endpoint_url"] = gamma_endpoint
            else:
                connection_properties["serverless_work_group"] = self.connection_details.host.split('.')[0]
                if is_gamma:
                    connection_properties["endpoint_url"] = serverless_gamma_endpoint
        return connection_properties