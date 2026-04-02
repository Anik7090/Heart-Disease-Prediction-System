#!/usr/bin/env python3
"""
ml/compare_models.py

Quick comparative evaluation script for saved model pipelines.

Place this file in the `ml/` folder. Run from project root:

Example usage:
  python -m ml.compare_models --data data/Cardiovascular_Disease_Dataset.csv --target target \
      --models "models/*.joblib" --out models/compare_results --test-size 0.2

Notes:
- Accepts glob patterns for --models.
- Models may be saved as a Pipeline directly or as a dict {'pipeline': ..., 'metadata': ...}.
- Produces:
    models/compare_results/compare_metrics.csv
    models/compare_results/roc_compare.png
    models/compare_results/pr_compare.png
    models/compare_results/<model_name>/confusion_matrix.png
    models/compare_results/<model_name>/classification_report.json
"""
import argparse
import glob
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
)
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")


def find_model_paths(patterns: List[str]) -> List[Path]:
    pths = []
    for pat in patterns:
        pths.extend([Path(p) for p in glob.glob(pat)])
    pths = sorted(set(pths))
    return [p for p in pths if p.exists()]


def load_joblib_model(path: Path):
    obj = joblib.load(path)
    if isinstance(obj, dict) and "pipeline" in obj:
        return obj["pipeline"], obj.get("metadata", {})
    return obj, {}


def safe_proba(model, X) -> np.ndarray:
    """Return probability estimates for the positive class if possible, else None."""
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)
        if probs.ndim == 2 and probs.shape[1] >= 2:
            return np.asarray(probs)[:, 1]
        return np.asarray(probs).ravel()
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        # map to probability-like [0,1] via sigmoid
        try:
            probs = 1 / (1 + np.exp(-scores))
            return probs
        except Exception:
            return None
    return None


def ensure_features_order(X: pd.DataFrame, metadata: Dict[str, Any]) -> pd.DataFrame:
    features = metadata.get("features")
    if features:
        # keep only features that exist in X, and follow the metadata order
        cols_present = [c for c in features if c in X.columns]
        if len(cols_present) > 0:
            # return a new frame with these columns; if others needed, they are ignored
            return X[cols_present].copy()
    return X.copy()


