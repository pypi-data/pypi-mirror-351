import yaml
from pydantic import BaseModel, ValidationError

class FieldSchema(BaseModel):
    type: str
    faker: str | None = None
    primary_key: bool = False
    max_length: int | None = None  # Thêm max_length

class TableSchema(BaseModel):
    fields: dict[str, FieldSchema]

class Schema(BaseModel):
    tables: dict[str, TableSchema]

def load_schema(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Schema(**data)
    except (yaml.YAMLError, ValidationError) as e:
        raise ValueError(f"Lỗi khi đọc schema: {e}")