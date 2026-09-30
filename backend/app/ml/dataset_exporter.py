import os
import json
import csv
from typing import List, Dict, Any

class DatasetExporter:
    """
    Extracts and exports pose landmark and biomechanical feature sequences into dataset formats.
    """
    @staticmethod
    def export_to_json(data: Dict[str, Any], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def export_features_to_csv(feature_rows: List[Dict[str, Any]], output_path: str):
        if not feature_rows:
            return
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        headers = list(feature_rows[0].keys())
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(feature_rows)
