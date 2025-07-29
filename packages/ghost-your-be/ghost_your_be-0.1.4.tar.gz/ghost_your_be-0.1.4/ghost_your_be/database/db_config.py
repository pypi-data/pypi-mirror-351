import requests
import yaml
from pydantic import BaseModel, create_model

class APISchemaGenerator:
    def __init__(self, api_url):
        self.api_url = api_url

    def generate_schema(self):
        response = requests.get(self.api_url)
        response.raise_for_status()
        data = response.json()

        schema = {"tables": {"dynamic_table": {"fields": {}}}}
        sample_data = data[0] if isinstance(data, list) else data
        for key, value in sample_data.items():
            schema["tables"]["dynamic_table"]["fields"][key] = {
                "type": type(value).__name__,
                "faker": f"vietnam_{key}" if key in ["name", "phone", "address"] else None,
                "primary_key": key == "id"
            }
        return schema

    def save_schema(self, output_path):
        schema = self.generate_schema()
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(schema, f, allow_unicode=True)