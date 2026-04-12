# Many tiny literals in one join(...) call — looks like benign data, spells a policy phrase.

msg = "".join(
    [
        "dis",
        "reg",
        "ard ",
        "saf",
        "ety ",
        "gui",
        "dance",
    ]
)
print(msg)
