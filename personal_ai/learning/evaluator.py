from pathlib import Path

import joblib
import pandas as pd

from .trainer import _normalize, DATA_PATH

def evaluate_model(model_path: Path) -> float:
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["text"].astype(str).apply(_normalize)
    df["intent"] = df["intent"].astype(str)
    model = joblib.load(model_path)
    return float(model.score(df["text"], df["intent"]))
