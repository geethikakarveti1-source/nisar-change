"""Writes a SYNTHETIC paddy dataset (fake!) as GeoTIFFs so we can test the pipeline end to end.
Never present this as real results."""
import datetime as dt
import numpy as np, rasterio
from rasterio.transform import from_bounds
from src.common.constants import CFG, ROOT

rng = np.random.default_rng(7)
bbox = CFG["aoi"]["bbox"]; res = 0.005
W = int(round((bbox[2]-bbox[0])/res)); H = int(round((bbox[3]-bbox[1])/res))
T = 8; start = dt.date(2026, 6, 15)
dates = [(start + dt.timedelta(days=12*i)).isoformat() for i in range(T)]
# stage means in dB: 1 flooded, 2 growth, 3 peak, 4 harvested  -> (copol, cross)
MEAN = {1: (-20, -27), 2: (-14, -20), 3: (-11, -15), 4: (-14, -25)}
bs = 12; offs = rng.integers(0, T, size=(H//bs+1, W//bs+1))
phase_off = np.kron(offs, np.ones((bs, bs), int))[:H, :W]
out = ROOT/"data/raw/demo"; out.mkdir(parents=True, exist_ok=True)
truth = np.zeros((T, H, W), np.uint8)
tr = from_bounds(*bbox, W, H)
for t, d in enumerate(dates):
    stage = ((t + phase_off) % T)  # 0..7 cycle position
    stage = np.select([stage < 1, stage < 4, stage < 7], [1, 2, 3], 4).astype(np.uint8)
    truth[t] = stage
    for k, pol in enumerate(CFG["polarizations"]):
        mean_db = np.vectorize(lambda s: MEAN[s][k])(stage)
        power = 10**(mean_db/10) * rng.gamma(8, 1/8, size=(H, W))  # speckle-like noise
        with rasterio.open(out/f"{d}_{pol}.tif", "w", driver="GTiff", height=H, width=W, count=1,
                           dtype="float32", crs="EPSG:4326", transform=tr, nodata=0) as dst:
            dst.write(power.astype("float32"), 1)
np.save(out/"truth.npy", truth)
print(f"wrote {T} dates x {len(CFG['polarizations'])} pols, {W}x{H} px -> {out}")
