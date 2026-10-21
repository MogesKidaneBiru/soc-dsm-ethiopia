"""SOC mapping pipeline consolidated from the accompanying analysis notebook."""

from pathlib import Path


# Configuration
CONFIG = {
    "analysis_table": "data/analysis_table.csv",
    "seed59_blocks_json": "data/seed59.json",
    "product_points": "data/products_at_points.csv",
    "output_dir": "outputs",
    "raster_dir": "data/rasters",
    "aez_raster": "data/rasters/ETH_AEZ.tif",
    "domain_raster": "data/rasters/domain.tif",
    "mapping_valid_raster": "data/rasters/mapping_valid.tif",
    "columns": {
        "id": "_source_row",
        "soc": "OC",
        "x": "x_proj",
        "y": "y_proj",
        "aez": "AEZ",
        "block": "block_id",
        "holdout": "holdout",
        "fold": "cv_fold",
    },
    "product_columns": {
        "id": "_source_row",
        "SoilGrids": "sg_mean",
        "iSDA": "isda_mean",
    },
    "continuous": (
        "s_silt s_sand s_clay c_map c_mat c_pet_mean c_pet_sd c_aet_mean c_aet_sd "
        "c_aet_cv c_ai c_bio2 c_bio4 c_bio5 c_bio6 c_bio15 c_bio16 c_bio17 "
        "c_smap_mean c_smap_sd c_era5_mean c_era5_sd o_ndvi_mean o_ndvi_sd "
        "o_evi_mean o_evi_sd o_npp_mean o_npp_sd o_red o_nir o_swir1 o_swir2 "
        "o_ndmi o_nbr2 o_msi r_dem r_slope r_aspect r_curvature r_twi r_tpi "
        "r_ls r_tri r_flowacc r_hillshade"
    ).split(),
    "categorical": (
        "s_texture_code s_rsg1_code s_rsg2_code s_drainage_code o_lulc_code "
        "p_geo p_glim p_lith"
    ).split(),
    "aez_legend": {
        1: "SA1",
        2: "SM2",
        3: "SM1",
        4: "A1",
        5: "M2",
        6: "M1",
        7: "SM3",
        8: "WB",
        9: "M3",
        10: "SH2",
        11: "SH1",
        12: "A2",
        13: "H2",
        14: "SA2",
        15: "H1",
        16: "H3",
        17: "SH3",
        18: "PH2",
        19: "PH1",
    },
    "crs": "EPSG:32637",
    "master_seed": 41,
    "holdout_seed": 59,
    "block_km": 75.0,
    "holdout_fraction": 0.20,
    "holdout_fraction_tolerance": 0.04,
    "rare_aez_threshold": 200,
    "large_aez_min_share": 0.05,
    "large_aez_max_share": 0.40,
    "rare_aez_max_share": 0.30,
    "high_soc_threshold": 5.0,
    "high_soc_min_share": 0.10,
    "high_soc_max_share": 0.35,
    "high_soc_weight": 0.5,
    "expected_n": {"full": 28920, "working": 22970, "holdout": 5950},
    "expected_blocks": {"working": 82, "holdout": 30},
    "expected_fold_n": [4340, 4140, 4680, 4935, 4875],
    "n_folds": 5,
    "fold_search": {
        "seed_start": 0,
        "n_seeds": 100,
        "size_cap_factor": 1.15,
        "weights": [1.0, 1.0, 0.5, 2.0],
    },
    "inner": {
        "fraction": 0.20,
        "tolerance": 0.05,
        "n_search": 30,
        "seed_base": 1000,
        "seed_step": 100,
    },
    "model_seed": 41,
    "tuning_seed": 17,
    "random_cv_seed": 42,
    "threads": 8,
    "early_stopping": 50,
    "weight_alpha": 0.5,
    "models": ["mean", "ok", "ridge_flowacc_log", "rf", "xgb", "cb", "cbqw"],
    "trials": {"ridge": 40, "rf": 50, "xgb": 80, "cb": 80},
    "search_spaces": {
        "ridge": {"alpha": {"type": "float", "low": 0.001, "high": 100.0, "log": True}},
        "rf": {
            "n_estimators": {"type": "int", "low": 200, "high": 800, "step": 100},
            "max_depth": {"type": "int", "low": 8, "high": 24},
            "min_samples_leaf": {"type": "int", "low": 1, "high": 10},
            "max_features": {"type": "float", "low": 0.3, "high": 1.0},
        },
        "xgb": {
            "n_estimators": {"type": "int", "low": 300, "high": 1500, "step": 100},
            "max_depth": {"type": "int", "low": 3, "high": 10},
            "learning_rate": {"type": "float", "low": 0.01, "high": 0.1, "log": True},
            "min_child_weight": {"type": "float", "low": 1.0, "high": 20.0},
            "subsample": {"type": "float", "low": 0.5, "high": 1.0},
            "colsample_bytree": {"type": "float", "low": 0.5, "high": 1.0},
            "reg_lambda": {"type": "float", "low": 0.0001, "high": 10.0, "log": True},
        },
        "cb": {
            "iterations": {"type": "int", "low": 500, "high": 2000, "step": 100},
            "depth": {"type": "int", "low": 4, "high": 10},
            "learning_rate": {"type": "float", "low": 0.01, "high": 0.1, "log": True},
            "l2_leaf_reg": {"type": "float", "low": 1.0, "high": 10.0, "log": True},
            "bagging_temperature": {"type": "float", "low": 0.0, "high": 1.0},
        },
    },
    "kriging": {
        "neighbours": 30,
        "pair_draws": 500000,
        "max_lag_km": 200.0,
        "bins": 20,
        "min_pairs": 30,
        "batch_size": 256,
    },
    "calibration": {
        "levels": [90, 95],
        "quantiles": {90: [0.05, 0.95], 95: [0.025, 0.975]},
        "methods": [
            "CQR_marginal",
            "CQR_AEZ",
            "CQR_predicted_quintile",
            "CQR_AEZ_x_predicted_quintile",
        ],
        "minimum_group_n": 100,
        "relative_score_limit": 1.05,
        "nest_95": True,
    },
    "aoa": {
        "main": "fold",
        "shap_batch": 256,
        "nn_batch": 256,
        "distance_workers": 8,
        "iqr_multiplier": 1.5,
    },
    "bootstrap": {"seed": 20261016, "replicates": 2000, "chunk": 50},
    "mapping": {
        "tile_size": 256,
        "nn_batch": 512,
        "backend": "blas",
        "nodata": -9999.0,
        "texture_limits": [85.0, 115.0],
        "water_cover_code": 80,
        "water_aez_code": 8,
    },
}
CONFIG["raster_paths"] = {
    name: str(Path(CONFIG["raster_dir"]) / (name + ".tif"))
    for name in CONFIG["continuous"] + CONFIG["categorical"]
}


import contextlib
import gc
import importlib.metadata
import json
import math
import pickle
import time

import numpy as np
import optuna
import pandas as pd
import rasterio
from catboost import CatBoostRegressor, Pool
from rasterio.windows import Window
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.stats import rankdata
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits
from xgboost import XGBRegressor


def relative_path(value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or ":" in str(path):
        raise ValueError("CONFIG paths must be relative to the script directory.")
    return Path(__file__).resolve().parent / path


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(clean(value), indent=2, allow_nan=False), encoding="utf-8"
    )


def save_csv(path, frame):
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def save_pickle(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        pickle.dump(value, stream, protocol=pickle.HIGHEST_PROTOCOL)


def inverse(values):
    values = np.asarray(values, float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite log prediction.")
    with np.errstate(over="raise", invalid="raise"):
        predictions = np.maximum(0.0, np.expm1(values))
    if not np.isfinite(predictions).all():
        raise ValueError("Nonfinite inverse prediction.")
    return predictions


def rank_weights(soc):
    ranks = pd.Series(np.asarray(soc, float)).rank(method="average").to_numpy() / len(
        soc
    )
    weights = ranks ** CONFIG["weight_alpha"]
    return (weights / weights.mean()).astype("float32")


def metrics(soc, prediction):
    soc, prediction = np.asarray(soc, float), np.asarray(prediction, float)
    n = len(soc)
    if not n:
        return dict(
            n=0,
            r2=None,
            rmse=None,
            mae=None,
            bias=None,
            ccc=None,
            rpiq=None,
            spearman=None,
        )
    if not np.isfinite(soc).all() or not np.isfinite(prediction).all():
        raise ValueError("Nonfinite metric values.")
    residual = soc - prediction
    sst = np.sum((soc - soc.mean()) ** 2)
    denominator = soc.var() + prediction.var() + (soc.mean() - prediction.mean()) ** 2
    rmse = float(np.sqrt(np.mean(residual**2)))
    ry, rp = rankdata(soc), rankdata(prediction)
    ry -= ry.mean()
    rp -= rp.mean()
    rank_denominator = np.linalg.norm(ry) * np.linalg.norm(rp)
    return dict(
        n=n,
        r2=1 - float(np.sum(residual**2) / sst) if n > 1 and sst > 0 else None,
        rmse=rmse,
        mae=float(np.abs(residual).mean()),
        bias=float(residual.mean()),
        ccc=float(
            2
            * np.mean((soc - soc.mean()) * (prediction - prediction.mean()))
            / denominator
        )
        if denominator > 0
        else None,
        rpiq=float(np.percentile(soc, 75) - np.percentile(soc, 25)) / rmse
        if rmse > 0
        else None,
        spearman=float(ry @ rp / rank_denominator) if rank_denominator > 0 else None,
    )


# 1. Analysis table and frozen spatial design
def boolean_values(series):
    values = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
                "1.0": True,
                "0.0": False,
            }
        )
    )
    if values.isna().any():
        raise ValueError("The holdout column contains missing or unknown flags.")
    return values.to_numpy(bool)


def load_analysis_table():
    data = pd.read_csv(relative_path(CONFIG["analysis_table"]))
    canonical = {
        "id": "_source_row",
        "soc": "OC",
        "x": "x_proj",
        "y": "y_proj",
        "aez": "AEZ",
        "block": "block_id",
        "holdout": "holdout",
        "fold": "cv_fold",
    }
    data = data.rename(columns={CONFIG["columns"][k]: v for k, v in canonical.items()})
    features = CONFIG["continuous"] + CONFIG["categorical"]
    required = ["_source_row", "OC", "x_proj", "y_proj", "AEZ"] + features
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError("Missing analysis columns: " + ", ".join(missing))
    if data._source_row.isna().any() or data._source_row.duplicated().any():
        raise ValueError("Sample IDs must be complete and unique.")
    for name in ["OC", "x_proj", "y_proj", "AEZ"] + features:
        data[name] = pd.to_numeric(data[name], errors="raise")
    if not np.isfinite(data[["OC", "x_proj", "y_proj", "AEZ"] + features]).all().all():
        raise ValueError(
            "Use the final complete analysis table; no rows are excluded here."
        )
    if data.OC.lt(0).any() or data.r_flowacc.lt(0).any():
        raise ValueError("SOC and flow accumulation must be nonnegative.")
    if data.duplicated(["x_proj", "y_proj"]).any():
        raise ValueError(
            "The input must already contain one merged record per location."
        )
    for name in ["AEZ"] + CONFIG["categorical"]:
        if not np.equal(data[name], np.floor(data[name])).all():
            raise ValueError("Noninteger category code: " + name)
        data[name] = data[name].astype("int64")
    data["AEZ_name"] = data.AEZ.map(CONFIG["aez_legend"])
    if data.AEZ_name.isna().any() or data.AEZ.eq(8).any():
        raise ValueError("Unknown AEZ code or water in the analysis table.")
    block_m = CONFIG["block_km"] * 1000
    blocks = np.floor(data.x_proj / block_m).astype("int64") * 10000 + np.floor(
        data.y_proj / block_m
    ).astype("int64")
    if "block_id" in data and not np.array_equal(data.block_id, blocks):
        raise ValueError("Block IDs do not match the notebook's 75-km grid.")
    data["block_id"] = blocks
    allocation_path = relative_path(CONFIG["seed59_blocks_json"])
    if allocation_path.is_file():
        allocation = json.loads(allocation_path.read_text(encoding="utf-8"))
        if allocation["seed"] != CONFIG["holdout_seed"]:
            raise ValueError("The frozen allocation is not seed 59.")
        holdout_mask = data.block_id.isin(allocation["holdout_blocks"]).to_numpy()
        if "holdout" in data and not np.array_equal(
            boolean_values(data.holdout), holdout_mask
        ):
            raise ValueError("The table and frozen seed-59 allocation disagree.")
    elif "holdout" in data:
        holdout_mask = boolean_values(data.holdout)
    else:
        raise FileNotFoundError(
            "Provide the final seed-59 holdout column or data/seed59.json. "
            "The accepted pre-merge draw cannot be regenerated from seed 59 alone."
        )
    data["holdout"] = holdout_mask
    if not data.groupby("block_id").holdout.nunique().eq(1).all():
        raise ValueError("A spatial block crosses working and holdout partitions.")
    counts = {
        "full": len(data),
        "working": int((~holdout_mask).sum()),
        "holdout": int(holdout_mask.sum()),
    }
    if counts != CONFIG["expected_n"]:
        raise ValueError(f"The final analysis cohort differs: {counts}")
    for role, selected in [("working", ~holdout_mask), ("holdout", holdout_mask)]:
        if data.loc[selected, "block_id"].nunique() != CONFIG["expected_blocks"][role]:
            raise ValueError("Unexpected block count for " + role)
    total = data.AEZ_name.value_counts()
    held = (
        data.loc[holdout_mask, "AEZ_name"]
        .value_counts()
        .reindex(total.index, fill_value=0)
    )
    share = held / total
    large = total >= CONFIG["rare_aez_threshold"]
    violations = large & (
        (share < CONFIG["large_aez_min_share"])
        | (share > CONFIG["large_aez_max_share"])
        | (held == 0)
        | (held == total)
    )
    violations |= ~large & (share > CONFIG["rare_aez_max_share"])
    if (
        violations.any()
        or abs(holdout_mask.mean() - CONFIG["holdout_fraction"])
        > CONFIG["holdout_fraction_tolerance"]
    ):
        raise ValueError("The frozen holdout fails the notebook's split criteria.")
    composition = pd.DataFrame(
        dict(
            zone=total.index,
            total_n=total.values,
            working_n=(total - held).values,
            holdout_n=held.values,
            holdout_share=share.values,
            large_zone=large.values,
            violation=violations.values,
        )
    )
    print("Full / working / holdout:", counts, flush=True)
    return data, composition


