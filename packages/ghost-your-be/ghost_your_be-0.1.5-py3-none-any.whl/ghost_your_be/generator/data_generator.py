from faker import Faker
from .vprovider import VietnamProvider
from .schema_loader import load_schema

class DataGenerator:
    def __init__(self, schema_path):
        self.schema = load_schema(schema_path)
        self.faker = Faker()
        self.faker.add_provider(VietnamProvider)

    def generate(self, count, table_name=None):
        data = []
        tables_to_generate = [table_name] if table_name else self.schema.tables.keys()
        
        for table_name in tables_to_generate:
            if table_name not in self.schema.tables:
                raise ValueError(f"Table '{table_name}' not found in schema")
                
            table_schema = self.schema.tables[table_name]
            for _ in range(count):
                row = {}
                for field_name, field_schema in table_schema.fields.items():
                    if field_schema.faker:
                        value = getattr(self.faker, field_schema.faker)()
                        # Cắt dữ liệu nếu có max_length
                        if field_schema.max_length and isinstance(value, str):
                            value = value[:field_schema.max_length]
                        row[field_name] = value
                    else:
                        if field_schema.type == "integer":
                            row[field_name] = self.faker.random_int(1, 1000)
                        elif field_schema.type == "string":
                            row[field_name] = self.faker.word()
                data.append(row)
        return data