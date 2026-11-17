"""
selection.py

Two ways to find the kth smallest value in a list.

deterministic_select uses the Median of Medians method. It always runs in
linear time, even on the worst possible input.

randomized_select uses Randomized Quickselect. It picks a random pivot, so its
running time is linear on average.

Both functions use k as a 1 based rank. That means k = 1 is the smallest value
and k = len(values) is the largest value. Neither function changes the list
that is passed in. They work on a copy.
"""

import random


def _check_input(values, k):
    """Make sure the list is not empty and k is a valid rank."""
    if len(values) == 0:
        raise ValueError("Cannot select from an empty list.")
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be a whole number.")
    if k < 1 or k > len(values):
        raise ValueError("k must be between 1 and " + str(len(values)) + ".")


def _insertion_sort(a, lo, hi):
    """Sort a[lo..hi] in place. This is only used on tiny groups of 5 or fewer."""
    for i in range(lo + 1, hi + 1):
        current = a[i]
        j = i - 1
        while j >= lo and a[j] > current:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = current


def _partition_three_way(a, lo, hi, pivot):
    """
    Rearrange a[lo..hi] into three parts around the pivot value.

    After this runs, a[lo..lt-1] is less than the pivot, a[lt..gt] is equal
    to the pivot, and a[gt+1..hi] is greater than the pivot. The function
    returns lt and gt.

    Keeping all the copies of the pivot together in the middle is how both
    algorithms deal with duplicates. If the list has many repeated values,
    the equal part can be large, and we can stop early when k lands inside it.
    """
    lt = lo
    i = lo
    gt = hi
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


# Deterministic selection (Median of Medians)

def _median_of_medians(a, lo, hi):
    """
    Pick a pivot for a[lo..hi] that is guaranteed to be close to the middle.

    Step 1: split the range into groups of 5.
    Step 2: sort each small group and find its median.
    Step 3: move every group median to the front of the range.
    Step 4: call the select routine on those medians to find their median.

    The value returned has at least about 3n/10 values on each side of it,
    which is what keeps the whole algorithm linear.
    """
    count = 0
    for start in range(lo, hi + 1, 5):
        end = min(start + 4, hi)
        _insertion_sort(a, start, end)
        middle = (start + end) // 2
        # Swap this group's median to the front so all medians sit together.
        a[lo + count], a[middle] = a[middle], a[lo + count]
        count += 1

    # Find the median of the medians we just collected.
    target = lo + (count - 1) // 2
    return _mom_select(a, lo, lo + count - 1, target)


def _mom_select(a, lo, hi, target):
    """
    Return the value that would sit at index target if a[lo..hi] were sorted.

    I wrote this as a loop instead of plain recursion on the side we keep.
    The only recursive call is the one inside _median_of_medians, which works
    on a list about one fifth the size. This keeps the call stack small.
    """
    while True:
        # Small ranges are faster to just sort directly.
        if hi - lo < 5:
            _insertion_sort(a, lo, hi)
            return a[target]

        pivot = _median_of_medians(a, lo, hi)
        lt, gt = _partition_three_way(a, lo, hi, pivot)

        if target < lt:
            hi = lt - 1        # The answer is in the "less than" part.
        elif target > gt:
            lo = gt + 1        # The answer is in the "greater than" part.
        else:
            return pivot       # The answer is one of the pivot copies.


def deterministic_select(values, k):
    """
    Return the kth smallest value using Median of Medians.

    Time:  O(n) in the worst case.
    Space: O(n) for the working copy, plus O(log n) for the call stack.

    Example:
        deterministic_select([7, 2, 9, 4], 2) returns 4
    """
    _check_input(values, k)
    a = list(values)
    return _mom_select(a, 0, len(a) - 1, k - 1)


# Randomized selection (Randomized Quickselect)

def randomized_select(values, k, rng=None):
    """
    Return the kth smallest value using Randomized Quickselect.

    Time:  O(n) expected. The worst case is O(n^2), but that needs the random
           pivots to be bad over and over, which is very unlikely.
    Space: O(n) for the working copy. The loop needs no extra stack space.

    rng lets you pass in a random.Random object with a seed. That makes runs
    repeatable, which is handy for testing. If you leave it out, the module
    level random generator is used.

    Example:
        randomized_select([7, 2, 9, 4], 2) returns 4
    """
    _check_input(values, k)
    if rng is None:
        rng = random
    a = list(values)
    lo = 0
    hi = len(a) - 1
    target = k - 1

    while lo < hi:
        # Pick any position in the current range at random and use its value.
        pivot = a[rng.randint(lo, hi)]
        lt, gt = _partition_three_way(a, lo, hi, pivot)

        if target < lt:
            hi = lt - 1
        elif target > gt:
            lo = gt + 1
        else:
            return pivot

    return a[lo]


def median(values, method="deterministic"):
    """
    Return the lower median of the list.

    For a list with an even length, this gives the smaller of the two middle
    values, which matches how order statistics are usually defined.
    """
    k = (len(values) + 1) // 2
    if method == "deterministic":
        return deterministic_select(values, k)
    if method == "randomized":
        return randomized_select(values, k)
    raise ValueError("method must be 'deterministic' or 'randomized'.")


if __name__ == "__main__":
    sample = [12, 3, 5, 7, 4, 19, 26, 3, 5, 5]
    print("List:", sample)
    print("Sorted for reference:", sorted(sample))
    for k in (1, 4, len(sample)):
        print("k =", k,
              "| deterministic:", deterministic_select(sample, k),
              "| randomized:", randomized_select(sample, k))
    print("Lower median:", median(sample))
