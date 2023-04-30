from pathlib import Path
from typing import Dict
import json


def load_config(config_name: str) -> Dict:
    with open(Path(__file__).parent.parent.parent / "configs" / "my_first_pipeline" / f"{config_name}.json") as f:
        config = json.load(f)
    return config
