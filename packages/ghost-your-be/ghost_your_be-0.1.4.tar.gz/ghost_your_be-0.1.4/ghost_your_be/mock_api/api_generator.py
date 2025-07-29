from ..generator.data_generator import DataGenerator

class APIGenerator:
    def __init__(self, schema_path):
        """Khởi tạo APIGenerator với đường dẫn schema."""
        self.generator = DataGenerator(schema_path)

    def generate_response(self, endpoint, count=5, code=200, message="Success"):
        """Tạo dữ liệu giả cho một endpoint API."""
        # Giả sử endpoint tương ứng với tên bảng trong schema.yml
        data = self.generator.generate(count)
        return {
            "endpoint": endpoint,
            "count": count,
            "code": code,
            "data": data,
            "message": message,
        }