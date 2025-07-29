import json
import os

import boto3
from botocore.exceptions import ClientError

from baresquare_sdk.core import exceptions, logger


def get_ssm_client():
    """Return an SSM client using the Singleton Pattern.

    :return: SSM client
    """
    global ssm_client
    if "ssm_client" not in globals() or ssm_client is None:
        if os.getenv("AWS_PROFILE") is not None:
            session = boto3.Session(profile_name=os.getenv("AWS_PROFILE"))
            ssm_client = session.client(service_name="ssm", region_name=os.getenv("PL_REGION"))
        else:
            ssm_client = boto3.client(service_name="ssm", region_name=os.getenv("PL_REGION", "us-east-1"))
    return ssm_client


def get_ssm_parameter(ssm_key: str, return_json: bool = False, **_) -> str | dict:
    """Retrieve parameter from AWS SSM.

    Args:
        ssm_key (str): The path to the parameter in AWS SSM
        return_json (bool): Whether to return the parameter as a json object
                            Defaults to False

    Returns:
        str | dict: The parameter value as a string or dictionary
    """
    logger.debug(f"Retrieving SSM param {ssm_key}")
    try:
        ssm_parameter = get_ssm_client().get_parameter(Name=ssm_key, WithDecryption=True)["Parameter"]["Value"]
        if return_json:
            return json.loads(ssm_parameter)
        return ssm_parameter
    except ClientError as e:
        logger.warning(f"Failed to retrieve SSM param from {ssm_key}")
        raise exceptions.ExceptionInfo(
            msg=f"Failed to retrieve SSM param from {ssm_key}",
            data={
                "ssm_parameter_name": ssm_key,
            },
        ) from e


def put_ssm_parameter(ssm_key: str, ssm_value: str, overwrite: bool, ssm_type="SecureString"):
    """Put parameter to AWS SSM.

    Args:
        ssm_key (str): The path to the parameter in AWS SSM
        ssm_value (str): The value of the SSM parameter
        overwrite (bool): Whether to overwrite an existing value for the SSM parameter
        ssm_type (str): one of 'String'|'StringList'|'SecureString'

    Returns:
        dict: Example: {'Version': 123,'Tier': 'Standard'|'Advanced'|'Intelligent-Tiering'}
    """
    logger.debug(f"Retrieving SSM param {ssm_key}")
    ssm_client = boto3.client(service_name="ssm", region_name=os.getenv("PL_REGION", "us-east-1"))
    try:
        ssm_client.put_parameter(Name=ssm_key, Value=ssm_value, Type=ssm_type, Overwrite=overwrite)
    except ClientError as error:
        logger.error(f"Failed to put SSM param {ssm_key}")
        raise error
