from deepdiff import DeepDiff
import requests
from rich.console import Console
from rich.table import Table
import click

class APIDiff:
    def __init__(self, mock_url, real_url):
        self.mock_url = mock_url
        self.real_url = real_url

    def compare(self):
        try:
            mock_response = requests.get(self.mock_url).json()
            real_response = requests.get(self.real_url).json()
        except requests.RequestException as e:
            print(f"Lỗi khi gọi API: {e}")
            return

        diff = DeepDiff(mock_response, real_response, ignore_order=True)
        
        console = Console()
        table = Table(title="Kết quả so sánh API")
        table.add_column("Loại thay đổi", style="cyan")
        table.add_column("Chi tiết", style="magenta")
        
        if not diff:
            console.print("[green]Mock API và API thật khớp hoàn toàn![/green]")
        else:
            for change_type, changes in diff.items():
                for change in changes:
                    table.add_row(change_type, str(change))
            console.print(table)
            
# @click.command()
# @click.option("--mock", help="Mock API URL")
# @click.option("--real", help="Real API URL")
# def compare(mock, real):
#     differ = APIDiff(mock, real)
#     differ.compare()