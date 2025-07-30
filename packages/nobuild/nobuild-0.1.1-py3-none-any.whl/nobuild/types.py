from typing import TypedDict, Literal

class NoBuildConfig(TypedDict):
    name: str
    version: str
    description: str

class BuildConfig(TypedDict):
    filename: str

class TargetConfig(TypedDict):
    distro: str
    version: str
    architecture: Literal["amd64"]

class Config(TypedDict):
    main: NoBuildConfig
    build: BuildConfig
    base: TargetConfig
    extra: dict

class Metadata(TypedDict):
    distro: str # Distro Name
    description: str
    author: str # Author of this nobuild module
    avaliable_features: list[str]