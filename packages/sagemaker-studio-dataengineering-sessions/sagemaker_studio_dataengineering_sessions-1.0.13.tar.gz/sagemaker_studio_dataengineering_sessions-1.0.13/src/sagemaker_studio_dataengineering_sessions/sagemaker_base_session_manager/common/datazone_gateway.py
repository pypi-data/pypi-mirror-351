import boto3
import botocore
import os
import logging

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import DOMAIN_ID, PROJECT_ID, DATAZONE_ENDPOINT_URL, \
    DATAZONE_DOMAIN_REGION, DOMAIN_EXECUTION_ROLE_PROFILE_NAME


class DataZoneGateway:
    def __init__(self):
        self.datazone_client = None
        self.logger = logging.getLogger(__name__)
        self.domain_identifier = None
        self.project_identifier = None

    def initialize_default_clients(self):
        self.logger.info("Initializing default clients.")
        self.initialize_clients(profile=DOMAIN_EXECUTION_ROLE_PROFILE_NAME,
                                region=DATAZONE_DOMAIN_REGION,
                                endpoint_url=DATAZONE_ENDPOINT_URL,
                                domain_identifier=DOMAIN_ID,
                                project_identifier=PROJECT_ID)
        self.logger.info("Initializing default clients done.")

    def initialize_clients(self, profile=None, region=None, endpoint_url=None, domain_identifier=None, project_identifier=None):
        if domain_identifier is None:
            raise RuntimeError("Domain identifier must be provided")
        self.domain_identifier = domain_identifier
        self.project_identifier = project_identifier
        self.datazone_client = self.create_datazone_client(profile, region, endpoint_url)

    def create_datazone_client(self, profile=None, region=None, endpoint_url=None):
        # add the private model of datazone
        os.environ['AWS_DATA_PATH'] = self._get_aws_model_dir()
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        if endpoint_url:
            return session.client("datazone", region_name=region, endpoint_url=endpoint_url)
        else:
            return session.client("datazone", region_name=region)

    def list_connections(self, project_id=None):
        self.logger.info(f"list_connections for project_id: {project_id}")
        next_token = None
        project_identifier = project_id if project_id else self.project_identifier
        connections = []
        while True:
            try:
                if next_token:
                    response = self.datazone_client.list_connections(domainIdentifier=self.domain_identifier,
                                                                     projectIdentifier=project_identifier,
                                                                     nextToken=next_token)
                else:
                    response = self.datazone_client.list_connections(domainIdentifier=self.domain_identifier,
                                                                     projectIdentifier=project_identifier)
                connections.extend(response['items'])
                if not 'nextToken' in response:
                    break
                else:
                    next_token = response['nextToken']
            except botocore.exceptions.ClientError as err:
                self.logger.error(f"Could not list connections."
                                  f"Request ID: {err.response['ResponseMetadata']['RequestId']}. "
                                  f"Http code: {err.response['ResponseMetadata']['HTTPStatusCode']}")
                raise err
        return connections

    def get_connection(self, connection_id, with_secret=False):
        self.logger.info(f"get_connection for connection id: {connection_id}")
        try:
            connection = self.datazone_client.get_connection(domainIdentifier=self.domain_identifier,
                                                             identifier=connection_id,
                                                             withSecret=with_secret)
            self.logger.info(f"get_connection done with connection id: {connection_id}")
            return connection
        except botocore.exceptions.ClientError as err:
            self.logger.error(f"Could not get_connection for connection id: {connection_id}. "
                              f"Request ID: {err.response['ResponseMetadata']['RequestId']}. "
                              f"Http code: {err.response['ResponseMetadata']['HTTPStatusCode']}")
            raise err


    def _get_aws_model_dir(self):
        # TODO: remove until aws model is public
        try:
            import sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager
            path = os.path.dirname(sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.__file__)
            return path + "/boto3_models"
        except ImportError:
            raise RuntimeError("Unable to import sagemaker_base_session_manager, "
                               "thus cannot initialize datazone client.")



