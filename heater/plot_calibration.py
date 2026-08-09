#!/usr/bin/env python3
"""
plot_calibration.py - plot a heater_calibration_*.csv (temperature vs time).

Shows heating (red), hold (orange), cooling (blue); marks events and a target
reference line. Saves a PNG next to the CSV. Backward-compatible with older
CSVs lacking a phase column.

Usage:  python3 plot_calibration.py heater_calibration_YYYYMMDD_HHMMSS.csv
Requires matplotlib:  pip install matplotlib --break-system-packages
"""

import sys
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = {"heating": "#c0392b", "hold": "#e67e22", "cooling": "#2980b9"}


def main(path):
    series = {"heating": ([], []), "hold": ([], []), "cooling": ([], [])}
    events = []
    with open(path) as f:
        for row in csv.DictReader(f):
            phase = row.get("phase") or "heating"
            note = row.get("note", "")
            if row.get("temp_c"):
                e = float(row["elapsed_s"]); c = float(row["temp_c"])
                series.setdefault(phase, ([], []))
                series[phase][0].append(e); series[phase][1].append(c)
                if note:
                    events.append((e, c, note))

    if not any(series[p][0] for p in series):
        print("No temperature rows found in", path)
        return

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for phase in ("heating", "hold", "cooling"):
        xs, ys = series.get(phase, ([], []))
        if xs:
            ax.plot(xs, ys, "-", color=COLORS.get(phase, "#555"),
                    linewidth=1.7, label=phase)

    ax.axhline(37.0, color="#27ae60", linestyle="--", linewidth=1, alpha=0.7, label="37 C target")

    for (e, c, note) in events:
        ax.plot(e, c, "o", color="#555", markersize=4)
        ax.annotate(note.split()[0], (e, c), fontsize=7.5,
                    xytext=(5, 5), textcoords="offset points", color="#555")

    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("Temperature (C)")
    ax.set_title("Heater Calibration - Heat / Hold / Cool")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)

    out = path.rsplit(".", 1)[0] + ".png"
    fig.tight_layout(); fig.savefig(out, dpi=130)
    print("saved", out)

    allc = [c for p in series for c in series[p][1]]
    base = series["heating"][1][0] if series["heating"][1] else float("nan")
    print("baseline: %.2f C   peak: %.2f C   heat:%d hold:%d cool:%d samples"
          % (base, max(allc), len(series['heating'][1]),
             len(series['hold'][1]), len(series['cooling'][1])))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "heater_calibration.csv")
