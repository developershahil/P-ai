from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from .trainer import _normalize, DATA_PATH


def evaluate_model(model_path: Path) -> dict:
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["text"].astype(str).apply(_normalize)
    df["intent"] = df["intent"].astype(str)
    model = joblib.load(model_path)
    pred = model.predict(df["text"])
    labels = sorted(set(df["intent"]) | set(pred))
    return {
        "accuracy": float(accuracy_score(df["intent"], pred)),
        "f1_macro": float(f1_score(df["intent"], pred, average="macro")),
        "labels": labels,
        "confusion_matrix": confusion_matrix(df["intent"], pred, labels=labels).tolist(),
    }
