"""
benchmark_structures.py

Compares array based and linked list based structures on the same jobs and
saves the results to results/structures_results.csv.

Jobs that are timed:
    stack      push n items, then pop them all
    queue      enqueue n items, then dequeue them all
    front      insert n items at the front of the structure
    access     read 1,000 random positions from a structure holding n items

It also measures how much memory a stack of 10,000 items uses with each
design, using the tracemalloc module from the standard library.

Run with:  python benchmark_structures.py
"""

import csv
import os
import random
import statistics
import time
import tracemalloc

from data_structures import (DynamicArray, ArrayStack, ArrayQueue,
                             SinglyLinkedList, LinkedStack, LinkedQueue)

SIZES = [1000, 2000, 4000, 8000]
TRIALS = 3
LOOKUPS = 1000


def stack_job(stack_class, n):
    s = stack_class()
    for i in range(n):
        s.push(i)
    while not s.is_empty():
        s.pop()


def queue_job(queue_class, n):
    q = queue_class()
    for i in range(n):
        q.enqueue(i)
    while not q.is_empty():
        q.dequeue()


def shifting_queue_job(n):
    """A naive array queue that removes from slot 0 and shifts everything left."""
    a = DynamicArray()
    for i in range(n):
        a.append(i)
    while len(a) > 0:
        a.delete(0)


def array_front_job(n):
    a = DynamicArray()
    for i in range(n):
        a.insert(0, i)


def linked_front_job(n):
    ll = SinglyLinkedList()
    for i in range(n):
        ll.insert_front(i)


def access_job(structure, positions):
    for p in positions:
        structure.get(p)


def median_ms(func, *args):
    times = []
    for _ in range(TRIALS):
        start = time.perf_counter()
        func(*args)
        times.append((time.perf_counter() - start) * 1000)
    return round(statistics.median(times), 3)


def memory_bytes(stack_class, n):
    """Return the bytes used to hold n small integers in the given stack."""
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    s = stack_class()
    for i in range(n):
        s.push(i)
    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return after - before


def main():
    rng = random.Random(532)
    rows = []
    for n in SIZES:
        array = DynamicArray()
        linked = SinglyLinkedList()
        for i in range(n):
            array.append(i)
            linked.insert_back(i)
        positions = [rng.randrange(n) for _ in range(LOOKUPS)]

        results = [
            ("stack", "ArrayStack", median_ms(stack_job, ArrayStack, n)),
            ("stack", "LinkedStack", median_ms(stack_job, LinkedStack, n)),
            ("queue", "ArrayQueue (circular)", median_ms(queue_job, ArrayQueue, n)),
            ("queue", "LinkedQueue", median_ms(queue_job, LinkedQueue, n)),
            ("queue", "Shifting array queue", median_ms(shifting_queue_job, n)),
            ("front", "DynamicArray.insert(0)", median_ms(array_front_job, n)),
            ("front", "SinglyLinkedList.insert_front", median_ms(linked_front_job, n)),
            ("access", "DynamicArray.get", median_ms(access_job, array, positions)),
            ("access", "SinglyLinkedList.get", median_ms(access_job, linked, positions)),
        ]
        for job, structure, ms in results:
            row = {"job": job, "structure": structure, "n": n, "time_ms": ms}
            rows.append(row)
            print(row)

    os.makedirs("results", exist_ok=True)
    with open(os.path.join("results", "structures_results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["job", "structure", "n", "time_ms"])
        writer.writeheader()
        writer.writerows(rows)
    print("Saved results/structures_results.csv")

    n = 10000
    with open(os.path.join("results", "memory_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["structure", "items", "bytes", "bytes_per_item"])
        for cls in (ArrayStack, LinkedStack):
            used = memory_bytes(cls, n)
            writer.writerow([cls.__name__, n, used, round(used / n, 1)])
            print(cls.__name__, "uses about", round(used / n, 1), "bytes per item")
    print("Saved results/memory_results.csv")


if __name__ == "__main__":
    main()
