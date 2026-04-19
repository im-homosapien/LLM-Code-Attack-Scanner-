import subprocess
import sys


def run_step(label: str, command: list[str]) -> None:
    print(f"\n=== {label} ===")
    subprocess.run(command, check=True)


def main() -> None:
    py = sys.executable
    run_step("Scanner Classification Metrics", [py, "pipeline.py"])
    run_step("LLM Defense Metrics", [py, "evaluation_llm.py"])
    run_step("Plot Graphs", [py, "plot_results.py"])
    print("\nAll steps completed.")


if __name__ == "__main__":
    main()
