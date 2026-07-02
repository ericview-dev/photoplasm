#!/usr/bin/env python3
"""
heater_calibration.py - Photoplasm Incubation Heater, Calibration Run

Drives the PTC heater (GPIO13 gate HIGH) and logs DS18B20 temperature vs. time
to a timestamped CSV, from cold up to plateau or a hard over-temp cutoff.

MODES:
  (default)          Full run: heat until plateau, MAX_TEMP cutoff, or runtime cap.
  --pulse SECONDS    Functional test: gate HIGH for SECONDS only, then stop.
                     Use this FIRST to confirm the heater heats and the sensor
                     tracks, before committing to a full run.

FAIL-SAFE (all modes): the gate is forced LOW on over-temp, on any sensor read/CRC
failure, on runtime cap, on Ctrl-C, and on exit. The heater cannot be left on by
this script. This is the first stage that produces heat - run it ATTENDED.

Board: low-side MOSFET (IRLZ44N). Gate HIGH = heater ON. Gate LOW = heater OFF.
Pi 5 / Bookworm / lgpio.
"""

import lgpio
import time
import csv
import argparse
from datetime import datetime

# ---- Configuration ---------------------------------------------------------
GATE = 13                        # GPIO13 -> MOSFET gate (via 470 ohm)
CHIP = 0                         # Pi 5: your working gpiochip number (some setups use 4)
SENSOR_ID = "28-33e70087fda7"    # DS18B20 hardware address (confirmed)
W1_PATH = "/sys/bus/w1/devices/%s/w1_slave" % SENSOR_ID

MAX_TEMP_C = 50.0                # HARD CUTOFF - gate forced LOW at/above this
LOG_INTERVAL_S = 2.0             # log cadence (DS18B20 conversion ~750 ms; keep >= 1 s)
MAX_RUNTIME_S = 1800             # absolute backstop (30 min) even if never plateaus
PLATEAU_WINDOW_S = 120           # look-back window for plateau detection
PLATEAU_BAND_C = 0.3             # plateau if temp range over the window < this
# ---------------------------------------------------------------------------


def read_temp():
    """Return temperature in C, or None on read/CRC failure (fail-safe -> caller cuts gate)."""
    try:
        with open(W1_PATH) as f:
            lines = f.readlines()
        if len(lines) < 2 or "YES" not in lines[0]:
            return None
        p = lines[1].find("t=")
        if p < 0:
            return None
        return int(lines[1][p + 2:]) / 1000.0
    except (OSError, ValueError, IndexError):
        return None


def run(pulse_seconds=None, max_temp=MAX_TEMP_C):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = "heater_calibration_%s.csv" % ts

    h = lgpio.gpiochip_open(CHIP)
    lgpio.gpio_claim_output(h, GATE, 0)   # claim gate as output, start LOW (heater off)

    start = time.time()
    last_log = -LOG_INTERVAL_S
    history = []  # list of (elapsed, temp) at each logged sample

    mode = ("PULSE %.0fs" % pulse_seconds) if pulse_seconds else "FULL RUN"
    print("Calibration run [%s] -> %s" % (mode, csv_path))
    print("Cutoff %.1f C | interval %.1fs | runtime cap %ds" % (max_temp, LOG_INTERVAL_S, MAX_RUNTIME_S))
    print("Ctrl-C stops safely (gate forced LOW). Run ATTENDED.\n")

    try:
        with open(csv_path, "w", newline="") as fcsv:
            w = csv.writer(fcsv)
            w.writerow(["elapsed_s", "timestamp", "temp_c", "gate", "note"])

            # Baseline (cold) reading BEFORE any heat
            t0 = read_temp()
            if t0 is None:
                print("ABORT: sensor read failed at start. Gate stays LOW.")
                w.writerow(["0.0", datetime.now().isoformat(), "", 0, "ABORT_SENSOR_START"])
                return csv_path
            w.writerow(["0.0", datetime.now().isoformat(), "%.3f" % t0, 0, "baseline_cold"])
            fcsv.flush()
            print("Baseline (cold): %.2f C" % t0)

            # Heater ON
            lgpio.gpio_write(h, GATE, 1)
            print(">>> GATE HIGH - heater ON\n")

            while True:
                now = time.time()
                elapsed = now - start
                temp = read_temp()

                # Fail-safe: sensor fault -> gate LOW, stop
                if temp is None:
                    lgpio.gpio_write(h, GATE, 0)
                    w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "", 0, "SENSOR_FAULT_GATE_LOW"])
                    print("SENSOR FAULT - gate forced LOW. Stopping.")
                    break

                # Hard over-temp cutoff
                if temp >= max_temp:
                    lgpio.gpio_write(h, GATE, 0)
                    w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "%.3f" % temp, 0, "MAX_TEMP_CUTOFF"])
                    print("CUTOFF: %.2f C >= %.1f C - gate LOW. Stopping." % (temp, max_temp))
                    break

                # Pulse mode: stop after the requested duration
                if pulse_seconds and elapsed >= pulse_seconds:
                    lgpio.gpio_write(h, GATE, 0)
                    w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "%.3f" % temp, 0, "PULSE_END"])
                    print("Pulse complete (%.0fs) at %.2f C - gate LOW." % (pulse_seconds, temp))
                    break

                # Runtime backstop
                if elapsed >= MAX_RUNTIME_S:
                    lgpio.gpio_write(h, GATE, 0)
                    w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "%.3f" % temp, 0, "MAX_RUNTIME"])
                    print("Runtime cap reached - gate LOW. Stopping.")
                    break

                # Log at interval
                if elapsed - last_log >= LOG_INTERVAL_S:
                    w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "%.3f" % temp, 1, ""])
                    fcsv.flush()
                    print("%7.1fs   %6.2f C" % (elapsed, temp))
                    last_log = elapsed
                    history.append((elapsed, temp))

                    # Plateau detection (full-run mode only)
                    if not pulse_seconds:
                        window = [t for (e, t) in history if elapsed - e <= PLATEAU_WINDOW_S]
                        if len(window) >= 5 and (max(window) - min(window)) < PLATEAU_BAND_C:
                            lgpio.gpio_write(h, GATE, 0)
                            w.writerow(["%.1f" % elapsed, datetime.now().isoformat(), "%.3f" % temp, 0, "PLATEAU_REACHED"])
                            print("Plateau ~%.2f C - gate LOW. Done." % temp)
                            break

                time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nInterrupted - forcing gate LOW.")
    finally:
        try:
            lgpio.gpio_write(h, GATE, 0)
            lgpio.gpio_free(h, GATE)
        finally:
            lgpio.gpiochip_close(h)
        print("Gate LOW, GPIO released.")
        print("Data: %s" % csv_path)

    return csv_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Photoplasm heater calibration run")
    ap.add_argument("--pulse", type=float, default=None, metavar="SEC",
                    help="functional test: gate HIGH for SEC seconds only, then stop")
    ap.add_argument("--max-temp", type=float, default=MAX_TEMP_C, metavar="C",
                    help="hard over-temp cutoff in C (default %.0f)" % MAX_TEMP_C)
    args = ap.parse_args()
    run(pulse_seconds=args.pulse, max_temp=args.max_temp)
