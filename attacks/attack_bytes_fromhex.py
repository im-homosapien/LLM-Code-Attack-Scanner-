# Binary decoding without base64 (still flagged by structural rule).

raw = bytes.fromhex("48656c6c6f")
print(raw.decode("ascii", errors="replace"))
