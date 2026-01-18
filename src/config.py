import hashlib
import json
from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str) -> Dict[str, Any]:
    cfg_path = Path(path)
    data = yaml.safe_load(cfg_path.read_text(encoding='utf-8'))
    return data


def config_hash(config: Dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()
