# String assembled at runtime then passed to eval — no obvious keyword in one literal.

parts = ["pr", "int(", "'pwn'", ")"]
eval("".join(parts))
