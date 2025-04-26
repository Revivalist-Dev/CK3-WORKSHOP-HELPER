import json
import os
from typing import Dict, Any, TypedDict, Optional


class Config(TypedDict):
    workshop_path: str
    local_mods_path: str
    output_path: str


DEFAULT_CONFIG: Config = {
    "workshop_path": "",
    "local_mods_path": "./mod_local",
    "output_path": "./local_mods"
}

CONFIG_PATH = 'config.json'


def load_config() -> Config:
    """Load configuration from file or return defaults"""
    try:
        with open(CONFIG_PATH, 'r') as config_file:
            content = config_file.read()
            loaded_config = json.loads(content)
            # Merge with defaults to ensure all keys exist
            return {**DEFAULT_CONFIG, **loaded_config}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()


def save_config(config: Config) -> None:
    """Save configuration to file"""
    with open(CONFIG_PATH, 'w') as config_file:
        content = json.dumps(config, indent=2)
        config_file.write(content)


def setup_config() -> Config:
    """Interactive setup for configuration"""
    print('CK3 Workshop Local Setup')
    print('=======================')

    config = load_config()

    # Ask for Steam Workshop path
    print('Enter your CK3 Steam Workshop mods directory')
    print('(e.g., C:/Program Files (x86)/Steam/steamapps/workshop/content/1158310):')
    workshop_path = input('> ')

    print('\nSetting up directories...')

    # Setup paths
    config["workshop_path"] = workshop_path
    
    # Ensure local mods directory exists
    try:
        os.makedirs(config["local_mods_path"], exist_ok=True)
        print(f"Created local mods directory: {config['local_mods_path']}")
    except Exception as error:
        print(f"Failed to create local mods directory: {error}")
        raise

    # Ensure output directory exists
    try:
        os.makedirs(config["output_path"], exist_ok=True)
        print(f"Created output directory: {config['output_path']}")
    except Exception as error:
        print(f"Failed to create output directory: {error}")
        raise

    save_config(config)
    
    print('\nConfiguration and directories setup successfully!')
    return config
