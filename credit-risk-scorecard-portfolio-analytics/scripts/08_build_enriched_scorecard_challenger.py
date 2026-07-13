from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT = Path(__file__).resolve().parents[1]
if "FINANCIAL_RISK_DATA_CORE" not in os.environ:
    raise RuntimeError("Set FINANCIAL_RISK_DATA_CORE to run the full Project 3 enriched rebuild.")
DATA_CORE = Path(os.environ["FINANCIAL_RISK_DATA_CORE"])
SOURCE_ENRICHED = DATA_CORE / "data" / "silver" / "silver_lendingclub_enriched_accepted.csv.gz"

PROCESSED = PROJECT / "data" / "processed"
REPORTS = PROJECT / "reports"
VISUALS = PROJECT / "visuals"
DOCS = PROJECT / "docs"

COLORS = {
    "ink": "#14213d",
    "blue": "#1d5f8a",
    "teal": "#14746f",
    "red": "#a63d40",
    "gold": "#b88732",
    "gray": "#697586",
    "line": "#d9e2ec",
    "bg": "#f7f9fb",
}

BASE_SCORE = 600
BASE_GOOD_ODDS = 20
PDO = 50

FEATURE_DESCRIPTIONS = {
    "fico_band_exp": "External creditworthiness band.",
    "dti_band_exp": "Debt burden relative to income.",
    "income_band_exp": "Repayment capacity proxy.",
    "loan_amount_band_exp": "Exposure size and affordability proxy.",
    "revol_util_band_exp": "Revolving credit utilization.",
    "revol_bal_band_exp": "Revolving balance burden.",
    "open_acc_band_exp": "Number of open credit accounts.",
    "total_acc_band_exp": "Depth of credit-file history.",
    "mort_acc_band_exp": "Mortgage account experience.",
    "pub_rec_band_exp": "Public record severity.",
    "bankruptcy_band_exp": "Bankruptcy history.",
    "term_band_exp": "Loan term/product tenor.",
    "emp_length_exp": "Employment stability proxy.",
    "purpose_exp": "Loan purpose risk profile.",
    "home_ownership_exp": "Housing stability proxy.",
    "verification_status_exp": "Income/identity verification status.",
    "application_type_exp": "Individual or joint application.",
}

FORMULA_FEATURES = list(FEATURE_DESCRIPTIONS)
POLICY_SENSITIVE_FEATURES = {"term_band_exp"}
CLEAN_SCORECARD_EXCLUSIONS = {
    "revol_util_band_exp": "Dropped from final clean scorecard because benchmark WOE-logistic coefficient showed sign reversal under WOE = ln(%Good / %Bad).",
    "mort_acc_band_exp": "Dropped from final clean scorecard because post-coarse WOE stability movement exceeded 0.50 in the test window.",
    "bankruptcy_band_exp": "Dropped from final clean scorecard because coefficient sign reversal appeared after removing heavier review variables.",
}
CLEAN_SCORECARD_EXCLUSION_TRIGGERS = {
    "revol_util_band_exp": "Benchmark sign reversal",
    "mort_acc_band_exp": "Post-coarse WOE stability breach > 0.50",
    "bankruptcy_band_exp": "Clean refit sign reversal",
}
TOP_CSI_FEATURES = [
    "term_band_exp",
    "fico_band_exp",
    "dti_band_exp",
    "verification_status_exp",
    "loan_amount_band_exp",
]
ORDINAL_FEATURES = {
    "fico_band_exp",
    "dti_band_exp",
    "income_band_exp",
    "loan_amount_band_exp",
    "revol_util_band_exp",
    "revol_bal_band_exp",
    "open_acc_band_exp",
    "total_acc_band_exp",
    "mort_acc_band_exp",
    "pub_rec_band_exp",
    "bankruptcy_band_exp",
    "term_band_exp",
}


def ensure_dirs() -> None:
    for folder in [PROCESSED, REPORTS, VISUALS, DOCS]:
        folder.mkdir(parents=True, exist_ok=True)


def ks_stat(y_true: pd.Series, scores: np.ndarray | pd.Series) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    return float(np.max(tpr - fpr))


def psi(expected: pd.Series, actual: pd.Series) -> float:
    categories = sorted(set(expected.index).union(set(actual.index)))
    expected = expected.reindex(categories).fillna(0.0001)
    actual = actual.reindex(categories).fillna(0.0001)
    return float(((actual - expected) * np.log(actual / expected)).sum())


def as_category(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("Missing").str.strip()


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["fico_band_exp"] = pd.cut(
        out["fico_score"],
        [-np.inf, 599, 639, 679, 719, 759, 799, np.inf],
        labels=["<600", "600-639", "640-679", "680-719", "720-759", "760-799", "800+"],
    )
    out["dti_band_exp"] = pd.cut(
        out["dti"],
        [-np.inf, 10, 20, 30, 40, 60, np.inf],
        labels=["<=10", "10-20", "20-30", "30-40", "40-60", "60+"],
    )
    out["income_band_exp"] = pd.cut(
        out["annual_inc"],
        [-np.inf, 30_000, 50_000, 75_000, 100_000, 150_000, np.inf],
        labels=["<30k", "30-50k", "50-75k", "75-100k", "100-150k", "150k+"],
    )
    out["loan_amount_band_exp"] = pd.cut(
        out["loan_amnt"],
        [-np.inf, 5_000, 10_000, 15_000, 25_000, 35_000, np.inf],
        labels=["<=5k", "5-10k", "10-15k", "15-25k", "25-35k", "35k+"],
    )
    out["revol_util_band_exp"] = pd.cut(
        out["revol_util"],
        [-np.inf, 20, 40, 60, 80, 100, np.inf],
        labels=["<=20", "20-40", "40-60", "60-80", "80-100", "100+"],
    )
    out["revol_bal_band_exp"] = pd.cut(
        out["revol_bal"],
        [-np.inf, 2_500, 7_500, 15_000, 30_000, 60_000, np.inf],
        labels=["<=2.5k", "2.5-7.5k", "7.5-15k", "15-30k", "30-60k", "60k+"],
    )
    out["open_acc_band_exp"] = pd.cut(
        out["open_acc"],
        [-np.inf, 3, 6, 10, 15, 25, np.inf],
        labels=["<=3", "4-6", "7-10", "11-15", "16-25", "25+"],
    )
    out["total_acc_band_exp"] = pd.cut(
        out["total_acc"],
        [-np.inf, 10, 20, 30, 50, 75, np.inf],
        labels=["<=10", "11-20", "21-30", "31-50", "51-75", "75+"],
    )
    out["mort_acc_band_exp"] = pd.cut(
        out["mort_acc"],
        [-np.inf, 0, 1, 3, 6, np.inf],
        labels=["0", "1", "2-3", "4-6", "6+"],
    )
    out["pub_rec_band_exp"] = pd.cut(
        out["pub_rec"],
        [-np.inf, 0, 1, 2, np.inf],
        labels=["0", "1", "2", "3+"],
    )
    out["bankruptcy_band_exp"] = pd.cut(
        out["pub_rec_bankruptcies"],
        [-np.inf, 0, 1, np.inf],
        labels=["0", "1", "2+"],
    )
    out["term_band_exp"] = out["term_months"].astype("Int64").astype("string")
    for col in ["emp_length", "purpose", "home_ownership", "verification_status", "application_type"]:
        out[f"{col}_exp"] = out[col].astype("string")
    for feature in FORMULA_FEATURES:
        out[feature] = as_category(out[feature])
    return out


def split_population(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "train_pre_2016": frame[frame["application_month"].dt.year <= 2015].copy(),
        "validation_2016": frame[frame["application_month"].dt.year == 2016].copy(),
        "test_2017": frame[frame["application_month"].dt.year == 2017].copy(),
    }


def build_woe_tables(train: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    rows = []
    maps: dict[str, dict[str, float]] = {}
    for feature in FORMULA_FEATURES:
        grouped = (
            train.groupby(feature, dropna=False)
            .agg(good_accounts=("good_flag", "sum"), bad_accounts=("bad_flag", "sum"), accounts=("id", "count"))
            .reset_index()
        )
        smooth = 0.5
        total_good = float(grouped["good_accounts"].sum())
        total_bad = float(grouped["bad_accounts"].sum())
        grouped["good_pct"] = (grouped["good_accounts"] + smooth) / (total_good + smooth * len(grouped))
        grouped["bad_pct"] = (grouped["bad_accounts"] + smooth) / (total_bad + smooth * len(grouped))
        grouped["woe"] = np.log(grouped["good_pct"] / grouped["bad_pct"])
        grouped["iv_bin"] = (grouped["good_pct"] - grouped["bad_pct"]) * grouped["woe"]
        variable_iv = float(grouped["iv_bin"].sum())
        maps[feature] = dict(zip(grouped[feature].astype(str), grouped["woe"]))
        for row in grouped.itertuples(index=False):
            rows.append(
                {
                    "feature": feature,
                    "business_meaning": FEATURE_DESCRIPTIONS[feature],
                    "bin": str(getattr(row, feature)),
                    "accounts": int(row.accounts),
                    "good_accounts": int(row.good_accounts),
                    "bad_accounts": int(row.bad_accounts),
                    "bad_rate": float(row.bad_accounts / row.accounts) if row.accounts else np.nan,
                    "woe": float(row.woe),
                    "iv_bin": float(row.iv_bin),
                    "iv_variable": variable_iv,
                }
            )
    return pd.DataFrame(rows), maps


def score_formula(
    splits: dict[str, pd.DataFrame],
    feature_iv: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, dict[int, float]]:
    iv_summary = (
        feature_iv.groupby(["feature", "business_meaning"], as_index=False)["iv_variable"]
        .max()
        .sort_values("iv_variable", ascending=False)
    )
    selected = iv_summary[iv_summary["iv_variable"] > 0.005].copy()
    selected["iv_weight"] = selected["iv_variable"] / selected["iv_variable"].sum()

    for name, frame in splits.items():
        score = np.zeros(len(frame))
        for row in selected.itertuples(index=False):
            score += (
                float(row.iv_weight)
                * frame[row.feature].astype(str).map(woe_maps[row.feature]).fillna(0.0).astype(float).values
            )
        splits[name]["expanded_formula_risk_score"] = -score

    train = splits["train_pre_2016"]
    train["expanded_formula_decile"], bins = pd.qcut(
        train["expanded_formula_risk_score"],
        10,
        labels=False,
        retbins=True,
        duplicates="drop",
    )
    bins[0] = -np.inf
    bins[-1] = np.inf
    labels = list(range(1, len(bins)))
    for frame in splits.values():
        frame["expanded_formula_decile"] = pd.cut(
            frame["expanded_formula_risk_score"],
            bins=bins,
            labels=labels,
            include_lowest=True,
        ).astype(int)
    pd_by_decile = train.groupby("expanded_formula_decile")["bad_flag"].mean().to_dict()
    for frame in splits.values():
        frame["expanded_formula_pd"] = frame["expanded_formula_decile"].map(pd_by_decile).clip(0.0001, 0.9999)

    return splits, selected, pd_by_decile


def metric_row(sample: str, model_name: str, frame: pd.DataFrame, score_col: str) -> dict[str, float | int | str]:
    scores = frame[score_col]
    y = frame["bad_flag"]
    auc = roc_auc_score(y, scores)
    return {
        "sample": sample,
        "model_name": model_name,
        "rows": int(len(frame)),
        "observed_default_rate": float(y.mean()),
        "average_pd_or_score": float(scores.mean()),
        "calibration_gap": float(y.mean() - scores.mean()),
        "auc": float(auc),
        "gini": float(2 * auc - 1),
        "ks": ks_stat(y, scores),
        "brier_score": float(brier_score_loss(y, scores)),
    }


def fit_logistic_challenger(splits: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore", min_frequency=100)),
        ]
    )
    preprocessor = ColumnTransformer([("categorical", categorical_pipeline, FORMULA_FEATURES)])
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("logistic", LogisticRegression(max_iter=500, C=0.8)),
        ]
    )
    model.fit(splits["train_pre_2016"][FORMULA_FEATURES], splits["train_pre_2016"]["bad_flag"])
    for frame in splits.values():
        frame["logistic_challenger_pd"] = model.predict_proba(frame[FORMULA_FEATURES])[:, 1]

    metrics = []
    for sample, frame in splits.items():
        metrics.append(metric_row(sample, "Expanded WOE formula scorecard", frame, "expanded_formula_pd"))
        metrics.append(metric_row(sample, "Logistic regression challenger", frame, "logistic_challenger_pd"))
    return pd.DataFrame(metrics), splits


def build_decile_report(train: pd.DataFrame) -> pd.DataFrame:
    out = (
        train.groupby("expanded_formula_decile")
        .agg(
            accounts=("id", "count"),
            observed_default_rate=("bad_flag", "mean"),
            avg_formula_pd=("expanded_formula_pd", "mean"),
            avg_formula_score=("expanded_formula_risk_score", "mean"),
        )
        .reset_index()
        .sort_values("expanded_formula_decile")
    )
    out["good_accounts"] = (out["accounts"] * (1 - out["observed_default_rate"])).round().astype(int)
    out["bad_accounts"] = (out["accounts"] * out["observed_default_rate"]).round().astype(int)
    return out


