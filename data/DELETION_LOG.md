# Data cleanup log

This project's `data/` folder is not tracked by git (only a handful of tiny
demo/test fixtures under `data/raw` and `data/raw_old` are). Deletions of the
large measurement-data folders below therefore leave no git history, so this
log is the record of what was removed, when, and why.

## 2026-09-15 — repo restructuring cleanup

Performed while reorganizing the doc notebooks into `evaluation_docs/`,
`adding_metadata/`, and `doc/` (misc), and introducing the new
`data/raw`, `data/processed`, `data/evaluation` layout described in the
top-level `README.md`. **`data/raw_mrdga/neuer_trial` was not touched** —
all new folders below were built as fresh copies of it.

| Removed path | Files | Reason |
|---|---|---|
| `data/raw_mrdga/repaired/` | 239 | Scratch/intermediate output of the one-time CSV-repair step in `evaluation_docs/add_columns_and_metadatalines.ipynb`. Superseded by the final files in `data/raw_mrdga/neuer_trial/raw`. Not referenced by any notebook path. |
| `data/raw_mrdga/repaired_testmetadata/` | 0 (empty) | Unused scratch folder from the same repair step. |
| `data/repaired_checks_export/` | 35 | Scratch output from the same repair/validation step. Not referenced by any notebook path. |
| `data/exported/` (top-level, flat) | 3421 | Superseded by `data/raw_mrdga/neuer_trial/exp` (now copied to `data/processed/`). Only appeared in stale cached cell *output* text from old notebook runs, not in any current code path. |
| `data/repeated_measurements/` (top-level, flat) | 54 | Orphaned side effect of a hardcoded path bug in `uvv/uvv_collection.py`'s `create_collections()` (it pointed at this old flat location instead of the `neuer_trial`/new `data/evaluation` structure). The bug is now fixed; going forward this data is written to `data/evaluation/repeated_measurements/`. |
| `data/raw/` (top-level, flat) — trimmed | 3126 of 3127 | Near-duplicate of `data/raw_mrdga`'s pre-repair loose files (99.7% identical by name, spot-checked identical content). Kept `demo_final_not_repeated.yaml`, the one file still read by `adding_metadata/create_yaml_files_for_old_measurements.ipynb`. `data/raw/` was then repopulated with a fresh copy of `data/raw_mrdga/neuer_trial/raw` (2764 files) per the new structure. |

## Renamed (not deleted)

| Old path | New path | Reason |
|---|---|---|
| `data/evaluation/` (top-level, flat, 1683 files) | `data/old_evaluation/` | This name was needed for the new `data/evaluation/` (a fresh copy of `raw_mrdga/neuer_trial/evaluation`, used by the current `evaluation_docs/` pipeline). The old flat folder is still actively used by `doc/bar_plots.ipynb` and is the output target of `adding_metadata/evaluation_to_material_overview_old.ipynb`, so it was renamed rather than deleted. Both notebooks (and `uvv/uvv_collection.py`'s `make_nice_bar_plots*` methods) were updated to point at `data/old_evaluation/`. |

## Left untouched (out of scope for this cleanup)

- `data/202507/` and `data/202508_repeating_trials/` — raw UVV batches from Jul/Aug/Oct 2025 (e.g. material LN330025) that have not been run through the repair/conversion pipeline yet. Not part of this reorganization; left exactly as found.
- `data/202402/`, `data/202402_proccesed_csv/` — inputs to the `adding_metadata/` (old-data) notebooks.
- `data/model_data/` — template file used by `evaluation_docs/add_columns_and_metadatalines.ipynb`.
- `data/raw_mrdga/` (loose pre-repair files + the `neuer_trial/` subfolder) — `raw_mrdga`'s loose files are the input to `add_columns_and_metadatalines.ipynb`; `neuer_trial/` is the frozen, authoritative archive that `data/raw`, `data/processed`, and `data/evaluation` were copied from, and was not modified.
