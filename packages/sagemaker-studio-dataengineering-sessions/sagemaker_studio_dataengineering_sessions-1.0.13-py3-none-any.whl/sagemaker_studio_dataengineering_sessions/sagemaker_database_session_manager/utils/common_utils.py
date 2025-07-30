def get_redshift_gamma_endpoint(region="us-east-1"):
    # TODO support other partition
    return f"https://aws-cookie-monster-qa.amazon.com"


def get_redshift_serverless_gamma_endpoint(region="us-east-1"):
    # TODO support other partition
    return f"https://qa.{region}.serverless.redshift.aws.a2z.com"


def get_athena_gamma_endpoint(region="us-east-1"):
    # TODO support other partition
    return f"https://athena-webservice-preprod.{region}.amazonaws.com/"
