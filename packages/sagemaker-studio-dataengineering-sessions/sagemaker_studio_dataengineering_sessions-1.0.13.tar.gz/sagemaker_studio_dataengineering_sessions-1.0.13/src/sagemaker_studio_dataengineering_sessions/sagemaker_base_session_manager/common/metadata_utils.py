import json


def retrieve_sagemaker_metadata_from_file(logger=None):
    try:
        # Opening JSON file
        with open('/opt/ml/metadata/resource-metadata.json') as f:
            metadata = json.load(f)
            return metadata
    except Exception as e:
        if logger is not None:
            logger.error(f"Unable to retrieve sagemaker metadata from file: {e}")
        return None
