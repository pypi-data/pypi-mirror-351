import os
import tempfile
from dadosfera.utils import consts
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import TextLoader, CSVLoader


class S3DirectoryLoader(BaseLoader):
    """Loading logic for loading documents from s3."""

    def __init__(self, bucket: str, loader: BaseLoader = TextLoader, prefix: str = ""):
        """Initialize with bucket and key name."""
        self.bucket = bucket
        self.prefix = prefix
        self.loader = loader

    def load(self):
        """Load documents."""
        try:
            import boto3
        except ImportError:
            raise ValueError(
                "Could not import boto3 python package. "
                "Please install it with `pip install boto3`."
            )
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(self.bucket)
        docs = []
        for obj in bucket.objects.filter(Prefix=self.prefix):
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{obj.key}"
                os.makedirs(os.path.dirname(file_path))
                bucket.download_file(obj.key, file_path)
                loader = self.loader(file_path, encoding="utf-8")

                if isinstance(loader, TextLoader):
                    docs.extend(loader.load_and_split())
                elif isinstance(loader, CSVLoader):
                    docs.extend(loader.load())
        return docs


def create_deeplake_dataset_from_s3_prefix(
    source_prefix: str,
    target_prefix: str,
    dataset_name: str,
    dataset_type: str = "text",
):

    if dataset_type == "text":
        loader = S3DirectoryLoader(consts.DADOSFERA_LANDING_ZONE, prefix=source_prefix)
    elif dataset_type == "csv":
        loader = S3DirectoryLoader(
            consts.DADOSFERA_LANDING_ZONE, prefix=source_prefix, loader=CSVLoader
        )

    docs = loader.load_and_split()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()

    dataset_path = (
        f"s3://{consts.DADOSFERA_LANDING_ZONE}/{target_prefix}/{dataset_name}"
    )
    DeepLake.from_documents(texts, embeddings, dataset_path=dataset_path)

    return dataset_path
