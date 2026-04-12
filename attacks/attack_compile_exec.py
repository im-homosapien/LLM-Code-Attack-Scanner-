# compile() hides behavior in a string; harder than a plain eval("...") one-liner.

code_obj = compile(
    "print('runtime assembled')",
    "<payload>",
    "exec",
)
exec(code_obj)