def apply_formula_variant(
    splits: dict[str, pd.DataFrame],
    selected: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
    prefix: str,
) -> dict[str, pd.DataFrame]:
    variant = selected.copy()
    variant["iv_weight"] = variant["iv_variable"] / variant["iv_variable"].sum()
    score_col = f"{prefix}_risk_score"
    decile_col = f"{prefix}_decile"
    pd_col = f"{prefix}_pd"
    for frame in splits.values():
        score = np.zeros(len(frame))
        for row in variant.itertuples(index=False):
            score += (
                float(row.iv_weight)
                * frame[row.feature].astype(str).map(woe_maps[row.feature]).fillna(0.0).astype(float).values
            )
        frame[score_col] = -score

    train = splits["train_pre_2016"]
    train[decile_col], bins = pd.qcut(
        train[score_col],
        10,
        labels=False,
        retbins=True,
        duplicates="drop",
    )
    bins[0] = -np.inf
    bins[-1] = np.inf
    labels = list(range(1, len(bins)))
    for frame in splits.values():
        frame[decile_col] = pd.cut(frame[score_col], bins=bins, labels=labels, include_lowest=True).astype(int)
    pd_map = train.groupby(decile_col)["bad_flag"].mean().to_dict()
    for frame in splits.values():
        frame[pd_col] = frame[decile_col].map(pd_map).clip(0.0001, 0.9999)
    return splits


def fit_logistic_for_features(
    splits: dict[str, pd.DataFrame],
    features: list[str],
    output_col: str,
) -> dict[str, pd.DataFrame]:
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore", min_frequency=100)),
        ]
    )
    preprocessor = ColumnTransformer([("categorical", categorical_pipeline, features)])
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("logistic", LogisticRegression(max_iter=500, C=0.8)),
        ]
    )
    model.fit(splits["train_pre_2016"][features], splits["train_pre_2016"]["bad_flag"])
    for frame in splits.values():
        frame[output_col] = model.predict_proba(frame[features])[:, 1]
    return splits


