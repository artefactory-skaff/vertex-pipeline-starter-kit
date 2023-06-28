from pathlib import Path
from typing import Dict
import json

def load_config(pipeline_name: str, config_name: str) -> Dict:
    config_filepath = Path(__file__).parent.parent.parent / "configs" / pipeline_name / f"{config_name}.json"
    with open(config_filepath) as f:
        config = json.load(f)
    return config
