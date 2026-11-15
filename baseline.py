"""Task B: rule-based crop-stage classifier + export for the web app.
Usage: python -m src.analysis.baseline [--sensor-note "DEMO (synthetic)"]"""
import argparse, json, warnings
import numpy as np
from PIL import Image
from src.common.constants import CFG, AOI, STAGES, path

COLORS = {1: (33, 113, 181), 2: (161, 217, 155), 3: (0, 109, 44), 4: (214, 185, 120)}


def classify(db, th):
    copol, cross = db[:, 0], db[:, 1]
    st = np.full(copol.shape, 4, np.uint8)               # default: harvested / fallow
    st[cross > th["growth_cross_db"]] = 2
    st[cross > th["peak_cross_db"]] = 3
    st[copol < th["water_copol_db"]] = 1                 # water overrides
    st[~np.isfinite(copol) | ~np.isfinite(cross)] = 0
    return st


def block_mean(a, f):
    if f == 1: return a
    H, W = a.shape[-2] // f * f, a.shape[-1] // f * f
    a = a[..., :H, :W]
    a = a.reshape(*a.shape[:-2], H // f, f, W // f, f)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return np.nanmean(a, axis=(-3, -1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--note", default="")
    a = ap.parse_args()
    z = np.load(path("cube") / f"cube_{AOI}.npz")
    db, dates, pols, bbox = z["db"], [str(d) for d in z["dates"]], [str(p) for p in z["pols"]], [float(b) for b in z["bbox"]]
    T, P, H, W = db.shape
    for k, p in enumerate(pols):   # help tune thresholds
        v = db[:, k][np.isfinite(db[:, k])]
        print(f"{p} dB percentiles 5/25/50/75/95:", np.round(np.percentile(v, [5, 25, 50, 75, 95]), 1))
    st = classify(db, CFG["baseline"])
    app = path("app_data")
    stats = {}
    for t, d in enumerate(dates):
        rgba = np.zeros((H, W, 4), np.uint8)
        for c, col in COLORS.items():
            rgba[st[t] == c] = (*col, 200)
        Image.fromarray(rgba).save(app / f"stage_{d}.png")
        valid = (st[t] > 0).sum()
        stats[d] = {STAGES[c]: round(100 * float((st[t] == c).sum()) / max(valid, 1), 1) for c in COLORS}
    f = int(np.ceil(max(H, W) / 200))
    small = block_mean(db, f)
    sh, sw = small.shape[-2:]
    series = {p: np.round(small[:, k].reshape(T, -1).T, 1).tolist() for k, p in enumerate(pols)}
    series = {p: [[None if np.isnan(x) else x for x in row] for row in rows] for p, rows in series.items()}
    json.dump(series, open(app / "series.json", "w"))
    meta = {"aoi": AOI, "bbox": bbox, "dates": dates, "pols": pols, "series_shape": [sh, sw], "note": a.note,
            "stages": {str(c): {"name": STAGES[c], "color": "#%02x%02x%02x" % COLORS[c]} for c in COLORS}, "stats": stats}
    json.dump(meta, open(app / "meta.json", "w"), indent=1)
    print(f"exported {T} dates -> {app}  (series grid {sh}x{sw})")


if __name__ == "__main__":
    main()
