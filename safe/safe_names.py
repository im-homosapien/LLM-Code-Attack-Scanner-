def make_harmonic_series(n):
    total = 0
    for i in range(1, n + 1):
        total += 1 / i
    return total

print(make_harmonic_series(5))