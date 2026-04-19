import json
import os

import matplotlib.pyplot as plt

OUTPUT_DIR = "results"
METRICS_PATH = os.path.join(OUTPUT_DIR, "latest_metrics.json")


def load_metrics() -> dict:
    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(
            f"Missing {METRICS_PATH}. Run 'py evaluation_llm.py' first."
        )
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metrics = load_metrics()

    labels = ["Without Scanner", "With Scanner"]
    asr_values = [
        metrics["without_scanner"]["asr_total"],
        metrics["with_scanner"]["asr_total"],
    ]
    block_values = [
        metrics["without_scanner"]["block_rate_attacks"],
        metrics["with_scanner"]["block_rate_attacks"],
    ]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, asr_values)
    plt.title("Attack Success Rate (ASR)")
    plt.ylabel("Rate")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "asr.png"), dpi=200)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.bar(labels, block_values)
    plt.title("Attack Block Rate")
    plt.ylabel("Rate")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "block_rate.png"), dpi=200)
    plt.close()

    print("Saved graphs:")
    print("- results/asr.png")
    print("- results/block_rate.png")


if __name__ == "__main__":
    main()