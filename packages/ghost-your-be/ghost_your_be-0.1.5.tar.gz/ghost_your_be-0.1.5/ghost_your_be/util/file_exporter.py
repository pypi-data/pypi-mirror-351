import json
import pandas as pd

def export_to_file(data, output_path):
    if output_path.endswith(".json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif output_path.endswith(".csv"):
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding="utf-8")
    else:
        raise ValueError("Định dạng file không được hỗ trợ!")