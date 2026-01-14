import hashlib
import pathlib
import re
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


def parse_to_bytes(size_str: str) -> int:
    units = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}

    match = re.match(r"^([-+]?[0-9.]+)\s*([a-zA-Z]?)$", size_str.strip())

    if not match:
        raise ValueError(f"Wrong format: {size_str}")

    number, unit = match.groups()
    number = float(number)
    unit = unit.upper()

    if unit in units:
        return int(number * units[unit])
    elif unit == "" or unit == "B":
        return int(number)
    else:
        raise ValueError(f"Unknown measure unit: {unit}")
