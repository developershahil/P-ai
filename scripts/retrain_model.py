"""Simple retraining pipeline entrypoint."""

from personal_ai.learning.trainer import train_and_compare


if __name__ == "__main__":
    result = train_and_compare()
    print("Retraining result:")
    for key, value in result.items():
        print(f"- {key}: {value}")