def assign_spatial_folds(data):
    work = data.loc[~data.holdout]
    n_folds = CONFIG["n_folds"]
    search = CONFIG["fold_search"]
    working_blocks = work.block_id.unique()
    sample_blocks = work.block_id.to_numpy()
    aez = work.AEZ_name.to_numpy()
    soc = work.OC.to_numpy(float)
    high = soc > CONFIG["high_soc_threshold"]
    aezs = pd.Series(aez).value_counts().index.tolist()
    block_high = work.assign(_hi=high).groupby("block_id")._hi.sum().to_dict()
    block_size = work.groupby("block_id").size().to_dict()
    heavy = [b for b in working_blocks if block_high.get(b, 0) > 0]
    light = [b for b in working_blocks if block_high.get(b, 0) == 0]
    cap = (len(work) / n_folds) * search["size_cap_factor"]
    records, best, best_score = [], None, float("inf")
    for seed in range(search["seed_start"], search["seed_start"] + search["n_seeds"]):
        rng = np.random.default_rng(seed)
        perturbation = rng.uniform(-0.5, 0.5, size=len(heavy))
        order = np.argsort(-(np.array([block_high[b] for b in heavy]) + perturbation))
        heavy_order = [heavy[i] for i in order]
        light_order = list(rng.permutation(light))
        sizes, high_counts = np.zeros(n_folds), np.zeros(n_folds)
        assignment = {}
        for block in heavy_order + light_order:
            valid = np.where(sizes + block_size[block] <= np.ceil(cap))[0]
            if not len(valid):
                assignment = None
                break
            if block_high[block] > 0:
                candidates = valid[high_counts[valid] == high_counts[valid].min()]
                fold = (
                    int(candidates[np.argmin(sizes[candidates])])
                    if len(candidates) > 1
                    else int(candidates[0])
                )
            else:
                fold = int(valid[np.argmin(sizes[valid])])
            assignment[block] = fold
            sizes[fold] += block_size[block]
            high_counts[fold] += block_high[block]
        if assignment is None:
            continue
        folds = np.array([assignment[b] for b in sample_blocks])
        sizes = np.bincount(folds, minlength=n_folds)
        if (sizes == 0).any():
            continue
        imbalance = []
        for zone in aezs:
            counts = np.bincount(folds[aez == zone], minlength=n_folds)
            imbalance.append(
                2.0
                if (counts > 0).sum() < n_folds - 1
                else counts.std() / counts.mean()
                if counts.mean() > 0
                else 1.0
            )
        medians = np.array([np.median(soc[folds == f]) for f in range(n_folds)])
        high_counts = np.array([(high & (folds == f)).sum() for f in range(n_folds)])
        terms = [
            sizes.max() / sizes.min(),
            float(np.mean(imbalance)),
            medians.std() / medians.mean() if medians.mean() > 0 else 1.0,
            high_counts.std() / high_counts.mean() if high_counts.mean() > 0 else 1.0,
        ]
        score = sum(w * t for w, t in zip(search["weights"], terms))
        records.append(dict(seed=seed, score=score, fold_sizes=sizes.tolist()))
        if score < best_score:
            best_score, best = score, assignment
    if best is None:
        raise ValueError("No valid five-fold block assignment.")
    result = data.copy()
    result["cv_fold"] = -1
    result.loc[~result.holdout, "cv_fold"] = (
        result.loc[~result.holdout, "block_id"].map(best).astype(int)
    )
    return result, records


def make_inner_split(data, seed):
    settings = CONFIG["inner"]
    fraction, tolerance = settings["fraction"], settings["tolerance"]
    counts = data.block_id.value_counts(sort=False).sort_values(
        ascending=False, kind="stable"
    )
    blocks = counts.index.to_numpy()
    target = int(fraction * len(data))
    total = data.AEZ_name.value_counts()
    best, best_score = None, float("inf")
    for offset in range(settings["n_search"]):
        rng = np.random.default_rng(seed + offset)
        n, selected = 0, set()
        for block in rng.permutation(blocks):
            n += counts[block]
            selected.add(block)
            if n >= target:
                break
        mask = data.block_id.isin(selected).to_numpy()
        if abs(mask.mean() - fraction) > tolerance:
            continue
        share = (
            data.loc[mask, "AEZ_name"].value_counts().reindex(total.index, fill_value=0)
            / total
        )
        score = abs(mask.mean() - fraction) + ((share - fraction) ** 2).sum()
        if score < best_score:
            best_score, best = score, (np.where(~mask)[0], np.where(mask)[0])
    if best is None:
        rng = np.random.default_rng(seed)
        n, selected = 0, []
        for block in rng.permutation(blocks):
            n += counts[block]
            selected.append(block)
            if n >= target:
                break
        mask = data.block_id.isin(selected).to_numpy()
        best = np.where(~mask)[0], np.where(mask)[0]
    return best


def spatial_design(data, output):
    if "cv_fold" in data:
        if not np.equal(data.cv_fold, np.floor(data.cv_fold)).all():
            raise ValueError("Noninteger frozen fold labels.")
        data["cv_fold"] = data.cv_fold.astype(int)
        candidates = []
    else:
        data, candidates = assign_spatial_folds(data)
    work = data.loc[~data.holdout].reset_index(drop=True)
    holdout = data.loc[data.holdout].reset_index(drop=True)
    sizes = (
        work.groupby("cv_fold").size().reindex(range(CONFIG["n_folds"]), fill_value=0)
    )
    if sizes.tolist() != CONFIG["expected_fold_n"]:
        raise ValueError(
            "Fold sizes differ from the frozen manuscript folds: " + str(sizes.tolist())
        )
    if not data.loc[data.holdout, "cv_fold"].eq(-1).all():
        raise ValueError("Holdout fold labels must be -1.")
    if not work.groupby("block_id").cv_fold.nunique().eq(1).all():
        raise ValueError("A working block crosses spatial folds.")
    contexts, records = {}, {}
    for fold in range(CONFIG["n_folds"]):
        train = np.flatnonzero(work.cv_fold.ne(fold))
        evaluate = np.flatnonzero(work.cv_fold.eq(fold))
        seed = CONFIG["inner"]["seed_base"] + fold * CONFIG["inner"]["seed_step"]
        inner_train, inner_evaluate = make_inner_split(
            work.iloc[train].reset_index(drop=True), seed
        )
        if (
            abs(len(inner_evaluate) / len(train) - CONFIG["inner"]["fraction"])
            > CONFIG["inner"]["tolerance"]
        ):
            raise ValueError("Inner split fails the original fraction-tolerance gate.")
        contexts[fold] = dict(
            outer=(train, evaluate), tune=(train[inner_train], train[inner_evaluate])
        )
        for role, (a, b) in contexts[fold].items():
            if set(work.iloc[a].block_id) & set(work.iloc[b].block_id):
                raise ValueError("Spatial training and evaluation blocks overlap.")
            records[f"f{fold}_{role}"] = dict(
                train_source_rows=work.iloc[a]._source_row.to_list(),
                evaluate_source_rows=work.iloc[b]._source_row.to_list(),
            )
    save_csv(output / "analysis_samples_folds.csv", data)
    save_json(output / "spatial_contexts.json", records)
    save_json(output / "fold_search.json", candidates)
    save_json(
        output / "seed59_allocation.json",
        dict(
            seed=59,
            block_width_km=75,
            holdout_blocks=sorted(int(b) for b in holdout.block_id.unique()),
        ),
    )
    return work, holdout, contexts


# 2. Preprocessing and nested spatial model fits
def category_tokens(frame):
    values = frame[CONFIG["categorical"]].to_numpy(float)
    if not np.isfinite(values).all() or not np.equal(values, np.floor(values)).all():
        raise ValueError("Invalid categorical codes.")
    return values.astype("int64").astype(str)


def fit_preprocessor(training, ridge=False):
    cont, cat = CONFIG["continuous"], CONFIG["categorical"]
    prep = dict(
        continuous=cont,
        categorical=cat,
        continuous_scaler=StandardScaler().fit(training[cont]),
        onehot_encoder=OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(
            category_tokens(training)
        ),
    )
    if ridge:
        prep["flowacc_scaler"] = StandardScaler().fit(
            np.log1p(training[["r_flowacc"]].to_numpy(float))
        )
    return prep


def transform_frame(frame, prep, native):
    cont, cat = prep["continuous"], prep["categorical"]
    continuous = prep["continuous_scaler"].transform(frame[cont]).astype("float32")
    if "flowacc_scaler" in prep:
        continuous[:, cont.index("r_flowacc")] = prep["flowacc_scaler"].transform(
            np.log1p(frame[["r_flowacc"]].to_numpy(float))
        )[:, 0]
    categories = category_tokens(frame)
    if not native:
        return np.column_stack(
            [continuous, prep["onehot_encoder"].transform(categories).astype("float32")]
        )
    X = pd.DataFrame(continuous, columns=cont)
    for j, name in enumerate(cat):
        X[name] = categories[:, j]
    return X


def learner_kind(alias):
    return (
        "ridge"
        if alias == "ridge_flowacc_log"
        else "cb"
        if alias.startswith("cb")
        else alias
    )


def estimator(kind, parameters, early=False, quantile=None):
    if kind == "ridge":
        return Ridge(**parameters, solver="lsqr")
    if kind == "rf":
        return RandomForestRegressor(
            **parameters, random_state=CONFIG["model_seed"], n_jobs=CONFIG["threads"]
        )
    if kind == "xgb":
        options = dict(
            parameters,
            objective="reg:squarederror",
            eval_metric="rmse",
            tree_method="hist",
            n_jobs=CONFIG["threads"],
            random_state=CONFIG["model_seed"],
        )
        if early:
            options["early_stopping_rounds"] = CONFIG["early_stopping"]
        return XGBRegressor(**options)
    loss = "RMSE" if quantile is None else f"Quantile:alpha={quantile}"
    return CatBoostRegressor(
        **parameters,
        loss_function=loss,
        eval_metric=loss,
        bootstrap_type="Bayesian",
        grow_policy="SymmetricTree",
        boosting_type="Plain",
        task_type="CPU",
        random_seed=CONFIG["model_seed"],
        thread_count=CONFIG["threads"],
        allow_writing_files=False,
        verbose=False,
    )


