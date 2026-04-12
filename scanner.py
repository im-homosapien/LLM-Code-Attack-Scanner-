# scanner.py
# Lexical (non-AST) scanner for Level II code-embedded prompt / jailbreak patterns.
# Goals: catch obfuscated strings and risky phrasing while staying easy to explain.

from __future__ import annotations

import re
from typing import Callable, Iterable, Optional, Tuple

# --- Phrases that strongly suggest prompt injection / policy override (lowercased) ---
INJECTION_PHRASES: Tuple[str, ...] = (
    "developer mode",
    "ignore previous",
    "ignore all",
    "ignore earlier",
    "disregard previous",
    "jailbreak",
    "override safety",
    "override safeguards",
    "bypass safety",
    "bypass restrictions",
    "without restrictions",
    "no restrictions",
    "step by step",
    "step-by-step",
    "simulate an uncensored",
    "do anything now",
    "you are now",
    "new instructions",
    "system prompt",
)

# --- Standalone risky tokens / short phrases (lowercased) ---
DANGEROUS_KEYWORDS: Tuple[str, ...] = (
    "bomb",
    "weapon",
    "counterfeit",
    "poison",
    "malware",
    "exploit",
    "ransomware",
    "drug",
    "illegal",
    "kill",
    "hack",
    "jailbreak",
    "override",
)

# Instruction-like openers often used in harmful “how to” requests (lowercased).
# Used only inside comments/docstrings (not whole-file), to avoid benign code text.
INSTRUCTION_OPENERS: Tuple[str, ...] = (
    "how to",
    "how do i",
    "how can i",
    "make a",
    "make an",
    "produce a",
    "create a",
    "build a",
    "get a",
    "obtain a",
    "recipe for",
    "tutorial for",
    "walkthrough for",
)

# “complete the following” is common in homework; only treat as suspicious when
# the rest of the line does not look like a benign exercise description.
_COMPLETE_FOLLOWING_OK = re.compile(
    r"complete the following\s+(?:"
    r"exercise|assignment|homework|practice|problem|section|chapter|lesson|quiz"
    r")\b",
    re.IGNORECASE,
)

# Suspicious identifier / function names (word-boundary safe; avoids e.g. make_harmonic_series).
_SUSPICIOUS_NAME_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bmake_harm(?!onic)(?:ful|ing)?\b", re.IGNORECASE),
    re.compile(r"\bproduce_(?:weapon|counter|bomb|drug|poison)\w*\b", re.IGNORECASE),
    re.compile(r"\bcreate_(?:bomb|weapon|malware|virus|exploit)\w*\b", re.IGNORECASE),
    re.compile(r"\bhow_to_(?:harm|kill|hack|weapon|bomb|poison)\w*\b", re.IGNORECASE),
    re.compile(r"\bbypass_(?:safety|filter|policy|rules)\w*\b", re.IGNORECASE),
    re.compile(r"\bjailbreak_\w+", re.IGNORECASE),
    re.compile(r"\boverride_(?:safety|policy|rules)\w*\b", re.IGNORECASE),
    re.compile(r"\b(?:prompt|system)_inject\w*\b", re.IGNORECASE),
)

# Two or more quoted chunks joined with '+' on the same line: "a" + "b" + "c"
_STRING_THEN_PLUS: re.Pattern[str] = re.compile(
    r"""(['"])(?:\\.|(?!\1).)*\1\s*\+""",
    re.IGNORECASE,
)

# Three or more letter-started identifiers joined by '+': a + b + c (+ d) ...
# Each '+' may be surrounded by spaces (Python style). Ignores 1 + 2 + 3 (digits).
_ID_PLUS_CHAIN: re.Pattern[str] = re.compile(
    r"[a-z_][a-z0-9_]*(?:\s*\+\s*[a-z_][a-z0-9_]*){2,}",
    re.IGNORECASE,
)

# chr()/ord()-based obfuscation: "".join(chr(...)) or "".join(map(chr, ...)).
_JOIN_WITH_CHR_CALL: re.Pattern[str] = re.compile(
    r"\.join\s*\(\s*(?:[^\(\)]|\([^()]*\))*?\bchr\s*\(",
    re.IGNORECASE | re.DOTALL,
)
_JOIN_WITH_MAP_CHR: re.Pattern[str] = re.compile(
    r"\.join\s*\(\s*map\s*\(\s*chr\b",
    re.IGNORECASE,
)

