"""Shared constants. Always build paths from ROOT - never hardcode C:/Users/..."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(ROOT / "config" / "config.yaml"))

AOI = CFG["aoi"]["name"]
NODATA = CFG["nodata"]
STAGES = {int(k): v for k, v in CFG["stage_classes"].items()}
POLS = CFG["polarizations"]


def path(key: str) -> Path:
    """path(\"cube\") -> <repo>/data/processed"""
    p = ROOT / CFG["paths"][key]
    p.mkdir(parents=True, exist_ok=True)
    return p
