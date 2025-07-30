import boto3
import logging

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import DATAZONE_DOMAIN_REGION


class StsGateway:
    def __init__(self):
        self.sts_client = None
        self.logger = logging.getLogger(__name__)

    def initialize_default_clients(self):
        self.logger.info("Initializing default sts client.")
        self.initialize_clients(region=DATAZONE_DOMAIN_REGION)
        self.logger.info("Initializing default sts client done.")

    def initialize_clients(self, profile=None, region=None):
        # add the private model of datazone
        self.logger.info(f"Initializing sts client. region = {region}")
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.sts_client = session.client("sts", region_name=region)

    def get_source_identity(self):
        try:
            response = self.sts_client.get_caller_identity()
            return response['Arn'].split('/')[-1].split('@')[0]
        except Exception as e:
            self.logger.error("Failed to retrieve source identity.", e)
            raise e
