# MSCS532 Assignment 6: Medians, Order Statistics, and Elementary Data Structures

This repository has two parts.

1. **Selection algorithms** that find the kth smallest value in a list:
   * Deterministic selection with Median of Medians (worst case O(n))
   * Randomized Quickselect (expected O(n))
2. **Elementary data structures** written from scratch in Python:
   * Dynamic array and matrix
   * Stack and queue built on arrays (the queue is circular)
   * Singly linked list, plus a stack and queue built on it
   * Rooted tree using left child, right sibling links


## Files

| File | What it does |
|---|---|
| `selection.py` | `deterministic_select`, `randomized_select`, and a `median` helper |
| `data_structures.py` | `DynamicArray`, `Matrix`, `ArrayStack`, `ArrayQueue`, `SinglyLinkedList`, `LinkedStack`, `LinkedQueue`, `RootedTree` |
| `test_selection.py` | Unit tests for the selection algorithms |
| `test_data_structures.py` | Unit tests for the data structures |
| `benchmark_selection.py` | Times both selection algorithms on random, sorted, reverse sorted, and duplicate heavy lists |
| `benchmark_structures.py` | Times array based and linked structures on the same jobs and measures memory |
| `plot_results.py` | Builds the charts from the CSV files |
| `results/` | Saved CSV results and charts |

## Requirements

* Python 3.10 or newer
* matplotlib (only needed for `plot_results.py`)

```
pip install matplotlib
```



## Summary of Findings

**Selection.** Both algorithms grew in a straight line as n went up, which matches O(n). Randomized Quickselect was about 3.4 to 4.1 times faster than Median of Medians at n = 100,000 on every input order. Median of Medians does a lot of extra work on each pass to guarantee a good pivot, and that cost shows up as a bigger constant. Sorted and reverse sorted lists did not slow down either algorithm. Lists with many duplicates were the fastest case because the three way partition can stop as soon as k lands inside the block of values equal to the pivot.

| Input (n = 100,000) | Median of Medians (ms) | Randomized Quickselect (ms) |
|---|---|---|
| Random | 79.45 | 19.54 |
| Sorted | 65.81 | 18.51 |
| Reverse sorted | 74.03 | 21.98 |
| Many duplicates | 50.49 | 12.34 |

**Data structures.** Array stacks and circular array queues ran about as fast as their linked versions, and the array stack used about 44 bytes per item compared to about 79 for the linked stack. The big gaps came from operations that do not fit a structure. Inserting 8,000 items at the front of an array took about 1,138 ms because every insert shifts the whole array, while the linked list took about 2 ms. A queue that removes from slot 0 of an array took about 1,169 ms, while the circular queue took about 3.5 ms. Going the other way, 1,000 random reads took 0.08 ms on the array and about 58 ms on the linked list, since a linked list has to walk node by node to reach a position.


## Author

Terrence Tatum, MSCS 532: Algorithms and Data Structures, University of the Cumberlands
