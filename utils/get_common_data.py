import json
from typing import Dict

def get_common_data(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)
