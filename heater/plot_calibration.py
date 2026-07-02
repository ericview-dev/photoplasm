#!/usr/bin/env python3
"""
plot_calibration.py - plot a heater_calibration_*.csv (temperature vs time).

Usage:
    python3 plot_calibration.py heater_calibration_YYYYMMDD_HHMMSS.csv

Saves a PNG next to the CSV. Marks event rows (baseline, cutoff, plateau, pulse end).
Requires matplotlib:  pip install matplotlib --break-system-packages
"""

import sys
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main(path):
    t, temp, events = [], [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row.get("temp_c"):
                e = float(row["elapsed_s"])
                c = float(row["temp_c"])
                t.append(e)
                temp.append(c)
                if row.get("note"):
                    events.append((e, c, row["note"]))

    if not t:
        print("No temperature rows found in", path)
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(t, temp, "-", color="#c0392b", linewidth=1.6, label="chamber temp")
    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("Temperature (C)")
    ax.set_title("Heater Calibration - Cold to Plateau")
    ax.grid(True, alpha=0.3)

    # 37 C target reference line
    ax.axhline(37.0, color="#2980b9", linestyle="--", linewidth=1, alpha=0.7, label="37 C target")

    # annotate event rows
    for (e, c, note) in events:
        ax.annotate(note, (e, c), fontsize=8,
                    xytext=(5, 5), textcoords="offset points", color="#555")
        ax.plot(e, c, "o", color="#555", markersize=4)

    ax.legend(loc="lower right", fontsize=9)
    out = path.rsplit(".", 1)[0] + ".png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print("saved", out)

    # quick summary
    print("baseline: %.2f C   peak: %.2f C   samples: %d   duration: %.0fs"
          % (temp[0], max(temp), len(temp), t[-1]))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "heater_calibration.csv")
