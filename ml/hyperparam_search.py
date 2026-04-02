# ml/hyperparam_search.py
"""
Hyperparameter tuning (randomized) for tree models.

Saves top-k models and cv results per model into `output_dir/hyperopt/<model_name>/`.

Usage example (from project root):
python -m ml.hyperparam_search \
    --data-path data/Cardiovascular_Disease_Dataset.csv \
    --target target \
    --output-dir models \
    --n-iter 30 \
    --cv 4 \
    --n-jobs -1 \
    --top-k 3

Notes:
- Defaults are conservative. Increase --n-iter for better search at cost of runtime.
- Requires ml.preprocessing.build_preprocessor and ml.model_config.get_models to exist.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import time
import warnings
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from scipy.stats import randint, uniform, loguniform
from ml.preprocessing import build_preprocessor, infer_feature_groups
import ml.model_config as model_config
from ml.utils import save_json

# Silence noisy warnings in search
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
warnings.filterwarnings("ignore", category=UserWarning)

RND = 42

def default_param_spaces():
    """
    Return a dict mapping model_key -> param_distributions for RandomizedSearchCV.
    These are intentionally compact but meaningful.
    """
    spaces = {
        "xgboost": {
            # param names are for 'clf__<param>' when used in pipeline
            "clf__n_estimators": randint(50, 500),
            "clf__max_depth": randint(3, 12),
            "clf__learning_rate": uniform(0.01, 0.4),
            "clf__subsample": uniform(0.6, 0.4),
            "clf__colsample_bytree": uniform(0.5, 0.5),
            "clf__reg_alpha": uniform(0.0, 1.0),
            "clf__reg_lambda": uniform(0.0, 1.0),
        },
        "lightgbm": {
            "clf__n_estimators": randint(50, 500),
            "clf__num_leaves": randint(16, 128),
            "clf__learning_rate": uniform(0.01, 0.4),
            "clf__subsample": uniform(0.6, 0.4),
            "clf__colsample_bytree": uniform(0.5, 0.5),
            "clf__reg_alpha": uniform(0.0, 1.0),
            "clf__reg_lambda": uniform(0.0, 1.0),
        },
        "catboost": {
            # CatBoost's sklearn wrapper uses same param names
            "clf__iterations": randint(50, 500),
            "clf__depth": randint(3, 10),
            "clf__learning_rate": uniform(0.01, 0.4),
            "clf__l2_leaf_reg": uniform(1, 10),
            "clf__border_count": randint(32, 255),
        },
        "random_forest": {
            "clf__n_estimators": randint(50, 500),
            "clf__max_depth": randint(3, 30),
            "clf__min_samples_split": randint(2, 10),
            "clf__min_samples_leaf": randint(1, 6),
            "clf__max_features": ["sqrt", "log2", None],
        }
    }
    return spaces


def run_search_for_model(model_name, pipeline, param_dist, X, y, n_iter=30, cv=4, n_jobs=-1, random_state=RND):
    """
    Run RandomizedSearchCV and return fitted RandomizedSearchCV object.
    """
    print(f"\nStarting RandomizedSearchCV for {model_name} — n_iter={n_iter}, cv={cv}")
    cv_split = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    rs = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="roc_auc",
        n_jobs=n_jobs,
        cv=cv_split,
        random_state=random_state,
        verbose=1,
        return_train_score=False
    )
    t0 = time.time()
    rs.fit(X, y)
    dt = time.time() - t0
    print(f"Search for {model_name} done in {dt:.1f}s — best score: {rs.best_score_:.6f}")
    return rs


def save_top_k_search(rs: RandomizedSearchCV, X, y, output_dir: Path, top_k: int = 1):
    """
    Save best pipeline (refit) and top_k candidate pipelines (refit on full X/y).
    - rs is fitted RandomizedSearchCV with refit=True (it will already have best_estimator_ refit on full)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    # Save full cv_results (json-serializable conversion)
    cvres = rs.cv_results_.copy()
    # Convert numpy arrays to lists
    cvres_s = {}
    for k, v in cvres.items():
        try:
            cvres_s[k] = v.tolist() if hasattr(v, "tolist") else v
        except Exception:
            cvres_s[k] = str(v)
    save_json(cvres_s, output_dir / "cv_results.json")

    # Save best estimator pipeline (rs.best_estimator_ is already refit on full X when refit=True)
    best_pipeline = rs.best_estimator_
    joblib.dump(best_pipeline, output_dir / "best_pipeline.joblib")

    # Save metadata summary (top_k by rank)
    ranks = np.argsort(cvres["rank_test_score"])
    top_k = min(top_k, len(ranks))
    summary = []
    for i in range(top_k):
        idx = ranks[i]
        entry = {
            "rank": int(cvres["rank_test_score"][idx]),
            "mean_test_score": float(cvres["mean_test_score"][idx]),
            "std_test_score": float(cvres["std_test_score"][idx]),
            "params": {k.replace("clf__", ""): (v[idx].item() if hasattr(v[idx], "item") else (v[idx] if not isinstance(v[idx], (list, np.ndarray)) else v[idx].tolist())) for k, v in cvres.items() if k.startswith("params")}
        }
        summary.append(entry)

    save_json(summary, output_dir / "top_k_models.json")

    # save each top-k as separate refit pipeline (we must reconstruct from params and fit on full data)
    # Note: RandomizedSearchCV provides param_distributions results but does not keep the actual estimator objects for all candidates.
    # We will refit pipelines for top_k parameter sets from cv_results_['params'].
    for i in range(top_k):
        idx = ranks[i]
        params = cvres["params"][idx]
        # create clone from best estimator and set params
        from sklearn.base import clone
        base = rs.best_estimator_
        candidate = clone(base)
        candidate.set_params(**params)
        candidate.fit(X, y)
        joblib.dump(candidate, output_dir / f"pipeline_rank_{i+1}.joblib")

    print(f"Saved top-{top_k} artifacts into {output_dir}")


