"""
benchmark_selection.py

Times deterministic_select and randomized_select on different input sizes
and input orders, then saves the results to results/selection_results.csv.

Each test finds the median (k = n // 2). Every case runs several times and
the median time is kept, since one slow run can throw off an average.

Run with:  python benchmark_selection.py
"""

import csv
import os
import random
import statistics
import time

from selection import deterministic_select, randomized_select

SIZES = [1000, 5000, 10000, 50000, 100000]
TRIALS = 5
SEED = 532


def make_input(kind, n, rng):
    """Build a list of size n in the requested order."""
    if kind == "random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "duplicates":
        # Only 10 different values, so most items repeat many times.
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError("unknown input kind: " + kind)


def time_ms(func, *args):
    """Run func once and return how long it took in milliseconds."""
    start = time.perf_counter()
    func(*args)
    return (time.perf_counter() - start) * 1000


def main():
    rng = random.Random(SEED)
    rows = []
    for kind in ["random", "sorted", "reverse", "duplicates"]:
        for n in SIZES:
            data = make_input(kind, n, rng)
            k = n // 2
            expected = sorted(data)[k - 1]

            det_times = []
            rand_times = []
            sort_times = []
            for trial in range(TRIALS):
                det_times.append(time_ms(deterministic_select, data, k))
                rand_times.append(time_ms(randomized_select, data, k, random.Random(SEED + trial)))
                sort_times.append(time_ms(lambda d: sorted(d)[k - 1], data))

            # Quick safety check that both algorithms really got it right.
            assert deterministic_select(data, k) == expected
            assert randomized_select(data, k) == expected

            row = {
                "distribution": kind,
                "n": n,
                "deterministic_ms": round(statistics.median(det_times), 3),
                "randomized_ms": round(statistics.median(rand_times), 3),
                "builtin_sort_ms": round(statistics.median(sort_times), 3),
            }
            rows.append(row)
            print(row)

    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", "selection_results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Saved results/selection_results.csv")


if __name__ == "__main__":
    main()
