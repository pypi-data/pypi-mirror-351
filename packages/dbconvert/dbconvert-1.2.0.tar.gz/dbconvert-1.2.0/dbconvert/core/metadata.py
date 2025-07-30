import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib
except ImportError:
    raise ImportError("tomli is required for Python < 3.11")

_metadata_cache: Optional[Dict[str, Any]] = None
PYPROJECT_PATH = Path("pyproject.toml")


def _parse_pyproject(path: Path) -> Dict[str, Any]:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} not found.")
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Error parsing TOML: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error reading {path}: {e}")


def load_pyproject_metadata() -> Dict[str, Any]:
    """Load and cache minimal metadata from pyproject.toml"""
    global _metadata_cache
    if _metadata_cache is not None:
        return _metadata_cache

    data = _parse_pyproject(PYPROJECT_PATH)

    _metadata_cache = {
        "internalurls": data.get("tool", {}).get("internalurls", {}),
        "repository": data.get("project", {}).get("urls", {}).get("Repository", ""),
        "name": data.get("project", {}).get("name", ""),
        "version": data.get("project", {}).get("version", ""),
    }

    return _metadata_cache
