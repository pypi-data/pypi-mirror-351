import csv
import json
from pathlib import Path
from typing import Any, Iterator, Literal
import jsonschema
import jsonref
import jsonschema_fill_default
from pydantic import BaseModel, FilePath, model_validator


class DataFormat(BaseModel):
    type: Literal["json_schema"] = "json_schema"
    strict: bool = True
    json_schema: dict[str, Any]

    @model_validator(mode='after')
    def is_valid_json_schema(self) -> "DataFormat":
        jsonschema.Draft202012Validator.check_schema(self.json_schema)
        return self


def validate(instance: dict | list, data_format: DataFormat) -> dict | list:
    schema = jsonref.replace_refs(data_format.json_schema)
    jsonschema.validate(instance, schema)  # type: ignore
    instance_with_defaults = jsonschema_fill_default.fill_default(instance, schema)  # type: ignore
    jsonschema.validate(instance_with_defaults, schema)  # type: ignore
    return instance_with_defaults


def read_csv(file_name: FilePath, **kwargs) -> Iterator[dict]:
    with open(file_name, newline="") as csv_file:
        for row in csv.DictReader(csv_file, **kwargs):
            yield row


def read_tsv(file_name: FilePath, **kwargs) -> Iterator[dict]:
    return read_csv(file_name, delimiter="\t", **kwargs)


def read_ndjson(file_name: FilePath) -> Iterator[dict]:
    with open(file_name) as ndjson_file:
        for line in ndjson_file:
            trimmed_line = line.strip()
            if trimmed_line != "":
                yield json.loads(trimmed_line)


def read_data(file_name: FilePath, file_type: str | None = None, **kwargs) -> Iterator[dict]:
    if type(file_name) is str:
        return read_data(Path(file_name), file_type=file_type, **kwargs)
    if file_type == "csv" or file_name.suffix == ".csv":
        return read_csv(file_name, **kwargs)
    if file_type == "tsv" or file_name.suffix == ".tsv":
        return read_tsv(file_name, **kwargs)
    if file_type == "ndjson" or file_name.suffix == ".ndjson":
        return read_ndjson(file_name, **kwargs)
    raise ValueError(f"Unknown file type of file {file_name}")