# Dynamic execution and encoded payloads (common in obfuscated exfil / prompt tricks).
_DYNAMIC_EXEC: re.Pattern[str] = re.compile(
    r"\b(?:eval|exec|compile)\s*\(",
    re.IGNORECASE,
)

_BASE64_DECODE: re.Pattern[str] = re.compile(
    r"\b(?:b64decode|a85decode|b32decode|bytes\.fromhex)\s*\(",
    re.IGNORECASE,
)

# List/tuple of literals fed to "".join(...)
_JOIN_LITERAL_LIST: re.Pattern[str] = re.compile(
    r"""['"]{2}\s*\.join\s*\(\s*\[\s*(?:['"][^'"]*['"]\s*,\s*){2,}""",
    re.IGNORECASE,
)

# Two or more adjacent format literals: "%s%s" % (...)  (avoids single "%d" % (x) false positives)
_FORMAT_TWO_LITERALS: re.Pattern[str] = re.compile(
    r"['\"][^'\"%]*%[^'\"]*['\"][^'\"]*['\"][^'\"%]*%[^'\"]*['\"]\s*%\s*\(",
    re.IGNORECASE,
)


def _line_has_string_concat_attack(line: str) -> bool:
    """True if the line chains several string literals with '+', a common Level II trick."""
    return len(_STRING_THEN_PLUS.findall(line)) >= 2


def _line_number_for_match(code: str, needle: str) -> int:
    """Best-effort 1-based line where substring ``needle`` appears."""
    idx = code.find(needle)
    if idx < 0:
        return 1
    return code.count("\n", 0, idx) + 1


def _scan_iterable(
    lines: Iterable[str],
    predicate: Callable[[str], Optional[str]],
) -> Optional[Tuple[int, str]]:
    """Return (line_no, reason) for first line where predicate returns a reason string."""
    for i, line in enumerate(lines, start=1):
        reason = predicate(line)
        if reason:
            return i, reason
    return None


def _quote_state_hash_comment(line: str) -> Optional[str]:
    """
    If the line contains a ``#`` comment outside quotes, return comment text (without #).
    Otherwise return None (``#`` is inside a string, or there is no comment).
    """
    in_single = in_double = False
    escape = False
    for i, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == "\\" and (in_single or in_double):
            escape = True
            continue
        if not in_double and ch == "'" and not in_single:
            in_single = True
            continue
        if not in_single and ch == '"' and not in_double:
            in_double = True
            continue
        if in_single and ch == "'":
            in_single = False
            continue
        if in_double and ch == '"':
            in_double = False
            continue
        if ch == "#" and not in_single and not in_double:
            return line[i + 1 :].strip()
    return None


def _extract_hash_comments(code: str) -> Iterable[str]:
    for line in code.splitlines():
        c = _quote_state_hash_comment(line)
        if c is not None:
            yield c


def _extract_triple_quoted_chunks(code: str) -> Iterable[str]:
    """
    Yield contents of triple-quoted regions (``'''`` or ``\"\"\"``).
    Best-effort: handles common cases; not a full tokenizer.
    """
    i = 0
    n = len(code)
    while i < n - 2:
        q = code[i : i + 3]
        if q in ("'''", '"""'):
            end = code.find(q, i + 3)
            if end == -1:
                break
            yield code[i + 3 : end]
            i = end + 3
            continue
        i += 1


def _complete_the_following_is_benign(text: str) -> bool:
    if "complete the following" not in text.lower():
        return False
    return bool(_COMPLETE_FOLLOWING_OK.search(text))


def _merged_alnum(code: str) -> str:
    """Merge runs of letters/digits across the whole file (spacing / newlines removed)."""
    return re.sub(r"[^a-z0-9]+", "", code.lower())


def _text_has_phrase(haystack_lower: str, phrase: str) -> bool:
    return phrase in haystack_lower


def _comment_or_docstring_hits(combined_lower: str) -> Optional[str]:
    """Return reason if comment/doc text matches risky instructional phrasing."""
    if _complete_the_following_is_benign(combined_lower):
        pass
    elif "complete the following" in combined_lower:
        return "Suspicious 'complete the following' style wording in a comment or docstring"

    for phrase in INJECTION_PHRASES:
        if phrase in combined_lower:
            return f"Suspicious phrase '{phrase}' in a comment or docstring"

    for opener in INSTRUCTION_OPENERS:
        if opener in combined_lower:
            return f"Instruction-seeking phrase '{opener}' in a comment or docstring"

    for kw in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", combined_lower):
            return f"Suspicious keyword '{kw}' in a comment or docstring"

    return None


