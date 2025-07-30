from pathlib import Path
from pydantic import BaseModel
import requests

from .data import DataFormat


class Task(BaseModel):
    id: str
    input_format: DataFormat
    output_format: DataFormat
    examples: list[dict] | None = None


def get_task(path: str, base_path: Path | None = None):
    try:
        response = requests.get(path, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise ValueError(f"Error fetching task from {path}: {response.text}")
        return Task.model_validate_json(response.json())
    except requests.exceptions.MissingSchema:
        if not Path(path).is_absolute():
            if base_path is not None:
                path = (base_path / path).__str__()
        with open(path) as file:
            return Task.model_validate_json(file.read())
