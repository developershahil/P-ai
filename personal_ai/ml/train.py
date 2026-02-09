import re
from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import cross_val_score
import numpy as np
import joblib

# --------- Load & clean data ----------
BASE_DIR = Path(__file__).resolve().parents[1]
data_path = BASE_DIR / "data" / "intents.csv"
df = pd.read_csv(data_path)

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)  # remove symbols
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["text"] = df["text"].astype(str).apply(normalize)

X = df["text"]
y = df["intent"].astype(str)

# --------- Features ----------
features = FeatureUnion([
    ("word", TfidfVectorizer(
        ngram_range=(1, 3),          # wider context
        min_df=1,
        sublinear_tf=True,           # log scaling
        strip_accents="unicode"
    )),
    ("char", TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 6),          # better typo handling
        sublinear_tf=True
    )),
])

# --------- Class weights ----------
classes = np.unique(y)
weights = compute_class_weight(class_weight="balanced", classes=classes, y=y)
class_weight = dict(zip(classes, weights))

# --------- Model ----------
clf = LogisticRegression(
    max_iter=4000,
    C=2.0,              # a bit less regularization (can try 1.0–3.0)
    n_jobs=None
)

model = Pipeline([
    ("features", features),
    ("clf", clf)
])

# --------- Evaluate (quick sanity check) ----------
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"📊 CV Accuracy: {scores.mean():.3f} ± {scores.std():.3f}")

# --------- Train full model ----------
model.fit(X, y)

# --------- Save ----------
model_dir = BASE_DIR / "models"
model_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_dir / "intent_model.pkl")
print("✅ Trained with improved normalization + n-grams + class weights")