def fit_estimator(
    model, kind, X, target, weights=None, evaluate=None, evaluate_target=None
):
    arguments = {}
    if weights is not None:
        arguments["sample_weight"] = weights
    if kind == "cb":
        arguments["cat_features"] = list(
            range(
                len(CONFIG["continuous"]),
                len(CONFIG["continuous"]) + len(CONFIG["categorical"]),
            )
        )
        if evaluate is not None:
            arguments.update(
                eval_set=(evaluate, evaluate_target),
                early_stopping_rounds=CONFIG["early_stopping"],
                use_best_model=True,
            )
    elif kind == "xgb" and evaluate is not None:
        arguments.update(eval_set=[(evaluate, evaluate_target)], verbose=False)
    model.fit(X, target, **arguments)
    return model


def tune_model(alias, fold, training, validation, folder):
    kind = learner_kind(alias)
    native = kind == "cb"
    prep = fit_preprocessor(training, ridge=kind == "ridge")
    X, V = (
        transform_frame(training, prep, native),
        transform_frame(validation, prep, native),
    )
    target, validation_target = (
        np.log1p(training.OC.to_numpy()),
        np.log1p(validation.OC.to_numpy()),
    )
    weights = rank_weights(training.OC) if alias.startswith("cbqw") else None
    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=CONFIG["tuning_seed"] + fold),
        pruner=optuna.pruners.NopPruner(),
    )

    def objective(trial):
        parameters = {}
        for name, specification in CONFIG["search_spaces"][kind].items():
            options = {
                k: v
                for k, v in specification.items()
                if k not in ["type", "low", "high"]
            }
            suggest = (
                trial.suggest_int
                if specification["type"] == "int"
                else trial.suggest_float
            )
            parameters[name] = suggest(
                name, specification["low"], specification["high"], **options
            )
        model = estimator(kind, parameters, early=True)
        fit_estimator(model, kind, X, target, weights, V, validation_target)
        prediction = model.predict(V)
        if not np.isfinite(prediction).all():
            raise ValueError("Nonfinite inner prediction.")
        trial.set_user_attr("effective_params", parameters)
        rounds = (
            int(model.tree_count_)
            if kind == "cb"
            else int(model.best_iteration) + 1
            if kind == "xgb"
            else None
        )
        if rounds:
            trial.set_user_attr("selected_rounds", rounds)
        return float(np.sqrt(np.mean((validation_target - prediction) ** 2)))

    budget = CONFIG["trials"][kind]
    for number in range(budget):
        study.optimize(objective, n_trials=1, n_jobs=1, show_progress_bar=False)
        if (number + 1) % 10 == 0:
            print(f"{alias}, fold {fold}: {number + 1}/{budget} trials", flush=True)
    parameters = study.best_trial.user_attrs["effective_params"].copy()
    rounds = study.best_trial.user_attrs.get("selected_rounds")
    if rounds:
        parameters["iterations" if kind == "cb" else "n_estimators"] = rounds
    save_csv(folder / "trials.csv", study.trials_dataframe())
    save_json(
        folder / "best_params.json",
        dict(
            params=parameters,
            inner_log_RMSE=study.best_value,
            trials=budget,
            tuning_seed=CONFIG["tuning_seed"] + fold,
        ),
    )
    return parameters


def save_model(model, kind, folder):
    folder.mkdir(parents=True, exist_ok=True)
    if kind == "cb":
        model.save_model(str(folder / "model.cbm"), format="cbm")
    elif kind == "xgb":
        model.save_model(str(folder / "model.ubj"))
    else:
        save_pickle(folder / "model.pkl", model)


def gamma(distance, parameters):
    psill, radius, nugget = parameters
    h = np.asarray(distance)
    u = np.minimum(h / radius, 1.0)
    return np.where(h == 0, 0.0, nugget + psill * (1.5 * u - 0.5 * u**3))


def fit_variogram(xy, z, cfg, seed):
    if not np.isfinite(xy).all() or not np.isfinite(z).all():
        raise RuntimeError("Invalid variogram training values.")
    variance = float(np.var(z))
    if variance <= 1e-12:
        return (
            None,
            pd.DataFrame(
                columns=["lag_km", "semivariance", "pair_count", "fitted_semivariance"]
            ),
            ["constant training field: mean prediction"],
        )
    rng = np.random.default_rng(seed)
    pairs = rng.integers(0, len(z), size=(cfg["pair_draws"], 2))
    pairs.sort(axis=1)
    pairs = np.unique(pairs[pairs[:, 0] != pairs[:, 1]], axis=0)
    h = np.linalg.norm(xy[pairs[:, 0]] - xy[pairs[:, 1]], axis=1)
    keep = (h > 0) & (h < cfg["max_lag_km"])
    pairs, h = pairs[keep], h[keep]
    g = 0.5 * (z[pairs[:, 0]] - z[pairs[:, 1]]) ** 2
    bins = np.floor(h / cfg["max_lag_km"] * cfg["bins"]).astype(int)
    counts = np.bincount(bins, minlength=cfg["bins"])
    good = counts >= cfg["min_pairs"]
    if good.sum() < 6:
        raise RuntimeError(
            "Fewer than six supported variogram bins; inspect the input field and lag settings."
        )
    lag = np.bincount(bins, weights=h, minlength=cfg["bins"])[good] / counts[good]
    semivariance = (
        np.bincount(bins, weights=g, minlength=cfg["bins"])[good] / counts[good]
    )
    upper = np.array([10 * variance, 2 * cfg["max_lag_km"], 10 * variance])
    lower = np.array([1e-12, 1.0, 0.0])
    w = np.sqrt(counts[good] / counts[good].max())
    fits = [
        least_squares(
            lambda p: w * (gamma(lag, p) - semivariance) / variance,
            x0=[0.7 * variance, r, 0.3 * variance],
            bounds=(lower, upper),
            x_scale=[variance, 50.0, variance],
            max_nfev=2000,
        )
        for r in [25.0, 75.0, 150.0]
    ]
    fits = [f for f in fits if f.success and np.isfinite(f.x).all()]
    if not fits:
        raise RuntimeError("Training-only variogram fit failed.")
    fitted = min(fits, key=lambda f: f.cost).x
    flags = []
    for j, name in [(0, "partial sill"), (1, "range"), (2, "nugget")]:
        if fitted[j] >= 0.99 * upper[j]:
            flags.append(name + " near upper fit bound")
    if fitted[1] <= 1.01:
        flags.append("range near lower fit bound")
    if fitted[0] <= variance * 1e-6:
        flags.append("negligible spatial partial sill")
    empirical = pd.DataFrame(
        {
            "lag_km": lag,
            "semivariance": semivariance,
            "pair_count": counts[good],
            "fitted_semivariance": gamma(lag, fitted),
        }
    )
    return fitted, empirical, flags


def krige(xy, z, query, parameters, cfg):
    if len(np.unique(xy, axis=0)) != len(xy):
        raise RuntimeError("Duplicate training coordinates require review.")
    k = min(cfg["neighbours"], len(z))
    if k < 2:
        raise RuntimeError("Too few kriging neighbours.")
    out = np.full(len(query), np.nan)
    out_var = np.full(len(query), np.nan)
    start = 0
    fallback = 0
    sum_error = 0.0
    negative_var = 0
    if parameters is None:
        out[:] = float(np.mean(z))
        out_var[:] = float(np.var(z))
        start = len(query)
    else:
        tree = cKDTree(xy)
        with contextlib.nullcontext():
            for offset in range(start, len(query), cfg["batch_size"]):
                q = query[offset : offset + cfg["batch_size"]]
                distance, index = tree.query(q, k=k, workers=1)
                neighbours = xy[index]
                between = np.linalg.norm(
                    neighbours[:, :, None, :] - neighbours[:, None, :, :], axis=-1
                )
                matrix = np.zeros((len(q), k + 1, k + 1))
                matrix[:, :k, :k] = gamma(between, parameters)
                matrix[:, :k, k] = 1.0
                matrix[:, k, :k] = 1.0
                rhs = np.column_stack([gamma(distance, parameters), np.ones(len(q))])
                try:
                    solution = np.linalg.solve(matrix, rhs[..., None])[..., 0]
                except np.linalg.LinAlgError:
                    solution = np.empty_like(rhs)
                    for row in range(len(q)):
                        try:
                            solution[row] = np.linalg.solve(matrix[row], rhs[row])
                        except np.linalg.LinAlgError:
                            solution[row] = np.linalg.lstsq(
                                matrix[row], rhs[row], rcond=1e-12
                            )[0]
                            fallback += 1
                if not np.allclose(
                    np.einsum("bij,bj->bi", matrix, solution),
                    rhs,
                    atol=1e-07,
                    rtol=1e-07,
                ):
                    raise RuntimeError(
                        "Kriging linear-system residual exceeds tolerance."
                    )
                lambdas = solution[:, :k]
                error = float(np.max(np.abs(lambdas.sum(axis=1) - 1)))
                if error > 1e-07:
                    raise RuntimeError("Kriging weights do not sum to one.")
                sum_error = max(sum_error, error)
                variance = np.sum(lambdas * rhs[:, :k], axis=1) + solution[:, k]
                negative_var += int((variance < -1e-08).sum())
                if (variance < -1e-08).any():
                    raise RuntimeError(
                        "Materially negative kriging variance; review the solve."
                    )
                out[offset : offset + len(q)] = np.sum(lambdas * z[index], axis=1)
                out_var[offset : offset + len(q)] = np.maximum(variance, 0)
    if not np.isfinite(out).all() or not np.isfinite(out_var).all():
        raise RuntimeError("Nonfinite kriging prediction.")
    return (
        out,
        out_var,
        {
            "least_squares_fallbacks": fallback,
            "maximum_weight_sum_error": sum_error,
            "negative_variance_count": negative_var,
            "neighbours": k,
        },
    )


def fit_cv_alias(work, contexts, alias, output):
    kind = learner_kind(alias)
    parameters, pieces, records = {}, [], []
    for fold in range(CONFIG["n_folds"]):
        train_index, evaluate_index = contexts[fold]["outer"]
        training = work.iloc[train_index].reset_index(drop=True)
        evaluate = work.iloc[evaluate_index].reset_index(drop=True)
        folder = output / "models" / alias / f"f{fold}"
        folder.mkdir(parents=True, exist_ok=True)
        if kind == "mean":
            value = float(training.OC.mean())
            prediction = np.full(len(evaluate), value)
            log_prediction = np.log1p(prediction)
            save_json(folder / "model.json", dict(training_mean=value))
        elif kind == "ok":
            xy = training[["x_proj", "y_proj"]].to_numpy() / 1000
            query = evaluate[["x_proj", "y_proj"]].to_numpy() / 1000
            target = np.log1p(training.OC.to_numpy())
            fitted, empirical, flags = fit_variogram(
                xy, target, CONFIG["kriging"], CONFIG["master_seed"] + fold
            )
            log_prediction, variance, solve = krige(
                xy, target, query, fitted, CONFIG["kriging"]
            )
            prediction = inverse(log_prediction)
            save_csv(folder / "variogram.csv", empirical)
            save_json(
                folder / "kriging.json",
                dict(parameters=fitted, flags=flags, solve=solve),
            )
            save_pickle(
                folder / "model.pkl",
                dict(xy_km=xy, log_target=target, parameters=fitted),
            )
        else:
            a, b = contexts[fold]["tune"]
            parameters[fold] = tune_model(
                alias,
                fold,
                work.iloc[a].reset_index(drop=True),
                work.iloc[b].reset_index(drop=True),
                folder,
            )
            prep = fit_preprocessor(training, ridge=kind == "ridge")
            X, V = (
                transform_frame(training, prep, kind == "cb"),
                transform_frame(evaluate, prep, kind == "cb"),
            )
            model = estimator(kind, parameters[fold])
            fit_estimator(
                model,
                kind,
                X,
                np.log1p(training.OC.to_numpy()),
                rank_weights(training.OC) if alias.startswith("cbqw") else None,
            )
            log_prediction = np.asarray(model.predict(V), float)
            prediction = inverse(log_prediction)
            save_model(model, kind, folder)
            save_pickle(folder / "preprocessor.pkl", prep)
            del model, X, V
            gc.collect()
        frame = evaluate[["_source_row", "block_id", "AEZ", "AEZ_name", "OC"]].copy()
        frame["fold"] = fold
        frame["log_prediction"], frame["prediction"] = log_prediction, prediction
        pieces.append(frame)
        records.append(dict(alias=alias, fold=fold, **metrics(evaluate.OC, prediction)))
        save_csv(folder / "predictions.csv", frame)
        print(f"{alias}, fold {fold}: R2={records[-1]['r2']:.6f}", flush=True)
    predictions = pd.concat(pieces, ignore_index=True).set_index(
        "_source_row", drop=False
    )
    predictions = predictions.loc[work._source_row].reset_index(drop=True)
    save_csv(output / "predictions" / f"{alias}_OOF.csv", predictions)
    return dict(parameters=parameters, predictions=predictions, metrics=records)


