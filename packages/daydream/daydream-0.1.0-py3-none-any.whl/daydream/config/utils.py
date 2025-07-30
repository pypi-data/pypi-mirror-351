from pathlib import Path
from typing import Any

import typer
import yaml
from pydantic import BaseModel

CONFIG_ROOT = Path(typer.get_app_dir("daydream", force_posix=True))
DEFAULT_CONFIG_FILE = Path(__file__).parent / "defaults.yaml"


class PluginConfig(BaseModel):
    enabled: bool = True
    config: dict[str, Any] = {}


class Config(BaseModel):
    plugins: dict[str, PluginConfig] = {}


def get_config_dir(profile: str, create: bool = False) -> Path:
    config_dir = CONFIG_ROOT / "profiles" / profile

    # Create a new config directory if it doesn't exist.
    if not config_dir.exists():
        if not create:
            raise FileNotFoundError(f"Config directory {config_dir} does not exist")
        config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def load_config(profile: str, create: bool = False) -> Config:
    config_path = get_config_dir(profile, create) / "config.yaml"

    # Create a new config file if it doesn't exist.
    if not config_path.exists():
        if not create:
            raise FileNotFoundError(f"Config file {config_path} does not exist")
        config_path.write_text(DEFAULT_CONFIG_FILE.read_text())

    # Merge the default config with the user config, with the user config taking precedence.
    return Config(
        **{
            **yaml.safe_load(DEFAULT_CONFIG_FILE.read_text()),
            **yaml.safe_load(config_path.read_text()),
        }
    )
