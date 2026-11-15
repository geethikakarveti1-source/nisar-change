# NISAR Change Tracker
Tracking paddy crop cycles (Kaveri delta, Tamil Nadu) with NISAR L-band SAR, GPU ML, and an interactive web map.

## Quick start
```bash
git clone <repo-url> && cd nisar-change
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.check_setup
```

## Team / tasks
| Task | Folder | Owner |
|---|---|---|
| A Data & preprocessing | src/data | |
| B Physics & baseline | src/analysis | |
| C ML & GPU | src/ml | |
| D Frontend & story | app | |

## Rules
1. Branch per task (e.g. task-b/baseline), PR into main, one reviewer.
2. Only edit your own folder.
3. Shared values live in config/config.yaml; file formats in contracts/CONTRACT.md.
4. Big data never goes in Git - use the shared drive.
