import configparser
from typing import Dict

from .types import NoBuildConfig, BuildConfig, TargetConfig, Config

def load_config() -> Config:
    config = configparser.ConfigParser()
    config.read('./nobuild.conf')

    config_dict: Dict[str, Dict] = {section: dict(config[section]) for section in config.sections()}

    nobuild_config: NoBuildConfig = {
        'name': config_dict['main']['name'],
        'version': config_dict['main']['version'],
        'description': config_dict['main']['description']
    }

    build_config: BuildConfig = {
        'filename': config_dict['build']['filename'],
    }

    target_config: TargetConfig = {
        'distro': config_dict['base']['distro'],
        'version': config_dict['base']['version'],
        'architecture': config_dict['base']['architecture']
    }

    final_config: Config = {
        'main': nobuild_config,
        'build': build_config,
        'base': target_config,
        'extra': config_dict['extra']
    }
    return final_config