def term_sensitivity_report(
    splits: dict[str, pd.DataFrame],
    selected: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    selected_no_term = selected[~selected["feature"].eq("term_band_exp")].copy()
    splits = apply_formula_variant(splits, selected_no_term, woe_maps, "formula_without_term")
    splits = fit_logistic_for_features(
        splits,
        [feature for feature in FORMULA_FEATURES if feature != "term_band_exp"],
        "logistic_without_term_pd",
    )
    test = splits["test_2017"]
    rows = [
        metric_row("test_2017", "Expanded WOE with term", test, "expanded_formula_pd"),
        metric_row("test_2017", "Expanded WOE without term", test, "formula_without_term_pd"),
        metric_row("test_2017", "Logistic with term", test, "logistic_challenger_pd"),
        metric_row("test_2017", "Logistic without term", test, "logistic_without_term_pd"),
    ]
    out = pd.DataFrame(rows)
    out["feature_scope"] = [
        f"{len(selected)} selected WOE features",
        f"{len(selected_no_term)} selected WOE features",
        f"{len(FORMULA_FEATURES)} candidate features",
        f"{len(FORMULA_FEATURES) - 1} candidate features",
    ]
    out["comment"] = [
        "Current expanded formula scorecard.",
        "Sensitivity check: removes product-tenor variable.",
        "Current logistic challenger.",
        "Sensitivity check: removes product-tenor variable.",
    ]
    return out, splits


def enriched_split_drift_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    pivot = metrics.pivot(index="sample", columns="model_name", values="average_pd_or_score")
    rows = []
    for sample in ["train_pre_2016", "validation_2016", "test_2017"]:
        sample_rows = metrics[(metrics["sample"] == sample) & (metrics["model_name"] == "Expanded WOE formula scorecard")]
        if sample_rows.empty:
            continue
        row = sample_rows.iloc[0]
        rows.append(
            {
                "sample": sample,
                "rows": int(row["rows"]),
                "observed_default_rate": float(row["observed_default_rate"]),
                "avg_formula_pd": float(pivot.loc[sample, "Expanded WOE formula scorecard"]),
                "avg_logistic_pd": float(pivot.loc[sample, "Logistic regression challenger"]),
                "comment": {
                    "train_pre_2016": "Model development window.",
                    "validation_2016": "Out-of-time validation; higher observed default creates under-prediction pressure.",
                    "test_2017": "Out-of-time test; mild under-prediction but ranking generalizes.",
                }[sample],
            }
        )
    return pd.DataFrame(rows)


def probability_calibration_by_decile(
    splits: dict[str, pd.DataFrame],
    pd_col: str,
    decile_col: str,
    average_col: str,
) -> pd.DataFrame:
    rows = []
    train = splits["train_pre_2016"].copy()
    train[decile_col], bins = pd.qcut(
        train[pd_col],
        10,
        labels=False,
        retbins=True,
        duplicates="drop",
    )
    bins[0] = -np.inf
    bins[-1] = np.inf
    labels = list(range(1, len(bins)))
    for sample, frame in splits.items():
        temp = frame.copy()
        temp[decile_col] = pd.cut(
            temp[pd_col],
            bins=bins,
            labels=labels,
            include_lowest=True,
        ).astype(int)
        grouped = (
            temp.groupby(decile_col)
            .agg(
                accounts=("id", "count"),
                **{average_col: (pd_col, "mean")},
                observed_default_rate=("bad_flag", "mean"),
            )
            .reset_index()
        )
        grouped["sample"] = sample
        grouped["calibration_gap"] = grouped["observed_default_rate"] - grouped[average_col]
        rows.append(grouped)
    out = pd.concat(rows, ignore_index=True)
    return out[["sample", decile_col, "accounts", average_col, "observed_default_rate", "calibration_gap"]]


def logistic_calibration_by_decile(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return probability_calibration_by_decile(
        splits,
        "logistic_challenger_pd",
        "logistic_calibration_decile",
        "avg_logistic_pd",
    )


def woe_logistic_calibration_by_decile(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return probability_calibration_by_decile(
        splits,
        "woe_logistic_scorecard_pd",
        "woe_logistic_decile",
        "avg_woe_logistic_pd",
    )


def enriched_feature_csi(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    train = splits["train_pre_2016"]
    rows = []
    for feature in TOP_CSI_FEATURES:
        expected = train[feature].value_counts(normalize=True)
        for sample in ["validation_2016", "test_2017"]:
            actual = splits[sample][feature].value_counts(normalize=True)
            csi = psi(expected, actual)
            rows.append(
                {
                    "feature": feature,
                    "sample": sample,
                    "csi_vs_train": csi,
                    "interpretation": "Low" if csi < 0.10 else "Watch" if csi < 0.25 else "High",
                }
            )
    return pd.DataFrame(rows)


def score_distribution_shift(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    train_dist = splits["train_pre_2016"]["expanded_formula_decile"].value_counts(normalize=True)
    rows = []
    for sample in ["train_pre_2016", "validation_2016", "test_2017"]:
        actual = splits[sample]["expanded_formula_decile"].value_counts(normalize=True)
        for decile in sorted(set(train_dist.index).union(set(actual.index))):
            rows.append(
                {
                    "sample": sample,
                    "expanded_formula_decile": int(decile),
                    "actual_share": float(actual.get(decile, 0.0)),
                    "train_share": float(train_dist.get(decile, 0.0)),
                    "share_gap": float(actual.get(decile, 0.0) - train_dist.get(decile, 0.0)),
                }
            )
    summary = []
    for sample in ["validation_2016", "test_2017"]:
        actual = splits[sample]["expanded_formula_decile"].value_counts(normalize=True)
        summary.append(
            {
                "sample": sample,
                "score_distribution_psi_vs_train": psi(train_dist, actual),
                "interpretation": "Low" if psi(train_dist, actual) < 0.10 else "Watch" if psi(train_dist, actual) < 0.25 else "High",
            }
        )
    pd.DataFrame(summary).to_csv(REPORTS / "37_enriched_score_distribution_psi.csv", index=False)
    return pd.DataFrame(rows)


def binning_quality_check(feature_iv: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature, group in feature_iv.groupby("feature", sort=False):
        ordered = group.reset_index(drop=True).copy()
        diffs = ordered["bad_rate"].diff().dropna()
        if feature in ORDINAL_FEATURES and not diffs.empty:
            monotonic = bool((diffs >= -1e-9).all() or (diffs <= 1e-9).all())
            monotonic_flag = "Monotonic" if monotonic else "Non-monotonic"
        else:
            monotonic_flag = "Not assessed - nominal"
        min_bin_accounts = int(ordered["accounts"].min())
        min_bin_share = float(ordered["accounts"].min() / ordered["accounts"].sum())
        sparse_flag = min_bin_share < 0.01
        if feature in POLICY_SENSITIVE_FEATURES:
            action = "Keep with policy-sensitive caveat; run without-term sensitivity."
        elif sparse_flag:
            action = "Review sparse bin before production scorecard."
        elif monotonic_flag == "Non-monotonic":
            action = "Review coarse binning and business pattern before production."
        else:
            action = "Accept for portfolio benchmark; revalidate for production."
        rows.append(
            {
                "feature": feature,
                "bins": int(ordered["bin"].nunique()),
                "min_bin_accounts": min_bin_accounts,
                "min_bin_share": min_bin_share,
                "min_bin_bad_rate": float(ordered["bad_rate"].min()),
                "max_bin_bad_rate": float(ordered["bad_rate"].max()),
                "missing_bin_present": bool(ordered["bin"].astype(str).str.lower().eq("missing").any()),
                "monotonic_flag": monotonic_flag,
                "business_pattern": FEATURE_DESCRIPTIONS[feature],
                "action": action,
                "diagnostic_stage": "Pre-coarse diagnostic",
                "final_used_in_scorecard": "No",
                "final_binning_reference": "Use reports/38_enriched_feature_iv_after_coarse_binning.csv and reports/39_woe_stability_after_coarse_binning.csv for final post-coarse review.",
            }
        )
    return pd.DataFrame(rows)


def feature_selection_rationale(iv_summary: pd.DataFrame) -> pd.DataFrame:
    out = iv_summary.copy()
    out["selection_rule"] = "Keep if IV > 0.005 for broad benchmark; production would use stricter governance criteria."
    out["keep_drop"] = np.where(out["selected_for_formula"], "Keep in benchmark", "Drop from benchmark")
    out["reason"] = np.select(
        [
            out["feature"].isin(POLICY_SENSITIVE_FEATURES),
            out["iv_variable"] >= 0.10,
            out["iv_variable"].between(0.02, 0.10, inclusive="left"),
            out["selected_for_formula"],
        ],
        [
            "High-IV policy-sensitive product tenor; keep with sensitivity check.",
            "Strong risk separation and business rationale.",
            "Useful supporting driver with business rationale.",
            "Low-IV supporting variable retained for broad benchmark, not final parsimonious production scorecard.",
        ],
        default="IV below benchmark threshold.",
    )
    return out[["feature", "business_meaning", "iv_variable", "selected_for_formula", "keep_drop", "selection_rule", "reason"]]


def add_woe_logistic_scorecard(
    splits: dict[str, pd.DataFrame],
    selected: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
    feature_iv: pd.DataFrame,
    output_col: str = "woe_logistic_scorecard_pd",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    selected_features = selected["feature"].tolist()
    woe_cols = [f"woe_logit_{feature}" for feature in selected_features]
    for frame in splits.values():
        for feature, col in zip(selected_features, woe_cols):
            frame[col] = frame[feature].astype(str).map(woe_maps[feature]).fillna(0.0).astype(float)

    model = LogisticRegression(max_iter=500, C=0.8)
    model.fit(splits["train_pre_2016"][woe_cols], splits["train_pre_2016"]["bad_flag"])
    for frame in splits.values():
        frame[output_col] = model.predict_proba(frame[woe_cols])[:, 1]

    coefficient_rows = []
    for feature, col, coefficient in zip(selected_features, woe_cols, model.coef_[0]):
        coefficient_rows.append(
            {
                "feature": feature,
                "business_meaning": FEATURE_DESCRIPTIONS[feature],
                "woe_column": col,
                "coefficient": float(coefficient),
                "interpretation": "Positive coefficient increases bad odds when WOE rises; negative coefficient lowers bad odds when WOE rises.",
            }
        )
    coefficients = pd.DataFrame(coefficient_rows)
    coefficients["model_intercept"] = float(model.intercept_[0])

    factor = PDO / np.log(2)
    offset = BASE_SCORE - factor * np.log(BASE_GOOD_ODDS)
    points_rows = []
    for row in coefficients.itertuples(index=False):
        bins = feature_iv[feature_iv["feature"] == row.feature]
        for bin_row in bins.itertuples(index=False):
            points_rows.append(
                {
                    "feature": row.feature,
                    "bin": bin_row.bin,
                    "woe": float(bin_row.woe),
                    "coefficient": float(row.coefficient),
                    "bin_points": float(-factor * row.coefficient * bin_row.woe),
                    "business_meaning": row.business_meaning,
                }
            )
    points = pd.DataFrame(points_rows)
    points["base_points_before_bin_contribution"] = float(offset - factor * model.intercept_[0])
    points["pdo"] = PDO
    points["base_score"] = BASE_SCORE
    points["base_good_odds"] = BASE_GOOD_ODDS
    return coefficients, points, splits


def copy_splits(splits: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {name: frame.copy() for name, frame in splits.items()}


def filter_selected(selected: pd.DataFrame, exclude: set[str]) -> pd.DataFrame:
    return selected[~selected["feature"].isin(exclude)].copy()


def scorecard_exclusion_log(benchmark_sign_review: pd.DataFrame, coarse_woe_stability: pd.DataFrame) -> pd.DataFrame:
    stability = (
        coarse_woe_stability.groupby("feature", as_index=False)
        .agg(max_validation_abs_diff=("validation_abs_diff", "max"), max_test_abs_diff=("test_abs_diff", "max"))
    )
    rows = []
    sign_map = benchmark_sign_review.set_index("feature").to_dict("index")
    stability_map = stability.set_index("feature").to_dict("index")
    for feature, reason in CLEAN_SCORECARD_EXCLUSIONS.items():
        sign = sign_map.get(feature, {})
        stable = stability_map.get(feature, {})
        rows.append(
            {
                "feature": feature,
                "exclusion_trigger": CLEAN_SCORECARD_EXCLUSION_TRIGGERS.get(feature, "Governance exclusion"),
                "exclusion_reason": reason,
                "benchmark_coefficient": sign.get("coefficient", np.nan),
                "benchmark_sign_status": sign.get("status", "Not assessed"),
                "max_validation_abs_diff": stable.get("max_validation_abs_diff", np.nan),
                "max_test_abs_diff": stable.get("max_test_abs_diff", np.nan),
                "final_clean_scorecard_use": "No",
                "governance_action": "Exclude from final clean scorecard; keep only as diagnostic/benchmark evidence until remediated.",
            }
        )
    return pd.DataFrame(rows)


def formula_calibration_by_decile(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for sample, frame in splits.items():
        grouped = (
            frame.groupby("expanded_formula_decile")
            .agg(
                accounts=("id", "count"),
                avg_formula_pd=("expanded_formula_pd", "mean"),
                observed_default_rate=("bad_flag", "mean"),
            )
            .reset_index()
            .rename(columns={"expanded_formula_decile": "formula_decile"})
        )
        grouped["sample"] = sample
        grouped["calibration_gap"] = grouped["observed_default_rate"] - grouped["avg_formula_pd"]
        rows.append(grouped)
    out = pd.concat(rows, ignore_index=True)
    return out[["sample", "formula_decile", "accounts", "avg_formula_pd", "observed_default_rate", "calibration_gap"]]


def calibration_comparison(formula_calibration: pd.DataFrame, logistic_calibration: pd.DataFrame) -> pd.DataFrame:
    formula = formula_calibration[formula_calibration["sample"] == "test_2017"].copy()
    logistic = logistic_calibration[logistic_calibration["sample"] == "test_2017"].copy()
    formula = formula.rename(
        columns={
            "formula_decile": "decile",
            "avg_formula_pd": "formula_pd",
            "observed_default_rate": "formula_observed_default",
            "calibration_gap": "formula_gap",
        }
    )[["decile", "accounts", "formula_pd", "formula_observed_default", "formula_gap"]]
    logistic = logistic.rename(
        columns={
            "logistic_calibration_decile": "decile",
            "avg_logistic_pd": "logistic_pd",
            "observed_default_rate": "logistic_observed_default",
            "calibration_gap": "logistic_gap",
        }
    )[["decile", "logistic_pd", "logistic_observed_default", "logistic_gap"]]
    return formula.merge(logistic, on="decile", how="outer").sort_values("decile")


def three_model_calibration_comparison(
    formula_calibration: pd.DataFrame,
    woe_logistic_calibration: pd.DataFrame,
    logistic_calibration: pd.DataFrame,
) -> pd.DataFrame:
    formula = formula_calibration[formula_calibration["sample"] == "test_2017"].rename(
        columns={
            "formula_decile": "decile",
            "avg_formula_pd": "formula_pd",
            "observed_default_rate": "formula_observed",
            "calibration_gap": "formula_gap",
        }
    )[["decile", "formula_pd", "formula_observed", "formula_gap"]]
    woe_logistic = woe_logistic_calibration[woe_logistic_calibration["sample"] == "test_2017"].rename(
        columns={
            "woe_logistic_decile": "decile",
            "avg_woe_logistic_pd": "woe_logistic_pd",
            "observed_default_rate": "woe_logistic_observed",
            "calibration_gap": "woe_logistic_gap",
        }
    )[["decile", "woe_logistic_pd", "woe_logistic_observed", "woe_logistic_gap"]]
    raw_logistic = logistic_calibration[logistic_calibration["sample"] == "test_2017"].rename(
        columns={
            "logistic_calibration_decile": "decile",
            "avg_logistic_pd": "raw_logistic_pd",
            "observed_default_rate": "raw_logistic_observed",
            "calibration_gap": "raw_logistic_gap",
        }
    )[["decile", "raw_logistic_pd", "raw_logistic_observed", "raw_logistic_gap"]]
    return (
        formula.merge(woe_logistic, on="decile", how="outer")
        .merge(raw_logistic, on="decile", how="outer")
        .sort_values("decile")
    )


def tail_calibration_review(logistic_calibration: pd.DataFrame) -> pd.DataFrame:
    review = logistic_calibration[
        logistic_calibration["sample"].isin(["validation_2016", "test_2017"])
        & logistic_calibration["logistic_calibration_decile"].isin([9, 10])
    ].copy()
    review["action"] = np.where(
        review["calibration_gap"] > 0.05,
        "Recalibrate high-risk tail before production use",
        "Monitor high-risk tail",
    )
    review["risk_note"] = "Average calibration gap is not enough; high-risk tail drives cutoff, EL, pricing and decline/manual-review policy."
    return review.rename(
        columns={
            "logistic_calibration_decile": "decile",
            "avg_logistic_pd": "avg_pd",
            "observed_default_rate": "observed_default",
            "calibration_gap": "gap",
        }
    )[["sample", "decile", "accounts", "avg_pd", "observed_default", "gap", "action", "risk_note"]]


def tail_recalibration_outputs(logistic_calibration: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    validation = logistic_calibration[logistic_calibration["sample"] == "validation_2016"].copy()
    validation["recalibration_factor_from_validation"] = (
        validation["observed_default_rate"] / validation["avg_logistic_pd"]
    ).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    factor_map = validation.set_index("logistic_calibration_decile")["recalibration_factor_from_validation"].to_dict()

    rows = []
    for row in logistic_calibration[logistic_calibration["sample"].isin(["validation_2016", "test_2017"])].itertuples(index=False):
        decile = int(row.logistic_calibration_decile)
        factor = float(factor_map.get(decile, 1.0))
        recalibrated_pd = float(np.clip(row.avg_logistic_pd * factor, 0.0001, 0.9999))
        rows.append(
            {
                "sample": row.sample,
                "decile": decile,
                "accounts": int(row.accounts),
                "pre_recalibration_pd": float(row.avg_logistic_pd),
                "observed_default_rate": float(row.observed_default_rate),
                "pre_recalibration_gap": float(row.calibration_gap),
                "validation_factor": factor,
                "recalibrated_pd_candidate": recalibrated_pd,
                "post_recalibration_gap": float(row.observed_default_rate - recalibrated_pd),
                "evaluation_use": "factor fitting only, not independent evaluation" if row.sample == "validation_2016" else "out-of-time check",
                "method": "Validation-2016 decile-level multiplicative calibration factor applied to average raw-logistic PD.",
                "production_status": "Candidate only - requires independent validation before pricing, ECL or automated cutoff use.",
            }
        )
    by_decile = pd.DataFrame(rows)
    plan = by_decile[by_decile["decile"].isin([9, 10])].copy()
    plan["tail_action"] = np.where(
        plan["post_recalibration_gap"].abs() <= plan["pre_recalibration_gap"].abs(),
        "Candidate recalibration reduces absolute tail gap",
        "Review alternative calibration method",
    )
    plan["governance_note"] = "Current PDs are pre-recalibration; high-risk tail should not be used for production pricing/ECL without approved recalibration."
    return plan, by_decile


def logistic_decile_bins(splits: dict[str, pd.DataFrame], pd_col: str) -> np.ndarray:
    _, bins = pd.qcut(
        splits["train_pre_2016"][pd_col],
        10,
        labels=False,
        retbins=True,
        duplicates="drop",
    )
    bins[0] = -np.inf
    bins[-1] = np.inf
    return bins


def recalibration_before_after_metrics(
    splits: dict[str, pd.DataFrame],
    logistic_calibration: pd.DataFrame,
) -> pd.DataFrame:
    validation = logistic_calibration[logistic_calibration["sample"] == "validation_2016"].copy()
    validation["factor"] = (
        validation["observed_default_rate"] / validation["avg_logistic_pd"]
    ).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    factor_map = validation.set_index("logistic_calibration_decile")["factor"].to_dict()
    bins = logistic_decile_bins(splits, "logistic_challenger_pd")
    labels = list(range(1, len(bins)))
    rows = []
    for sample in ["validation_2016", "test_2017"]:
        frame = splits[sample].copy()
        frame["logistic_decile"] = pd.cut(
            frame["logistic_challenger_pd"],
            bins=bins,
            labels=labels,
            include_lowest=True,
        ).astype(int)
        frame["recalibration_factor"] = frame["logistic_decile"].map(factor_map).fillna(1.0).astype(float)
        frame["recalibrated_pd_candidate"] = (frame["logistic_challenger_pd"] * frame["recalibration_factor"]).clip(0.0001, 0.9999)
        before = (
            frame.groupby("logistic_decile")
            .agg(avg_pd=("logistic_challenger_pd", "mean"), observed=("bad_flag", "mean"))
            .reset_index()
        )
        before["gap"] = before["observed"] - before["avg_pd"]
        after = (
            frame.groupby("logistic_decile")
            .agg(avg_pd=("recalibrated_pd_candidate", "mean"), observed=("bad_flag", "mean"))
            .reset_index()
        )
        after["gap"] = after["observed"] - after["avg_pd"]
        high_tail_before = float(before.loc[before["logistic_decile"].eq(10), "gap"].iloc[0])
        high_tail_after = float(after.loc[after["logistic_decile"].eq(10), "gap"].iloc[0])
        decision = (
            "Fitting sample only - zero/low validation gap is mechanical, not independent evidence; no final recalibrated PD selected."
            if sample == "validation_2016"
            else "Diagnostic candidate reduces high-risk underprediction but over-corrects several lower/mid deciles; no final recalibrated PD selected."
        )
        rows.append(
            {
                "sample": sample,
                "method": "Validation-2016 decile-level multiplicative factor",
                "mean_abs_calibration_gap_before": float(before["gap"].abs().mean()),
                "mean_abs_calibration_gap_after": float(after["gap"].abs().mean()),
                "max_abs_calibration_gap_before": float(before["gap"].abs().max()),
                "max_abs_calibration_gap_after": float(after["gap"].abs().max()),
                "high_risk_tail_gap_before": high_tail_before,
                "high_risk_tail_gap_after": high_tail_after,
                "brier_score_before": float(brier_score_loss(frame["bad_flag"], frame["logistic_challenger_pd"])),
                "brier_score_after": float(brier_score_loss(frame["bad_flag"], frame["recalibrated_pd_candidate"])),
                "evaluation_use": "factor fitting only, not independent evaluation" if sample == "validation_2016" else "out-of-time check",
                "decision": decision,
            }
        )
    return pd.DataFrame(rows)


def post_coarse_model_stack_performance(
    coarse_performance: pd.DataFrame,
    metrics: pd.DataFrame,
) -> pd.DataFrame:
    coarse_formula = coarse_performance.copy()
    coarse_formula["model"] = "Coarse expanded WOE formula"
    coarse_formula = coarse_formula.rename(columns={"brier_score": "brier"})
    clean_woe = metrics[metrics["model_name"].eq("WOE logistic scorecard")].copy()
    clean_woe["model"] = "Final clean WOE-logistic scorecard"
    clean_woe = clean_woe.rename(columns={"brier_score": "brier"})
    raw = metrics[metrics["model_name"].eq("Logistic regression challenger")].copy()
    raw["model"] = "Raw logistic challenger"
    raw = raw.rename(columns={"brier_score": "brier"})
    cols = ["model", "sample", "auc", "gini", "ks", "brier", "calibration_gap", "rows", "observed_default_rate"]
    return pd.concat([coarse_formula[cols], clean_woe[cols], raw[cols]], ignore_index=True)


def woe_logistic_feature_sensitivity(
    coarse_splits: dict[str, pd.DataFrame],
    coarse_selected: pd.DataFrame,
    coarse_woe_maps: dict[str, dict[str, float]],
    coarse_feature_iv: pd.DataFrame,
) -> pd.DataFrame:
    variants = [
        ("With mort_acc, without revol_util", {"revol_util_band_exp"}),
        ("Without mort_acc and without revol_util", {"revol_util_band_exp", "mort_acc_band_exp"}),
    ]
    rows = []
    for name, exclusions in variants:
        variant_selected = filter_selected(coarse_selected, exclusions)
        variant_splits = copy_splits(coarse_splits)
        _, _, variant_splits = add_woe_logistic_scorecard(
            variant_splits,
            variant_selected,
            coarse_woe_maps,
            coarse_feature_iv,
            output_col="variant_pd",
        )
        for sample, frame in variant_splits.items():
            row = metric_row(sample, name, frame, "variant_pd")
            row["excluded_features"] = ", ".join(sorted(exclusions))
            row["feature_count"] = len(variant_selected)
            rows.append(row)
    return pd.DataFrame(rows)


def final_model_recommendation(metrics: pd.DataFrame, clean_exclusion_log: pd.DataFrame) -> pd.DataFrame:
    test = metrics[metrics["sample"].eq("test_2017")].set_index("model_name")
    clean = test.loc["WOE logistic scorecard"]
    raw = test.loc["Logistic regression challenger"]
    formula = test.loc["Expanded WOE formula scorecard"]
    exclusion_note = "; ".join(clean_exclusion_log["feature"].tolist())
    return pd.DataFrame(
        [
            {
                "model": "Thin baseline scorecard",
                "use_case": "Portfolio foundation / EL / cutoff / monitoring",
                "status": "Keep",
                "reason": "Large 1.3M-row base, transparent target and economics; ranking is moderate, not production underwriting.",
            },
            {
                "model": "Expanded WOE formula",
                "use_case": "Explainability benchmark",
                "status": "Keep as benchmark",
                "reason": f"Transparent IV-weighted formula layer; test AUC {formula['auc']:.3f}, KS {formula['ks']:.3f}.",
            },
            {
                "model": "Final clean WOE-logistic scorecard",
                "use_case": "Clean scorecard candidate for portfolio demonstration",
                "status": "Conditional candidate",
                "reason": f"Removes {exclusion_note}; test AUC {clean['auc']:.3f}, KS {clean['ks']:.3f}. Portfolio demonstration only because retained variables still require independent stability, fairness/proxy and calibration validation.",
            },
            {
                "model": "Raw logistic regression challenger",
                "use_case": "Performance benchmark",
                "status": "Benchmark only",
                "reason": f"Best AUC/KS among public-data candidates at AUC {raw['auc']:.3f}, KS {raw['ks']:.3f}, but lower explainability and governance readiness.",
            },
            {
                "model": "Final production model",
                "use_case": "Automated underwriting / pricing / ECL",
                "status": "Not selected",
                "reason": "Public data is insufficient for production use; final clean still has conditional-review variables and recalibration is diagnostic only. Production would need internal bank data, independent validation, approved calibration and adverse-action review.",
            },
        ]
    )


def build_coarse_binning_reports(
    splits: dict[str, pd.DataFrame],
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, dict[str, float]],
    pd.DataFrame,
    dict[str, pd.DataFrame],
]:
    train = splits["train_pre_2016"]
    adjusted = {name: frame.copy() for name, frame in splits.items()}
    logs = []
    min_count = 1000

    def apply_mapping(feature: str, mapping: dict[str, str], action: str) -> None:
        for old_bin, new_bin in mapping.items():
            old_count = int((train[feature].astype(str) == old_bin).sum())
            logs.append(
                {
                    "feature": feature,
                    "old_bin": old_bin,
                    "old_count": old_count,
                    "minimum_count_rule": min_count,
                    "action": action,
                    "new_bin": new_bin,
                }
            )
        for frame in adjusted.values():
            frame[feature] = frame[feature].astype(str).replace(mapping)

    apply_mapping("dti_band_exp", {"30-40": "30+", "40-60": "30+", "60+": "30+"}, "merge high/extreme DTI into 30+ to enforce minimum bin size")
    apply_mapping(
        "application_type_exp",
        {"Individual": "All application types", "Joint App": "All application types"},
        "collapse low-IV sparse application type before final feature-governance review",
    )
    apply_mapping("revol_util_band_exp", {"100+": "80+" , "80-100": "80+"}, "merge high utilization tail")
    apply_mapping("total_acc_band_exp", {"75+": "51+" , "51-75": "51+"}, "merge sparse total-account tail")
    purpose_counts = train["purpose_exp"].astype(str).value_counts()
    purpose_target = "other" if "other" in set(purpose_counts.index.astype(str)) else "Other/Rare purpose"
    purpose_mapping = {
        bin_value: purpose_target
        for bin_value, count in purpose_counts.items()
        if count < min_count and bin_value != purpose_target
    }
    if purpose_mapping:
        apply_mapping("purpose_exp", purpose_mapping, f"merge rare loan-purpose category into {purpose_target}")

    coarse_feature_iv, coarse_woe_maps = build_woe_tables(adjusted["train_pre_2016"])
    coarse_splits, coarse_selected, _ = score_formula(adjusted, coarse_feature_iv, coarse_woe_maps)
    coarse_metrics = []
    for sample, frame in coarse_splits.items():
        coarse_metrics.append(metric_row(sample, "Coarse-binned expanded WOE formula", frame, "expanded_formula_pd"))
    coarse_performance = pd.DataFrame(coarse_metrics)

    coarse_iv_summary = (
        coarse_feature_iv.groupby(["feature", "business_meaning"], as_index=False)
        .agg(iv_variable=("iv_variable", "max"), bins=("bin", "nunique"), min_bin_accounts=("accounts", "min"))
        .sort_values("iv_variable", ascending=False)
    )
    coarse_iv_summary["selected_for_formula"] = coarse_iv_summary["feature"].isin(coarse_selected["feature"])
    coarse_iv_summary["minimum_count_rule"] = min_count
    coarse_iv_summary["minimum_count_rule_status"] = np.where(
        coarse_iv_summary["min_bin_accounts"] >= min_count,
        "Pass",
        "Review - diagnostic exception",
    )
    return pd.DataFrame(logs), coarse_iv_summary, coarse_performance, coarse_feature_iv, coarse_woe_maps, coarse_selected, coarse_splits


def feature_selection_governance(
    selection: pd.DataFrame,
    binning_quality: pd.DataFrame,
    feature_csi: pd.DataFrame,
) -> pd.DataFrame:
    max_csi = feature_csi.groupby("feature", as_index=False)["csi_vs_train"].max().rename(columns={"csi_vs_train": "max_csi"})
    out = selection.merge(binning_quality[["feature", "monotonic_flag", "action"]], on="feature", how="left")
    out = out.merge(max_csi, on="feature", how="left")
    out["stability_check"] = np.select(
        [out["max_csi"].isna(), out["max_csi"] < 0.10, out["max_csi"] < 0.25],
        ["Not in top CSI sample", "Pass", "Watch"],
        default="Review",
    )
    out["correlation_redundancy_check"] = "Review with WOE correlation matrix; IV is not final selection criterion."
    out["adverse_action_explainability"] = np.where(
        out["feature"].isin(["purpose_exp", "home_ownership_exp", "verification_status_exp", "term_band_exp"]),
        "Review explanation wording and proxy risk",
        "Generally explainable with standard credit-risk reason code",
    )
    out["final_action"] = np.where(
        out["selected_for_formula"],
        "Keep for benchmark; revalidate before production",
        "Drop from benchmark",
    )
    return out.rename(columns={"iv_variable": "IV", "selected_for_formula": "selected_flag"})[
        [
            "feature",
            "IV",
            "selected_flag",
            "reason",
            "business_meaning",
            "stability_check",
            "correlation_redundancy_check",
            "adverse_action_explainability",
            "final_action",
        ]
    ]


def coefficient_sign_review(coefficients: pd.DataFrame) -> pd.DataFrame:
    out = coefficients[["feature", "business_meaning", "coefficient"]].copy()
    out["expected_sign"] = "Negative under WOE = ln(%Good / %Bad) and target = bad_flag"
    out["actual_sign"] = np.where(out["coefficient"] < 0, "Negative", np.where(out["coefficient"] > 0, "Positive", "Zero"))
    out["status"] = np.where(out["coefficient"] < 0, "Pass", "Review")
    out["action"] = np.where(
        out["status"].eq("Pass"),
        "Accept sign direction for benchmark; continue monitoring stability.",
        "Review sign reversal; test dropping variable or applying monotonic/coarse-binning before production.",
    )
    return out


def final_production_candidate_features(
    coarse_selected: pd.DataFrame,
    coarse_iv: pd.DataFrame,
    benchmark_sign_review: pd.DataFrame,
    coarse_woe_stability: pd.DataFrame,
    final_clean_features: set[str],
) -> pd.DataFrame:
    iv_summary = (
        coarse_iv.groupby(["feature", "business_meaning"], as_index=False)
        .agg(iv_variable=("iv_variable", "max"), bins=("bin", "nunique"), min_bin_accounts=("accounts", "min"))
    )
    iv_summary["selected_for_formula"] = iv_summary["feature"].isin(coarse_selected["feature"])
    stability = (
        coarse_woe_stability.groupby("feature", as_index=False)
        .agg(max_validation_abs_diff=("validation_abs_diff", "max"), max_test_abs_diff=("test_abs_diff", "max"))
    )
    out = iv_summary.merge(benchmark_sign_review[["feature", "coefficient", "actual_sign", "status"]], on="feature", how="left")
    out = out.merge(stability, on="feature", how="left")
    out["max_abs_woe_diff"] = out[["max_validation_abs_diff", "max_test_abs_diff"]].max(axis=1)
    out["woe_stability_threshold_rule"] = "<=0.10 Pass; >0.10-0.25 Monitor; >0.25-0.50 Conditional Review; >0.50 Do not use without remediation"
    out["woe_stability_bucket"] = np.select(
        [
            out["max_abs_woe_diff"] <= 0.10,
            out["max_abs_woe_diff"] <= 0.25,
            out["max_abs_woe_diff"] <= 0.50,
            out["max_abs_woe_diff"] > 0.50,
        ],
        [
            "Pass",
            "Monitor",
            "Conditional Review",
            "Do not use without remediation",
        ],
        default="Not assessed",
    )
    out["selected_for_final_clean_scorecard"] = out["feature"].isin(final_clean_features)
    out["clean_exclusion_reason"] = out["feature"].map(CLEAN_SCORECARD_EXCLUSIONS).fillna("")
    out["candidate_decision"] = np.select(
        [
            ~out["selected_for_formula"],
            out["feature"].isin(CLEAN_SCORECARD_EXCLUSIONS),
            out["status"].eq("Review"),
            out["min_bin_accounts"] < 1000,
            out["max_abs_woe_diff"] > 0.50,
            out["max_abs_woe_diff"] > 0.25,
            out["max_abs_woe_diff"] > 0.10,
        ],
        [
            "Drop - not selected by IV threshold / low signal",
            "Drop from final clean scorecard - governance exclusion",
            "Drop from final clean scorecard - coefficient sign reversal",
            "Review - sparse bin remains after coarse-binning",
            "Do not use without remediation - WOE stability movement",
            "Conditional Review - WOE stability movement",
            "Monitor - WOE stability movement",
        ],
        default="Candidate with governance controls",
    )
    out["governance_note"] = np.where(
        out["selected_for_final_clean_scorecard"],
        "Retained in final clean portfolio-demonstration scorecard subject to independent validation, fairness/proxy review and monitoring.",
        "Do not treat as final production variable without remediation or documented override.",
    )
    return out.sort_values(["selected_for_formula", "iv_variable"], ascending=[False, False])


def correlation_and_redundancy_review(
    splits: dict[str, pd.DataFrame],
    selected: pd.DataFrame,
    woe_maps: dict[str, dict[str, float]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = splits["train_pre_2016"]
    selected_features = selected["feature"].tolist()
    transformed = pd.DataFrame(
        {
            feature: train[feature].astype(str).map(woe_maps[feature]).fillna(0.0).astype(float)
            for feature in selected_features
        }
    )
    corr = transformed.corr().fillna(0.0)
    corr.index.name = "feature"
    pairs = []
    for i, left in enumerate(selected_features):
        for right in selected_features[i + 1 :]:
            value = float(corr.loc[left, right])
            if abs(value) >= 0.25 or (left, right) in {
                ("open_acc_band_exp", "total_acc_band_exp"),
                ("term_band_exp", "loan_amount_band_exp"),
                ("fico_band_exp", "verification_status_exp"),
                ("revol_util_band_exp", "revol_bal_band_exp"),
            }:
                pairs.append(
                    {
                        "feature_pair": f"{left} vs {right}",
                        "correlation": value,
                        "relationship": "WOE-transformed Pearson correlation on train window",
                        "risk": "Potential redundancy or shared policy/product signal" if abs(value) >= 0.25 else "Business-related pair to monitor",
                        "decision": "Monitor; final production scorecard would choose based on stability, explainability and incremental value.",
                    }
                )
    return corr.reset_index(), pd.DataFrame(pairs).sort_values("correlation", key=lambda s: s.abs(), ascending=False)


def woe_stability_review(splits: dict[str, pd.DataFrame], feature_iv: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample_parts = []
    monotonic_rows = []
    train_woe = feature_iv[["feature", "bin", "woe"]].rename(columns={"woe": "train_woe"})
    for sample in ["validation_2016", "test_2017"]:
        frame = splits[sample]
        for feature in FORMULA_FEATURES:
            grouped = (
                frame.groupby(feature)
                .agg(good_accounts=("good_flag", "sum"), bad_accounts=("bad_flag", "sum"), accounts=("id", "count"))
                .reset_index()
                .rename(columns={feature: "bin"})
            )
            smooth = 0.5
            total_good = grouped["good_accounts"].sum()
            total_bad = grouped["bad_accounts"].sum()
            grouped[f"{sample}_woe"] = np.log(
                ((grouped["good_accounts"] + smooth) / (total_good + smooth * len(grouped)))
                / ((grouped["bad_accounts"] + smooth) / (total_bad + smooth * len(grouped)))
            )
            grouped["feature"] = feature
            sample_parts.append(grouped[["feature", "bin", f"{sample}_woe"]])

    stability = train_woe.copy()
    for sample in ["validation_2016", "test_2017"]:
        sample_frame = pd.concat(
            [part for part in sample_parts if f"{sample}_woe" in part.columns],
            ignore_index=True,
        )
        stability = stability.merge(sample_frame, on=["feature", "bin"], how="left")
    stability["validation_abs_diff"] = (stability["validation_2016_woe"] - stability["train_woe"]).abs()
    stability["test_abs_diff"] = (stability["test_2017_woe"] - stability["train_woe"]).abs()
    stability["stability_flag"] = np.where(
        stability[["validation_abs_diff", "test_abs_diff"]].max(axis=1) <= 0.25,
        "Stable",
        "Review",
    )
    stability["action"] = np.where(
        stability["stability_flag"].eq("Stable"),
        "Accept for benchmark",
        "Review bin stability before production",
    )

    for feature, group in feature_iv.groupby("feature", sort=False):
        ordered = group.reset_index(drop=True)
        diffs = ordered["woe"].diff().dropna()
        if feature in ORDINAL_FEATURES and not diffs.empty:
            monotonic = bool((diffs >= -1e-9).all() or (diffs <= 1e-9).all())
            flag = "Monotonic" if monotonic else "Non-monotonic"
        else:
            flag = "Not assessed - nominal"
        monotonic_rows.append(
            {
                "feature": feature,
                "bin_count": int(ordered["bin"].nunique()),
                "monotonic_flag": flag,
                "action": "Accept categorical pattern" if flag == "Not assessed - nominal" else "Review coarse-binning before production" if flag == "Non-monotonic" else "Accept for benchmark",
            }
        )
    return pd.DataFrame(monotonic_rows), stability


def enriched_cutoff_strategy(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = splits["test_2017"]
    rows = []
    for cutoff in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.50]:
        formula_approved = frame["expanded_formula_pd"] <= cutoff
        logistic_approved = frame["logistic_challenger_pd"] <= cutoff
        woe_logistic_approved = frame["woe_logistic_scorecard_pd"] <= cutoff
        rows.append(
            {
                "pd_cutoff": cutoff,
                "formula_approval_rate": float(formula_approved.mean()),
                "formula_approved_bad_rate": float(frame.loc[formula_approved, "bad_flag"].mean()) if formula_approved.any() else np.nan,
                "woe_logistic_approval_rate": float(woe_logistic_approved.mean()),
                "woe_logistic_approved_bad_rate": float(frame.loc[woe_logistic_approved, "bad_flag"].mean()) if woe_logistic_approved.any() else np.nan,
                "logistic_approval_rate": float(logistic_approved.mean()),
                "logistic_approved_bad_rate": float(frame.loc[logistic_approved, "bad_flag"].mean()) if logistic_approved.any() else np.nan,
                "comment": "Accepted/booked test sample cutoff benchmark, not full applicant-level approval simulation.",
            }
        )
    return pd.DataFrame(rows)


def challenger_decision_matrix(
    metrics: pd.DataFrame,
    tail_review: pd.DataFrame,
    feature_csi: pd.DataFrame,
) -> pd.DataFrame:
    test = metrics[metrics["sample"] == "test_2017"].set_index("model_name")
    formula = test.loc["Expanded WOE formula scorecard"]
    woe_logit = test.loc["WOE logistic scorecard"]
    raw_logit = test.loc["Logistic regression challenger"]
    max_tail_gap = float(tail_review["gap"].max())
    max_csi = float(feature_csi["csi_vs_train"].max())
    rows = [
        ("AUC/Gini/KS", f"AUC {formula['auc']:.3f}, KS {formula['ks']:.3f}", f"AUC {raw_logit['auc']:.3f}, KS {raw_logit['ks']:.3f}", "Logistic challenger", "Raw logistic has best discrimination."),
        ("WOE-logistic classic scorecard", "Heuristic IV-weighted score", f"WOE logistic AUC {woe_logit['auc']:.3f}", "WOE logistic scorecard", "Classic scorecard bridges transparency and coefficient estimation."),
        ("Brier", f"{formula['brier_score']:.3f}", f"{raw_logit['brier_score']:.3f}", "Logistic challenger", "Lower Brier indicates better probability accuracy."),
        ("High-risk tail gap", "Tail review needed", f"Max decile 9-10 gap {max_tail_gap:.2%}", "No production winner", "Tail recalibration required before production use."),
        ("PSI/CSI stability", "Score/feature drift documented", f"Max top-feature CSI {max_csi:.3f}", "Tie", "Stability is acceptable for benchmark, still requires production monitoring."),
        ("Explainability", "High", "Medium", "Formula scorecard", "Scorecard is easier for policy and adverse-action explanation."),
        ("Adverse-action usability", "High", "Medium", "Formula scorecard", "Reason codes map naturally to scorecard variables."),
        ("Implementation complexity", "Low/medium", "Medium/high", "Formula scorecard", "Raw logistic needs stronger calibration and governance controls."),
        ("Governance burden", "Medium", "High", "Formula scorecard", "Higher-performance challenger needs independent validation and calibration governance."),
    ]
    return pd.DataFrame(rows, columns=["criterion", "formula_scorecard", "logistic_challenger", "winner", "comment"])


def static_governance_reports() -> dict[str, pd.DataFrame]:
    reject_scope = pd.DataFrame(
        [
            ("Rejected applicant population", "Yes", "Segmentation and sensitivity analysis"),
            ("Rejected default outcome", "No", "Cannot validate reject default behavior"),
            ("Inferred bad labels", "No", "Optional future scenario, not production"),
            ("Retrained scorecard with rejects", "No", "Future work only"),
        ],
        columns=["item", "available", "treatment"],
    )
    monitoring = pd.DataFrame(
        [
            ("Enriched score PSI", ">0.10 watch, >0.25 material", "Investigate population drift"),
            ("Top feature CSI", ">0.10 watch", "Segment review and data/process check"),
            ("Decile 10 calibration gap", ">5 pp", "Tail recalibration assessment"),
            ("AUC drop", ">10% vs OOT baseline", "Challenger review"),
            ("KS drop", ">10% vs OOT baseline", "Policy review"),
            ("Default rate shift", ">2 pp vs development", "Recalibration assessment"),
        ],
        columns=["metric", "threshold", "action"],
    )
    reason_codes = pd.DataFrame(
        [
            ("fico_band_exp", "Lower FICO means higher risk", "Credit history risk", "Credit history is weaker than lower-risk bands.", "High"),
            ("dti_band_exp", "Higher DTI means higher risk", "High debt-to-income ratio", "Debt obligations are high relative to income.", "High"),
            ("revol_util_band_exp", "Higher utilization usually means higher risk", "High revolving credit usage", "Not used in final clean scorecard because benchmark coefficient sign reversal must be remediated before adverse-action use.", "Not suitable until sign reversal is resolved"),
            ("emp_length_exp", "Shorter/unstable employment may increase risk", "Limited employment stability", "Employment history is less stable.", "Medium"),
            ("loan_amount_band_exp", "Higher amount may increase exposure/affordability risk", "High requested exposure", "Requested loan amount increases exposure.", "Medium"),
            ("term_band_exp", "Longer tenor may increase uncertainty", "Long repayment tenor", "Loan tenor increases repayment uncertainty.", "Review"),
            ("verification_status_exp", "Verification status may signal documentation risk", "Limited verification evidence", "Application verification level requires review.", "Review"),
        ],
        columns=["feature", "risk_direction", "example_reason_code", "business_explanation", "adverse_action_suitability"],
    )
    fairness = pd.DataFrame(
        [
            ("home_ownership_exp", "May proxy wealth/housing stability", "Can reflect repayment stability, but must be monitored", "Review wording carefully", "Monitor approval/default impact by segment", "Review"),
            ("income_band_exp", "May correlate with socioeconomic status", "Repayment capacity is central to credit risk", "Explain as affordability/capacity", "Monitor disparate impact", "Keep with monitoring"),
            ("purpose_exp", "May correlate with social/economic profile", "Loan purpose affects risk and use of funds", "Use broad categories only", "Avoid overly granular sparse categories", "Review"),
            ("emp_length_exp", "May proxy age/career stability", "Employment stability can affect repayment capacity", "Explain as employment history only", "Monitor segment impact", "Review"),
            ("fico_band_exp", "Creditworthiness signal, but requires fair-use controls", "Core credit history indicator", "Strong adverse-action explainability", "Monitor policy and compliance use", "Keep"),
            ("term_band_exp", "Policy/product segmentation proxy", "Tenor affects uncertainty and exposure duration", "Explain as product tenor", "Run without-term sensitivity", "Keep with caveat"),
            ("verification_status_exp", "May proxy channel/documentation quality", "Verification affects data confidence", "Use operational/documentation explanation", "Monitor channel bias", "Review"),
        ],
        columns=["feature", "potential_proxy_risk", "business_justification", "adverse_action_explainability", "monitoring_action", "keep_or_review"],
    )
    signoff = pd.DataFrame(
        [
            ("Feature approved", "Credit Risk + Compliance", "Business rationale, no leakage, proxy review"),
            ("Binning approved", "Model Development", "Minimum bin size, WOE stability, monotonicity review"),
            ("Model approved", "Model Risk", "Validation metrics, calibration, tail review, challenger comparison"),
            ("Cutoff approved", "Credit Policy", "Risk appetite, expected loss impact, operational capacity"),
            ("Monitoring approved", "Portfolio Risk", "PSI/CSI triggers, calibration triggers, owner/frequency"),
            ("Production use approved", "Risk Committee", "Independent validation, data lineage, adverse-action review"),
        ],
        columns=["decision", "owner", "required_evidence"],
    )
    return {
        "reject_scope": reject_scope,
        "monitoring": monitoring,
        "reason_codes": reason_codes,
        "fairness": fairness,
        "signoff": signoff,
    }


def population_bridge(base: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    summary_path = REPORTS / "formula_engine_summary.json"
    if summary_path.exists():
        formula_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        portfolio_rows = int(formula_summary["account_rows"])
        matured_rows = int(formula_summary["matured_rows"])
        reject_rows = int(formula_summary["reject_population_rows"])
    else:
        portfolio_rows = 1_347_681
        matured_rows = 1_291_521
        reject_rows = 27_648_741
    enriched_test_auc = float(
        metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Expanded WOE formula scorecard")]["auc"].iloc[0]
    )
    logistic_test_auc = float(
        metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Logistic regression challenger")]["auc"].iloc[0]
    )
    return pd.DataFrame(
        [
            {
                "dataset_layer": "Portfolio base",
                "population": "Accepted/booked lending accounts",
                "rows": portfolio_rows,
                "matured_or_train_rows": matured_rows,
                "features": "Thin/core fields",
                "used_for": "Target, baseline PD, expected loss, cutoff, monitoring and stress/pricing framework.",
                "not_used_for": "Not used for enriched model benchmark.",
                "headline_metric": "Baseline AUC 0.626 on large portfolio foundation.",
            },
            {
                "dataset_layer": "Enriched accepted sample",
                "population": "Accepted loans with richer application-time variables",
                "rows": int(len(base)),
                "matured_or_train_rows": int(metrics.loc[metrics["sample"].eq("train_pre_2016"), "rows"].iloc[0]),
                "features": f"{len(FORMULA_FEATURES)} candidate features",
                "used_for": "Expanded WOE scorecard and logistic challenger benchmark.",
                "not_used_for": "Not directly comparable to the 1.3M-row baseline AUC as the same population/model.",
                "headline_metric": f"Expanded WOE AUC {enriched_test_auc:.3f}; logistic challenger AUC {logistic_test_auc:.3f}.",
            },
            {
                "dataset_layer": "Rejected applicant data",
                "population": "Rejected applications",
                "rows": reject_rows,
                "matured_or_train_rows": 0,
                "features": "Application attributes only",
                "used_for": "Reject inference sensitivity and selection-bias discussion.",
                "not_used_for": "No observed default outcome; not used as labeled model training data.",
                "headline_metric": "Sensitivity only, not true reject-inference implementation.",
            },
        ]
    )


def write_reports(
    base: pd.DataFrame,
    feature_iv: pd.DataFrame,
    selected: pd.DataFrame,
    metrics: pd.DataFrame,
    deciles: pd.DataFrame,
    pd_by_decile: dict[int, float],
    bridge: pd.DataFrame,
    term_sensitivity: pd.DataFrame,
    split_drift: pd.DataFrame,
    logistic_calibration: pd.DataFrame,
    feature_csi: pd.DataFrame,
    score_shift: pd.DataFrame,
    binning_quality: pd.DataFrame,
    selection_rationale: pd.DataFrame,
    woe_logistic_coefficients: pd.DataFrame,
    woe_logistic_points: pd.DataFrame,
    woe_logistic_sign_review: pd.DataFrame,
    benchmark_woe_logistic_coefficients: pd.DataFrame,
    benchmark_woe_logistic_points: pd.DataFrame,
    benchmark_woe_logistic_sign_review: pd.DataFrame,
    clean_exclusion_log: pd.DataFrame,
    formula_calibration: pd.DataFrame,
    calibration_compare: pd.DataFrame,
    woe_logistic_calibration: pd.DataFrame,
    three_model_calibration: pd.DataFrame,
    tail_review: pd.DataFrame,
    tail_recalibration_plan: pd.DataFrame,
    recalibrated_pd_by_decile: pd.DataFrame,
    recalibration_metrics: pd.DataFrame,
    coarse_log: pd.DataFrame,
    coarse_iv: pd.DataFrame,
    coarse_performance: pd.DataFrame,
    post_coarse_stack_performance: pd.DataFrame,
    mort_acc_sensitivity: pd.DataFrame,
    coarse_woe_stability: pd.DataFrame,
    production_candidate_features: pd.DataFrame,
    final_model_recommendation_table: pd.DataFrame,
    feature_governance: pd.DataFrame,
    corr_matrix: pd.DataFrame,
    redundant_review: pd.DataFrame,
    monotonicity_review: pd.DataFrame,
    woe_stability: pd.DataFrame,
    enriched_cutoffs: pd.DataFrame,
    challenger_matrix: pd.DataFrame,
    static_reports: dict[str, pd.DataFrame],
) -> None:
    legacy_confusing_reports = [
        "38_" + "woe_logistic_scorecard_coefficients.csv",
        "38_" + "woe_logistic_scorecard_points.csv",
        "38_" + "woe_logistic_coefficient_sign_review.csv",
        "39_final_" + "production_candidate_feature_list.csv",
    ]
    for filename in legacy_confusing_reports:
        path = REPORTS / filename
        if path.exists():
            path.unlink()

    iv_summary = (
        feature_iv.groupby(["feature", "business_meaning"], as_index=False)
        .agg(iv_variable=("iv_variable", "max"), bins=("bin", "nunique"), accounts=("accounts", "sum"))
        .sort_values("iv_variable", ascending=False)
    )
    iv_summary["selected_for_formula"] = iv_summary["feature"].isin(selected["feature"])
    feature_iv.to_csv(REPORTS / "35_enriched_feature_woe_detail.csv", index=False)
    iv_summary.to_csv(REPORTS / "35_enriched_feature_iv_summary.csv", index=False)
    selected.to_csv(REPORTS / "35_enriched_formula_selected_features.csv", index=False)
    metrics.to_csv(REPORTS / "36_challenger_model_comparison.csv", index=False)
    deciles.to_csv(REPORTS / "36_expanded_scorecard_decile_pd.csv", index=False)
    bridge.to_csv(REPORTS / "37_population_bridge.csv", index=False)
    term_sensitivity.to_csv(REPORTS / "37_term_sensitivity_comparison.csv", index=False)
    split_drift.to_csv(REPORTS / "37_enriched_split_drift_summary.csv", index=False)
    logistic_calibration.to_csv(REPORTS / "37_logistic_calibration_by_decile.csv", index=False)
    feature_csi.to_csv(REPORTS / "37_enriched_feature_csi_top5.csv", index=False)
    score_shift.to_csv(REPORTS / "37_enriched_score_distribution_shift.csv", index=False)
    binning_quality.to_csv(REPORTS / "37_enriched_binning_quality_check.csv", index=False)
    selection_rationale.to_csv(REPORTS / "37_feature_selection_rationale.csv", index=False)
    woe_logistic_coefficients.to_csv(REPORTS / "40_final_clean_woe_logistic_scorecard_coefficients.csv", index=False)
    woe_logistic_points.to_csv(REPORTS / "40_final_clean_woe_logistic_scorecard_points.csv", index=False)
    woe_logistic_sign_review.to_csv(REPORTS / "40_final_clean_woe_logistic_coefficient_sign_review.csv", index=False)
    benchmark_woe_logistic_coefficients.to_csv(REPORTS / "40_benchmark_woe_logistic_scorecard_coefficients.csv", index=False)
    benchmark_woe_logistic_points.to_csv(REPORTS / "40_benchmark_woe_logistic_scorecard_points.csv", index=False)
    benchmark_woe_logistic_sign_review.to_csv(REPORTS / "40_benchmark_woe_logistic_coefficient_sign_review.csv", index=False)
    clean_exclusion_log.to_csv(REPORTS / "40_final_clean_scorecard_exclusion_log.csv", index=False)
    formula_calibration.to_csv(REPORTS / "38_formula_scorecard_calibration_by_decile.csv", index=False)
    calibration_compare.to_csv(REPORTS / "38_formula_vs_logistic_calibration_comparison.csv", index=False)
    woe_logistic_calibration.to_csv(REPORTS / "39_woe_logistic_calibration_by_decile.csv", index=False)
    three_model_calibration.to_csv(REPORTS / "38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv", index=False)
    tail_review.to_csv(REPORTS / "38_tail_calibration_review.csv", index=False)
    tail_recalibration_plan.to_csv(REPORTS / "39_tail_recalibration_plan.csv", index=False)
    recalibrated_pd_by_decile.to_csv(REPORTS / "39_recalibrated_pd_by_decile.csv", index=False)
    recalibration_metrics.to_csv(REPORTS / "40_recalibration_before_after_metrics.csv", index=False)
    coarse_log.to_csv(REPORTS / "38_binning_coarse_adjustment_log.csv", index=False)
    coarse_iv.to_csv(REPORTS / "38_enriched_feature_iv_after_coarse_binning.csv", index=False)
    coarse_performance.to_csv(REPORTS / "38_model_performance_after_coarse_binning.csv", index=False)
    post_coarse_stack_performance.to_csv(REPORTS / "40_post_coarse_model_stack_performance.csv", index=False)
    mort_acc_sensitivity.to_csv(REPORTS / "40_mort_acc_sensitivity.csv", index=False)
    coarse_woe_stability.to_csv(REPORTS / "39_woe_stability_after_coarse_binning.csv", index=False)
    production_candidate_features.to_csv(REPORTS / "39_final_scorecard_feature_governance_list.csv", index=False)
    final_model_recommendation_table.to_csv(REPORTS / "40_final_model_recommendation.csv", index=False)
    feature_governance.to_csv(REPORTS / "38_feature_selection_governance.csv", index=False)
    corr_matrix.to_csv(REPORTS / "38_feature_correlation_matrix.csv", index=False)
    redundant_review.to_csv(REPORTS / "38_redundant_feature_review.csv", index=False)
    monotonicity_review.to_csv(REPORTS / "38_woe_monotonicity_review.csv", index=False)
    woe_stability.to_csv(REPORTS / "38_woe_stability_train_test.csv", index=False)
    enriched_cutoffs.to_csv(REPORTS / "38_enriched_cutoff_strategy_formula_vs_logistic.csv", index=False)
    challenger_matrix.to_csv(REPORTS / "38_challenger_decision_matrix.csv", index=False)
    static_reports["reject_scope"].to_csv(REPORTS / "38_reject_inference_scope.csv", index=False)
    static_reports["monitoring"].to_csv(REPORTS / "38_enriched_monitoring_triggers.csv", index=False)
    static_reports["reason_codes"].to_csv(REPORTS / "38_reason_code_mapping.csv", index=False)
    static_reports["fairness"].to_csv(REPORTS / "38_fairness_proxy_review.csv", index=False)
    static_reports["signoff"].to_csv(REPORTS / "38_governance_signoff_matrix.csv", index=False)

    criteria = pd.DataFrame(
        [
            (
                "Ranking improvement",
                "Challenger should materially improve AUC/KS versus formula baseline.",
                "Pass",
                "Logistic challenger improves test AUC and KS versus expanded WOE formula.",
            ),
            (
                "Calibration discipline",
                "Higher AUC is not enough if calibration materially worsens.",
                "Conditional Pass",
                "Average test calibration gap is manageable, but high-risk tail requires recalibration control before production use.",
            ),
            (
                "Explainability",
                "Model must support adverse-action and policy conversations.",
                "Pass with control",
                "Formula scorecard remains primary explanation layer; logistic is benchmark/challenger.",
            ),
            (
                "Leakage control",
                "Do not use lender decision outputs as predictors.",
                "Pass",
                "Sub-grade and interest rate are excluded because they can reflect lender pricing/risk decisions.",
            ),
            (
                "Stability and monitoring",
                "Any accepted challenger must pass PSI, drift and out-of-time checks.",
                "Pass for portfolio benchmark",
                "Out-of-time metrics, split drift, score distribution PSI and top-feature CSI are documented; production would still add ongoing monthly monitoring.",
            ),
        ],
        columns=["criterion", "acceptance_rule", "status", "comment"],
    )
    criteria.to_csv(REPORTS / "36_challenger_acceptance_criteria.csv", index=False)

    test_formula = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Expanded WOE formula scorecard")].iloc[0]
    test_woe_logistic = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "WOE logistic scorecard")].iloc[0]
    test_logistic = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Logistic regression challenger")].iloc[0]
    no_term_formula = term_sensitivity[term_sensitivity["model_name"] == "Expanded WOE without term"].iloc[0]
    no_term_logistic = term_sensitivity[term_sensitivity["model_name"] == "Logistic without term"].iloc[0]
    test_tail_recalibration = recalibrated_pd_by_decile[
        (recalibrated_pd_by_decile["sample"] == "test_2017") & (recalibrated_pd_by_decile["decile"] == 10)
    ].iloc[0]
    summary = {
        "enriched_rows": int(len(base)),
        "feature_count_total": len(FORMULA_FEATURES),
        "selected_formula_features": int(len(selected)),
        "train_rows": int(metrics.loc[metrics["sample"].eq("train_pre_2016"), "rows"].iloc[0]),
        "validation_rows": int(metrics.loc[metrics["sample"].eq("validation_2016"), "rows"].iloc[0]),
        "test_rows": int(metrics.loc[metrics["sample"].eq("test_2017"), "rows"].iloc[0]),
        "expanded_formula_test_auc": float(test_formula["auc"]),
        "expanded_formula_test_gini": float(test_formula["gini"]),
        "expanded_formula_test_ks": float(test_formula["ks"]),
        "expanded_formula_test_calibration_gap": float(test_formula["calibration_gap"]),
        "woe_logistic_test_auc": float(test_woe_logistic["auc"]),
        "woe_logistic_test_gini": float(test_woe_logistic["gini"]),
        "woe_logistic_test_ks": float(test_woe_logistic["ks"]),
        "woe_logistic_test_calibration_gap": float(test_woe_logistic["calibration_gap"]),
        "logistic_challenger_test_auc": float(test_logistic["auc"]),
        "logistic_challenger_test_gini": float(test_logistic["gini"]),
        "logistic_challenger_test_ks": float(test_logistic["ks"]),
        "logistic_challenger_test_calibration_gap": float(test_logistic["calibration_gap"]),
        "formula_without_term_test_auc": float(no_term_formula["auc"]),
        "formula_without_term_test_ks": float(no_term_formula["ks"]),
        "logistic_without_term_test_auc": float(no_term_logistic["auc"]),
        "logistic_without_term_test_ks": float(no_term_logistic["ks"]),
        "test_decile_10_pre_recalibration_gap": float(test_tail_recalibration["pre_recalibration_gap"]),
        "test_decile_10_post_recalibration_gap": float(test_tail_recalibration["post_recalibration_gap"]),
        "formula_pd_decile_map": {str(k): float(v) for k, v in pd_by_decile.items()},
    }
    (REPORTS / "36_challenger_model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    text = f"""# Enriched Scorecard And Challenger Benchmark

## Why This Module Was Added

The original 1.3M-row portfolio foundation is strong for target definition, expected loss, cutoff economics and monitoring,
but its modeling feature set is intentionally thin. This enriched LendingClub accepted-loan sample adds application-time
risk drivers such as loan term, revolving utilization, open accounts, public records, bankruptcies, mortgage accounts,
employment length, verification status and application type.

## Population Bridge

The project uses three related but distinct data layers. The AUC 0.626 baseline and the AUC 0.765/0.793 enriched
models are **not directly comparable as the same model on the same population**. The baseline measures performance on
the large portfolio foundation with a thinner feature set, while the enriched models benchmark performance on a smaller
accepted-loan sample with stronger application-time variables.

| Dataset layer | Rows | Role | Not used for |
|---|---:|---|---|
| Portfolio base | {int(bridge.loc[bridge['dataset_layer'].eq('Portfolio base'), 'rows'].iloc[0]):,} | Target, PD baseline, EL, cutoff, monitoring | Enriched model benchmark |
| Enriched accepted sample | {len(base):,} | Expanded WOE and logistic challenger | Direct comparison to 1.3M baseline as same model/population |
| Rejected applicant data | {int(bridge.loc[bridge['dataset_layer'].eq('Rejected applicant data'), 'rows'].iloc[0]):,} | Reject inference sensitivity | Labeled reject model training |

## Data Scope

| Item | Value |
|---|---:|
| Enriched accepted-loan rows | {len(base):,} |
| Candidate risk features | {len(FORMULA_FEATURES)} |
| Features selected into expanded formula | {len(selected)} |
| Train rows <= 2015 | {summary['train_rows']:,} |
| Validation rows 2016 | {summary['validation_rows']:,} |
| Test rows 2017 | {summary['test_rows']:,} |

Note: IV values are calculated on the {summary['train_rows']:,}-row training window, not on the full {len(base):,}-row enriched sample. This prevents look-ahead bias in WOE fitting and PD mapping.

## Out-Of-Time Test Performance

| Model | AUC | Gini | KS | Calibration Gap | Brier |
|---|---:|---:|---:|---:|---:|
| Expanded WOE formula scorecard | {test_formula['auc']:.3f} | {test_formula['gini']:.3f} | {test_formula['ks']:.3f} | {test_formula['calibration_gap']:.2%} | {test_formula['brier_score']:.3f} |
| WOE logistic scorecard | {test_woe_logistic['auc']:.3f} | {test_woe_logistic['gini']:.3f} | {test_woe_logistic['ks']:.3f} | {test_woe_logistic['calibration_gap']:.2%} | {test_woe_logistic['brier_score']:.3f} |
| Logistic regression challenger | {test_logistic['auc']:.3f} | {test_logistic['gini']:.3f} | {test_logistic['ks']:.3f} | {test_logistic['calibration_gap']:.2%} | {test_logistic['brier_score']:.3f} |

## Classic Scorecard Caveat

The expanded WOE formula scorecard is a transparent IV-weighted heuristic scoring layer. The final clean WOE-logistic
scorecard fits logistic regression on WOE-transformed variables and provides coefficient-estimated scorecard points in
`reports/40_final_clean_woe_logistic_scorecard_points.csv`. The final public points file is rebuilt on the post-coarse-binning
feature set and excludes `revol_util_band_exp`, `mort_acc_band_exp` and `bankruptcy_band_exp` because benchmark diagnostics
found sign or stability issues. Benchmark full-scorecard evidence is retained separately in the `40_benchmark_*` reports.

## Term Sensitivity

`term_band_exp` is available at origination and is not an outcome variable, so it is retained as an application-time
product-tenor feature. However, its IV is very high, so it is treated as policy-sensitive. In production validation,
I would test whether performance depends too heavily on product-tenor segmentation.

| Model | Features | Test AUC | Test KS | Comment |
|---|---|---:|---:|---|
| Expanded WOE with term | {term_sensitivity.iloc[0]['feature_scope']} | {term_sensitivity.iloc[0]['auc']:.3f} | {term_sensitivity.iloc[0]['ks']:.3f} | Current formula scorecard |
| Expanded WOE without term | {term_sensitivity.iloc[1]['feature_scope']} | {term_sensitivity.iloc[1]['auc']:.3f} | {term_sensitivity.iloc[1]['ks']:.3f} | Product-tenor sensitivity |
| Logistic with term | {term_sensitivity.iloc[2]['feature_scope']} | {term_sensitivity.iloc[2]['auc']:.3f} | {term_sensitivity.iloc[2]['ks']:.3f} | Current challenger |
| Logistic without term | {term_sensitivity.iloc[3]['feature_scope']} | {term_sensitivity.iloc[3]['auc']:.3f} | {term_sensitivity.iloc[3]['ks']:.3f} | Product-tenor sensitivity |

## Enriched Split Drift

| Sample | Rows | Observed default | Avg formula PD | Avg logistic PD | Comment |
|---|---:|---:|---:|---:|---|
| Train <=2015 | {int(split_drift.iloc[0]['rows']):,} | {split_drift.iloc[0]['observed_default_rate']:.2%} | {split_drift.iloc[0]['avg_formula_pd']:.2%} | {split_drift.iloc[0]['avg_logistic_pd']:.2%} | Model development |
| Validation 2016 | {int(split_drift.iloc[1]['rows']):,} | {split_drift.iloc[1]['observed_default_rate']:.2%} | {split_drift.iloc[1]['avg_formula_pd']:.2%} | {split_drift.iloc[1]['avg_logistic_pd']:.2%} | Out-of-time validation |
| Test 2017 | {int(split_drift.iloc[2]['rows']):,} | {split_drift.iloc[2]['observed_default_rate']:.2%} | {split_drift.iloc[2]['avg_formula_pd']:.2%} | {split_drift.iloc[2]['avg_logistic_pd']:.2%} | Out-of-time test |

Enriched model drift is now documented through split default rates, score distribution PSI and top-feature CSI. Current
results support a portfolio benchmark story, while production use would still require recurring feature-level monitoring.

## Calibration And Binning Evidence Added

- Logistic calibration by decile: `reports/37_logistic_calibration_by_decile.csv`
- Formula vs logistic calibration comparison: `reports/38_formula_vs_logistic_calibration_comparison.csv`
- Three-model calibration comparison: `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`
- WOE-logistic calibration by decile: `reports/39_woe_logistic_calibration_by_decile.csv`
- High-risk tail calibration review: `reports/38_tail_calibration_review.csv`
- Tail recalibration plan: `reports/39_tail_recalibration_plan.csv`
- Recalibrated PD by decile candidate: `reports/39_recalibrated_pd_by_decile.csv`
- Top-feature CSI: `reports/37_enriched_feature_csi_top5.csv`
- Score distribution shift: `reports/37_enriched_score_distribution_shift.csv`
- Binning quality check: `reports/37_enriched_binning_quality_check.csv`
- Feature selection rationale: `reports/37_feature_selection_rationale.csv`
- Final clean coefficient sign review: `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv`
- Post-coarse WOE stability: `reports/39_woe_stability_after_coarse_binning.csv`
- Final scorecard feature governance list: `reports/39_final_scorecard_feature_governance_list.csv`
- Final clean scorecard exclusion log: `reports/40_final_clean_scorecard_exclusion_log.csv`
- Recalibration before/after metrics: `reports/40_recalibration_before_after_metrics.csv`
- Post-coarse model stack performance: `reports/40_post_coarse_model_stack_performance.csv`
- Mort-account sensitivity: `reports/40_mort_acc_sensitivity.csv`
- Final model recommendation: `reports/40_final_model_recommendation.csv`
- Coarse-binning adjustment log: `reports/38_binning_coarse_adjustment_log.csv`
- Challenger decision matrix: `reports/38_challenger_decision_matrix.csv`
- Reason code, fairness/proxy and governance sign-off matrices: `reports/38_reason_code_mapping.csv`, `reports/38_fairness_proxy_review.csv`, `reports/38_governance_signoff_matrix.csv`

## High-Risk Tail Calibration

Average calibration gap is not enough. High-risk tail calibration must be reviewed separately because decile 9-10 drives
cutoff, expected loss, pricing, manual review and decline policy. Current PDs are pre-recalibration and should not be used
for production pricing, ECL or automated cutoff decisions without approved recalibration. A candidate validation-factor
recalibration table is provided; for test decile 10 it moves the gap from {test_tail_recalibration['pre_recalibration_gap']:.2%}
to {test_tail_recalibration['post_recalibration_gap']:.2%}. The before/after metrics also show that this method can
over-correct lower and mid deciles, so it is diagnostic evidence only; no final recalibrated PD is selected.

## Coarse-Binning And Final Candidate Controls

The coarse-binning pass now enforces the 1,000-account minimum-count rule in the post-coarse feature summary. DTI tail
bins are merged into `30+`, rare loan purposes are merged into `other`, and the sparse/low-IV application-type variable
is collapsed before final scorecard feature-governance review. The WOE-logistic scorecard points file is generated from this
post-coarse feature set. The final clean portfolio-demonstration WOE-logistic layer removes `revol_util_band_exp`, `mort_acc_band_exp` and
`bankruptcy_band_exp`; the full benchmark version is kept only as diagnostic evidence.

`reports/40_final_clean_woe_logistic_coefficient_sign_review.csv` checks whether final clean coefficients are directionally consistent
with the WOE convention `WOE = ln(%Good / %Bad)` and `target = bad_flag`. The benchmark sign review is retained separately
in `reports/40_benchmark_woe_logistic_coefficient_sign_review.csv` to show why exclusions were made.

## Senior Interpretation

- The expanded WOE formula scorecard materially improves ranking power versus the thin 1.3M-row baseline.
- Logistic regression is a valid challenger because it improves AUC/KS, but it is kept as a benchmark rather than the primary public story.
- The final clean scorecard remains the explanation layer because it is easier to audit, map to policy, discuss with credit officers and support adverse-action style reasoning.
- `sub_grade` and `int_rate` are deliberately excluded because they can encode lender pricing/risk decisions and create leakage-like contamination.
- `term_band_exp` is retained as a business-valid origination variable, but treated as policy-sensitive due to high IV.
- A production model is not selected from this public dataset; it would require independent validation, ongoing PSI/calibration monitoring, adverse-action review and approval from model governance.

## Selected Feature Themes

The final clean scorecard drivers are product tenor, FICO band, DTI, verification status, loan amount, home ownership,
income band, purpose, open accounts, employment length, public records and revolving balance. Mortgage-account,
revolving-utilization and bankruptcy variables are retained only as benchmark/diagnostic evidence until remediated.
"""
    (REPORTS / "36_challenger_model_summary.md").write_text(text, encoding="utf-8")


def plot_outputs(
    metrics: pd.DataFrame,
    deciles: pd.DataFrame,
    logistic_calibration: pd.DataFrame,
    score_shift: pd.DataFrame,
    calibration_compare: pd.DataFrame,
    recalibrated_pd_by_decile: pd.DataFrame,
) -> None:
    test_metrics = metrics[metrics["sample"] == "test_2017"].copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    x = np.arange(len(test_metrics))
    width = 0.34
    ax.bar(x - width / 2, test_metrics["auc"], width, label="AUC", color=COLORS["blue"])
    ax.bar(x + width / 2, test_metrics["ks"], width, label="KS", color=COLORS["teal"])
    ax.set_xticks(x)
    ax.set_xticklabels(test_metrics["model_name"], rotation=12, ha="right")
    ax.set_ylim(0, 0.9)
    ax.set_title("Out-of-Time Model Benchmark", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.grid(axis="y", color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "challenger_auc_ks_comparison.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(
        deciles["expanded_formula_decile"],
        deciles["observed_default_rate"],
        marker="o",
        color=COLORS["red"],
        label="Observed default rate",
    )
    ax.plot(
        deciles["expanded_formula_decile"],
        deciles["avg_formula_pd"],
        marker="o",
        color=COLORS["blue"],
        label="Formula PD",
    )
    ax.set_title("Expanded Scorecard PD By Train Decile", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Risk decile")
    ax.set_ylabel("Default rate / PD")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "expanded_scorecard_decile_pd.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    test_calibration = logistic_calibration[logistic_calibration["sample"] == "test_2017"].copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(
        test_calibration["logistic_calibration_decile"],
        test_calibration["observed_default_rate"],
        marker="o",
        color=COLORS["red"],
        label="Observed default rate",
    )
    ax.plot(
        test_calibration["logistic_calibration_decile"],
        test_calibration["avg_logistic_pd"],
        marker="o",
        color=COLORS["blue"],
        label="Average logistic PD",
    )
    ax.set_title("Logistic Challenger Calibration By Decile", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Logistic PD decile")
    ax.set_ylabel("Default rate / PD")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "logistic_calibration_curve.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    shift_plot = score_shift[score_shift["sample"].isin(["validation_2016", "test_2017"])].copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    for sample, color in [("validation_2016", COLORS["teal"]), ("test_2017", COLORS["gold"])]:
        temp = shift_plot[shift_plot["sample"] == sample]
        ax.plot(
            temp["expanded_formula_decile"],
            temp["share_gap"],
            marker="o",
            color=color,
            label=sample,
        )
    ax.axhline(0, color=COLORS["gray"], linewidth=1)
    ax.set_title("Expanded Score Distribution Shift Vs Train", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Expanded formula decile")
    ax.set_ylabel("Share gap vs train")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "enriched_score_distribution_shift.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(
        calibration_compare["decile"],
        calibration_compare["formula_gap"],
        marker="o",
        color=COLORS["teal"],
        label="Formula gap",
    )
    ax.plot(
        calibration_compare["decile"],
        calibration_compare["woe_logistic_gap"] if "woe_logistic_gap" in calibration_compare.columns else calibration_compare["logistic_gap"],
        marker="o",
        color=COLORS["blue"],
        label="WOE-logistic gap" if "woe_logistic_gap" in calibration_compare.columns else "Logistic gap",
    )
    if "raw_logistic_gap" in calibration_compare.columns:
        ax.plot(
            calibration_compare["decile"],
            calibration_compare["raw_logistic_gap"],
            marker="o",
            color=COLORS["red"],
            label="Raw logistic gap",
        )
    elif "logistic_gap" in calibration_compare.columns:
        ax.plot(
            calibration_compare["decile"],
            calibration_compare["logistic_gap"],
            marker="o",
            color=COLORS["red"],
            label="Logistic gap",
        )
    ax.axhline(0, color=COLORS["gray"], linewidth=1)
    ax.axhline(0.05, color=COLORS["gold"], linestyle="--", label="Tail review threshold")
    ax.set_title("Formula Vs Challenger Calibration Gap", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Risk / PD decile")
    ax.set_ylabel("Observed default - predicted PD")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "formula_vs_logistic_calibration_gap.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    test_recalibration = recalibrated_pd_by_decile[recalibrated_pd_by_decile["sample"] == "test_2017"].copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(
        test_recalibration["decile"],
        test_recalibration["observed_default_rate"],
        marker="o",
        color=COLORS["red"],
        label="Observed default",
    )
    ax.plot(
        test_recalibration["decile"],
        test_recalibration["pre_recalibration_pd"],
        marker="o",
        color=COLORS["blue"],
        label="Pre-recalibration PD",
    )
    ax.plot(
        test_recalibration["decile"],
        test_recalibration["recalibrated_pd_candidate"],
        marker="o",
        color=COLORS["teal"],
        label="Validation-factor recalibrated PD",
    )
    ax.set_title("Tail Recalibration Before / After", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Raw logistic PD decile")
    ax.set_ylabel("Default rate / PD")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "recalibration_before_after.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def write_risk_committee_memo(
    metrics: pd.DataFrame,
    term_sensitivity: pd.DataFrame,
    tail_review: pd.DataFrame,
    challenger_matrix: pd.DataFrame,
) -> None:
    formula = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Expanded WOE formula scorecard")].iloc[0]
    woe_logit = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "WOE logistic scorecard")].iloc[0]
    logistic = metrics[(metrics["sample"] == "test_2017") & (metrics["model_name"] == "Logistic regression challenger")].iloc[0]
    max_tail_gap = float(tail_review["gap"].max())
    text = f"""# Risk Committee Memo - Project 3

## Objective

Assess a public-data credit risk scorecard and portfolio analytics workflow for recruiter-facing demonstration, not production deployment.

## Data Scope

- Portfolio base: 1.35M accepted/booked accounts for target, EL, cutoff and monitoring.
- Enriched accepted sample: 331.9K rows for expanded WOE scorecard, WOE-logistic scorecard and raw logistic challenger.
- Rejected applicants: 27.6M records for reject inference sensitivity only; no observed repayment outcome.

## Key Findings

- Thin portfolio baseline has moderate ranking power: AUC 0.626, KS 0.180.
- Expanded WOE formula scorecard improves to AUC {formula['auc']:.3f}, KS {formula['ks']:.3f}.
- WOE logistic scorecard, the classic coefficient-estimated scorecard layer, achieves AUC {woe_logit['auc']:.3f}, KS {woe_logit['ks']:.3f}.
- Raw logistic challenger achieves AUC {logistic['auc']:.3f}, KS {logistic['ks']:.3f}.
- Removing term reduces formula AUC to {term_sensitivity.iloc[1]['auc']:.3f} and logistic AUC to {term_sensitivity.iloc[3]['auc']:.3f}, showing product tenor is important but not the only signal.

## Calibration And Tail Risk

Average calibration is acceptable for a portfolio benchmark, but high-risk tail gap reaches {max_tail_gap:.2%}. Decile 9-10 should be recalibrated before any production use.

## Cutoff Recommendation

The 20% PD cutoff in the baseline is a booked-account simulation only. It should be used to discuss segmentation and expected loss, not as a true applicant-level approval strategy.

## Required Approvals Before Production

- Feature approval from Credit Risk and Compliance.
- Binning approval from Model Development.
- Independent validation from Model Risk.
- Cutoff approval from Credit Policy.
- Monitoring trigger approval from Portfolio Risk.
- Final production approval from Risk Committee.

## Committee Position

Use this project as a portfolio demonstration of risk analytics judgment. Do not use for automated underwriting, pricing, credit limit assignment or IFRS 9 reporting without independent validation, recalibration, production data lineage, adverse-action review and governance approval.
"""
    (DOCS / "risk_committee_memo.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    usecols = [
        "id",
        "application_month",
        "loan_status",
        "default_flag",
        "good_flag",
        "bad_flag",
        "term_months",
        "home_ownership",
        "fico_score",
        "total_acc",
        "open_acc",
        "pub_rec",
        "pub_rec_bankruptcies",
        "revol_util",
        "revol_bal",
        "mort_acc",
        "annual_inc",
        "dti",
        "purpose",
        "loan_amnt",
        "application_type",
        "verification_status",
        "emp_length",
    ]
    base = pd.read_csv(SOURCE_ENRICHED, compression="gzip", usecols=usecols, parse_dates=["application_month"])
    base = build_features(base)
    splits = split_population(base)
    feature_iv, woe_maps = build_woe_tables(splits["train_pre_2016"])
    splits, selected, pd_by_decile = score_formula(splits, feature_iv, woe_maps)
    metrics, splits = fit_logistic_challenger(splits)
    (
        coarse_log,
        coarse_iv,
        coarse_performance,
        coarse_feature_iv,
        coarse_woe_maps,
        coarse_selected,
        coarse_splits,
    ) = build_coarse_binning_reports(splits)
    benchmark_splits = copy_splits(coarse_splits)
    benchmark_woe_logistic_coefficients, benchmark_woe_logistic_points, benchmark_splits = add_woe_logistic_scorecard(
        benchmark_splits,
        coarse_selected,
        coarse_woe_maps,
        coarse_feature_iv,
        output_col="benchmark_woe_logistic_scorecard_pd",
    )
    benchmark_woe_logistic_sign_review = coefficient_sign_review(benchmark_woe_logistic_coefficients)
    _, coarse_woe_stability = woe_stability_review(coarse_splits, coarse_feature_iv)
    clean_exclusion_log = scorecard_exclusion_log(benchmark_woe_logistic_sign_review, coarse_woe_stability)
    clean_selected = filter_selected(coarse_selected, set(CLEAN_SCORECARD_EXCLUSIONS))
    clean_splits = copy_splits(coarse_splits)
    woe_logistic_coefficients, woe_logistic_points, clean_splits = add_woe_logistic_scorecard(
        clean_splits,
        clean_selected,
        coarse_woe_maps,
        coarse_feature_iv,
        output_col="woe_logistic_scorecard_pd",
    )
    for sample in splits:
        splits[sample]["woe_logistic_scorecard_pd"] = clean_splits[sample]["woe_logistic_scorecard_pd"].to_numpy()
    woe_logistic_metrics = [
        metric_row(sample, "WOE logistic scorecard", frame, "woe_logistic_scorecard_pd")
        for sample, frame in splits.items()
    ]
    metrics = pd.concat([metrics, pd.DataFrame(woe_logistic_metrics)], ignore_index=True)
    term_sensitivity, splits = term_sensitivity_report(splits, selected, woe_maps)
    split_drift = enriched_split_drift_summary(metrics)
    logistic_calibration = logistic_calibration_by_decile(splits)
    woe_logistic_calibration = woe_logistic_calibration_by_decile(splits)
    formula_calibration = formula_calibration_by_decile(splits)
    calibration_compare = calibration_comparison(formula_calibration, logistic_calibration)
    three_model_calibration = three_model_calibration_comparison(
        formula_calibration,
        woe_logistic_calibration,
        logistic_calibration,
    )
    tail_review = tail_calibration_review(logistic_calibration)
    tail_recalibration_plan, recalibrated_pd_by_decile = tail_recalibration_outputs(logistic_calibration)
    recalibration_metrics = recalibration_before_after_metrics(splits, logistic_calibration)
    feature_csi = enriched_feature_csi(splits)
    score_shift = score_distribution_shift(splits)
    binning_quality = binning_quality_check(feature_iv)
    deciles = build_decile_report(splits["train_pre_2016"])

    sample_cols = [
        "id",
        "application_month",
        "bad_flag",
        "expanded_formula_decile",
        "expanded_formula_pd",
        "woe_logistic_scorecard_pd",
        "logistic_challenger_pd",
        *FORMULA_FEATURES,
    ]
    combined = pd.concat(splits.values(), ignore_index=True)
    combined[sample_cols].sample(n=min(100_000, len(combined)), random_state=42).to_csv(
        PROCESSED / "enriched_scorecard_challenger_sample.csv.gz",
        index=False,
        compression="gzip",
    )

    iv_summary = (
        feature_iv.groupby(["feature", "business_meaning"], as_index=False)
        .agg(iv_variable=("iv_variable", "max"), bins=("bin", "nunique"), accounts=("accounts", "sum"))
        .sort_values("iv_variable", ascending=False)
    )
    iv_summary["selected_for_formula"] = iv_summary["feature"].isin(selected["feature"])
    selection_rationale = feature_selection_rationale(iv_summary)
    feature_governance = feature_selection_governance(selection_rationale, binning_quality, feature_csi)
    corr_matrix, redundant_review = correlation_and_redundancy_review(splits, selected, woe_maps)
    monotonicity_review, woe_stability = woe_stability_review(splits, feature_iv)
    woe_logistic_sign_review = coefficient_sign_review(woe_logistic_coefficients)
    production_candidate_features = final_production_candidate_features(
        coarse_selected,
        coarse_feature_iv,
        benchmark_woe_logistic_sign_review,
        coarse_woe_stability,
        set(clean_selected["feature"]),
    )
    post_coarse_stack_performance = post_coarse_model_stack_performance(coarse_performance, metrics)
    mort_acc_sensitivity = woe_logistic_feature_sensitivity(
        coarse_splits,
        coarse_selected,
        coarse_woe_maps,
        coarse_feature_iv,
    )
    enriched_cutoffs = enriched_cutoff_strategy(splits)
    challenger_matrix = challenger_decision_matrix(metrics, tail_review, feature_csi)
    final_model_recommendation_table = final_model_recommendation(metrics, clean_exclusion_log)
    static_reports = static_governance_reports()
    bridge = population_bridge(base, metrics)

    write_reports(
        base,
        feature_iv,
        selected,
        metrics,
        deciles,
        pd_by_decile,
        bridge,
        term_sensitivity,
        split_drift,
        logistic_calibration,
        feature_csi,
        score_shift,
        binning_quality,
        selection_rationale,
        woe_logistic_coefficients,
        woe_logistic_points,
        woe_logistic_sign_review,
        benchmark_woe_logistic_coefficients,
        benchmark_woe_logistic_points,
        benchmark_woe_logistic_sign_review,
        clean_exclusion_log,
        formula_calibration,
        calibration_compare,
        woe_logistic_calibration,
        three_model_calibration,
        tail_review,
        tail_recalibration_plan,
        recalibrated_pd_by_decile,
        recalibration_metrics,
        coarse_log,
        coarse_iv,
        coarse_performance,
        post_coarse_stack_performance,
        mort_acc_sensitivity,
        coarse_woe_stability,
        production_candidate_features,
        final_model_recommendation_table,
        feature_governance,
        corr_matrix,
        redundant_review,
        monotonicity_review,
        woe_stability,
        enriched_cutoffs,
        challenger_matrix,
        static_reports,
    )
    write_risk_committee_memo(metrics, term_sensitivity, tail_review, challenger_matrix)
    plot_outputs(metrics, deciles, logistic_calibration, score_shift, three_model_calibration, recalibrated_pd_by_decile)
    print("Enriched scorecard challenger completed")
    print((REPORTS / "36_challenger_model_summary.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
