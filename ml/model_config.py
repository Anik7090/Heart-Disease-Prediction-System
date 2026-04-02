# ml/model_config.py
from typing import Dict
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

RANDOM_SEED = 42

def get_models(random_state: int = RANDOM_SEED) -> Dict[str, object]:
    """
    Return a dict of model_name -> sklearn-compatible estimator instances.
    These are sensible defaults; tune hyperparams separately if desired.
    """
    models = {
        "xgboost": xgb.XGBClassifier(eval_metric='logloss', random_state=random_state, n_jobs=-1),
        "lightgbm": lgb.LGBMClassifier(random_state=random_state, n_jobs=-1, verbose=-1),
        "catboost": CatBoostClassifier(random_state=random_state, logging_level="Silent"),
        "random_forest": RandomForestClassifier(random_state=random_state, n_jobs=-1),
        "svm": SVC(probability=True, random_state=random_state),
        "knn": KNeighborsClassifier()
    }
    return models