def summarize_cv(results, output):
    rows, fold_rows = [], []
    for alias, result in results.items():
        scores = pd.DataFrame(result["metrics"])
        pooled = metrics(result["predictions"].OC, result["predictions"].prediction)
        row = dict(alias=alias)
        for name in ["r2", "rmse", "mae", "bias", "ccc", "rpiq"]:
            row[name + "_fold_mean"] = float(scores[name].mean())
            row[name + "_fold_sd_ddof1"] = float(scores[name].std(ddof=1))
            row[name + "_pooled"] = pooled[name]
        rows.append(row)
        fold_rows.extend(result["metrics"])
    summary = pd.DataFrame(rows)
    save_csv(output / "model_comparison.csv", summary)
    save_csv(output / "fold_metrics.csv", pd.DataFrame(fold_rows))
    print(summary.round(6).to_string(index=False), flush=True)
    return summary


def nested_spatial_cv(work, contexts, output):
    results = {
        alias: fit_cv_alias(work, contexts, alias, output) for alias in CONFIG["models"]
    }
    summarize_cv(results, output)
    return results


# 3. Matched nested random CV
def random_cv(work, output):
    contexts = {}
    splitter = KFold(
        CONFIG["n_folds"], shuffle=True, random_state=CONFIG["random_cv_seed"]
    )
    for fold, (train, evaluate) in enumerate(splitter.split(work)):
        a, b = train_test_split(
            train,
            test_size=0.20,
            random_state=CONFIG["inner"]["seed_base"]
            + CONFIG["inner"]["seed_step"] * fold,
        )
        contexts[fold] = dict(outer=(train, evaluate), tune=(a, b))
    save_json(
        output / "random_contexts.json",
        {
            str(f): {
                role: [work.iloc[i]._source_row.to_list() for i in pair]
                for role, pair in context.items()
            }
            for f, context in contexts.items()
        },
    )
    return fit_cv_alias(work, contexts, "cbqw_random", output)


# 4. Median-parameter working-set refits and holdout predictions
def median_parameters(parameters, kind):
    records = [parameters[f] for f in range(CONFIG["n_folds"])]
    result = {}
    for name in records[0]:
        value = float(np.median([record[name] for record in records]))
        is_integer = CONFIG["search_spaces"][kind].get(name, {}).get("type") == "int"
        result[name] = int(round(value)) if is_integer else value
    return result


def final_refit(work, holdout, cv_results, output):
    parameters = {
        alias: median_parameters(result["parameters"], learner_kind(alias))
        for alias, result in cv_results.items()
        if result["parameters"]
    }
    save_json(
        output / "frozen_parameters.json",
        dict(
            policy="median outer-fold optima",
            parameters=parameters,
            main_model="cbqw",
            weight_alpha=CONFIG["weight_alpha"],
        ),
    )
    joined = holdout[["_source_row", "block_id", "AEZ", "AEZ_name", "OC"]].copy()
    point_model, point_prep = None, None
    for alias in CONFIG["models"]:
        kind = learner_kind(alias)
        folder = output / "models" / alias
        folder.mkdir(parents=True, exist_ok=True)
        if kind == "mean":
            prediction = np.full(len(holdout), float(work.OC.mean()))
            log_prediction = np.log1p(prediction)
            save_json(folder / "model.json", dict(training_mean=float(work.OC.mean())))
        elif kind == "ok":
            xy = work[["x_proj", "y_proj"]].to_numpy() / 1000
            target = np.log1p(work.OC.to_numpy())
            fitted, empirical, flags = fit_variogram(
                xy, target, CONFIG["kriging"], CONFIG["model_seed"] + 5
            )
            log_prediction, variance, solve = krige(
                xy,
                target,
                holdout[["x_proj", "y_proj"]].to_numpy() / 1000,
                fitted,
                CONFIG["kriging"],
            )
            prediction = inverse(log_prediction)
            save_csv(folder / "variogram.csv", empirical)
            save_json(
                folder / "kriging.json",
                dict(parameters=fitted, flags=flags, solve=solve),
            )
            save_pickle(
                folder / "model.pkl",
                dict(xy_km=xy, log_target=target, parameters=fitted),
            )
        else:
            prep = fit_preprocessor(work, ridge=kind == "ridge")
            X, V = (
                transform_frame(work, prep, kind == "cb"),
                transform_frame(holdout, prep, kind == "cb"),
            )
            model = estimator(kind, parameters[alias])
            fit_estimator(
                model,
                kind,
                X,
                np.log1p(work.OC.to_numpy()),
                rank_weights(work.OC) if alias == "cbqw" else None,
            )
            log_prediction = np.asarray(model.predict(V), float)
            prediction = inverse(log_prediction)
            save_model(model, kind, folder)
            save_pickle(folder / "preprocessor.pkl", prep)
            if alias == "cbqw":
                point_model, point_prep = model, prep
            else:
                del model
            del X, V
            gc.collect()
        joined[alias] = prediction
        packet = holdout[["_source_row", "block_id", "OC"]].copy()
        packet["log_prediction"], packet["prediction"] = log_prediction, prediction
        save_csv(folder / "predictions.csv", packet)
    national, zones = [], []
    for alias in CONFIG["models"]:
        national.append(dict(model=alias, **metrics(joined.OC, joined[alias])))
        for code, zone in CONFIG["aez_legend"].items():
            if zone == "WB":
                continue
            frame = joined.loc[joined.AEZ.eq(code)]
            score = metrics(frame.OC, frame[alias])
            raw_r2 = score["r2"]
            if len(frame) < 30:
                score["r2"] = None
            zones.append(
                dict(
                    model=alias,
                    AEZ=code,
                    AEZ_name=zone,
                    small_n_lt30=len(frame) < 30,
                    r2_descriptive=raw_r2,
                    **score,
                )
            )
    save_csv(output / "holdout_predictions.csv", joined)
    save_csv(output / "holdout_metrics.csv", pd.DataFrame(national))
    save_csv(output / "AEZ_metrics.csv", pd.DataFrame(zones))
    print(
        "Holdout evaluation\n" + pd.DataFrame(national).round(6).to_string(index=False),
        flush=True,
    )
    return dict(
        model=point_model,
        preprocessor=point_prep,
        parameters=parameters,
        predictions=joined,
    )


# 5. Quantile models and signed CQR
METHODS = CONFIG["calibration"]["methods"]
LEVELS = CONFIG["calibration"]["levels"]
MIN_N = CONFIG["calibration"]["minimum_group_n"]
RELATIVE_SCORE_LIMIT = CONFIG["calibration"]["relative_score_limit"]
SECTION_A = "A. Working OOF — decision basis"
SECTION_B = "B. Hold-out — post-hoc check"


