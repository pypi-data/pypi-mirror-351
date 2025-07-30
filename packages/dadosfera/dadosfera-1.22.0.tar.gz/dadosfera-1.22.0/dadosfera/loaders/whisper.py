import os
import tempfile
import time
import logging
import openai
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dadosfera.utils.file import compute_sha1_from_content

logger = logging.getLogger(__name__)


class WhisperGenericLoader:
    def __init__(self, raw_document: bytes, file_name: str) -> None:
        self.raw_document = raw_document
        self.file_name = file_name
        self.dateshort = time.strftime("%Y%m%d-%H%M%S")

    def load(self):
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=self.file_name,
            ) as tmp_file:
                tmp_file.write(self.raw_document)
                tmp_file.flush()
                tmp_file.close()
                temp_filename = tmp_file.name

                with open(tmp_file.name, "rb") as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)

            logger.info(f"The following transcript was generated: {transcript.text}")

            logger.info("Computing SHA1 from content")
            file_sha = compute_sha1_from_content(
                transcript.text.encode(
                    "utf-8"
                )  # pyright: ignore reportPrivateUsage=none
            )

            logger.info("Computing File Size from content")
            file_size = len(
                transcript.text.encode(
                    "utf-8"
                )  # pyright: ignore reportPrivateUsage=none
            )

            chunk_size = 500
            chunk_overlap = 0

            logger.info("Splitting file using tiktoken encoder")
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
            texts = text_splitter.split_text(transcript.text)

            logger.info("Successfully splitted the content into texts")

            docs_with_metadata = [
                Document(
                    page_content=text,
                    metadata={
                        "file_sha1": file_sha,
                        "file_size": file_size,
                        "file_name": self.file_name,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "date": self.dateshort,
                    },
                )
                for text in texts
            ]
            return docs_with_metadata
        finally:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
