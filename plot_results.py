"""
plot_results.py

Turns the CSV files in results/ into charts. Run the two benchmark scripts
first so the CSV files exist.

Run with:  python plot_results.py
Needs:     matplotlib  (pip install matplotlib)
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")      # Save straight to files without opening a window.
import matplotlib.pyplot as plt


def read_csv(name):
    with open(os.path.join("results", name), newline="") as f:
        return list(csv.DictReader(f))


def plot_selection():
    rows = read_csv("selection_results.csv")
    kinds = ["random", "sorted", "reverse", "duplicates"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, kind in zip(axes.flat, kinds):
        part = [r for r in rows if r["distribution"] == kind]
        n = [int(r["n"]) for r in part]
        ax.plot(n, [float(r["deterministic_ms"]) for r in part], marker="o", label="Deterministic (Median of Medians)")
        ax.plot(n, [float(r["randomized_ms"]) for r in part], marker="s", label="Randomized Quickselect")
        ax.set_title(kind.capitalize() + " input")
        ax.set_xlabel("Input size (n)")
        ax.set_ylabel("Time (ms)")
        ax.grid(True, alpha=0.3)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle("Time to find the median")
    fig.tight_layout()
    fig.savefig(os.path.join("results", "selection_runtime.png"), dpi=200)
    plt.close(fig)


def plot_structures():
    rows = read_csv("structures_results.csv")
    jobs = [("stack", "Push then pop n items"),
            ("queue", "Enqueue then dequeue n items"),
            ("front", "Insert n items at the front"),
            ("access", "1,000 random reads")]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, (job, title) in zip(axes.flat, jobs):
        part = [r for r in rows if r["job"] == job]
        for name in dict.fromkeys(r["structure"] for r in part):
            mine = [r for r in part if r["structure"] == name]
            ax.plot([int(r["n"]) for r in mine], [float(r["time_ms"]) for r in mine], marker="o", label=name)
        ax.set_title(title)
        ax.set_xlabel("n")
        ax.set_ylabel("Time (ms)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("Array based versus linked structures")
    fig.tight_layout()
    fig.savefig(os.path.join("results", "structures_runtime.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    plot_selection()
    plot_structures()
    print("Saved results/selection_runtime.png and results/structures_runtime.png")