def _whole_file_obfuscation(code: str) -> Optional[str]:
    """Patterns that only show up when considering the full source text."""
    if _JOIN_WITH_CHR_CALL.search(code) or _JOIN_WITH_MAP_CHR.search(code):
        return "Possible chr()/join-based obfuscation of a hidden string"

    if _DYNAMIC_EXEC.search(code):
        return "Dynamic execution pattern (eval/exec/compile) - often used to hide payloads"

    if _BASE64_DECODE.search(code):
        return "Base64 / binary decoding call - may hide a string payload"

    if _JOIN_LITERAL_LIST.search(code):
        return "Multiple string literals joined via ''.join([...])"

    if _FORMAT_TWO_LITERALS.search(code):
        return "Percent-format string built from multiple format literals"

    collapsed = re.sub(r"\s+", " ", code)
    if _ID_PLUS_CHAIN.search(collapsed):
        return "Long chain of identifiers joined with '+' (possible split-string assembly)"

    return None


def scan_code(code: str) -> dict:
    """
    Scan source text for Level II style embedded attacks.

    Returns:
        {'status': 'SAFE' | 'ATTACK', 'reason': str}
    """
    if not code.strip():
        return {"status": "SAFE", "reason": "Empty input; nothing to scan"}

    lower = code.lower()

    # --- 1) High-signal phrases anywhere in source (strings + code) ---
    for phrase in INJECTION_PHRASES:
        if phrase in lower:
            return {
                "status": "ATTACK",
                "reason": f"Suspicious phrase '{phrase}' detected (line {_line_number_for_match(code, phrase)})",
            }

    for kw in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return {
                "status": "ATTACK",
                "reason": f"Suspicious keyword '{kw}' detected (line {_line_number_for_match(code, kw)})",
            }

    if "complete the following" in lower and not _complete_the_following_is_benign(code):
        needle = "complete the following"
        return {
            "status": "ATTACK",
            "reason": f"'{needle}' style wording detected (line {_line_number_for_match(code, needle)})",
        }

    # --- 2) Merged-alphabet scan: catches splits like 'ig'+'nore' or 'de'+'veloper' ---
    blob = _merged_alnum(code)
    for phrase in INJECTION_PHRASES:
        merged_phrase = re.sub(r"[^a-z0-9]+", "", phrase)
        if len(merged_phrase) >= 8 and merged_phrase in blob:
            return {
                "status": "ATTACK",
                "reason": f"Possible split-string obfuscation reconstructing '{phrase}'",
            }

    # --- 3) Per-line: string literal chains and suspicious names ---
    lines = code.splitlines()

    def line_string_concat(line: str) -> Optional[str]:
        if _line_has_string_concat_attack(line):
            return "Multiple string literals joined with '+' on one line (Level II style)"
        return None

    hit = _scan_iterable(lines, line_string_concat)
    if hit:
        ln, reason = hit
        return {"status": "ATTACK", "reason": f"{reason} (line {ln})"}

    def line_name_patterns(line: str) -> Optional[str]:
        for pat in _SUSPICIOUS_NAME_PATTERNS:
            if pat.search(line):
                return f"Suspicious identifier matching /{pat.pattern}/"
        return None

    hit = _scan_iterable(lines, line_name_patterns)
    if hit:
        ln, reason = hit
        return {"status": "ATTACK", "reason": f"{reason} (line {ln})"}

    # --- 4) Hash (#) comments with quote-aware extraction ---
    hash_blob = "\n".join(_extract_hash_comments(code))
    if hash_blob.strip():
        hlow = hash_blob.lower()
        r = _comment_or_docstring_hits(hlow)
        if r:
            return {"status": "ATTACK", "reason": r}

    # --- 5) Triple-quoted docstrings / string blocks ---
    for chunk in _extract_triple_quoted_chunks(code):
        cl = chunk.lower()
        r = _comment_or_docstring_hits(cl)
        if r:
            return {"status": "ATTACK", "reason": r + " (triple-quoted region)"}

    # --- 6) Whole-file structural heuristics ---
    wf = _whole_file_obfuscation(code)
    if wf:
        return {"status": "ATTACK", "reason": wf}

    return {"status": "SAFE", "reason": "No Level II attack patterns detected"}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8", errors="ignore") as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = scan_code(code)
    print(f"{result['status']}: {result['reason']}")
