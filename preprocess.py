"""Task A: GeoTIFFs named <YYYY-MM-DD>_<pol>.tif (linear power) -> aligned dB cube.
Usage: python -m src.data.preprocess data/raw/demo --sensor DEMO --res 0.005
Add --amplitude if your rasters are amplitude, not power."""
import argparse, json, re, warnings
from collections import defaultdict
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from scipy.ndimage import uniform_filter
from src.common.constants import CFG, AOI, POLS, path


def lee_filter(img, size=5, looks=4):
    """Classic Lee speckle filter on LINEAR power. NaNs preserved."""
    valid = np.isfinite(img)
    x = np.where(valid, img, 0.0)
    mean = uniform_filter(x, size); sq = uniform_filter(x * x, size)
    var = np.maximum(sq - mean * mean, 0)
    cu2 = 1.0 / looks
    var_x = np.maximum((var - mean * mean * cu2) / (1 + cu2), 0)
    k = np.divide(var_x, var, out=np.zeros_like(var), where=var > 0)
    out = mean + k * (x - mean)
    out[~valid] = np.nan
    return out


def regrid(src_path, bbox, width, height):
    dst = np.full((height, width), np.nan, np.float32)
    with rasterio.open(src_path) as src:
        reproject(source=rasterio.band(src, 1), destination=dst, src_transform=src.transform,
                  src_crs=src.crs, src_nodata=src.nodata,
                  dst_transform=from_bounds(*bbox, width, height), dst_crs="EPSG:4326",
                  dst_nodata=np.nan, resampling=Resampling.average)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--sensor", default="NISAR")
    ap.add_argument("--res", type=float, default=CFG["resolution_deg"])
    ap.add_argument("--amplitude", action="store_true"); ap.add_argument("--no-filter", action="store_true")
    a = ap.parse_args()
    bbox = CFG["aoi"]["bbox"]
    W = int(round((bbox[2] - bbox[0]) / a.res)); H = int(round((bbox[3] - bbox[1]) / a.res))
    files = defaultdict(dict)
    for f in Path(a.folder).glob("*.tif"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_([a-z]{2})\.tif$", f.name)
        if m: files[m.group(1)][m.group(2)] = f
    dates = sorted(d for d in files if all(p in files[d] for p in POLS))
    for d in sorted(set(files) - set(dates)): print("skip (missing pol):", d)
    if not dates: raise SystemExit("No complete dates found. Names must look like 2026-07-01_hh.tif")
    db = np.full((len(dates), len(POLS), H, W), np.nan, np.float32)
    for t, d in enumerate(dates):
        for k, pol in enumerate(POLS):
            x = regrid(files[d][pol], bbox, W, H)
            if a.amplitude: x = x ** 2
            x[x <= 0] = np.nan
            if not a.no_filter: x = lee_filter(x)
            db[t, k] = 10 * np.log10(np.maximum(x, 1e-10))
        print("processed", d)
    db[~np.isfinite(db)] = np.nan
    out = path("cube") / f"cube_{AOI}.npz"
    np.savez_compressed(out, db=db, dates=np.array(dates), pols=np.array(POLS), bbox=np.array(bbox))
    json.dump([{"date": d, "sensor": a.sensor, "pols": POLS} for d in dates], open(path("cube") / "dates.json", "w"), indent=1)
    print("saved", out, db.shape)


if __name__ == "__main__":
    main()
