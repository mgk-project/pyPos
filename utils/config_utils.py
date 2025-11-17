import json
import os
from utils.path_utils import get_project_base_dir

CONFIG_FILE = os.path.join(get_project_base_dir(), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "api_base_url": "https://beta.mayagrahakencana.com",
            "client_name": "Default Client",
            "request_timeout": 3
        }
        save_config(default_config)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    defaults = {
        "api_base_url": "https://beta.mayagrahakencana.com",
        "client_name": "Default Client",
        "request_timeout": 3,
    }
    for key, value in defaults.items():
        config.setdefault(key, value)

    return config

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)