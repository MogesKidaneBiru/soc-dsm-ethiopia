# soc-dsm-ethiopia
Code for national soil organic carbon mapping in Ethiopia with spatial validation, conformal prediction intervals and area of applicability assessment.
# National soil organic carbon mapping with calibrated uncertainty and applicability

This repository contains the analysis code for:

> Biru, M.K., Pavan, W., Biratu, G.K., Sida, T.S., Nunes, M.R. Reliable national soil carbon maps require calibrated uncertainty and applicability. *Computers and Electronics in Agriculture* (submitted).

The pipeline maps topsoil soil organic carbon (SOC) across Ethiopia at 250 m resolution. It includes:

- spatially blocked hold-out and cross-validation (75 km blocks)
- nested hyperparameter tuning and model comparison (mean baseline, ordinary kriging, ridge regression, random forest, XGBoost, CatBoost)
- rank-weighted CatBoost (CatBoost-QW) point and quantile models
- conformalized quantile regression (CQR) prediction intervals with group calibration
- a SHAP-weighted dissimilarity index and area of applicability (AOA)
- national raster prediction and benchmarking against SoilGrids 2.0 and iSDAsoil

## Requirements

Python [3.x]. Install dependencies with:

    pip install -r requirements.txt

## Data

The soil observations are available from the Ministry of Agriculture of Ethiopia on request. The expected input format is described in `data/README.md`, and `data/example_input.csv` provides synthetic values for testing.

## Usage

Set paths in the `CONFIG` block at the top of `soc_dsm_pipeline.py`, then run:

    python soc_dsm_pipeline.py

Results are written to `outputs/`.

## Citation

Please cite the article above. Citation metadata are in `CITATION.cff`.

## License

MIT License. See `LICENSE`.
