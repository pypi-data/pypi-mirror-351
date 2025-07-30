import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LayerConfig:
    contains_modules: List[str]
    upstream: Optional[List[str]]
    downstream: Optional[List[str]]


@dataclass
class LibConfig:
    upstream: Optional[List[str]]  # Layers allowed to use this lib


def load_config(
    config_path: Path,
) -> tuple[Dict[str, LayerConfig], Dict[str, LibConfig], List[str]]:
    with open(config_path, "rb") as f:
        raw_config = tomllib.load(f)

    layers_config = raw_config.get("layers", {})
    libs_config = raw_config.get("libs", {})
    exclude_modules = raw_config.get("exclude_modules", [])

    if not isinstance(exclude_modules, list):
        exclude_modules = []

    layers = {}
    for layer_name, layer_info in layers_config.items():
        upstream = layer_info.get("upstream", "none")
        if upstream == "none":
            upstream_parsed = None
        elif isinstance(upstream, list):
            upstream_parsed = upstream
        else:
            upstream_parsed = None

        downstream = layer_info.get("downstream", "none")
        if downstream == "none":
            downstream_parsed = None
        elif isinstance(downstream, list):
            downstream_parsed = downstream
        else:
            downstream_parsed = None

        contains_modules = layer_info.get("contains_modules", [])
        if not isinstance(contains_modules, list):
            contains_modules = []

        layers[layer_name] = LayerConfig(
            contains_modules=contains_modules,
            upstream=upstream_parsed,
            downstream=downstream_parsed,
        )

    libs = {}
    for lib_name, lib_info in libs_config.items():
        upstream = lib_info.get("upstream", "none")
        if upstream == "none":
            upstream_parsed = None
        elif isinstance(upstream, list):
            upstream_parsed = upstream
        else:
            upstream_parsed = None

        libs[lib_name] = LibConfig(upstream=upstream_parsed)

    return layers, libs, exclude_modules
