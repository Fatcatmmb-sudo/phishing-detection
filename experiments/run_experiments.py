
"""Run phishing URL model experiments reproducibly.

Uses train.csv for fitting, validation.csv for all comparisons and model choice,
then evaluates the selected full-feature model once on test.csv.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
FEATURES = json.loads((ARTIFACTS / "features.json").read_text(encoding="utf-8"))

LABEL = "type"
SEED = 42
POSITIVE = "phishing"


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    url = frame["normalized_url"].fillna("").astype(str)
    host = frame["hostname"].fillna("").astype(str)

    return pd.DataFrame(
        {
            "url_length": url.str.len(),
            "hostname_length": host.str.len(),
            "dot_count": url.str.count(r"\."),
            "hyphen_count": url.str.count("-"),
            "digit_count": url.str.count(r"\d"),
            "at_count": url.str.count("@"),
            "slash_count": url.str.count("/"),
            "question_count": url.str.count(r"\?"),
            "equal_count": url.str.count("="),
            "has_https": url.str.lower().str.startswith("https://").astype("int8"),
        },
        index=frame.index,
    )[FEATURES]


def metrics(model, x_train, y_train, x_val, y_val):
    train_pred = model.predict(x_train)
    val_pred = model.predict(x_val)

    return {
        "tree_depth": model.get_depth() if hasattr(model, "get_depth") else "",
        "train_accuracy": accuracy_score(y_train, train_pred),
        "val_accuracy": accuracy_score(y_val, val_pred),
        "val_precision": precision_score(
            y_val, val_pred, pos_label=POSITIVE, zero_division=0
        ),
        "val_recall": recall_score(
            y_val, val_pred, pos_label=POSITIVE, zero_division=0
        ),
        "val_f1": f1_score(
            y_val, val_pred, pos_label=POSITIVE, zero_division=0
        ),
    }


def main():
    train = pd.read_csv(DATA / "train.csv")
    val = pd.read_csv(DATA / "validation.csv")
    test = pd.read_csv(DATA / "test.csv")

    y_train = train[LABEL]
    y_val = val[LABEL]

    x_train = make_features(train)
    x_val = make_features(val)

    records = []
    fitted = {}

    def run(name, model, columns=None, group=""):
        cols = columns if columns is not None else FEATURES

        model.fit(x_train[cols], y_train)

        row = {
            "experiment_id": "",
            "model": type(model).__name__,
            "features": len(cols),
            "random_state": SEED,
            "max_depth": getattr(model, "max_depth", "") or "",
            **metrics(model, x_train[cols], y_train, x_val[cols], y_val),
            "notes": name if not group else f"{group}: {name}",
        }

        records.append(row)
        fitted[name] = (model, cols)

        print(
            f"{name}: "
            f"F1={row['val_f1']:.4f}, "
            f"Recall={row['val_recall']:.4f}, "
            f"Precision={row['val_precision']:.4f}, "
            f"TrainAcc={row['train_accuracy']:.4f}",
            flush=True,
        )

    # EXP001: baseline reference.
    run(
        "EXP001 baseline reference",
        DecisionTreeClassifier(random_state=SEED),
    )

    # Group 2: change one tree-complexity parameter at a time.
    for name, params in [
        ("max_depth=10", {"max_depth": 10}),
        ("max_depth=15", {"max_depth": 15}),
        ("max_depth=20", {"max_depth": 20}),
        ("min_samples_split=10", {"min_samples_split": 10}),
        ("min_samples_split=50", {"min_samples_split": 50}),
        ("min_samples_leaf=5", {"min_samples_leaf": 5}),
        ("min_samples_leaf=20", {"min_samples_leaf": 20}),
    ]:
        run(
            name,
            DecisionTreeClassifier(random_state=SEED, **params),
            group="overfitting",
        )

    # Group 3: compare the default tree with balanced class weights.
    run(
        "class_weight=balanced",
        DecisionTreeClassifier(
            random_state=SEED,
            class_weight="balanced",
        ),
        group="class imbalance",
    )

    # Group 4: one-feature-group models and leave-one-group-out ablations.
    groups = {
        "length": ["url_length", "hostname_length"],
        "host_shape": ["dot_count", "hyphen_count"],
        "special_chars": [
            "digit_count",
            "at_count",
            "slash_count",
            "question_count",
            "equal_count",
        ],
        "protocol": ["has_https"],
    }

    for group, columns in groups.items():
        run(
            f"only_{group}",
            DecisionTreeClassifier(random_state=SEED),
            columns,
            "feature group only",
        )

        remaining = [c for c in FEATURES if c not in columns]

        run(
            f"without_{group}",
            DecisionTreeClassifier(random_state=SEED),
            remaining,
            "feature group removed",
        )

    # Group 5: compare classifiers on the same ten features.
    rf = RandomForestClassifier(
        n_estimators=120,
        min_samples_leaf=2,
        class_weight=None,
        n_jobs=-1,
        random_state=SEED,
    )

    run("RandomForest 120 trees, min_samples_leaf=2", rf)

    # Group 5.1: test RandomForest without HTTPS.
    rf_without_https = RandomForestClassifier(
        n_estimators=120,
        min_samples_leaf=2,
        class_weight=None,
        n_jobs=-1,
        random_state=SEED,
    )

    features_without_https = [
        feature for feature in FEATURES
        if feature != "has_https"
    ]

    if len(features_without_https) != len(FEATURES) - 1:
        raise ValueError("Could not remove exactly one has_https feature.")

    run(
        "RandomForest without has_https",
        rf_without_https,
        columns=features_without_https,
        group="HTTPS ablation",
    )

    # Group 6: LinearSVC comparison on the same ten features.
    svc = make_pipeline(
        StandardScaler(),
        LinearSVC(
            class_weight=None,
            random_state=SEED,
            max_iter=5000,
            dual="auto",
        ),
    )

    run("LinearSVC with StandardScaler", svc)

    # Append only new experiments; preserve existing experiment history.
    log_path = EXPERIMENTS / "experiment_log.csv"
    old = pd.read_csv(log_path)

    existing_notes = set(
        old.get("notes", pd.Series(dtype=str)).astype(str)
    )

    existing_ids = (
        old["experiment_id"]
        .dropna()
        .astype(str)
        .str.extract(r"EXP(\d+)")[0]
        .dropna()
        .astype(int)
    )

    next_id = (
        int(existing_ids.max()) + 1
        if not existing_ids.empty
        else 1
    )

    new_rows = []

    for row in records:
        if row["notes"] in existing_notes:
            continue

        row["experiment_id"] = f"EXP{next_id:03d}"
        next_id += 1
        new_rows.append(row)

    if new_rows:
        updated_log = pd.concat(
            [old, pd.DataFrame(new_rows)],
            ignore_index=True,
        )
        updated_log.to_csv(log_path, index=False)

        print(
            f"\nAdded {len(new_rows)} new experiment(s) to experiment_log.csv",
            flush=True,
        )
    else:
        print("\nNo new experiments to append.", flush=True)

    all_results = pd.read_csv(log_path)

    all_results.to_csv(
        ROOT / "reports" / "results_summary.csv",
        index=False,
    )

    # Select only full-feature, probability-capable models, with high phishing
    # recall as a floor; ranking uses validation F1.
    # The 9-feature HTTPS ablation is deliberately excluded from deployment.
    eligible = [
        "EXP001 baseline reference",
        "max_depth=10",
        "max_depth=15",
        "max_depth=20",
        "min_samples_split=10",
        "min_samples_split=50",
        "min_samples_leaf=5",
        "min_samples_leaf=20",
        "class_weight=balanced",
        "RandomForest 120 trees, min_samples_leaf=2",
    ]

    scored = []

    for name in eligible:
        model, cols = fitted[name]

        row = next(
            r for r in records
            if r["notes"] == name
            or r["notes"].endswith(f": {name}")
        )

        scored.append((name, row))

    high_recall = [
        item for item in scored
        if item[1]["val_recall"] >= 0.95
    ]

    winner_name, winner_row = max(
        high_recall or scored,
        key=lambda item: item[1]["val_f1"],
    )

    winner, winner_cols = fitted[winner_name]

    if winner_cols != FEATURES or not hasattr(winner, "predict_proba"):
        raise RuntimeError(
            "Selected model is not compatible with the API feature/probability contract."
        )

    # One final holdout evaluation after model selection.
    x_test = make_features(test)
    y_test = test[LABEL]

    test_pred = winner.predict(x_test[FEATURES])

    final = {
        "selected_experiment": winner_name,
        "selection_rule": (
            "highest validation F1 among full-feature predict_proba "
            "models with phishing recall >= 0.95"
        ),
        "validation": {
            key: float(winner_row[key])
            for key in (
                "val_accuracy",
                "val_precision",
                "val_recall",
                "val_f1",
            )
        },
        "test": {
            "accuracy": float(accuracy_score(y_test, test_pred)),
            "precision_phishing": float(
                precision_score(
                    y_test,
                    test_pred,
                    pos_label=POSITIVE,
                    zero_division=0,
                )
            ),
            "recall_phishing": float(
                recall_score(
                    y_test,
                    test_pred,
                    pos_label=POSITIVE,
                    zero_division=0,
                )
            ),
            "f1_phishing": float(
                f1_score(
                    y_test,
                    test_pred,
                    pos_label=POSITIVE,
                    zero_division=0,
                )
            ),
        },
    }

    (ROOT / "reports" / "final_evaluation.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    joblib.dump(winner, ARTIFACTS / "selected_model.joblib")

    print("\nSELECTED:", winner_name, flush=True)
    print(json.dumps(final, ensure_ascii=False, indent=2), flush=True)
    print(
        "Saved artifacts/selected_model.joblib and reports/final_evaluation.json",
        flush=True,
    )


if __name__ == "__main__":
    main()
