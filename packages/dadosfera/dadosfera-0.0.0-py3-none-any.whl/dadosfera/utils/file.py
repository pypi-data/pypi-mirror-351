import hashlib

def convert_bytes(bytes, precision=2):
    """Converts bytes into a human-friendly format."""
    abbreviations = ["B", "KB", "MB"]
    if bytes <= 0:
        return "0 B"
    size = bytes
    index = 0
    while size >= 1024 and index < len(abbreviations) - 1:
        size /= 1024
        index += 1
    return f"{size:.{precision}f} {abbreviations[index]}"


def compute_sha1_from_file(file_path):
    with open(file_path, "rb") as file:
        bytes = file.read()
        readable_hash = compute_sha1_from_content(bytes)
    return readable_hash


def compute_sha1_from_content(content):
    readable_hash = hashlib.sha1(content).hexdigest()
    return readable_hash
