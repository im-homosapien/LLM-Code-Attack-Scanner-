# LLM-Code-Attack-Scanner

**Course**: CS4371/5378 – Computer Security  
**Paper**: Security Attacks on LLM-based Code Completion Tools  
**Link**: https://arxiv.org/pdf/2408.11006

## Project Description

We are reproducing the **Level II Code Embedded Attack** from the paper and building a simple **scanner** to detect hidden prompt injections in code.

## Current Status

- Basic lexical scanner implemented (`scanner.py`)
- 3 example attack files created and tested successfully
- Scanner correctly detects attacks (string concatenation, suspicious comments, bad keywords, suspicious names)

## Files

- `scanner.py` → Main scanner that checks for Level II attack patterns
- `attacks/` → Folder containing attack example files
  - `attack_concat.py`
  - `attack_comment.py`
  - `attack_name.py`

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

## Team Roles

| Member | Role |
|--------|------|
| Knowledge Neupane | Scanner development |
| Justin Le Nguyen | Creating more attack examples (20–30 files) |
| Anh Ngoc Nguyen | Ollama + CodeLlama setup + pipeline |
| Anuska Dhital | Evaluation and paper summary |
