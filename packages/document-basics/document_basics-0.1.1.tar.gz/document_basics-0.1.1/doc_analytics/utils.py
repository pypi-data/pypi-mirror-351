import re


def to_valid_filename(name: str, replacement: str = "_") -> str:
    # Remove invalid characters (Windows + Unix reserved)
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    name = re.sub(invalid_chars, replacement, name)
    
    # Strip leading/trailing whitespace and dots
    name = name.strip().strip(".")

    # Optional: limit length (e.g., 255 chars for filenames)
    max_length = 255
    return name[:max_length] or "untitled"


def cast(obj, cls):
    return cls(obj) if not isinstance(obj, cls) else obj


