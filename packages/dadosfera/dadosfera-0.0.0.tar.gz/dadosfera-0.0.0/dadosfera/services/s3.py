import boto3
from typing import Optional, Union, Dict, Any, List
import logging
import chardet

logger = logging.getLogger(__name__)

def list_s3_objects(
    bucket_name: str,
    prefix: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List objects in an S3 bucket with pagination support.

    This function lists objects in an AWS S3 bucket under a specified prefix,
    handling pagination automatically. It filters out zero-byte objects and
    validates the response status for each page of results.

    Args:
        bucket_name (str): Name of the S3 bucket.
            Example: "my-company-data-bucket"
        
        prefix (str): Prefix to filter objects in the bucket.
            Acts like a folder path in the S3 bucket.
            Example: "data/2024/01/" or "logs/"
        
        aws_access_key_id (Optional[str], optional): AWS access key ID.
            If not provided, falls back to default credentials.
            Defaults to None.
            
        aws_secret_access_key (Optional[str], optional): AWS secret access key.
            If not provided, falls back to default credentials.
            Defaults to None.

    Returns:
        List[Dict[str, Any]]: List of S3 object metadata dictionaries.

    Raises:
        Exception: When S3 API returns a non-200 status code.
        
        botocore.exceptions.ClientError: When AWS API calls fail.
            Common cases:
            - Invalid credentials
            - Insufficient permissions
            - Bucket does not exist
            - Network issues
        
        boto3.exceptions.NoCredentialsError: When no AWS credentials are available
            and none are provided.

    Examples:
        List all objects in a specific prefix:
        >>> objects = list_s3_objects('my-bucket', 'data/2024/')
        >>> for obj in objects:
        ...     print(f"Found {obj['Key']} of size {obj['Size']}")

        Using explicit credentials:
        >>> objects = list_s3_objects(
        ...     'my-bucket',
        ...     'logs/',
        ...     aws_access_key_id='AKIAXXXXXXXXXXXXXXXX',
        ...     aws_secret_access_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        ... )

    Notes:
        - Uses us-east-1 region by default
        - Automatically handles pagination of results
        - Filters out zero-byte objects (typically folder markers)
        - Uses boto3 session for AWS API calls
        - Validates HTTP status code for each page
    
    Performance Considerations:
        - For buckets with many objects, this function may make multiple API calls
        - Consider using prefix to narrow down results
        - Response time depends on number of objects and network conditions
        - Memory usage scales with number of non-zero-byte objects

    See Also:
        - AWS S3 ListObjects documentation:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjects.html
        - boto3 S3 documentation:
          https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    """
    session = boto3.Session()
    client = session.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="us-east-1"
    )

    paginator = client.get_paginator("list_objects")
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    s3_objects = []
    for page in page_iterator:
        # Just validating if the request was successful
        if page["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception(
                "received a status code different than 200 "
                f"status_code: {page['ResponseMetadata']['HTTPStatusCode']}"
            )
        if "Contents" in page:
            for s3_object in page["Contents"]:
                if s3_object["Size"] > 0:
                    s3_objects.append(s3_object)
    return s3_objects

def get_objects_from_s3(bucket_name: str, prefix: str) -> List[Dict[str, str]]:
    """Retrieve and decode objects from AWS S3 with automatic character encoding detection.

    This function retrieves objects from an AWS S3 bucket, automatically detects
    their character encoding using chardet, and returns their decoded contents.
    It uses the list_s3_objects function to get object metadata before downloading
    each object individually.

    Args:
        bucket_name (str): Name of the S3 bucket to search.
            Example: "my-company-data-bucket"
        
        prefix (str): Prefix (folder path) to filter objects in the bucket.
            Example: "data/2024/01/" or "logs/"

    Returns:
        List[Dict[str, str]]: List of dictionaries containing file information.
            Each dictionary contains:
            - file_content (str): Decoded content of the file
            - key (str): Full S3 key/path of the object
            - file_name (str): Extracted file name without extension
            Example: [
                {
                    'file_content': 'content of file1...',
                    'key': 'data/2024/01/file1.txt',
                    'file_name': 'file1'
                },
                ...
            ]
            Returns empty list if no objects are found.

    Raises:
        botocore.exceptions.ClientError: When AWS API calls fail.
            Common cases:
            - Invalid credentials
            - Insufficient permissions
            - Bucket does not exist
            - Object does not exist
            - Network issues
        
        UnicodeDecodeError: When file content cannot be decoded with detected encoding.
        
        boto3.exceptions.NoCredentialsError: When no AWS credentials are available.

    Example:
        >>> objects = get_objects_from_s3('my-bucket', 'data/2024/')
        >>> for obj in objects:
        ...     print(f"File {obj['file_name']} content length: {len(obj['file_content'])}")

    Notes:
        - Uses us-east-1 region by default
        - Uses chardet to detect file encoding
        - Logs operations at INFO and DEBUG levels
        - Requires list_s3_objects function
        - Returns empty list instead of None when no objects found


    Dependencies:
        - boto3: AWS SDK for Python
        - chardet: Character encoding detection
        - logging: For operation logging
        - list_s3_objects: Custom function for listing S3 objects

    See Also:
        - AWS S3 GetObject documentation:
          https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
        - chardet documentation:
          https://chardet.readthedocs.io/en/latest/usage.html
    """
    session = boto3.Session()
    client = session.client('s3', region_name='us-east-1')

    logger.info(f"Listing objects in bucket {bucket_name} for prefix {prefix}")
    objects_metadata = list_s3_objects(bucket_name=bucket_name, prefix=prefix)
    logger.info(f"Found {len(objects_metadata)} objects")

    objects = []
    for object_metadata in objects_metadata:
        response = client.get_object(Bucket=bucket_name, Key=object_metadata['Key'])
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            body = response['Body'].read()

            encoding = chardet.detect(body[:10000])['encoding']
            if encoding is not None:
                body = body.decode(encoding)

            logger.debug(f"Detected encoding {encoding} for file {object_metadata['Key']}")
            objects.append({
                'file_content': body,
                'key': object_metadata['Key'],
                'file_name': object_metadata['Key'].split('/')[-1].split('.')[0]
            })

    return objects

def get_s3_bucket_size(bucket_name, prefix="", aws_access_key_id = None, aws_secret_access_key = None):
    """Calculates the size of the S3 bucket or prefix in bytes.


    Args:
        bucket_name (str): Name of the S3 bucket to search.
            Example: "my-company-data-bucket"
        
        prefix (str): Prefix (folder path) to filter objects in the bucket.
            Example: "data/2024/01/" or "logs/"
        aws_access_key_id (Optional[str], optional): AWS access key ID.
            If not provided, falls back to default credentials.
            Defaults to None.
            
        aws_secret_access_key (Optional[str], optional): AWS secret access key.
            If not provided, falls back to default credentials.
            Defaults to None.

    Returns:
        total_size (float): size of the S3 bucket

    Raises:
        botocore.exceptions.ClientError: When AWS API calls fail.
            Common cases:
            - Invalid credentials
            - Insufficient permissions
            - Bucket does not exist
            - Object does not exist
            - Network issues
        
        
    Example:
        >>> objects = get_objects_from_s3('my-bucket', 'data/2024/')
        >>> for obj in objects:
        ...     print(f"File {obj['file_name']} content length: {len(obj['file_content'])}")

    Notes:
        - Uses us-east-1 region by default

    Dependencies:
        - boto3: AWS SDK for Python

    """
    session = boto3.Session()
    client = session.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="us-east-1"
    )
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    total_size = 0
    for page in pages:
        for obj in page.get("Contents", []):
            total_size += obj["Size"]

    return total_size
