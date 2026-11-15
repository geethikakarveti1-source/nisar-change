"""Run after cloning: python -m scripts.check_setup"""
from src.common.constants import ROOT, CFG, STAGES, path

print("Repo root:", ROOT)
print("AOI:", CFG["aoi"]["name"], CFG["aoi"]["bbox"])
print("Stage classes:", STAGES)
for k in CFG["paths"]:
    print(f"  {k:10s} -> {path(k)}")
print("Setup OK")
