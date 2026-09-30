"""Input and upload validation shared by the Flask routes."""

from __future__ import annotations

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def required_text(value: object, label: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required.")
    result = value.strip()
    if len(result) > maximum:
        raise ValueError(f"{label} must be {maximum} characters or fewer.")
    return result


def safe_upload(file: FileStorage) -> tuple[str, bytes]:
    filename = secure_filename(file.filename or "")
    if not filename or "." not in filename:
        raise ValueError("Choose a PDF, DOCX, or TXT resume file.")
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF, DOCX, and TXT files are supported.")
    content = file.stream.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise ValueError("The selected resume file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Resume files must be 5 MB or smaller.")
    signatures = {"pdf": content.startswith(b"%PDF"), "docx": content.startswith(b"PK")}
    if extension in signatures and not signatures[extension]:
        raise ValueError(f"The file contents do not look like a valid {extension.upper()} file.")
    return filename, content
