import boto3
from crewai.tools import BaseTool
from typing import Literal
import json

class S3FileQueryTool(BaseTool):
    name: Literal["S3 File Query Tool"] = "S3 File Query Tool"
    description: Literal["Reads the content of a file from the given S3 path."] = "Reads the content of a file from the given S3 path."

    def __init__(self, s3_path: str = None):
        super().__init__()
        self._s3_path = s3_path

    def _run(self, input_str: str = None) -> str:
        try:
            if not input_str:
                return "Missing input for S3 path."

            # Try to extract 'path' from JSON input
            try:
                parsed = json.loads(input_str)
                s3_path = parsed.get("path")
            except json.JSONDecodeError:
                s3_path = input_str  # fallback if not JSON

            if not s3_path or not s3_path.startswith("s3://"):
                return f"Invalid S3 path: '{s3_path}'. It must start with 's3://'."

            s3 = boto3.client("s3")
            bucket, key = s3_path.replace("s3://", "").split("/", 1)
            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            return content
        except Exception as e:
            return f"Error reading S3 file: {e}"