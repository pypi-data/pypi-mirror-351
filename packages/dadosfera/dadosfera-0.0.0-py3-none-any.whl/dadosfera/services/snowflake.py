import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dadosfera.services.secretsmanager import get_credentials
from snowflake.snowpark import Session

def serialize_private_key_for_session(private_key: str) -> bytes:
    """Serialize a PEM-formatted private key into DER-encoded PKCS#8 format.

    This function takes a PEM-formatted private key string and converts it into
    a DER-encoded PKCS#8 format suitable for session use. The function performs
    the following steps:
    1. Loads the PEM private key from string
    2. Converts it to DER encoding in PKCS#8 format
    3. Returns the unencrypted bytes

    Args:
        private_key (str): A PEM-formatted private key string.
            Must be a valid PEM-encoded private key.
            Example: "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----"

    Returns:
        bytes: The DER-encoded private key in PKCS#8 format.
            Returns raw bytes without encryption.
            Can be used directly in cryptographic operations.

    Raises:
        ValueError: If the private key string is invalid or corrupted.
        TypeError: If the input is not a string.
        cryptography.exceptions.UnsupportedAlgorithm: If the key format is not supported.

    Example:
        >>> pem_key = "-----BEGIN PRIVATE KEY-----\\nMIIE...\\n-----END PRIVATE KEY-----"
        >>> der_bytes = serialize_private_key_for_session(pem_key)
        >>> len(der_bytes)
        1234

    Notes:
        - The output is not encrypted and should be handled securely
        - Uses the cryptography library's default backend
        - Commonly used for preparing keys for TLS/SSL sessions

    See Also:
        - PKCS#8 Specification: https://tools.ietf.org/html/rfc5208
        - PEM Format: https://tools.ietf.org/html/rfc7468
    """
    p_key = serialization.load_pem_private_key(
        private_key.encode("utf-8"),
        password=None,
        backend=default_backend()
    )
    p_key_private_bytes = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return p_key_private_bytes


def _get_connection_parameters(secret_id):
    secret_values = get_credentials(secret_id=secret_id)

    connection_parameters = {
        "user": secret_values["username"],
        "private_key": serialize_private_key_for_session(secret_values["private_key"]),
        "database": secret_values["database"],
        "role": secret_values["role"],
        "account": f"{secret_values['account']}.{secret_values['region']}",
        "warehouse": secret_values['warehouse']
    }

    return connection_parameters

def get_snowpark_session(secret_id):
    connection_parameters = _get_connection_parameters(secret_id)
    return Session.builder.configs(connection_parameters).create()

def get_snowflake_connector_session(secret_id):
    connection_parameters = _get_connection_parameters(secret_id)
    conn = snowflake.connector.connect(**connection_parameters)
    return conn.cursor()

def fetch_data_as_df(cursor, query):
    cursor.execute(query)
    data_list = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    return pd.DataFrame(data_list, columns=column_names)
