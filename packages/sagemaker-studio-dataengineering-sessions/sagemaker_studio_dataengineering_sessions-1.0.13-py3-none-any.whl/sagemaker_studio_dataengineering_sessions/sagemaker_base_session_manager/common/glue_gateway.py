import boto3
import os
import logging

from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import DATAZONE_DOMAIN_REGION


class GlueGateway:
    def __init__(self):
        self.glue_client = None
        self.logger = logging.getLogger(__name__)

    def initialize_default_clients(self):
        self.logger.info("Initializing default glue client.")
        self.initialize_clients(region=DATAZONE_DOMAIN_REGION)
        self.logger.info("Initializing default glue client done.")

    def initialize_clients(self, profile=None, region=None, endpoint_url=None):
        # add the private model of datazone
        self.logger.info(f"Initializing glue client. region = {region} endpoint = {endpoint_url}")
        os.environ['AWS_DATA_PATH'] = self._get_aws_model_dir()
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        if endpoint_url:
            self.glue_client = session.client("glue", region_name=region, endpoint_url=endpoint_url)
        else:
            self.glue_client = session.client("glue", region_name=region)

    def get_catalogs(self, parent_catalog_id=None):
        self.logger.info(f"get_catalogs start. parent_catalog_id = {parent_catalog_id}")
        next_token = None
        catalogs = []
        while True:
            if next_token:
                response = self.glue_client.get_catalogs(Recursive=True, HasDatabases=True, NextToken=next_token)
            else:
                response = self.glue_client.get_catalogs(Recursive=True, HasDatabases=True)
            catalogs.extend(response['CatalogList'])
            if not 'NextToken' in response:
                break
            else:
                next_token = response['NextToken']
        self.logger.info("get_catalogs done.")
        return catalogs

    def _get_aws_model_dir(self):
        # TODO: remove until aws model is public
        try:
            import sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager
            path = os.path.dirname(sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.__file__)
            return path + "/boto3_models"
        except ImportError:
            raise RuntimeError("Unable to import sagemaker_base_session_manager, thus cannot initialize datazone client.")
