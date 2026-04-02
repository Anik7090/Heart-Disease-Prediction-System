# api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Single input schema - include the features your model expects.
class SingleInput(BaseModel):
    age: float
    gender: Any
    chestpain: int
    restingBP: float
    serumcholestrol: float
    fastingbloodsugar: int
    restingrelectro: int
    maxheartrate: float
    exerciseangia: int
    oldpeak: float
    slope: int
    noofmajorvessels: int

class BatchInput(BaseModel):
    records: List[SingleInput]

class PredictResponse(BaseModel):
    prediction: int
    probability: float

# New small model for top features in the explain response
class TopFeature(BaseModel):
    feature: str
    impact: float

class ExplainResponse(BaseModel):
    prediction: int
    probability: float
    contributions: Optional[Dict[str, float]]  # transformed feature -> shap
    base_value: Optional[float] = None
    aggregated: Optional[Dict[str, float]] = None  # aggregated feature -> contribution
    top_features: Optional[List[TopFeature]] = None  # list of { feature: str, impact: float }

class ModelInfoResponse(BaseModel):
    """
    Response for /model-info
    - cv_report: full cv_report.json (per-model CV scores) or null
    - eval_metrics: models/eval_results/metrics.json or null
    - messages: optional list of status messages
    """
    cv_report: Optional[Dict[str, Any]] = None
    eval_metrics: Optional[Dict[str, Any]] = None
    messages: Optional[List[str]] = None