def main(args):
    data_path = Path(args.data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Data path not found: {data_path}")

    df = pd.read_csv(data_path)
    if args.id_column and args.id_column in df.columns:
        df = df.drop(columns=[args.id_column])

    if args.target not in df.columns:
        raise ValueError(f"Target '{args.target}' not in dataset columns")

    X = df.drop(columns=[args.target])
    y = df[args.target]

    numeric_feats, categorical_feats = infer_feature_groups(list(X.columns), numeric_hints=None)
    preprocessor = build_preprocessor(numeric_feats, categorical_feats)

    # Prepare models from model_config (we'll only tune a subset)
    all_models = model_config.get_models(random_state=args.random_state)
    tune_models_keys = ["xgboost", "lightgbm", "catboost", "random_forest"]
    param_spaces = default_param_spaces()

    out_base = Path(args.output_dir) / "hyperopt"
    out_base.mkdir(parents=True, exist_ok=True)

    for key in tune_models_keys:
        if key not in all_models:
            print(f"Skipping {key} (not found in model registry).")
            continue
        clf = all_models[key]
        # For CatBoost, ensure silent training
        if key == "catboost":
            try:
                clf.set_params(logging_level="Silent")
            except Exception:
                pass

        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("clf", clf)])
        ps = param_spaces.get(key, {})
        if len(ps) == 0:
            print(f"No param space for {key}, skipping search.")
            continue

        rs = run_search_for_model(key, pipeline, ps, X, y, n_iter=args.n_iter, cv=args.cv, n_jobs=args.n_jobs, random_state=args.random_state)

        model_out_dir = out_base / key
        save_top_k_search(rs, X, y, model_out_dir, top_k=args.top_k)

        # save brief report
        report = {
            "model": key,
            "best_score": float(rs.best_score_),
            "best_params": {k.replace("clf__", ""): v for k, v in rs.best_params_.items()}
        }
        save_json(report, model_out_dir / "summary.json")

    print("Hyperparameter search finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, default="../data/Cardiovascular_Disease_Dataset.csv")
    parser.add_argument("--target", type=str, default="target")
    parser.add_argument("--id-column", type=str, default="patientid")
    parser.add_argument("--output-dir", type=str, default="../models")
    parser.add_argument("--n-iter", type=int, default=30, help="RandomizedSearchCV n_iter")
    parser.add_argument("--cv", type=int, default=4, help="CV folds")
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--top-k", type=int, default=3, help="Save top-k refit models")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()
    main(args)
