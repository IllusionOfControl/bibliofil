import hashlib
import pathlib
from typing import IO


def calculate_md5(file_path_or_obj: str | pathlib.Path | IO) -> str | None:
    hash_md5 = hashlib.md5()
    try:
        if isinstance(file_path_or_obj, (str, pathlib.Path)):
            with open(file_path_or_obj, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
        else:
            for chunk in iter(lambda: file_path_or_obj.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None
