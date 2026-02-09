import os
import time

from .trainer import train_and_compare

DAY_SECONDS = 24 * 60 * 60

def run_daily_loop() -> None:
    run_once = os.getenv("RUN_ONCE", "0").lower() in {"1", "true", "yes"}
    while True:
        result = train_and_compare()
        print(f"Daily training result: {result}")
        if run_once:
            break
        time.sleep(DAY_SECONDS)

if __name__ == "__main__":
    run_daily_loop()
