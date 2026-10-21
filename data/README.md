# Input data

The soil observations used in this study were collected by the Ethiopian Soil Information System (EthioSIS) and are available from the Ministry of Agriculture of Ethiopia on request (https://nsis.moa.gov.et/). They are not redistributed here.

The pipeline expects one table, `data/analysis_table.csv`, with one row per sampling location and the following columns:

| Column | Description |
|---|---|
| `soc` | Soil organic carbon (% OC, 0-20 cm) |
| `x`, `y` | Projected coordinates (EPSG:32637, m) |
| `aez` | Agro-ecological zone code |
| covariates | The 53 environmental covariates listed in Supplementary Table S1 of the article |

`example_input.csv` contains synthetic values in the same format. It is provided only to test that the code runs and does not reproduce the published results.
