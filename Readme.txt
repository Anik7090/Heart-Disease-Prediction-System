# Cardiovascular Disease Risk Prediction with Explainable AI

**A full-stack, production-ready ML web application** that predicts the risk of cardiovascular disease using state-of-the-art gradient boosting models (CatBoost, LightGBM, XGBoost) + classical algorithms. Automatically selects the best-performing model and delivers **SHAP-powered explanations** — both globally and per individual prediction.

Beautiful Next.js frontend • FastAPI backend • End-to-end pipeline

![Heart Health AI Demo](https://via.placeholder.com/1400x700/3b82f6/ffffff?text=Cardiovascular+Disease+Risk+Prediction+%E2%9C%A8)  
_Replace with your actual screenshot_

## Features

### Machine Learning

- Complete preprocessing pipeline (imputers, scalers, encoders)
- Supported models:
  - CatBoost • LightGBM • XGBoost
  - RandomForest • SVM • KNN • Logistic Regression
- Automatic best-model selection
- Randomized Cross-validation + Optuna hyperparameter tuning
- Full evaluation: ROC-AUC, Precision, Recall, F1, etc.
- SHAP explainability (global summary, bar plots, waterfall charts)

### FastAPI Backend

- `POST /predict` → Single prediction
- `POST /predict/batch` → Batch predictions
- `POST /predict/upload` → CSV upload & bulk prediction
- `POST /explain` → SHAP explanation for any record
- `GET /model-info` → JSON metrics & CV report
- `GET /model-info/ui` → Beautiful HTML performance dashboard
- Full CORS support

### Next.js Frontend (App Router + Tailwind + ShadCN)

- Responsive hero landing page with CTA
- Interactive medical checkup form
- Real-time validation using Zod + React Hook Form
- Dark / Light mode support
- Results display:
  - Risk prediction (Positive / Negative)
  - Probability percentage
  - Interactive SHAP feature contribution bars
  - Detailed contribution table
- Built with Next.js 15, TailwindCSS, ShadCN UI, Tabler Icons

## Project Structure

```bash
.
├── ml/                              # ML training & interpretation scripts
│   ├── preprocessing.py
│   ├── train.py
│   ├── evaluate.py
│   ├── compare_models.py
│   ├── interpret.py
│   ├── hyperparam_search.py
│   └── data/
│       └── Cardiovascular_Disease_Dataset.csv   # Place dataset here
│
├── api/                             # FastAPI server
│   ├── api.py
│   ├── schemas.py
│   └── utils.py
│
├── models/                                 # Auto-generated as results of training+testing
│   ├── best_model_pipeline.joblib          # final winner model (backend api uses this model to predict)
│   ├── cv_report.json                      # performance metrics of top models.
│   ├── eval_results/                       #all files inside eval_results are generated after evauation (after runung evaluation.py)
│   ├───────── metrics.json                 # (final performance metric)
│   ├───────── feature_importances.csv      #(evaluated every feature or attribute impact on results)
│   ├───────── classification_report.json   #(performace reports)
│   ├───────── evaluation_summary.json      #summary
│   ├───────── confusion_matrix.png         #confusion_matrix (best model)
│   ├───────── pr_curve.png                 #pr_curve (best model)
│   ├───────── roc_curve.png                #roc_curve (best model)
│   ├── explain/                            #all files inside eval_results are generated after evauation (after runung interpret.py)
│   ├──                                     # contains images+html view of Shap evaluation or feauture importance with summary_plot.png
│   ├── hyperopt/                           # #all files inside eval_results are generated after evauation (after runung hyperparam_search.py)
│   └──                                     # contains hyperparameter tuning results or randomised CV results for each model
│
├── frontend/                               # Next.js frontend (rename from client-app if needed)
│   ├── app/
│   ├── components/
│   ├── public/
│   └── next.config.js
│
├── requirements.txt
├── README.md
└── LICENSE
```

### Setup (Go through instructions and cli commands)

## Create Virtual Environment

```bash
python3 -m venv .venv             # for python version 3.9 if any error try (python -m venv .venv )
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate           # Windows
```

## Install requirements

```bash
pip install -r requirements.txt
```

## Training

```bash
python -m ml.train \
 --data-path data/Cardiovascular_Disease_Dataset.csv \
 --target target \
 --output-dir models
```

# Outputs:

models/best_model_pipeline.joblib
Cross-validation report
Evaluation plots & metrics

# Evaluate

```bash
python -m ml.evaluate \
  --data-path data/Cardiovascular_Disease_Dataset.csv \
  --model-path models/best_model_pipeline.joblib \
  --output-dir models/eval_results \
  --target target \
  --test-size 0.2 \
  --random-state 42 \
  --id-column patientid
```

# Interpret Generate SHAP Explanations

SHAP (SHapley Additive exPlanations) explains individual predictions by computing the contribution of each feature.

```bash
python -m ml.interpret \
      --model-path models/best_model_pipeline.joblib \
      --data-path data/Cardiovascular_Disease_Dataset.csv \
      --target target \
      --output-dir models/explain \
      --max-background 200 \
      --n-samples 50
```

# Run FastAPI Server

```bash
uvicorn api.api:app --reload --port 8000
```

#Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Note

The project is fully compatible with macOS and Linux systems.
However, due to certain configurations or environment-specific differences, it may not be fully compatible with Windows in some cases.
