# From raw spectra to evaluated H₂O₂ concentrations

This describes how the code in this repository turns raw UV-Vis spectrometer
files into the aggregated concentration-vs-time data and figures used for the
analysis. It mirrors the four notebooks in `docs/evaluation_docs/`, run in
that order; each one reads the previous notebook's output.

## Background

H₂O₂ produced during a photocatalysis experiment is quantified with a
colorimetric assay: an aliquot of the reaction solution is mixed with
titanium(IV) oxysulfate (TiOSO₄), which forms a yellow peroxo-titanium
complex with H₂O₂. A UV-Vis spectrometer records an absorbance spectrum of
this mixture at a series of times after the reaction is started, and the
absorbance at 420 nm is proportional to the H₂O₂ concentration in the
aliquot. Every raw file therefore represents *one aliquot taken at one time
point*, and a full experiment ("batch") consists of several such files, one
per time point, plus a YAML file recording the experimental conditions
(material, excitation wavelength, catalyst loading, sonication time, sample
dilution, etc.).

## 1. `add_columns_and_metadatalines.ipynb` — repair raw exports (one-time)

The spectrometer's raw CSV export occasionally has malformed metadata lines
or inconsistent column counts. This notebook detects and repairs those
issues and writes the corrected raw CSV + YAML pairs to `data/raw/`. This is
historical bookkeeping: `data/raw/` already contains the repaired files, so
this step normally does not need to be re-run.

## 2. `conversion_to_single_batches.ipynb` — raw spectrum → per-measurement concentration

For each raw CSV/YAML pair, `create_outfiles()` (`scripts/uvv/package.py`):

1. parses the spectrometer export into a clean wavelength/absorbance table,
2. merges it with the YAML metadata,
3. writes the result as a `.csv` + `.meta.yaml` + `.meta.json` triplet into
   `data/processed/`.

These processed files are then loaded into a `UVVCollection`
(`scripts/uvv/uvv_collection.py`), which computes, for every measurement:

- **dilution factor** — `(extracted sample + complexing agent + dilution) / extracted sample`,
  correcting for the aliquot having been diluted before measurement, and
- **c(H₂O₂)** — `abs420 / 0.61 × dilution factor`, the absorbance at 420 nm
  converted to a H₂O₂ concentration (mmol L⁻¹) and corrected back to the
  original, undiluted reaction volume.

Measurements belonging to the same reaction ("batch": same material,
wavelength, loading, sonication, extraction date, ...) are grouped into a
time series and written to `data/evaluation/single_batch/<phase>/`, one file
per batch, with `time` and `c(H₂O₂)` columns. Repeated/duplicate
measurements are separated out and processed the same way into
`data/evaluation/repeated_measurements/`.

## 3. `evaluation_to_material_overview_batch_filtering.ipynb` — statistics per material/condition

This notebook loads all single-batch files (`UVVBatchCollection`) and:

1. **Baseline-corrects** each batch: `c(H₂O₂)_baseline = c(H₂O₂) − c(H₂O₂) at t=0`,
   removing any assay background (clipped to zero if the blank happens to
   read negative).
2. **Separates rerun batches** — some reactions were repeated using the same
   catalyst (named `<batch>a`, `<batch>a2`, ...); these are analyzed
   separately (see the rerun comparison plots below) rather than mixed into
   the main statistics.
3. **Groups** the remaining ("normal") batches by material, excitation
   wavelength, catalyst loading, sonication time, phase, and (in one pass)
   synthesis date — and, in a second pass, ignoring synthesis date, to give a
   date-agnostic summary across all batches of the same material/condition.
4. **Flags outliers** at each time point with a Grubbs test (iteratively
   removes the most deviant point while its Grubbs statistic exceeds the
   critical value for the given sample size and α = 0.05).
5. **Computes statistics** per time point over the (non-outlier)
   measurements: mean c(H₂O₂), standard error, and the 95 % confidence
   interval (`t.ppf(0.975, n−1) × SE`).

Results are written as CSV files named
`<material>_<wavelength>nm_<loading>_g_L_<sonication>min_<phase>[_<date>].csv`
under `data/evaluation/material_excwavelength_loading_sonication/`
(per-date) and its `ignore_synthesis_date/` subfolder (date-agnostic); a
`_calculatedfrom.csv` sibling of each file keeps the underlying
per-measurement data with the Grubbs pass/fail flag for traceability. Rerun
batches get their own bar-plot comparison (original vs. rerun cycles) under
`material_excwavelength_loading_sonication/rerun/`.

## 4. `compare_results copy_workingfile.ipynb` — cross-material comparison, quantum yield, kinetics

Starting from the date-agnostic CSVs above, this notebook:

1. **Groups by material and excitation wavelength**, producing bar plots
   (all time points, and a fixed 1–6 h selection) and line plots comparing
   all materials at each wavelength, saved under
   `.../comparison_plots/for_publication/`.
2. **Computes the apparent quantum yield (AQY)** at 4 h: the incident photon
   flux is calculated from the LED power density, illuminated area and
   photon energy at the excitation wavelength (`E = hc/λ`); AQY is then
   `2 × (moles of H₂O₂ produced × Avogadro's number) / (number of incident
   photons)` — the factor of 2 accounts for the two-electron reduction of O₂
   to H₂O₂.
3. **Fits reaction kinetics**: for each material/wavelength, an nth-order
   growth model is fit (via least-squares) to the concentration-vs-time data
   up to the concentration maximum, scanning the reaction order n from 0 to
   4 and keeping the fit with the best R²; rate constant, order, and R² are
   collected in `kinetic_fitting_order_scan/best_fit_summary.csv`.

## The "old measurements" track (`docs/adding_metadata/`)

Measurements made before this per-measurement YAML metadata convention
existed (`data/pre_metadata_raw/`) are a separate, older dataset. Three
notebooks bring them into a comparable form:

- **`create_yaml_files_for_old_measurements.ipynb`** builds a YAML metadata
  file for each old raw CSV (using a hand-made table of experiment start
  times, `data/starting_times.csv`, and a template metadata file) and
  renames the files to the current `<batch>_<n>.csv`/`.yaml` convention,
  writing the result to `data/pre_metadata_processed/`.
- **`sort_old_measurements.ipynb`** sorts each batch's files by irradiation
  time into `data/pre_metadata_processed/sorted/`.
- **`evaluation_to_material_overview_old.ipynb`** is an earlier version of
  step 3 above (without rerun-batch handling), applied to this older dataset.

From `data/pre_metadata_processed/` onward, these measurements can be fed
into the same `conversion_to_single_batches.ipynb` → ... → `compare_results
copy_workingfile.ipynb` pipeline as any other batch.
