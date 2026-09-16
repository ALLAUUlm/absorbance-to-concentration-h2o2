# UVV tools

Tools to convert and evaluate files from the UVVis spectrometer (UVV) at the institute of electrochemistry.

# Installation instructions

This package can be installed with pip:

```sh
pip install git+https://gitlab.uni-ulm.de/inst-echem/tools/uvv.git
```

# Development

Clone the repository

```sh
git clone https://gitlab.uni-ulm.de/inst-echem/tools/uvv.git
cd uvv
```

Create an environment

```sh
mamba env create -f environment.yaml
mamba activate uvv-dev
```

Install uvv

```sh
pip install -e .
```

# Repository layout

```
evaluation_docs/   notebooks that convert and evaluate the current raw data (run in order, see below)
adding_metadata/    notebooks that digitize/sort/evaluate older, pre-neuer_trial measurements
doc/               everything else (helper notebooks not part of either pipeline)
uvv/               the installable package the notebooks import (UVVCollection, UVVBatchCollection, ...)
data/
  raw/             raw UVV CSV/YAML files — a copy of data/raw_mrdga/neuer_trial/raw. NOT edited by any notebook.
  processed/       per-measurement output of create_outfiles() (was called "exported"/"exp")
  evaluation/      aggregated per-material statistics, plots and publication figures
  old_evaluation/  legacy flat evaluation output, still used by doc/bar_plots.ipynb and produced by
                   adding_metadata/evaluation_to_material_overview_old.ipynb
  raw_mrdga/       raw_mrdga/neuer_trial/ is the frozen, authoritative archive that data/raw,
                   data/processed and data/evaluation are copied from. It is never modified by these
                   notebooks; raw_mrdga's loose files are the pre-repair input to
                   add_columns_and_metadatalines.ipynb.
  202402/, 202402_proccesed_csv/   inputs to the adding_metadata/ notebooks
  model_data/      template file used by add_columns_and_metadatalines.ipynb
  DELETION_LOG.md  record of what was removed from data/ during cleanup and why
```

`data/202507/` and `data/202508_repeating_trials/` hold raw UVV batches (2025-07/08/10) that have not
yet been run through the repair/conversion pipeline below — they are not part of any notebook's input
path yet.

# Instructions on how to use `evaluation_docs/` to produce scientifically reasonable data

Run these notebooks in this order to go from raw spectrometer files to the publication plots.

## 1. add_columns_and_metadatalines.ipynb

One-time repair step for the raw CSV exports: fixes tokenizing/metadata-line errors in the files
under `data/raw_mrdga/` and writes the corrected raw files (plus their YAML metadata) into
`data/raw_mrdga/neuer_trial/raw` — the frozen archive that `data/raw/` is copied from. You normally
don't need to re-run this; it's kept for provenance/traceability of how `neuer_trial/raw` was produced.

## 2. conversion_to_single_batches.ipynb

This notebook converts raw UVV spectrometer CSV files into structured batch data:

1. **Load raw files**: Specify the input folder (`data/raw/`) containing raw CSV files and convert them using `create_outfiles()`
2. **Handle existing outputs**: Choose whether to overwrite existing output files
3. **Create collection**: Load converted files (`data/processed/`) into a `UVVCollection` object and remove repeated measurements
4. **Process batches**: Filter data (e.g., H₂O₂ concentration) and save as individual batch files to `data/evaluation/`
5. **Validate metadata**: Check that all entries have required metadata fields (irradiation time, phases, etc.)

Key outputs: Processed batch files organized by measurement metadata in `data/evaluation/single_batch`.

## 3. evaluation_to_material_overview_batch_filtering.ipynb

This notebook aggregates and analyzes batch data to create material overview summaries:

1. **Load batch collection**: Import processed batch files from `data/evaluation/single_batch` into a `UVVBatchCollection` object
2. **Separate rerun batches**: Detect batches that were re-measured (`...a`, `...a2`, ...) and treat them separately from normal batches
3. **Calculate baseline corrections**: Compute H₂O₂ concentration relative to baseline for each measurement
4. **Group by material properties**: Organize data by material name, excitation wavelength, loading, sonication time, phase, and synthesis date
5. **Apply outlier detection**: Use Grubbs test to identify and flag statistical outliers in concentration measurements
6. **Compute statistics**: Calculate mean H₂O₂ concentration, 95% confidence intervals, and standard error for each time point
7. **Generate overview files**: Export aggregated results to CSV files organized by material parameters in `data/evaluation/material_excwavelength_loading_sonication`
8. **Create date-agnostic summaries**: Repeat analysis ignoring synthesis dates for broader material comparisons, and plot rerun-batch comparisons

Key outputs: Statistical summaries and material overview data with outliers marked for quality assurance.

## 4. compare_results copy_workingfile.ipynb

This notebook compares H₂O₂ concentration data across different excitation wavelengths and materials, fits kinetic models, and calculates apparent quantum efficiency (AQE):

1. **Load and group data**: Import aggregated CSV files from `data/evaluation/material_excwavelength_loading_sonication`, filter by loading and sonication parameters, and concatenate files by material and excitation wavelength
2. **Generate comparison plots**: Create bar plots showing average H₂O₂ concentration vs. time for each material across three excitation wavelengths (365, 406, 450 nm) with 95% confidence interval error bars
3. **Calculate AQE**: Compute apparent quantum efficiency at 4 hours using photon energy calculations, normalizing H₂O₂ moles produced to incident photon count
4. **Evaluate reaction kinetics**: Fit experimental data to nth-order growth models using least-squares curve fitting to determine rate constants and goodness-of-fit (R² values)
5. **Export results**: Save comparison plots (PNG), kinetic fit parameters (CSV), and AQE summary tables organized in `data/evaluation/material_excwavelength_loading_sonication/ignore_synthesis_date/comparison_plots/for_publication/`

Key outputs: Wavelength comparison visualizations, kinetic model parameters, AQE values, and fitted growth curves in the `for_publication/` directory.

# `adding_metadata/` — notebooks for older, pre-digitized measurements

These notebooks handle measurements from before the `neuer_trial` raw-data pipeline existed
(`data/202402/`, `data/202402_proccesed_csv/`). They are historical/superseded by the pipeline above
but kept for reference and reproducibility of the older results.

- **create_yaml_files_for_old_measurements.ipynb** — pairs old CSV exports with YAML metadata, sorts them by irradiation time, and writes them into `data/202402_proccesed_csv/sorted/`.
- **sort_old_measurements.ipynb** — sorts/renames paired CSV+YAML files within a batch by irradiation time.
- **evaluation_to_material_overview_old.ipynb** — an earlier version of `evaluation_to_material_overview_batch_filtering.ipynb`, without rerun-batch handling. Writes into `data/raw_mrdga/neuer_trial/evaluation/` and into the legacy `data/old_evaluation/` folder.

# `doc/` — other scripts

Notebooks that don't belong to either pipeline above:

- **bar_plots.ipynb** — an earlier/simpler bar-plot generator, superseded by the plots produced in `compare_results copy_workingfile.ipynb`. Reads from and writes to `data/old_evaluation/`.
- **Bandgap_determination.ipynb** — standalone Tauc-plot-style linear-fit calculations for bandgap determination; unrelated to the H₂O₂ evaluation pipeline.
