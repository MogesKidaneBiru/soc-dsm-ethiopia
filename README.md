# National soil organic carbon mapping

`soc_dsm_pipeline.py` consolidates the paper's notebook into one script, from
the final extracted sample table to fitted models, predictions, calibrated
intervals, applicability maps and product benchmarks. Raw preparation,
sample-covariate extraction, downloading and figures are excluded.

## Inputs

Edit the relative paths in `CONFIG`; paths resolve from the script's directory.

- **`data/analysis_table.csv`:** the final 28,920-location table in its saved row
  order. Required columns: `_source_row` (unique ID), `OC` (percent SOC),
  `x_proj`, `y_proj` (metres, EPSG:32637), `AEZ` (raster code), and the 45
  continuous/eight categorical covariates listed in `CONFIG`. Categories remain
  integer codes. Locations must already be merged, filtered and complete, with
  texture fractions normalized as in the notebook. AEZ names use its verified legend.
- **Frozen splits:** retain `holdout`, `block_id` and `cv_fold` from the final
  table. Fold labels are 0–4 for working rows and -1 for hold-out rows. If
  `holdout` is missing, supply `data/seed59.json` with `seed: 59` and the original
  `holdout_blocks` list. Missing block IDs and fold labels are reconstructed
  using the notebook's grid and fold search. Counts are checked. The accepted
  pre-merge seed-59 allocation is never replaced by a fresh random draw.
- **`data/rasters/`:** the prepared, aligned 250-m predictor TIFFs, including
  filled RSG layers, plus `ETH_AEZ.tif`, `mapping_valid.tif` and `domain.tif`.
  The domain has three bands named `country`, `water`, `land`. Use the same
  stack and masks as the analysis table; individual paths are configurable.
  Mapping retains the notebook's texture closure and validity rules. It does
  not fill RSG values, create masks or resample rasters.
- **`data/products_at_points.csv`:** `_source_row`, `sg_mean`, `isda_mean`,
  already in percent SOC at 0–20 cm. Include **working and hold-out locations**.
  A hold-out-only CSV cannot support working-only linear recalibration and
  causes an error. Missing products remain missing; comparisons use matched cases.

## Run

The notebook records Python 3.11.15. In a Python 3.11 environment:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python soc_dsm_pipeline.py
```

`outputs/` must be absent or empty. There is no checkpoint recovery, overwrite
or reduced-trial mode. The full nested analysis is computationally expensive.

## Outputs and analysis

Outputs are grouped by step: partitions, spatial/random CV, final fits,
calibration, applicability, maps and benchmarks. Models, preprocessors, tuning
trials, OOF/hold-out predictions, metrics, paired bootstrap intervals,
configuration and package versions are saved. GeoTIFFs contain SOC, calibrated
90/95% bounds and widths, interval flags, DI and fold/LOO AOA masks. AOA masks
use 1 for inside, 0 for outside and -9999 for NoData.

CatBoost-QW remains prespecified, with fixed rank exponent 0.5. Ridge uses only
the `log1p` flow-accumulation correction. There is no winsorization, upper
prediction clipping or smearing. The notebook's fourth CQR candidate, AEZ ×
predicted quintile, is retained to preserve its working-OOF selection rule.
Groups below n=100 fall back nationally; 95% bounds envelop 90% bounds.

Ridge correction and calibration alternatives were developed after earlier
results were inspected. Numerical calibration selection uses working OOF data
only; this reproduction is not fresh confirmation. Spatial OOF calibration has
no exact split-conformal guarantee. Bootstrap intervals condition on fitted models.

The seven modeling-package pins are printed notebook versions. Original
Rasterio/threadpoolctl versions were not printed; their labeled pins are tested
compatibility versions.

## Soil data

Soil observations are available from the Ethiopian Ministry of Agriculture on
request. Restricted observations and sample tables are not included here.