def plot_roc(all_info: List[Dict[str, Any]], outpath: Path):
    plt.figure(figsize=(8, 6))
    plotted = False
    for info in all_info:
        probs = info.get("probs")
        y = info["y"]
        name = info["name"]
        if probs is None:
            continue
        try:
            fpr, tpr, _ = roc_curve(y, probs)
            auc = roc_auc_score(y, probs)
            plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", linewidth=2)
            plotted = True
        except Exception:
            continue
    if not plotted:
        # nothing to plot
        return
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC curve comparison")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def plot_pr(all_info: List[Dict[str, Any]], outpath: Path):
    plt.figure(figsize=(8, 6))
    plotted = False
    for info in all_info:
        probs = info.get("probs")
        y = info["y"]
        name = info["name"]
        if probs is None:
            continue
        try:
            prec, rec, _ = precision_recall_curve(y, probs)
            ap = average_precision_score(y, probs)
            plt.plot(rec, prec, label=f"{name} (AP={ap:.3f})", linewidth=2)
            plotted = True
        except Exception:
            continue
    if not plotted:
        return
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall comparison")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def plot_confusion(cm: np.ndarray, classes: List[Any], outpath: Path, title: str = "Confusion Matrix"):
    plt.figure(figsize=(4, 3.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def evaluate_models(
    data_csv: Path,
    target: str,
    model_patterns: List[str],
    out_dir: Path,
    test_size: float = 0.0,
    random_state: int = 42,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_csv)
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in CSV.")

    X = df.drop(columns=[target])
    y = df[target].astype(int)

    # split if requested
    if test_size and test_size > 0.0:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y if len(y.unique())>1 else None
        )
        X_eval = X_test
        y_eval = y_test
    else:
        X_eval = X
        y_eval = y

    model_paths = find_model_paths(model_patterns)
    if not model_paths:
        raise ValueError(f"No model files matched patterns: {model_patterns}")

    results = []
    all_info = []

    for mp in model_paths:
        try:
            model_obj, metadata = load_joblib_model(mp)
        except Exception as e:
            print(f"Skipping {mp} — failed to load: {e}")
            continue

        name = mp.stem
        print(f"Evaluating model: {name}")

        X_in = ensure_features_order(X_eval, metadata)

        # predictions
        try:
            y_pred = model_obj.predict(X_in)
        except Exception as e:
            print(f"Model {name} failed to predict: {e}")
            continue

        probs = safe_proba(model_obj, X_in)

        # metrics
        acc = accuracy_score(y_eval, y_pred)
        prec = precision_score(y_eval, y_pred, zero_division=0)
        rec = recall_score(y_eval, y_pred, zero_division=0)
        f1 = f1_score(y_eval, y_pred, zero_division=0)

        roc_auc = None
        avg_prec = None
        if probs is not None and len(np.unique(y_eval)) == 2:
            try:
                roc_auc = roc_auc_score(y_eval, probs)
            except Exception:
                roc_auc = None
            try:
                avg_prec = average_precision_score(y_eval, probs)
            except Exception:
                avg_prec = None

        cm = confusion_matrix(y_eval, y_pred)
        crep = classification_report(y_eval, y_pred, output_dict=True, zero_division=0)

        # save per-model artifacts
        model_out = out_dir / name
        model_out.mkdir(parents=True, exist_ok=True)
        # confusion matrix plot
        try:
            classes = sorted(list(np.unique(np.concatenate((y_eval.values, y_pred), axis=0))))
            plot_confusion(cm, classes, model_out / "confusion_matrix.png", title=f"{name} — Confusion Matrix")
        except Exception as e:
            print(f"Could not plot confusion for {name}: {e}")
        # save classification report
        with open(model_out / "classification_report.json", "w") as fh:
            json.dump(crep, fh, indent=2)

        results.append({
            "model": name,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": roc_auc,
            "avg_precision": avg_prec,
            "n_samples": int(len(y_eval))
        })

        all_info.append({"name": name, "probs": probs, "y": y_eval.values})

    # summary CSV
    df_res = pd.DataFrame(results).sort_values(by="roc_auc", ascending=False, na_position="last")
    df_res.to_csv(out_dir / "compare_metrics.csv", index=False)
    with open(out_dir / "compare_metrics.json", "w") as fh:
        json.dump(df_res.fillna("").to_dict(orient="records"), fh, indent=2)

    # combined plots
    try:
        plot_roc(all_info, out_dir / "roc_compare.png")
    except Exception as e:
        print("Failed to plot combined ROC:", e)
    try:
        plot_pr(all_info, out_dir / "pr_compare.png")
    except Exception as e:
        print("Failed to plot combined PR:", e)

    print("Done. Artifacts saved to:", out_dir)
    print("Summary CSV:", out_dir / "compare_metrics.csv")


def main():
    parser = argparse.ArgumentParser(description="Compare saved ML pipelines on a dataset.")
    parser.add_argument("--data", required=True, help="CSV dataset path")
    parser.add_argument("--target", required=True, help="Target column name")
    parser.add_argument("--models", required=True, nargs="+", help="Model path patterns (glob allowed), e.g. models/*.joblib")
    parser.add_argument("--out", default="models/compare_results", help="Output directory for results")
    parser.add_argument("--test-size", type=float, default=0.0, help="Optional test split fraction (0-1). If 0, evaluate on full data.")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    model_patterns = args.models
    evaluate_models(data_path, args.target, model_patterns, Path(args.out), test_size=args.test_size, random_state=args.random_state)


if __name__ == "__main__":
    main()
