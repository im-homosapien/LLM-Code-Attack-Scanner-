# LLM-Code-Attack-Scanner

**Course**: CS4371/5378 – Computer Security  
**Paper**: Security Attacks on LLM-based Code Completion Tools  
**Link**: https://arxiv.org/pdf/2408.11006

## Project Description

We are reproducing the **Level II Code Embedded Attack** from the paper and building a simple **scanner** to detect hidden prompt injections in code.

## Current Status

- Basic lexical scanner implemented (`scanner.py`)
- Added multiple **attack files** to test suspicious embedded prompt patterns
- Added multiple **safe files** to test normal code and possible false positives
- Added `pipeline.py` to scan all test files and print both per-file results and evaluation metrics

## Files

- `scanner.py` → Main scanner that checks for Level II attack patterns
- `pipeline.py` → Runs the scanner on all files in `attacks/` and `safe/`, prints results, and computes evaluation metrics
- `attacks/` → Folder containing attack example files
- `safe/` → Folder containing safe example files

## Dataset Structure

Organize the files like this:

```text
project/
│── scanner.py
│── pipeline.py
│── attacks/
│   ├── attack_comment.py
│   ├── attack_concat.py
│   ├── attack_name.py
│   └── ...
│── safe/
│   ├── safe_math.py
│   ├── safe_loop.py
│   └── ...
```
All files inside:
- `attacks/` are treated as true label = `ATTACK`
- `safe/` are treated as true label = `SAFE`

## How to Run the Scanner

On Windows, if `python` is not on your PATH, use the **Python Launcher** (`py`):

```bash
# Test an attack file
py scanner.py attacks/attack_concat.py
```

If `python` works on your machine, you can use:

```bash
python scanner.py attacks/attack_concat.py
```

**Expected output example** (for `attack_concat.py`):

```text
ATTACK: Multiple string concatenations detected on line 3 (Level II style)
```

## How to Run the Full Pipeline

To scan every file in the `attacks/` and `safe/` folders and print the evaluation:

```bash
python pipeline.py
```

The pipeline will:
- read every file in `attacks/` and `safe/`
- run `scan_code()` on each file
- print the scanner result for each file
- compare the scanner result with the file’s true label
- print evaluation metrics

## Evaluation Metrics

The pipeline prints:
- **TP (True Positive)**: attack file correctly detected as `ATTACK`
- **TN (True Negative)**: safe file correctly detected as `SAFE`
- **FP (False Positive)**: safe file incorrectly flagged as `ATTACK`
- **FN (False Negative)**: attack file incorrectly missed as `SAFE`
- **Accuracy**
- **Precision**
- **Recall**
- **F1 Score**

These metrics help show how well the scanner performs, not just whether it works on one or two examples.

## Team Roles

| Member | Role |
|--------|------|
| Knowledge Neupane | Scanner development |
| Justin Le Nguyen | Creating more attack examples (20–30 files) |
| Anh Ngoc Nguyen | Ollama + CodeLlama setup + pipeline |
| Anuska Dhital | Evaluation and paper summary |
