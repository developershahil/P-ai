import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.utils.class_weight import compute_class_weight

from personal_ai.core.config import SETTINGS

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "intents.csv"
AUTO_DATA_PATH = BASE_DIR / "data" / "auto_intents.csv"
MODEL_DIR = BASE_DIR / "models"
CURRENT_MODEL = MODEL_DIR / "intent_model.pkl"
BACKUP_MODEL = MODEL_DIR / "intent_model.backup.pkl"
CANDIDATE_MODEL = MODEL_DIR / "intent_model.candidate.pkl"
METRICS_PATH = MODEL_DIR / "model_metrics.json"
VERSION_PATH = MODEL_DIR / "model_version.json"


@dataclass
class TrainingResult:
    accuracy: float
    f1_macro: float
    confusion_matrix: list
    labels: list[str]
    model_path: Path


def _normalize(text: str) -> str:
    text = text.lower()
    text = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(text.split())


def _load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["text"].astype(str).apply(_normalize)
    df["intent"] = df["intent"].astype(str).str.strip()

    if AUTO_DATA_PATH.exists():
        auto_df = pd.read_csv(AUTO_DATA_PATH)
        if {"text", "intent"}.issubset(auto_df.columns):
            auto_df = auto_df.copy()
            if "confidence" in auto_df.columns:
                auto_df = auto_df[auto_df["confidence"].astype(float) >= SETTINGS.auto_learn_min_conf]
            auto_df["text"] = auto_df["text"].astype(str).apply(_normalize)
            auto_df["intent"] = auto_df["intent"].astype(str).str.strip()
            auto_df = auto_df[["text", "intent"]]
            df = pd.concat([df, auto_df], ignore_index=True)

    return df.dropna(subset=["text", "intent"]).drop_duplicates()


def _build_model(class_weight: dict) -> Pipeline:
    features = FeatureUnion(
        [
            ("word", TfidfVectorizer(ngram_range=(1, 3), min_df=1, sublinear_tf=True, strip_accents="unicode")),
            ("char", TfidfVectorizer(analyzer="char", ngram_range=(3, 6), sublinear_tf=True)),
        ]
    )
    clf = LogisticRegression(max_iter=4000, C=2.0, n_jobs=None, class_weight=class_weight)
    return Pipeline([("features", features), ("clf", clf)])


def _train_candidate() -> TrainingResult:
    df = _load_dataset()
    if df.empty:
        raise ValueError("Training data is empty.")

    X = df["text"]
    y = df["intent"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SETTINGS.model_random_state, stratify=y
    )
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight = dict(zip(classes, weights))
    model = _build_model(class_weight)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = float(accuracy_score(y_test, predictions))
    f1_macro = float(f1_score(y_test, predictions, average="macro"))
    labels = sorted(set(y_test) | set(predictions))
    matrix = confusion_matrix(y_test, predictions, labels=labels).tolist()

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, CANDIDATE_MODEL)
    return TrainingResult(
        accuracy=accuracy,
        f1_macro=f1_macro,
        confusion_matrix=matrix,
        labels=labels,
        model_path=CANDIDATE_MODEL,
    )


def _load_model(path: Path) -> Pipeline | None:
    if not path.exists():
        return None
    return joblib.load(path)


def _evaluate_model(model: Pipeline, X_test: pd.Series, y_test: pd.Series) -> tuple[float, float]:
    pred = model.predict(X_test)
    return float(accuracy_score(y_test, pred)), float(f1_score(y_test, pred, average="macro"))


def _write_metrics(best_accuracy: float, best_f1: float, candidate: TrainingResult) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "best_accuracy": best_accuracy,
        "best_f1_macro": best_f1,
        "candidate_accuracy": candidate.accuracy,
        "candidate_f1_macro": candidate.f1_macro,
        "labels": candidate.labels,
        "confusion_matrix": candidate.confusion_matrix,
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_version(promoted: bool) -> dict:
    prior = {"version": 0}
    if VERSION_PATH.exists():
        try:
            prior = json.loads(VERSION_PATH.read_text(encoding="utf-8"))
        except Exception:
            prior = {"version": 0}

    version = int(prior.get("version", 0)) + (1 if promoted else 0)
    payload = {
        "version": version,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "model_file": CURRENT_MODEL.name,
    }
    VERSION_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def train_and_compare() -> dict:
    df = _load_dataset()
    if df.empty:
        raise ValueError("Training data is empty.")

    X = df["text"]
    y = df["intent"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SETTINGS.model_random_state, stratify=y
    )

    candidate_result = _train_candidate()
    candidate_model = joblib.load(candidate_result.model_path)
    candidate_accuracy, candidate_f1 = _evaluate_model(candidate_model, X_test, y_test)

    existing_model = _load_model(CURRENT_MODEL)
    if existing_model is None:
        CURRENT_MODEL.write_bytes(candidate_result.model_path.read_bytes())
        _write_metrics(best_accuracy=candidate_accuracy, best_f1=candidate_f1, candidate=candidate_result)
        version = _write_version(promoted=True)
        return {
            "action": "promoted",
            "candidate_accuracy": candidate_accuracy,
            "candidate_f1_macro": candidate_f1,
            "best_accuracy": candidate_accuracy,
            "best_f1_macro": candidate_f1,
            "version": version["version"],
        }

    existing_accuracy, existing_f1 = _evaluate_model(existing_model, X_test, y_test)
    if (
        candidate_accuracy >= existing_accuracy + SETTINGS.model_improvement_threshold
        or candidate_f1 >= existing_f1 + SETTINGS.model_improvement_threshold
    ):
        BACKUP_MODEL.write_bytes(CURRENT_MODEL.read_bytes())
        CURRENT_MODEL.write_bytes(candidate_result.model_path.read_bytes())
        _write_metrics(best_accuracy=candidate_accuracy, best_f1=candidate_f1, candidate=candidate_result)
        version = _write_version(promoted=True)
        return {
            "action": "promoted",
            "candidate_accuracy": candidate_accuracy,
            "candidate_f1_macro": candidate_f1,
            "best_accuracy": candidate_accuracy,
            "best_f1_macro": candidate_f1,
            "version": version["version"],
        }

    _write_metrics(best_accuracy=existing_accuracy, best_f1=existing_f1, candidate=candidate_result)
    version = _write_version(promoted=False)
    return {
        "action": "kept",
        "candidate_accuracy": candidate_accuracy,
        "candidate_f1_macro": candidate_f1,
        "best_accuracy": existing_accuracy,
        "best_f1_macro": existing_f1,
        "version": version["version"],
    }


if __name__ == "__main__":
    result = train_and_compare()
    print(result)
