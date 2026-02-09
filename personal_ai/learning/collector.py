import csv
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
AUTO_DATA_PATH = BASE_DIR / "data" / "auto_intents.csv"
FIELDNAMES = ["text", "intent", "confidence", "source", "timestamp"]

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def log_sample(text: str, intent: str, confidence: float, source: str = "auto") -> None:
    text = _normalize(text or "")
    intent = _normalize(intent or "")
    if not text or not intent:
        return
    if len(text.split()) < 1:
        return

    AUTO_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = AUTO_DATA_PATH.exists()

    with AUTO_DATA_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "text": text.strip(),
                "intent": intent.strip(),
                "confidence": f"{confidence:.4f}",
                "source": source,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
