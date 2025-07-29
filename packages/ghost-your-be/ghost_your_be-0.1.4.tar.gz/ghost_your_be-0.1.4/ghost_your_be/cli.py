import click
import json
from .generator.data_generator import DataGenerator
from .database.db_connector import DBConnector
from .database.db_config import APISchemaGenerator
from .comparer.api_diff import APIDiff
from .mock_api.mock_server import run_mock_server
from .util.file_exporter import export_to_file
from .util.license import validate_license

@click.group()
def cli():
    """ghost-your-be CLI: Tạo dữ liệu giả, mock API và so sánh API."""
    pass

@cli.command()
@click.option("--schema", required=True, help="Path to schema YAML file")
@click.option("--count", default=5, help="Number of rows to generate")
@click.option("--db-url", help="Database URL (e.g., sqlite:///data.db, mysql+pymysql://user:pass@localhost:3306/db, mongodb://localhost:27017/db)")
@click.option("--table", help="Table/collection name to save data")
@click.option("--output", help="Output file (JSON or CSV)")
@click.option("--drop-table", is_flag=True, help="Xóa bảng/collection trước khi lưu dữ liệu")
def generate(schema, count, db_url, table, output, drop_table):
    """Tạo dữ liệu giả từ schema.yml và lưu vào database hoặc file."""
    generator = DataGenerator(schema_path=schema)
    data = generator.generate(count, table_name=table)
    
    if db_url and table:
        connector = DBConnector(db_url)
        if connector.save_to_db(table, data, drop_table=drop_table):
            click.echo(f"Lưu {count} bản ghi vào {table} ({db_url})")
        else:
            click.echo("Lưu vào database thất bại!")
        connector.close()
    elif output:
        export_to_file(data, output)
        click.echo(f"Dữ liệu đã được lưu vào {output}")
    else:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))

@cli.command()
@click.option("--api-url", required=True, help="API URL to generate schema")
@click.option("--output", default="schema.yml", help="Output schema file")
def generate_schema(api_url, output):
    """Tạo schema.yml từ API response."""
    generator = APISchemaGenerator(api_url)
    generator.save_schema(output)
    click.echo(f"Schema đã được lưu vào {output}")

@cli.command()
@click.option("--schema", required=True, help="Path to schema YAML file")
@click.option("--port", default=8000, help="Port for mock server")
def mock_api(schema, port):
    """Chạy mock API server."""
    import os
    os.environ["SCHEMA_PATH"] = schema
    run_mock_server(port=port)

@cli.command()
@click.option("--mock", required=True, help="Mock API URL")
@click.option("--real", required=True, help="Real API URL")
def compare(mock, real):
    """So sánh mock API và API thật."""
    differ = APIDiff(mock, real)
    differ.compare()

@cli.command()
@click.option("--key", required=True, help="License key for Pro version")
def activate(key):
    """Kích hoạt bản Pro."""
    if validate_license(key):
        click.echo("Kích hoạt bản Pro thành công!")
    else:
        click.echo("License key không hợp lệ!")

if __name__ == "__main__":
    cli()