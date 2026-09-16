# KPHIS photocatalytic H2O2 evaluation

Self-contained copy of the UVV evaluation pipeline: scripts, notebooks, and the
data actually used by them. Split out from `uvv_biphasic` (which remains the
canonical git repository for the `uvv` package and holds additional data not
needed here, e.g. `202507/`, `202508_repeating_trials/`).

## Layout

```
scripts/           the uvv Python package (installable), copied from uvv_biphasic/uvv
  uvv/
  setup.py, pyproject.toml, environment.yaml

docs/              notebooks, grouped as in uvv_biphasic/README.md
  evaluation_docs/   current pipeline (run in this order):
                     add_columns_and_metadatalines.ipynb (one-time raw repair, historical)
                     conversion_to_single_batches.ipynb
                     evaluation_to_material_overview_batch_filtering.ipynb
                     compare_results copy_workingfile.ipynb
  adding_metadata/   old-data notebooks (create_yaml_files_for_old_measurements.ipynb,
                     sort_old_measurements.ipynb, evaluation_to_material_overview_old.ipynb)
  doc/               everything else (bar_plots.ipynb, Bandgap_determination.ipynb)

data/
  raw/               raw UVV CSV/YAML files. NOT edited by any notebook.
  processed/          per-measurement output of create_outfiles()
  evaluation/         aggregated statistics, plots, publication figures
  old_evaluation/     legacy flat evaluation output (bar_plots.ipynb, evaluation_to_material_overview_old.ipynb)
  raw_mrdga/          pre-repair raw dump + neuer_trial/ (frozen archive add_columns_and_metadatalines.ipynb builds)
  pre_metadata_raw/          old measurements from before per-measurement YAML metadata existed
                             (was "202402/"); input to adding_metadata/create_yaml_files_for_old_measurements.ipynb
  pre_metadata_processed/    those same measurements after metadata was added and files renamed to the
                             current convention (was "202402_proccesed_csv/"); also the working folder
                             adding_metadata/sort_old_measurements.ipynb sorts in place
  model_data/         template file used by add_columns_and_metadatalines.ipynb
```

## Setup

The notebooks import the `uvv` package from `scripts/uvv`. To point your
environment's editable install at this copy:

```sh
mamba activate uvv-dev   # or your environment
pip install -e scripts
```

Each notebook's second cell does `os.chdir(...)` up to this project's root, so
all data paths inside notebooks are written relative to here (e.g. `data/raw/`),
regardless of which `docs/<group>/` subfolder the notebook lives in.

## Verified

`evaluation_docs/conversion_to_single_batches.ipynb`,
`evaluation_to_material_overview_batch_filtering.ipynb`, and
`compare_results copy_workingfile.ipynb` were re-run end-to-end against this
copy and reproduce the exact same numbers as the original run (1282/1300
collection sizes, 150 normal + 12 special batch groups, identical r² values
in the kinetic fits, etc.).
