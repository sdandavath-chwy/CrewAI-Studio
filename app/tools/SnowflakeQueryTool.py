import boto3
import json
from botocore.exceptions import ClientError
from snowflake.snowpark import Session
from crewai.tools import BaseTool
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pydantic import Field
from typing import Literal



def get_account_id():
    client = boto3.client("sts")
    return client.get_caller_identity()["Account"]

def get_env():
    account_id = get_account_id()
    if account_id == '977247693856':
        return 'dev'
    elif account_id == '204130544204':
        return 'prd'
    elif account_id == '894285811264':
        return 'stg'
    else:
        return None

def get_secret(secret_name):
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    return json.loads(get_secret_value_response['SecretString'])

def get_password(private_key):
    p_key = serialization.load_pem_private_key(
        private_key.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    return p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def get_snowflake_session():
    env = get_env()
    secret_name = f"/chewy/{env}/us-east-1/worker_sc_fp/airflow/connections/svc_sc_fp_worker"
    secret = get_secret(secret_name)
    private_key = secret["extra"]["private_key_content"]
    pkb = get_password(private_key)
    return Session.builder.configs({
        "account": secret["extra"]["account"],
        "user": secret["login"],
        "private_key": pkb,
        "database": secret["extra"]["database"],
        "warehouse": secret["extra"]["warehouse"],
        "schema": "SC_FORECAST_SANDBOX"
    }).create()


class SnowflakeQueryTool(BaseTool):
    name: Literal["Snowflake Query Tool"] = "Snowflake Query Tool"
    description: Literal["Execute a SQL query against the Snowflake forecasting sandbox."] = (
        "Execute a SQL query against the Snowflake forecasting sandbox."
    )

    def _run(self, query: str) -> str:
        try:
            session = get_snowflake_session()
            df = session.sql(query).to_pandas()
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing query: {e}"