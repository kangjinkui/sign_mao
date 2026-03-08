from pathlib import Path


def validate_upload_filename(filename: str) -> None:
    if not filename:
        raise ValueError("EMPTY_FILENAME")
    ext = Path(filename).suffix.lower()
    if ext not in {".xlsx"}:
        raise ValueError("INVALID_FILE_TYPE")
