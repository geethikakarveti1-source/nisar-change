# Data contract (agree on day 0; change only via PR everyone approves)

| Item | Spec |
|---|---|
| CRS | EPSG:4326 lat/lon grid (set in config.yaml) |
| Resolution | resolution_deg in config.yaml |
| Dates | ISO `YYYY-MM-DD` |
| Polarizations | lowercase: hh, hv (vv, vh for Sentinel-1) |
| Units | dB, float32, nodata = NaN |
| Cube axis order | [time, pol, y, x] |
| Stage classes | 0 nodata, 1 flooded, 2 growth, 3 peak, 4 harvested (uint8 GeoTIFF) |

## Files
| File | From -> To | Notes |
|---|---|---|
| cube_<aoi>.npz (keys: db[T,P,H,W], dates, pols, bbox; NaN = nodata) | A -> B, C | the aligned data cube |
| dates.json | A -> all | `[{"date":"2026-07-01","sensor":"NISAR","pols":["hh","hv"]}, ...]` |
| stage_baseline_<date>.tif | B -> D | uint8 stage map |
| stage_ml_<date>.tif | C -> D | same format as baseline |
| stats.json | B -> D | `{"2026-07-01": {"flooded": 12.3, "growth": 40.1, ...}}` (% of area) |
| pixel_series.json | B -> D | `{"lat":..,"lon":..,"dates":[..],"hh":[..],"hv":[..]}` |
| metrics.json | C -> D | `{"model":..,"f1":..,"iou":..,"baseline_f1":..}` |

Naming: lowercase, underscores, no spaces.
Put a tiny example of each file in `contracts/sample/`.