def conformal_quantile(scores, level):
    values = np.asarray(scores, float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("Invalid calibration scores.")
    rank = math.ceil((len(values) + 1) * level / 100 - 1e-12)
    if rank > len(values):
        raise ValueError("Too few national calibration observations for this level.")
    return float(np.partition(values, rank - 1)[rank - 1]), int(rank)


def interval_arrays(y, point, lower, upper, level):
    y, point, lower, upper = [np.asarray(v, float) for v in [y, point, lower, upper]]
    if len({v.shape for v in [y, point, lower, upper]}) != 1:
        raise ValueError("Interval shapes differ.")
    if not all(np.isfinite(v).all() for v in [y, point, lower, upper]):
        raise ValueError("Nonfinite interval inputs.")
    empty = (lower > upper) | (upper < 0)
    lo, hi = inverse(lower), inverse(upper)
    covered = ~empty & (y >= lo) & (y <= hi)
    width = np.where(empty, 0.0, hi - lo)
    score = width + 2 / (1 - level / 100) * (
        np.maximum(lo - y, 0) + np.maximum(y - hi, 0)
    )
    score[empty] = np.nan
    return dict(
        lo=lo,
        hi=hi,
        empty=empty,
        covered=covered,
        width=width,
        score=score,
        point_outside=empty | (point < lo) | (point > hi),
    )


def summary(arrays, mask):
    mask = np.asarray(mask, bool)
    n = int(mask.sum())
    if not n:
        return dict(
            n=0,
            coverage_pct=None,
            mean_width_OC=None,
            mean_interval_score_OC=None,
            n_empty=0,
            n_point_outside=0,
        )
    empty = int(arrays["empty"][mask].sum())
    return dict(
        n=n,
        coverage_pct=float(100 * arrays["covered"][mask].mean()),
        mean_width_OC=float(arrays["width"][mask].mean()),
        mean_interval_score_OC=None if empty else float(arrays["score"][mask].mean()),
        n_empty=empty,
        n_point_outside=int(arrays["point_outside"][mask].sum()),
    )


def quintile_edges(values):
    values = np.asarray(values, float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("Invalid quintile values.")
    return np.unique(np.quantile(values, [0.2, 0.4, 0.6, 0.8])).tolist()


def bins(values, edges):
    return (
        np.searchsorted(
            np.asarray(edges, float), np.asarray(values, float), side="right"
        )
        + 1
    )


def group_keys(method, aez, predicted_bin):
    aez = np.asarray(aez, int)
    predicted_bin = np.asarray(predicted_bin, int)
    if method == METHODS[0]:
        return np.full(len(aez), "national", dtype=object)
    if method == METHODS[1]:
        return np.array(["AEZ:" + str(x) for x in aez], dtype=object)
    if method == METHODS[2]:
        return np.array(["Q:" + str(x) for x in predicted_bin], dtype=object)
    if method == METHODS[3]:
        return np.array(
            ["AEZ:" + str(x) + "|Q:" + str(q) for x, q in zip(aez, predicted_bin)],
            dtype=object,
        )
    raise ValueError("Unknown calibration method: " + method)


def calibrator(scores, aez, point, method, level, edges, land):
    national, rank = conformal_quantile(scores, level)
    predicted = bins(point, edges)
    keys = group_keys(method, aez, predicted)
    if method == METHODS[0]:
        universe = ["national"]
    elif method == METHODS[1]:
        universe = ["AEZ:" + str(int(z)) for z in land.VALUE]
    elif method == METHODS[2]:
        universe = ["Q:" + str(q) for q in range(1, len(edges) + 2)]
    else:
        universe = [
            "AEZ:" + str(int(z)) + "|Q:" + str(q)
            for z in land.VALUE
            for q in range(1, len(edges) + 2)
        ]
    records = [
        dict(
            method=method,
            level=level,
            group="national",
            calibration_n=len(scores),
            correction_signed=national,
            fallback=False,
            used_n=len(scores),
            used_rank=rank,
        )
    ]
    if method != METHODS[0]:
        for key in universe:
            mask = keys == key
            count = int(mask.sum())
            fallback = count < MIN_N
            correction, used_rank = (
                (national, rank)
                if fallback
                else conformal_quantile(np.asarray(scores)[mask], level)
            )
            records.append(
                dict(
                    method=method,
                    level=level,
                    group=key,
                    calibration_n=count,
                    correction_signed=correction,
                    fallback=fallback,
                    used_n=len(scores) if fallback else count,
                    used_rank=used_rank,
                )
            )
    return pd.DataFrame(records)


def apply_corrections(table, method, level, aez, point, edges):
    table = table.loc[table.method.eq(method) & table.level.eq(level)].set_index(
        "group"
    )
    if "national" not in table.index or table.index.duplicated().any():
        raise ValueError("Invalid correction table.")
    keys = group_keys(method, aez, bins(point, edges))
    national = table.loc["national"]
    correction = []
    fallback = []
    calibration_n = []
    for key in keys:
        row = table.loc[key] if key in table.index else national
        correction.append(float(row.correction_signed))
        fallback.append(bool(row.fallback) if key in table.index else True)
        calibration_n.append(int(row.calibration_n) if key in table.index else 0)
    return np.array(correction), np.array(fallback), np.array(calibration_n)


def assessed_bounds(frame, tables, edges, raw_style):
    shape = (len(METHODS), len(LEVELS), len(frame))
    lo = np.empty(shape)
    hi = np.empty(shape)
    correction = np.empty(shape)
    fallback = np.empty(shape, bool)
    counts = np.empty(shape, int)
    nesting = []
    for mi, method in enumerate(METHODS):
        original = {}
        for li, level in enumerate(LEVELS):
            c, f, n = apply_corrections(
                tables, method, level, frame.AEZ, frame.point_prediction, edges
            )
            if raw_style == "working":
                rawlo, rawhi = frame[f"raw_lower_{level}"], frame[f"raw_upper_{level}"]
            else:
                rawlo, rawhi = (
                    frame[f"raw_lower_log_{level}"],
                    frame[f"raw_upper_log_{level}"],
                )
            a, b = (
                np.minimum(rawlo, rawhi).to_numpy() - c,
                np.maximum(rawlo, rawhi).to_numpy() + c,
            )
            lo[mi, li], hi[mi, li] = a, b
            correction[mi, li], fallback[mi, li], counts[mi, li] = c, f, n
            original[level] = interval_arrays(
                frame.OC, frame.point_prediction, a, b, level
            )
        oldlo, oldhi = lo[mi, 1].copy(), hi[mi, 1].copy()
        lo[mi, 1] = np.minimum(lo[mi, 0], oldlo)
        hi[mi, 1] = np.maximum(hi[mi, 0], oldhi)
        after = interval_arrays(
            frame.OC, frame.point_prediction, lo[mi, 1], hi[mi, 1], 95
        )
        if np.any(original[95]["covered"] & ~after["covered"]):
            raise RuntimeError("95% nesting lost coverage.")
        if np.any(
            ~original[90]["empty"]
            & (
                after["empty"]
                | (after["lo"] > original[90]["lo"])
                | (after["hi"] < original[90]["hi"])
            )
        ):
            raise RuntimeError("95% nesting failed containment.")
        for variant, arr in [("original95", original[95]), ("nested95", after)]:
            nesting.append(
                dict(
                    method=method,
                    variant=variant,
                    level=95,
                    n_bounds_changed=int(
                        ((oldlo != lo[mi, 1]) | (oldhi != hi[mi, 1])).sum()
                    ),
                    **summary(arr, np.ones(len(frame), bool)),
                )
            )
    return dict(
        lower_log=lo,
        upper_log=hi,
        correction=correction,
        national_fallback=fallback,
        group_calibration_n=counts,
    ), nesting


def select_method(table):
    rows = []
    if set(table.section) != {SECTION_A}:
        raise ValueError("Selection accepts working OOF results only.")
    for order, method in enumerate(METHODS):
        national = table.loc[
            table.method.eq(method) & table.scope.eq("overall")
        ].sort_values("level")
        if national.level.tolist() != LEVELS:
            raise ValueError("Missing levels for selection.")
        score = (
            float(national.mean_interval_score_OC.mean())
            if national.mean_interval_score_OC.notna().all()
            else np.nan
        )
        groups = table.loc[
            table.method.eq(method) & table.scope.ne("overall") & table.n.gt(0)
        ]
        worst = groups.sort_values(
            ["coverage_pct", "level", "scope", "group"], kind="stable"
        ).iloc[0]
        rows.append(
            dict(
                method=method,
                mean_two_level_interval_score_OC=score,
                worst_group_coverage_pct=float(worst.coverage_pct),
                worst_group=str(worst.scope) + ":" + str(worst.group),
                worst_group_level=int(worst.level),
                worst_group_n=int(worst.n),
                tie_order=order,
            )
        )
    result = pd.DataFrame(rows)
    finite = result.mean_two_level_interval_score_OC.notna()
    if not finite.any():
        raise RuntimeError(
            "No calibration candidate has finite overall interval scores at both levels."
        )
    best_score = float(result.loc[finite, "mean_two_level_interval_score_OC"].min())
    result["score_limit_OC"] = RELATIVE_SCORE_LIMIT * best_score
    result["score_eligible"] = finite & (
        result.mean_two_level_interval_score_OC
        <= RELATIVE_SCORE_LIMIT * best_score + 1e-12
    )
    ranking = result.loc[result.score_eligible].sort_values(
        ["worst_group_coverage_pct", "mean_two_level_interval_score_OC", "tie_order"],
        ascending=[False, True, True],
        kind="stable",
    )
    chosen = ranking.iloc[0].method
    result["selected"] = result.method.eq(chosen)
    return str(chosen), result


def calibration_comparison(frame, bounds, predicted_edges, land, section):
    predicted = bins(frame.point_prediction, predicted_edges)
    observed = (
        np.ones(len(frame), int)
        if frame.OC.nunique() == 1
        else (pd.qcut(frame.OC, 5, labels=False, duplicates="drop").to_numpy() + 1)
    )
    groups = [("overall", "all", np.ones(len(frame), bool))]
    groups += [
        ("predicted_quintile", "Q" + str(q), predicted == q)
        for q in range(1, len(predicted_edges) + 2)
    ]
    groups += [
        ("observed_quintile", "Q" + str(int(q)), observed == q)
        for q in sorted(np.unique(observed))
    ]
    groups += [
        ("AEZ", str(zone.MAEZ), frame.AEZ.to_numpy(int) == int(zone.VALUE))
        for zone in land.itertuples()
    ]
    rows = []
    for mi, method in enumerate(METHODS):
        for li, level in enumerate(LEVELS):
            arrays = interval_arrays(
                frame.OC,
                frame.point_prediction,
                bounds["lower_log"][mi, li],
                bounds["upper_log"][mi, li],
                level,
            )
            for scope, group, mask in groups:
                rows.append(
                    dict(
                        section=section,
                        method=method,
                        level=level,
                        bounds="nested95" if level == 95 else "original90",
                        scope=scope,
                        group=group,
                        small_group_n_lt_100=0 < int(mask.sum()) < MIN_N,
                        n_national_fallback=int(
                            bounds["national_fallback"][mi, li, mask].sum()
                        ),
                        **summary(arrays, mask),
                    )
                )
    return pd.DataFrame(rows)


def calibration_tables(frame, edges, land):
    return pd.concat(
        [
            calibrator(
                frame[f"CQR_score_{level}"].to_numpy(),
                frame.AEZ,
                frame.point_prediction,
                method,
                level,
                edges,
                land,
            )
            for method in METHODS
            for level in LEVELS
        ],
        ignore_index=True,
    )


def quantile_tag(tau):
    return "q" + str(int(round(1000 * tau))).zfill(3)


def fit_quantile(training, evaluate, parameters, tau, prep, output, name):
    X, V = transform_frame(training, prep, True), transform_frame(evaluate, prep, True)
    model = estimator("cb", parameters, quantile=tau)
    fit_estimator(
        model, "cb", X, np.log1p(training.OC.to_numpy()), rank_weights(training.OC)
    )
    prediction = np.asarray(model.predict(V), float)
    if not np.isfinite(prediction).all():
        raise ValueError("Nonfinite quantile prediction.")
    path = output / "models" / (name + ".cbm")
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(path), format="cbm")
    print("Quantile fit:", name, "training n:", len(training), flush=True)
    return model, prediction


def interval_prediction_table(frame, bounds):
    rows = []
    for mi, method in enumerate(METHODS):
        for li, level in enumerate(LEVELS):
            arrays = interval_arrays(
                frame.OC,
                frame.point_prediction,
                bounds["lower_log"][mi, li],
                bounds["upper_log"][mi, li],
                level,
            )
            table = frame[["_source_row", "block_id", "AEZ", "AEZ_name", "OC"]].copy()
            table["method"], table["level"] = method, level
            table["point_prediction"] = frame.point_prediction.to_numpy()
            table["lower_log"] = bounds["lower_log"][mi, li]
            table["upper_log"] = bounds["upper_log"][mi, li]
            for name in [
                "lo",
                "hi",
                "empty",
                "covered",
                "width",
                "score",
                "point_outside",
            ]:
                table[name] = arrays[name]
            rows.append(table)
    return pd.concat(rows, ignore_index=True)


def quantiles_and_calibration(work, holdout, contexts, cv_results, final, output):
    working = work[
        ["_source_row", "block_id", "cv_fold", "AEZ", "AEZ_name", "OC"]
    ].copy()
    working["point_log"] = cv_results["cbqw"]["predictions"].log_prediction.to_numpy()
    working["point_prediction"] = inverse(working.point_log)
    evaluation = holdout[["_source_row", "block_id", "AEZ", "AEZ_name", "OC"]].copy()
    evaluation["point_prediction"] = final["predictions"].cbqw.to_numpy()
    land = pd.DataFrame(
        [(code, name) for code, name in CONFIG["aez_legend"].items() if name != "WB"],
        columns=["VALUE", "MAEZ"],
    )
    for level in LEVELS:
        lower = np.full(len(work), np.nan)
        upper = np.full(len(work), np.nan)
        taus = CONFIG["calibration"]["quantiles"][level]
        for fold in range(CONFIG["n_folds"]):
            a, b = contexts[fold]["outer"]
            training, evaluate = (
                work.iloc[a].reset_index(drop=True),
                work.iloc[b].reset_index(drop=True),
            )
            prep = fit_preprocessor(training)
            for tau, destination in zip(taus, [lower, upper]):
                model, prediction = fit_quantile(
                    training,
                    evaluate,
                    cv_results["cbqw"]["parameters"][fold],
                    tau,
                    prep,
                    output,
                    f"f{fold}_{quantile_tag(tau)}",
                )
                destination[b] = prediction
                del model
                gc.collect()
        working[f"raw_lower_{level}"], working[f"raw_upper_{level}"] = lower, upper
        working[f"raw_crossing_{level}"] = lower > upper
        lo, hi = np.minimum(lower, upper), np.maximum(lower, upper)
        working[f"CQR_score_{level}"] = np.maximum(
            lo - np.log1p(working.OC), np.log1p(working.OC) - hi
        )
    save_csv(output / "working_quantile_predictions.csv", working)
    edges = quintile_edges(working.point_prediction)
    shape = len(METHODS), len(LEVELS), len(working)
    lower_log, upper_log = np.empty(shape), np.empty(shape)
    fallback = np.empty(shape, bool)
    fold_corrections, fold_edges, working_nesting = [], {}, []
    for fold in range(CONFIG["n_folds"]):
        mask = working.cv_fold.eq(fold).to_numpy()
        assessment = working.loc[mask].reset_index(drop=True)
        calibration = working.loc[~mask].reset_index(drop=True)
        fold_edges[str(fold)] = quintile_edges(calibration.point_prediction)
        table = calibration_tables(calibration, fold_edges[str(fold)], land)
        bounds, nesting = assessed_bounds(
            assessment, table, fold_edges[str(fold)], "working"
        )
        lower_log[:, :, mask] = bounds["lower_log"]
        upper_log[:, :, mask] = bounds["upper_log"]
        fallback[:, :, mask] = bounds["national_fallback"]
        fold_corrections.append(table.assign(assessment_fold=fold))
        working_nesting.extend(dict(assessment_fold=fold, **row) for row in nesting)
    working_bounds = dict(
        lower_log=lower_log, upper_log=upper_log, national_fallback=fallback
    )
    working_comparison = calibration_comparison(
        working, working_bounds, edges, land, SECTION_A
    )
    chosen, selection = select_method(working_comparison)
    table = calibration_tables(working, edges, land)
    policy = dict(
        method=chosen,
        predicted_edges=edges,
        other_fold_predicted_edges=fold_edges,
        minimum_group_n=MIN_N,
        signed=True,
        nesting_95=CONFIG["calibration"]["nest_95"],
        choice_basis="Working OOF only; existing holdout is a post-hoc check.",
        selection="Best worst-group coverage; mean two-level interval score <=1.05 times best.",
        post_inspection_method_development=True,
        exact_conformal_guarantee=False,
    )
    save_json(output / "phase8_calibration_choice.json", policy)
    save_json(
        output / "phase8_interval_policy.json",
        dict(
            nest_95=True,
            rule="lower95=min(lower90,lower95); upper95=max(upper90,upper95)",
        ),
    )
    save_csv(output / "full_working_corrections.csv", table)
    save_csv(
        output / "working_fold_corrections.csv",
        pd.concat(fold_corrections, ignore_index=True),
    )
    save_csv(output / "working_nesting_diagnostics.csv", pd.DataFrame(working_nesting))
    save_csv(output / "selection_metrics.csv", selection)
    save_csv(output / "working_interval_metrics.csv", working_comparison)
    save_csv(
        output / "working_intervals.csv",
        interval_prediction_table(working, working_bounds),
    )
    print("Working-only calibration choice:", chosen, flush=True)
    models, raw_holdout = {}, {}
    for tau in [0.025, 0.05, 0.95, 0.975]:
        models[tau], raw_holdout[tau] = fit_quantile(
            work,
            holdout,
            final["parameters"]["cbqw"],
            tau,
            final["preprocessor"],
            output,
            "final_" + quantile_tag(tau),
        )
    for level in LEVELS:
        a, b = CONFIG["calibration"]["quantiles"][level]
        evaluation[f"raw_lower_log_{level}"] = raw_holdout[a]
        evaluation[f"raw_upper_log_{level}"] = raw_holdout[b]
        evaluation[f"raw_crossing_{level}"] = raw_holdout[a] > raw_holdout[b]
    evaluated_bounds, holdout_nesting = assessed_bounds(
        evaluation, table, edges, "holdout"
    )
    holdout_comparison = calibration_comparison(
        evaluation, evaluated_bounds, edges, land, SECTION_B
    )
    save_csv(output / "holdout_quantile_predictions.csv", evaluation)
    save_csv(output / "holdout_interval_metrics.csv", holdout_comparison)
    save_csv(output / "holdout_nesting_diagnostics.csv", pd.DataFrame(holdout_nesting))
    save_csv(
        output / "holdout_intervals.csv",
        interval_prediction_table(evaluation, evaluated_bounds),
    )
    print(
        holdout_comparison.loc[holdout_comparison.scope.eq("overall")]
        .round(6)
        .to_string(index=False),
        flush=True,
    )
    return dict(
        models=models,
        policy=policy,
        table=table,
        edges=edges,
        holdout_bounds=evaluated_bounds,
        holdout_frame=evaluation,
    )


def calibrate_pixels(calibration, aez, prediction, raw_quantiles):
    method = calibration["policy"]["method"]
    lower, upper, fallbacks = {}, {}, {}
    codes = np.asarray(aez, int)
    for level in LEVELS:
        a, b = CONFIG["calibration"]["quantiles"][level]
        correction, fallback, _ = apply_corrections(
            calibration["table"], method, level, codes, prediction, calibration["edges"]
        )
        lower[level] = np.minimum(raw_quantiles[a], raw_quantiles[b]) - correction
        upper[level] = np.maximum(raw_quantiles[a], raw_quantiles[b]) + correction
        fallbacks[level] = fallback
    lower[95] = np.minimum(lower[90], lower[95])
    upper[95] = np.maximum(upper[90], upper[95])
    result = {}
    for level in LEVELS:
        empty = (lower[level] > upper[level]) | (upper[level] < 0)
        lo, hi = inverse(lower[level]), inverse(upper[level])
        result.update(
            {
                f"PI{level}_lo_OC": lo,
                f"PI{level}_hi_OC": hi,
                f"PI{level}_width_OC": np.where(empty, 0.0, hi - lo),
                f"PI{level}_empty": empty,
                f"PI{level}_national_fallback": fallbacks[level],
            }
        )
        a, b = CONFIG["calibration"]["quantiles"][level]
        result[f"PI{level}_crossing_raw"] = raw_quantiles[a] > raw_quantiles[b]
    result["predicted_SOC_quintile"] = bins(prediction, calibration["edges"])
    return result


# 6. Working-SHAP dissimilarity and fold-based AOA
def distance_transform(frame, prep):
    continuous = prep["scaler"].transform(frame[prep["continuous"]])
    categories = category_tokens(frame)
    encoded = prep["encoder"].transform(categories)
    X = np.column_stack([continuous, encoded]) * np.asarray(prep["sqrt_column_weights"])
    unseen = np.column_stack(
        [
            ~np.isin(categories[:, j], prep["encoder"].categories_[j])
            for j in range(len(prep["categorical"]))
        ]
    )
    return np.ascontiguousarray(X, dtype="float64"), unseen.any(axis=1), unseen


def nearest_batches(query, reference, own_indices=None):
    tree = cKDTree(reference)
    distances, indices = [], []
    settings = CONFIG["aoa"]
    for start in range(0, len(query), settings["nn_batch"]):
        stop = start + settings["nn_batch"]
        d, i = tree.query(
            query[start:stop],
            k=2 if own_indices is not None else 1,
            workers=settings["distance_workers"],
        )
        if own_indices is not None:
            pick = np.where(i[:, 0] == own_indices[start:stop], 1, 0)
            d, i = d[np.arange(len(d)), pick], i[np.arange(len(i)), pick]
        distances.append(d)
        indices.append(i)
    return np.concatenate(distances), np.concatenate(indices)


def applicability(work, holdout, final, calibration, output):
    features = CONFIG["continuous"] + CONFIG["categorical"]
    model, base = final["model"], final["preprocessor"]
    parts = []
    for start in range(0, len(work), CONFIG["aoa"]["shap_batch"]):
        frame = work.iloc[start : start + CONFIG["aoa"]["shap_batch"]]
        X = transform_frame(frame, base, True)
        values = model.get_feature_importance(
            Pool(X, cat_features=CONFIG["categorical"]),
            type="ShapValues",
            shap_calc_type="Regular",
            thread_count=CONFIG["threads"],
        )
        if values.shape != (len(frame), len(features) + 1):
            raise ValueError("Unexpected native SHAP shape.")
        if np.max(np.abs(values.sum(axis=1) - model.predict(X))) > 1e-5:
            raise ValueError("SHAP additivity failed.")
        parts.append(values)
    values = np.concatenate(parts)
    importance = np.abs(values[:, :-1]).mean(axis=0)
    if not np.isfinite(importance).all() or importance.sum() <= 0:
        raise ValueError("Invalid working SHAP weights.")
    weights = importance / importance.sum()
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(
        category_tokens(work)
    )
    column_weights = list(weights[: len(CONFIG["continuous"])])
    for j, levels in enumerate(encoder.categories_):
        column_weights.extend([weights[len(CONFIG["continuous"]) + j]] * len(levels))
    prep = dict(
        continuous=CONFIG["continuous"],
        categorical=CONFIG["categorical"],
        scaler=StandardScaler().fit(work[CONFIG["continuous"]]),
        encoder=encoder,
        sqrt_column_weights=np.sqrt(column_weights),
        raw_feature_weights=dict(zip(features, weights)),
    )
    reference, unseen, _ = distance_transform(work, prep)
    query, unseen_holdout, unseen_variables = distance_transform(holdout, prep)
    if unseen.any():
        raise ValueError("Working reference contains an unseen category.")
    loo, _ = nearest_batches(reference, reference, np.arange(len(reference)))
    scale = float(loo.mean())
    if scale <= 1e-12:
        raise ValueError("Degenerate working-LOO normalization.")
    fold_distances = np.full(len(work), np.nan)
    for fold in range(CONFIG["n_folds"]):
        mask = work.cv_fold.eq(fold).to_numpy()
        fold_distances[mask] = nearest_batches(reference[mask], reference[~mask])[0]
    if not np.isfinite(fold_distances).all() or (fold_distances + 1e-9 < loo).any():
        raise ValueError("Invalid fold distances.")
    distances, nearest = nearest_batches(query, reference)
    thresholds = {}
    for method, d in [("fold", fold_distances), ("loo", loo)]:
        q25, q75 = np.percentile(d / scale, [25, 75])
        thresholds[method] = dict(
            threshold=float(q75 + CONFIG["aoa"]["iqr_multiplier"] * (q75 - q25)),
            Q1=float(q25),
            Q3=float(q75),
            distance_scale=scale,
            reference_n=len(reference),
            zero_distances=int((d == 0).sum()),
        )
    working_di = work[["_source_row", "block_id", "cv_fold", "AEZ", "AEZ_name"]].copy()
    working_di["loo_distance"], working_di["fold_distance"] = loo, fold_distances
    working_di["DI_loo"], working_di["DI_fold"] = loo / scale, fold_distances / scale
    evaluated = holdout[["_source_row", "block_id", "AEZ", "AEZ_name"]].copy()
    evaluated["DI"] = distances / scale
    evaluated["nearest_reference_source_row"] = work.iloc[
        nearest
    ]._source_row.to_numpy()
    evaluated["unseen_category"] = unseen_holdout
    for j, name in enumerate(CONFIG["categorical"]):
        evaluated["unseen_" + name] = unseen_variables[:, j]
    selected = METHODS.index(calibration["policy"]["method"])
    intervals = interval_arrays(
        holdout.OC,
        final["predictions"].cbqw,
        calibration["holdout_bounds"]["lower_log"][selected, 0],
        calibration["holdout_bounds"]["upper_log"][selected, 0],
        90,
    )
    rows = []
    for method, threshold in thresholds.items():
        inside = (distances / scale <= threshold["threshold"]) & ~unseen_holdout
        evaluated["inside_" + method] = inside
        for name, mask in [
            ("all", np.ones(len(holdout), bool)),
            ("inside", inside),
            ("outside", ~inside),
        ]:
            rows.append(
                dict(
                    AOA_method=method,
                    domain=name,
                    share_pct=100 * float(mask.mean()),
                    **metrics(
                        holdout.loc[mask, "OC"], final["predictions"].loc[mask, "cbqw"]
                    ),
                    **{
                        "PI_coverage_pct": summary(intervals, mask)["coverage_pct"],
                        "PI_mean_width_OC": summary(intervals, mask)["mean_width_OC"],
                    },
                )
            )
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "SHAP_working.npz",
        source_rows=work._source_row.to_numpy(),
        features=np.asarray(features),
        shap=values[:, :-1],
        base=values[:, -1],
    )
    np.savez_compressed(
        output / "AOA_reference.npz",
        weighted_reference=reference,
        source_rows=work._source_row.to_numpy(),
        cv_fold=work.cv_fold.to_numpy(),
    )
    save_pickle(output / "AOA_distance_preprocessor.pkl", prep)
    save_csv(
        output / "AOA_raw_feature_weights.csv",
        pd.DataFrame(
            dict(
                feature=features,
                mean_abs_SHAP=importance,
                normalized_SHAP_weight=weights,
            )
        ),
    )
    save_csv(output / "working_DI.csv", working_di)
    save_csv(output / "evaluation_DI.csv", evaluated)
    save_csv(output / "AOA_both_evaluation_metrics.csv", pd.DataFrame(rows))
    save_json(
        output / "AOA_thresholds.json",
        dict(
            methods=thresholds,
            distance_scale=scale,
            AOA_MAIN=CONFIG["aoa"]["main"],
            weights_source="Working SHAP only",
        ),
    )
    print("AOA thresholds:", clean(thresholds), flush=True)
    return dict(
        preprocessor=prep,
        reference=reference,
        distance_scale=scale,
        thresholds=thresholds,
    )


