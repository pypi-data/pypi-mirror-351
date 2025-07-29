import json
import yaml
from typing import Dict, Any

class ConfigError(Exception):
    pass

def load_config(file_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file."""
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                return json.load(f)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                raise ConfigError("Unsupported config file format. Use JSON or YAML.")
    except Exception as e:
        raise ConfigError(f"Failed to load config: {str(e)}")
