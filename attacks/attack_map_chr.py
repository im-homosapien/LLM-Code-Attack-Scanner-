# Harder split: ordinals passed through map(chr, ...) instead of a generator.

nums = [106, 97, 105, 108, 98, 114, 101, 97, 107]
hidden = "".join(map(chr, nums))
print(hidden)
