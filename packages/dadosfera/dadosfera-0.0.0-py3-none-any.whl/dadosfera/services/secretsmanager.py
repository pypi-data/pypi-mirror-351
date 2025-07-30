import json

def get_credentials(secret_id: str) -> dict:
    """Retrieve and parse credentials from AWS Secrets Manager.

    This function retrieves a secret from AWS Secrets Manager and parses its JSON content.
    It uses the default AWS credentials from the environment or AWS configuration files
    and assumes the secret is stored as a JSON string.

    Args:
        secret_id (str): The identifier of the secret in AWS Secrets Manager.
            Can be the secret name or ARN.
            Example: "my-app/production/db-credentials" or
            "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-123abc"

    Returns:
        dict: The parsed JSON content of the secret.
            Contains key-value pairs stored in the secret.
            Example: {"username": "admin", "password": "secret123"}

    Raises:
        botocore.exceptions.ClientError: When the secret cannot be retrieved.
            Common cases:
            - Secret not found
            - Insufficient permissions
            - Invalid region
            - Network issues
        json.JSONDecodeError: When the secret string is not valid JSON.
        boto3.exceptions.NoCredentialsError: When AWS credentials are not available.

    Example:
        >>> credentials = get_credentials("my-app/production/db-credentials")
        >>> print(credentials["username"])
        admin

    Notes:
        - Uses the us-east-1 region by default
        - Requires appropriate AWS credentials and permissions
        - Assumes the secret is stored as a JSON string
        - Uses the default boto3 session

    See Also:
        - AWS Secrets Manager documentation:
          https://docs.aws.amazon.com/secretsmanager/latest/userguide/
        - boto3 Secrets Manager documentation:
          https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
    """
    import boto3
    session = boto3.Session()
    secrets_manager_client = session.client("secretsmanager", region_name="us-east-1")
    response = secrets_manager_client.get_secret_value(SecretId=secret_id)
    return json.loads(response["SecretString"])
