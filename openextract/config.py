"""Configuration loading and management for OpenExtract."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: str | Path) -> Dict[str, Any]:
    """Load YAML file and return as dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(pipeline_path: str | Path, settings_path: str | Path | None = None) -> Dict[str, Any]:
    """
    Load pipeline config and optionally merge with global settings.
    
    Args:
        pipeline_path: Path to pipeline YAML configuration
        settings_path: Optional path to global settings.yaml
    
    Returns:
        Merged configuration dictionary
    """
    pipeline_config = load_yaml(pipeline_path)
    
    if settings_path and Path(settings_path).exists():
        settings = load_yaml(settings_path)
        # Merge: pipeline config takes precedence
        return _merge_configs(settings, pipeline_config)
    
    return pipeline_config


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two config dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def resolve_api_key(provider_config: Dict[str, Any]) -> str:
    """
    Resolve API key from environment variable if specified.
    
    Args:
        provider_config: Provider configuration dictionary
    
    Returns:
        API key string
    
    Raises:
        ValueError: If api_key_env is specified but not found in environment
    """
    if "api_key_env" in provider_config:
        env_var = provider_config["api_key_env"]
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"Environment variable {env_var} not found for API key")
        return api_key
    elif "api_key" in provider_config:
        return provider_config["api_key"]
    else:
        raise ValueError("No api_key or api_key_env specified in provider config")
