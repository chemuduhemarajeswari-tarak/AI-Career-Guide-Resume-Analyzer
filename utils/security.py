import os
import re
from werkzeug.utils import secure_filename


VALID_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024


def is_allowed_extension(filename):
    if not filename:
        return False
    extension = os.path.splitext(filename)[1].lower()
    return extension in VALID_EXTENSIONS


def safe_upload_name(filename):
    name = secure_filename(filename)
    if not name:
        return 'upload_file'
    return name


def validate_file_size(file_storage):
    if file_storage is None:
        return False
    if file_storage.content_length and file_storage.content_length > MAX_FILE_SIZE:
        return False
    try:
        file_storage.stream.seek(0, os.SEEK_END)
        size = file_storage.stream.tell()
        file_storage.stream.seek(0)
        return size <= MAX_FILE_SIZE
    except Exception:
        return False


def sanitize_text(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()