# 7. Paired whole-block bootstrap, conditional on fitted models
def model_bootstrap(frame, output):
    blocks = np.sort(frame.block_id.unique())
    settings = CONFIG["bootstrap"]
    B = settings["replicates"]
    draw = np.random.default_rng(settings["seed"]).integers(
        0, len(blocks), size=(B, len(blocks))
    )
    groups = frame.groupby("block_id", sort=True)
    n = groups.OC.size().reindex(blocks).to_numpy()
    sy = groups.OC.sum().reindex(blocks).to_numpy()
    sy2 = (
        frame.assign(y2=frame.OC**2)
        .groupby("block_id")
        .y2.sum()
        .reindex(blocks)
        .to_numpy()
    )
    nn, yy = n[draw].sum(axis=1), sy[draw].sum(axis=1)
    sst = sy2[draw].sum(axis=1) - yy**2 / nn
    rows, replicates = [], []
    for alias in ["ridge_flowacc_log", "rf", "xgb", "cb"]:
        sampled = {}
        for model in ["cbqw", alias]:
            residual = frame.OC - frame[model]
            sums = (
                pd.DataFrame(
                    dict(block_id=frame.block_id, se=residual**2, ae=np.abs(residual))
                )
                .groupby("block_id")
                .sum()
                .reindex(blocks)
            )
            se = sums.se.to_numpy()[draw].sum(axis=1)
            ae = sums.ae.to_numpy()[draw].sum(axis=1)
            sampled[model] = dict(
                r2=np.where(sst > 0, 1 - se / sst, np.nan),
                rmse=np.sqrt(se / nn),
                mae=ae / nn,
            )
        for metric in ["r2", "rmse", "mae"]:
            delta = sampled["cbqw"][metric] - sampled[alias][metric]
            valid = np.isfinite(delta)
            if valid.sum() < 0.95 * B:
                raise ValueError("Too many invalid block-bootstrap replicates.")
            lo, hi = np.quantile(delta[valid], [0.025, 0.975])
            estimate = (
                metrics(frame.OC, frame.cbqw)[metric]
                - metrics(frame.OC, frame[alias])[metric]
            )
            rows.append(
                dict(
                    comparison="cbqw minus " + alias,
                    metric=metric,
                    estimate=estimate,
                    lo_95=lo,
                    hi_95=hi,
                    n_blocks=len(blocks),
                    replicates=B,
                    valid_replicates=int(valid.sum()),
                    unit="Evaluation blocks; fixed fitted models",
                )
            )
            replicates.extend(
                dict(
                    comparison="cbqw minus " + alias,
                    metric=metric,
                    replicate=i,
                    delta=value,
                )
                for i, value in enumerate(delta)
                if np.isfinite(value)
            )
    save_csv(output / "paired_block_bootstrap.csv", pd.DataFrame(rows))
    save_csv(output / "paired_block_bootstrap_replicates.csv", pd.DataFrame(replicates))


