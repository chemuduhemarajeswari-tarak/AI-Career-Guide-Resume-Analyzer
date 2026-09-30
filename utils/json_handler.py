import json
from pathlib import Path


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def read_json(file_path, default=None):
    file_path = str(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()
            if not text:
                return default
            return json.loads(text)
    except FileNotFoundError:
        if default is not None:
            write_json(file_path, default)
        return default
    except (json.JSONDecodeError, TypeError, ValueError):
        if default is not None:
            write_json(file_path, default)
        return default


def write_json(file_path, payload):
    ensure_parent(file_path)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(payload, file, indent=2)


def append_json(file_path, payload):
    existing = read_json(file_path, [])
    if not isinstance(existing, list):
        existing = []
    existing.append(payload)
    write_json(file_path, existing)


def update_json(file_path, key, value):
    data = read_json(file_path, {})
    if not isinstance(data, dict):
        data = {}
    data[key] = value
    write_json(file_path, data)
