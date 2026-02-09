import csv
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
AUTO_DATA_PATH = BASE_DIR / "data" / "auto_intents.csv"
FIELDNAMES = ["text", "intent", "confidence", "source", "timestamp"]

def log_sample(text: str, intent: str, confidence: float, source: str = "auto") -> None:
    if not text or not intent:
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