# 8. National prediction on the prepared raster grid
class ExactBLAS:
    """Exhaustive float64 search with direct refinement of near ties."""

    def __init__(self, reference, batch=512, threads=8):
        self.reference = np.ascontiguousarray(reference, dtype=np.float64)
        if (
            self.reference.ndim != 2
            or not len(self.reference)
            or (not np.isfinite(self.reference).all())
        ):
            raise ValueError("Reference must be a finite, nonempty float64 matrix.")
        self.center = self.reference.mean(axis=0)
        self.r = np.ascontiguousarray(self.reference - self.center)
        self.norm = np.einsum("ij,ij->i", self.r, self.r)
        self.max_norm = float(self.norm.max())
        self.batch, self.threads = (int(batch), int(threads))
        if self.batch < 1 or self.threads < 1:
            raise ValueError("Positive batch/threads required.")

    def query(self, query):
        query = np.ascontiguousarray(query, dtype=np.float64)
        if (
            query.ndim != 2
            or query.shape[1] != self.reference.shape[1]
            or (not np.isfinite(query).all())
        ):
            raise ValueError("Query shape/values differ from reference.")
        distances = np.empty(len(query))
        indices = np.empty(len(query), dtype=np.int64)
        eps = np.finfo(np.float64).eps
        with threadpool_limits(limits=self.threads, user_api="blas"):
            for start in range(0, len(query), self.batch):
                raw = query[start : start + self.batch]
                q = raw - self.center
                qnorm = np.einsum("ij,ij->i", q, q)
                squared = q @ self.r.T
                squared *= -2.0
                squared += qnorm[:, None]
                squared += self.norm[None, :]
                best = squared.min(axis=1)
                envelope = (
                    eps
                    * (64.0 + 16.0 * query.shape[1])
                    * (
                        qnorm
                        + self.max_norm
                        + 2.0 * np.sqrt(qnorm * self.max_norm)
                        + 1.0
                    )
                )
                if not np.isfinite(squared).all() or not np.isfinite(envelope).all():
                    raise FloatingPointError(
                        "Distance overflow; no approximate fallback."
                    )
                for j in range(len(raw)):
                    candidate = np.flatnonzero(
                        squared[j] <= best[j] + 2.0 * envelope[j]
                    )
                    if not len(candidate):
                        raise RuntimeError("No nearest-neighbour candidate.")
                    best_exact, best_index = (np.inf, -1)
                    for block in range(0, len(candidate), 4096):
                        ix = candidate[block : block + 4096]
                        delta = self.reference[ix] - raw[j]
                        direct = np.einsum("ij,ij->i", delta, delta)
                        k = int(np.argmin(direct))
                        if direct[k] < best_exact:
                            best_exact, best_index = (float(direct[k]), int(ix[k]))
                    distances[start + j] = np.sqrt(best_exact)
                    indices[start + j] = best_index
        return (distances, indices)


class TreeSearch:
    def __init__(self, reference, workers=8):
        self.tree, self.workers = cKDTree(reference), int(workers)

    def query(self, query):
        return self.tree.query(query, k=1, eps=0.0, p=2, workers=self.workers)


def raster_input_paths():
    paths = {name: relative_path(path) for name, path in CONFIG["raster_paths"].items()}
    paths.update(
        AEZ=relative_path(CONFIG["aez_raster"]),
        domain=relative_path(CONFIG["domain_raster"]),
        mapping_valid=relative_path(CONFIG["mapping_valid_raster"]),
    )
    return paths


def validate_raster_grid():
    paths = raster_input_paths()
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    with rasterio.open(paths["domain"]) as source:
        grid = dict(
            width=source.width,
            height=source.height,
            crs=source.crs,
            transform=source.transform,
        )
        if source.count != 3 or source.descriptions != ("country", "water", "land"):
            raise ValueError(
                "The prepared domain raster requires country, water and land bands."
            )
    if grid["crs"] != rasterio.crs.CRS.from_string(CONFIG["crs"]):
        raise ValueError("The prepared rasters must use the configured projected CRS.")
    for name, path in paths.items():
        with rasterio.open(path) as source:
            if (
                source.width != grid["width"]
                or source.height != grid["height"]
                or source.transform != grid["transform"]
                or source.crs != grid["crs"]
            ):
                raise ValueError("Raster grid mismatch: " + name)
            if (
                source.scales != (1.0,) * source.count
                or source.offsets != (0.0,) * source.count
            ):
                raise ValueError("Non-default raster scale or offset: " + name)
            if name != "domain" and source.count != 1:
                raise ValueError("Expected a single-band raster: " + name)
    if grid["transform"].b != 0 or grid["transform"].d != 0:
        raise ValueError("Rotated grids are not supported by the notebook.")
    return grid, paths


def raster_windows(grid):
    size = CONFIG["mapping"]["tile_size"]
    for row in range(0, grid["height"], size):
        for column in range(0, grid["width"], size):
            yield Window(
                column,
                row,
                min(size, grid["width"] - column),
                min(size, grid["height"] - row),
            )


def read_raster_tile(handles, window):
    settings = CONFIG["mapping"]
    features = CONFIG["continuous"] + CONFIG["categorical"]
    valid = handles["mapping_valid"].read(1, window=window) == 1
    land = handles["domain"].read(3, window=window) == 1
    columns = {
        name: handles[name]
        .read(1, window=window, masked=True)
        .astype("float64")
        .filled(np.nan)
        for name in features + ["AEZ"]
    }
    complete = land.copy()
    for values in columns.values():
        complete &= np.isfinite(values) & (values != settings["nodata"])
    for name in ["s_rsg1_code", "s_rsg2_code"]:
        complete &= columns[name] != 0
    complete &= columns["AEZ"] != settings["water_aez_code"]
    complete &= columns["o_lulc_code"] != settings["water_cover_code"]
    fractions = ["s_silt", "s_sand", "s_clay"]
    total = sum(columns[name] for name in fractions)
    lo, hi = settings["texture_limits"]
    complete &= (total >= lo) & (total <= hi)
    for name in fractions:
        complete &= (columns[name] >= 0) & (columns[name] <= 100)
    for name in fractions:
        columns[name] = np.divide(
            columns[name] * 100,
            total,
            out=np.full(total.shape, np.nan),
            where=total > 0,
        )
    if not np.array_equal(valid, complete):
        raise ValueError(
            "Prepared mapping validity differs from the notebook rule at " + str(window)
        )
    frame = pd.DataFrame({name: columns[name][valid] for name in features})
    return frame, valid, columns["AEZ"][valid]


def national_mapping(final, calibration, aoa, output):
    grid, paths = validate_raster_grid()
    output.mkdir(parents=True, exist_ok=True)
    interval_names = [
        f"PI{level}_{suffix}"
        for level in LEVELS
        for suffix in [
            "lo_OC",
            "hi_OC",
            "width_OC",
            "empty",
            "national_fallback",
            "crossing_raw",
        ]
    ]
    names = (
        ["SOC_OC_pct"]
        + interval_names
        + ["predicted_SOC_quintile", "DI", "categorical_unseen", "AOA_fold", "AOA_loo"]
    )
    settings = CONFIG["mapping"]
    if settings["backend"] == "blas":
        engine = ExactBLAS(
            aoa["reference"], batch=settings["nn_batch"], threads=CONFIG["threads"]
        )
    elif settings["backend"] == "ckdtree":
        engine = TreeSearch(aoa["reference"], workers=CONFIG["threads"])
    else:
        raise ValueError("Use the notebook's exact blas or ckdtree backend.")
    thresholds = np.array(
        [aoa["thresholds"][method]["threshold"] for method in ["fold", "loo"]]
    )
    boundary_tree = None
    started = time.monotonic()
    with contextlib.ExitStack() as stack:
        handles = {
            name: stack.enter_context(rasterio.open(path))
            for name, path in paths.items()
        }
        destinations = {}
        for name in names:
            dtype = "float64" if name in ["DI", "categorical_unseen"] else "float32"
            path = output / (name + ".tif")
            destination = stack.enter_context(
                rasterio.open(
                    path,
                    "w",
                    driver="GTiff",
                    width=grid["width"],
                    height=grid["height"],
                    count=1,
                    dtype=dtype,
                    crs=grid["crs"],
                    transform=grid["transform"],
                    nodata=settings["nodata"],
                    tiled=True,
                    blockxsize=256,
                    blockysize=256,
                    compress="deflate",
                    predictor=3,
                    BIGTIFF="IF_SAFER",
                    NUM_THREADS="1",
                )
            )
            destination.set_band_description(1, name)
            destination.update_tags(
                calibration=calibration["policy"]["method"],
                AOA_MAIN=CONFIG["aoa"]["main"],
                units="percent OC"
                if name.startswith(("SOC", "PI")) and name.endswith(("pct", "OC"))
                else "see layer name",
            )
            destinations[name] = destination
        windows = list(raster_windows(grid))
        for number, window in enumerate(windows, 1):
            frame, valid, aez = read_raster_tile(handles, window)
            values = {}
            if len(frame):
                X = transform_frame(frame, final["preprocessor"], True)
                prediction = inverse(
                    final["model"].predict(X, thread_count=CONFIG["threads"])
                )
                values["SOC_OC_pct"] = prediction
                raw = {
                    tau: model.predict(X, thread_count=CONFIG["threads"])
                    for tau, model in calibration["models"].items()
                }
                values.update(calibrate_pixels(calibration, aez, prediction, raw))
                weighted, unseen, _ = distance_transform(frame, aoa["preprocessor"])
                distances = np.empty(len(frame))
                for start in range(0, len(frame), settings["nn_batch"]):
                    stop = start + settings["nn_batch"]
                    query = weighted[start:stop]
                    d, nearest = engine.query(query)
                    if settings["backend"] == "blas":
                        near = np.any(
                            np.isclose(
                                (d / aoa["distance_scale"])[:, None],
                                thresholds[None, :],
                                rtol=5e-12,
                                atol=5e-12,
                            ),
                            axis=1,
                        )
                        if near.any():
                            if boundary_tree is None:
                                boundary_tree = TreeSearch(
                                    aoa["reference"], CONFIG["threads"]
                                )
                            d[near], nearest[near] = boundary_tree.query(query[near])
                    distances[start:stop] = d
                values["DI"] = distances / aoa["distance_scale"]
                values["categorical_unseen"] = unseen
                for method in ["fold", "loo"]:
                    values["AOA_" + method] = (
                        values["DI"] <= aoa["thresholds"][method]["threshold"]
                    ) & ~unseen
            for name, destination in destinations.items():
                tile = np.full(
                    valid.shape, settings["nodata"], dtype=destination.dtypes[0]
                )
                if len(frame):
                    tile[valid] = values[name]
                if not np.isfinite(tile).all():
                    raise ValueError("Use explicit NoData in raster output tiles.")
                destination.write(tile, 1, window=window)
            if number == 1 or number % 10 == 0 or number == len(windows):
                print(
                    f"Mapping {number}/{len(windows)} tiles; {(time.monotonic() - started) / 60:.1f} min",
                    flush=True,
                )
    save_json(
        output / "mapping_layers.json",
        dict(
            layers={name: name + ".tif" for name in names},
            AOA_MAIN=CONFIG["aoa"]["main"],
            calibration=calibration["policy"]["method"],
            signed=True,
            nested95=True,
            point_model="cbqw",
            target="percent OC, 0-20 cm",
        ),
    )


