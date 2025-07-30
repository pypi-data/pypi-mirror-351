import streamlit as st
from dadosfera.services.s3 import get_s3_bucket_size


def get_storage_usage_in_gb(bucket_name, prefix):
    size_in_bytes = get_s3_bucket_size(bucket_name=bucket_name, prefix=prefix)
    size_in_gb = size_in_bytes / (1_024 * 1_024 * 1_024)
    return size_in_gb
