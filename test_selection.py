"""
test_selection.py

Unit tests for selection.py. Each test checks the answer against Python's
built in sorted function, which we trust to be correct.

Run with:  python -m unittest -v
"""

import random
import unittest

from selection import deterministic_select, randomized_select, median


class TestSelection(unittest.TestCase):

    def check_every_k(self, values):
        """Try every possible k on this list with both algorithms."""
        expected = sorted(values)
        for k in range(1, len(values) + 1):
            self.assertEqual(deterministic_select(values, k), expected[k - 1])
            self.assertEqual(randomized_select(values, k, random.Random(k)), expected[k - 1])

    def test_single_item(self):
        self.check_every_k([42])

    def test_small_lists(self):
        self.check_every_k([3, 1, 2])
        self.check_every_k([5, 4, 3, 2, 1, 0])

    def test_duplicates(self):
        self.check_every_k([5, 1, 5, 5, 2, 5, 1, 9, 5])

    def test_all_the_same(self):
        self.check_every_k([7] * 50)

    def test_sorted_and_reversed(self):
        self.check_every_k(list(range(60)))
        self.check_every_k(list(range(60, 0, -1)))

    def test_negative_and_float_values(self):
        self.check_every_k([-3.5, 2, 0, -10, 8.25, 2, -3.5])

    def test_many_random_lists(self):
        rng = random.Random(2026)
        for size in (1, 2, 5, 6, 11, 25, 101, 500):
            values = [rng.randint(-50, 50) for _ in range(size)]
            k = rng.randint(1, size)
            expected = sorted(values)[k - 1]
            self.assertEqual(deterministic_select(values, k), expected)
            self.assertEqual(randomized_select(values, k, rng), expected)

    def test_input_list_is_not_changed(self):
        values = [9, 8, 7, 6, 5, 4, 3, 2, 1]
        copy = list(values)
        deterministic_select(values, 3)
        randomized_select(values, 3)
        self.assertEqual(values, copy)

    def test_median_helper(self):
        self.assertEqual(median([4, 1, 3, 2]), 2)
        self.assertEqual(median([4, 1, 3, 2, 5], method="randomized"), 3)
        with self.assertRaises(ValueError):
            median([1, 2], method="other")

    def test_bad_input(self):
        for func in (deterministic_select, randomized_select):
            with self.assertRaises(ValueError):
                func([], 1)
            with self.assertRaises(ValueError):
                func([1, 2, 3], 0)
            with self.assertRaises(ValueError):
                func([1, 2, 3], 4)
            with self.assertRaises(TypeError):
                func([1, 2, 3], 1.5)


if __name__ == "__main__":
    unittest.main()