# 9. Raw and working-only recalibrated product benchmarks
def product_values(data):
    raw = pd.read_csv(relative_path(CONFIG["product_points"]))
    columns = CONFIG["product_columns"]
    needed = [columns["id"], columns["SoilGrids"], columns["iSDA"]]
    missing = sorted(set(needed) - set(raw.columns))
    if missing:
        raise ValueError("Missing product CSV columns: " + ", ".join(missing))
    selected = (
        raw[needed]
        .rename(
            columns={
                columns["id"]: "_source_row",
                columns["SoilGrids"]: "SoilGrids",
                columns["iSDA"]: "iSDA",
            }
        )
        .copy()
    )
    if selected._source_row.isna().any():
        raise ValueError("Missing product sample IDs.")
    for product in ["SoilGrids", "iSDA"]:
        selected[product] = pd.to_numeric(selected[product], errors="coerce").replace(
            [CONFIG["mapping"]["nodata"], np.inf, -np.inf], np.nan
        )
    if selected._source_row.duplicated().any():
        grouped = selected.groupby("_source_row", dropna=False)[
            ["SoilGrids", "iSDA"]
        ].nunique(dropna=False)
        if grouped.gt(1).any().any():
            raise ValueError("Conflicting product values for the same sample ID.")
        selected = selected.drop_duplicates("_source_row")
    result = data.merge(selected, on="_source_row", how="left", validate="one_to_one")
    for product in ["SoilGrids", "iSDA"]:
        values = result[product].dropna()
        if ((values < 0) | (values > 100)).any():
            raise ValueError(
                product
                + " must already be percent OC at 0-20 cm; no conversion is applied."
            )
        training = result.loc[~result.holdout & result[product].notna(), product]
        if len(training) < 3 or np.ptp(training.to_numpy(float)) <= 1e-12:
            raise ValueError(
                "Provide working-set product values as well as holdout values for "
                + product
                + ". Recalibration cannot be fitted from a holdout-only product CSV."
            )
    return result


def product_bootstrap(frame, output):
    names = ["r2", "rmse", "mae", "bias", "ccc", "spearman"]
    products = ["SoilGrids", "iSDA", "SoilGrids_recalibrated", "iSDA_recalibrated"]
    settings = CONFIG["bootstrap"]
    blocks = np.sort(frame.block_id.unique())
    if len(blocks) < 2:
        raise ValueError(
            "At least two evaluation blocks are required for the product bootstrap."
        )
    groups = [np.flatnonzero(frame.block_id.eq(block)) for block in blocks]
    rng = np.random.default_rng(settings["seed"])
    draw = rng.integers(0, len(blocks), size=(settings["replicates"], len(blocks)))
    values = np.full((settings["replicates"], len(products), len(names)), np.nan)
    for start in range(0, settings["replicates"], settings["chunk"]):
        for j, row in enumerate(draw[start : start + settings["chunk"]]):
            index = np.concatenate([groups[k] for k in row])
            soc = frame.OC.to_numpy()[index]
            ours = metrics(soc, frame.ours.to_numpy()[index])
            for p, product in enumerate(products):
                other = metrics(soc, frame[product].to_numpy()[index])
                for k, name in enumerate(names):
                    if ours[name] is not None and other[name] is not None:
                        values[start + j, p, k] = ours[name] - other[name]
        print(
            "Product bootstrap:",
            min(start + settings["chunk"], settings["replicates"]),
            "/",
            settings["replicates"],
            flush=True,
        )
    baseline = metrics(frame.OC, frame.ours)
    rows = []
    for p, product in enumerate(products):
        other = metrics(frame.OC, frame[product])
        for k, name in enumerate(names):
            distribution = values[:, p, k]
            distribution = distribution[np.isfinite(distribution)]
            estimate = (
                baseline[name] - other[name]
                if baseline[name] is not None and other[name] is not None
                else None
            )
            rows.append(
                dict(
                    comparison="ours minus " + product,
                    metric=name,
                    estimate=estimate,
                    lo_95=float(np.percentile(distribution, 2.5))
                    if len(distribution)
                    else None,
                    hi_95=float(np.percentile(distribution, 97.5))
                    if len(distribution)
                    else None,
                    n=len(frame),
                    n_blocks=len(blocks),
                    replicates=settings["replicates"],
                    valid_replicates=len(distribution),
                    unit="Whole evaluation blocks; fixed fitted models and working recalibration coefficients",
                )
            )
    save_csv(output / "paired_block_bootstrap.csv", pd.DataFrame(rows))
    np.savez_compressed(
        output / "paired_bootstrap_deltas.npz",
        deltas=values,
        products=np.asarray(products),
        metrics=np.asarray(names),
    )


def benchmark_products(data, final, output):
    data = product_values(data)
    training = data.loc[~data.holdout].copy()
    evaluate = data.loc[data.holdout].copy()
    point = final["predictions"][["_source_row", "cbqw"]].rename(
        columns={"cbqw": "ours"}
    )
    evaluate = evaluate.merge(
        point, on="_source_row", how="left", validate="one_to_one"
    )
    coefficients, ranges = [], []
    for product in ["SoilGrids", "iSDA"]:
        fit = training.loc[training[product].notna()]
        x, soc = fit[product].to_numpy(float), fit.OC.to_numpy(float)
        slope = float(np.mean((x - x.mean()) * (soc - soc.mean())) / x.var())
        intercept = float(soc.mean() - slope * x.mean())
        evaluate[product + "_recalibrated"] = intercept + slope * evaluate[product]
        coefficients.append(
            dict(
                product=product,
                intercept=intercept,
                slope=slope,
                n_working_fit=len(fit),
                holdout_used=False,
                prediction_clipping=False,
            )
        )
        v = data[product].dropna()
        ranges.append(
            dict(
                product=product,
                n_valid=len(v),
                n_missing=int(data[product].isna().sum()),
                minimum=float(v.min()),
                maximum=float(v.max()),
                units="percent OC",
                depth_cm="0-20",
                conversion="none",
            )
        )
    models = [
        "ours",
        "SoilGrids",
        "iSDA",
        "SoilGrids_recalibrated",
        "iSDA_recalibrated",
    ]
    common = evaluate.loc[evaluate[models].notna().all(axis=1)].reset_index(drop=True)
    if len(common) < 3:
        raise ValueError("Too few matched holdout product values.")
    records = []
    groups = [("national", common)] + [
        (zone, common.loc[common.AEZ_name.eq(zone)])
        for zone in sorted(data.AEZ_name.unique())
    ]
    for zone, frame in groups:
        for model in models:
            records.append(
                dict(
                    zone=zone,
                    model=model,
                    small_n_lt30=len(frame) < 30,
                    cohort="Existing holdout; post-hoc benchmarking; no retuning",
                    **metrics(frame.OC, frame[model]),
                )
            )
    deciles, edges = pd.qcut(
        common.OC, 10, labels=False, retbins=True, duplicates="drop"
    )
    common["observed_SOC_decile"] = deciles + 1
    decile_rows = []
    for decile, frame in common.groupby("observed_SOC_decile"):
        for model in models:
            decile_rows.append(
                dict(
                    decile=int(decile),
                    model=model,
                    OC_min=float(frame.OC.min()),
                    OC_max=float(frame.OC.max()),
                    **metrics(frame.OC, frame[model]),
                )
            )
    save_csv(output / "product_sanity_checks.csv", pd.DataFrame(ranges))
    save_csv(output / "working_linear_recalibration.csv", pd.DataFrame(coefficients))
    save_csv(output / "point_metrics.csv", pd.DataFrame(records))
    save_csv(output / "bias_by_observed_SOC_decile.csv", pd.DataFrame(decile_rows))
    save_csv(
        output / "matched_point_predictions.csv",
        common[
            ["_source_row", "block_id", "AEZ", "AEZ_name", "OC"]
            + models
            + ["observed_SOC_decile"]
        ],
    )
    save_json(
        output / "benchmark_cohort.json",
        dict(
            n_holdout=len(evaluate),
            n_matched=len(common),
            missing_by_product={
                name: int(evaluate[name].isna().sum()) for name in ["SoilGrids", "iSDA"]
            },
            observed_decile_edges=edges,
            recalibration="Unweighted working-only OLS with intercept; no clipping",
        ),
    )
    product_bootstrap(common, output)
    print(
        pd.DataFrame(records)
        .loc[lambda frame: frame.zone.eq("national")]
        .round(6)
        .to_string(index=False),
        flush=True,
    )


def main():
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    data, composition = load_analysis_table()
    validate_raster_grid()
    product_values(data)
    output = relative_path(CONFIG["output_dir"])
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            "Use an empty output_dir. This script does not resume or overwrite a previous run."
        )
    output.mkdir(parents=True, exist_ok=True)
    save_json(output / "config.json", CONFIG)
    save_json(
        output / "package_versions.json",
        {
            name: importlib.metadata.version(name)
            for name in [
                "numpy",
                "pandas",
                "scipy",
                "scikit-learn",
                "catboost",
                "xgboost",
                "optuna",
                "rasterio",
                "threadpoolctl",
            ]
        },
    )
    save_csv(output / "partitions" / "holdout_AEZ_composition.csv", composition)
    work, holdout, contexts = spatial_design(data, output / "partitions")
    cv = nested_spatial_cv(work, contexts, output / "spatial_cv")
    random = random_cv(work, output / "random_cv")
    comparison = summarize_cv(
        {"cbqw": cv["cbqw"], "cbqw_random": random}, output / "random_cv"
    )
    q = comparison.set_index("alias")
    save_json(
        output / "random_cv" / "random_minus_spatial.json",
        dict(
            mean_R2_gap=q.loc["cbqw_random", "r2_fold_mean"]
            - q.loc["cbqw", "r2_fold_mean"],
            pooled_R2_gap=q.loc["cbqw_random", "r2_pooled"]
            - q.loc["cbqw", "r2_pooled"],
        ),
    )
    final = final_refit(work, holdout, cv, output / "final")
    calibration = quantiles_and_calibration(
        work, holdout, contexts, cv, final, output / "calibration"
    )
    aoa = applicability(work, holdout, final, calibration, output / "applicability")
    model_bootstrap(final["predictions"], output / "final")
    national_mapping(final, calibration, aoa, output / "maps")
    benchmark_products(data, final, output / "benchmark")
    print(
        "SOC DSM pipeline complete. Main point model: CatBoost-QW, alpha=0.5.",
        flush=True,
    )


if __name__ == "__main__":
    main()
