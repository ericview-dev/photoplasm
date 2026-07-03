#!/usr/bin/env python3
"""
heater_calibration.py - Photoplasm Incubation Heater, Calibration Run

Drives the PTC heater (GPIO13) and logs DS18B20 temperature vs. time to a
timestamped CSV. In target mode it runs three phases in one dataset:

    HEATING  -> gate HIGH until temp reaches --target
    HOLD     -> maintain target for --hold seconds via bang-bang (gate cycles)
    COOLING  -> gate LOW, log passive cooldown for a span = heat-up time
                (or --cooldown seconds if given)

phase column in the CSV marks heating / hold / cooling.

MODES:
  --target C [--hold SEC] [--band C] [--cooldown SEC]
                     Calibration: heat to C, optionally hold, then cool.
  --pulse SECONDS    Functional test: gate HIGH for SECONDS only.
  (default)          Full run: heat until plateau / MAX_TEMP / runtime cap.

FAIL-SAFE (all modes): gate forced LOW on over-temp, on any sensor read/CRC
failure while heating or holding, on runtime cap, on Ctrl-C, and on exit.
The heater cannot be left on by this script. Run ATTENDED.

Board: low-side MOSFET (IRLZ44N). Gate HIGH = heater ON. Pi 5 / lgpio.
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

MAX_TEMP_C = 50.0                # HARD CUTOFF - gate forced LOW at/above this (safety backstop)
LOG_INTERVAL_S = 2.0             # log cadence (DS18B20 conversion ~750 ms; keep >= 1 s)
MAX_RUNTIME_S = 1800             # heating-phase backstop (30 min)
PLATEAU_WINDOW_S = 120           # plateau look-back window
PLATEAU_BAND_C = 0.3             # plateau if temp range over window < this
HOLD_BAND_C = 0.5                # default hysteresis for the hold phase
COOLDOWN_CAP_S = 1800            # cooldown time cap (30 min) if baseline not reached
HOLD_CAP_MARGIN_S = 15           # absolute hold guard: hold can never exceed hold+this
# ---------------------------------------------------------------------------


def read_temp():
    """Return temperature in C, or None on read/CRC failure."""
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


def run(pulse_seconds=None, target_c=None, hold_seconds=0.0,
        band_c=HOLD_BAND_C, cooldown_seconds=None, max_temp=MAX_TEMP_C):

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = "heater_calibration_%s.csv" % ts

    h = lgpio.gpiochip_open(CHIP)
    lgpio.gpio_claim_output(h, GATE, 0)
    gate_state = 0

    def set_gate(level):
        nonlocal gate_state
        lgpio.gpio_write(h, GATE, level)
        gate_state = level

    start = time.time()
    last_log = -LOG_INTERVAL_S
    history = []
    t_reach = None
    do_cooldown = False

    if target_c:
        mode = "TARGET %.1f C" % target_c
        if hold_seconds:
            mode += " + HOLD %.0fs (band %.1f)" % (hold_seconds, band_c)
        mode += " + cooldown"
    elif pulse_seconds:
        mode = "PULSE %.0fs" % pulse_seconds
    else:
        mode = "FULL RUN (plateau/cutoff)"
    print("Calibration run [%s] -> %s" % (mode, csv_path))
    print("Cutoff %.1f C | interval %.1fs | runtime cap %ds" % (max_temp, LOG_INTERVAL_S, MAX_RUNTIME_S))
    print("Ctrl-C stops safely (gate forced LOW). Run ATTENDED.\n")

    try:
        with open(csv_path, "w", newline="") as fcsv:
            w = csv.writer(fcsv)
            w.writerow(["elapsed_s", "timestamp", "temp_c", "gate", "phase", "note"])

            def log(temp, phase, note=""):
                tstr = "%.3f" % temp if temp is not None else ""
                w.writerow(["%.1f" % (time.time() - start), datetime.now().isoformat(),
                            tstr, gate_state, phase, note])
                fcsv.flush()

            # --- Baseline (cold) ---
            t0 = read_temp()
            if t0 is None:
                print("ABORT: sensor read failed at start. Gate stays LOW.")
                log(None, "heating", "ABORT_SENSOR_START")
                return csv_path
            log(t0, "heating", "baseline_cold")
            print("Baseline (cold): %.2f C" % t0)

            # --- Heater ON ---
            set_gate(1)
            print(">>> GATE HIGH - heater ON\n")

            # ================= HEATING =================
            while True:
                elapsed = time.time() - start
                temp = read_temp()

                if temp is None:
                    set_gate(0)
                    log(None, "heating", "SENSOR_FAULT_GATE_LOW")
                    print("SENSOR FAULT - gate forced LOW. Stopping.")
                    return csv_path

                if target_c and temp >= target_c:
                    set_gate(0)
                    t_reach = elapsed
                    log(temp, "heating", "TARGET_REACHED")
                    print("Target %.1f C reached at %.1fs (%.2f C) - gate LOW." % (target_c, elapsed, temp))
                    do_cooldown = True
                    break

                if temp >= max_temp:
                    set_gate(0)
                    t_reach = elapsed
                    log(temp, "heating", "MAX_TEMP_CUTOFF")
                    print("CUTOFF: %.2f C >= %.1f C - gate LOW." % (temp, max_temp))
                    do_cooldown = bool(target_c)
                    break

                if pulse_seconds and elapsed >= pulse_seconds:
                    set_gate(0)
                    log(temp, "heating", "PULSE_END")
                    print("Pulse complete (%.0fs) at %.2f C - gate LOW." % (pulse_seconds, temp))
                    break

                if elapsed >= MAX_RUNTIME_S:
                    set_gate(0)
                    t_reach = elapsed
                    log(temp, "heating", "MAX_RUNTIME")
                    print("Runtime cap reached - gate LOW.")
                    do_cooldown = bool(target_c)
                    break

                if elapsed - last_log >= LOG_INTERVAL_S:
                    log(temp, "heating")
                    print("%7.1fs   %6.2f C   [heating]" % (elapsed, temp))
                    last_log = elapsed
                    history.append((elapsed, temp))
                    # Plateau detection is ONLY for full-run mode (no target). In target
                    # mode it must never fire - early thermal-lag flat spots look like
                    # plateaus and would abort the climb before reaching target.
                    if not pulse_seconds and not target_c:
                        window = [t for (e, t) in history if elapsed - e <= PLATEAU_WINDOW_S]
                        if len(window) >= 5 and (max(window) - min(window)) < PLATEAU_BAND_C:
                            set_gate(0)
                            t_reach = elapsed
                            log(temp, "heating", "PLATEAU_REACHED")
                            print("Plateau ~%.2f C at %.1fs - gate LOW." % (temp, elapsed))
                            break
                time.sleep(0.25)

            # ================= HOLD (bang-bang) =================
            if do_cooldown and target_c and hold_seconds and t_reach is not None:
                hold_start = time.time()
                hold_hard_cap = hold_start + hold_seconds + HOLD_CAP_MARGIN_S  # absolute wall
                log(None, "hold", "HOLD_START %.0fs at %.1f C (band %.1f, hard cap +%.0fs)"
                    % (hold_seconds, target_c, band_c, HOLD_CAP_MARGIN_S))
                print("\n>>> HOLD %.0fs at %.1f C (bang-bang, band %.1f)\n" % (hold_seconds, target_c, band_c))
                last_log = time.time() - start
                on_low = target_c - band_c   # turn heater ON below this
                while (time.time() - hold_start) < hold_seconds:
                    if time.time() >= hold_hard_cap:   # absolute runtime guard
                        set_gate(0)
                        log(read_temp(), "hold", "HOLD_HARD_CAP_GATE_LOW")
                        print("HOLD hard cap reached - gate forced LOW.")
                        break
                    elapsed = time.time() - start
                    temp = read_temp()
                    if temp is None:
                        set_gate(0)
                        log(None, "hold", "SENSOR_FAULT_GATE_LOW")
                        print("SENSOR FAULT during hold - gate forced LOW. Stopping.")
                        return csv_path
                    if temp >= max_temp:               # safety backstop
                        set_gate(0)
                        log(temp, "hold", "MAX_TEMP_CUTOFF")
                        print("CUTOFF during hold - gate LOW.")
                        break
                    # bang-bang: OFF at/above target, ON at/below (target - band)
                    if temp >= target_c and gate_state == 1:
                        set_gate(0)
                    elif temp <= on_low and gate_state == 0:
                        set_gate(1)
                    if elapsed - last_log >= LOG_INTERVAL_S:
                        log(temp, "hold")
                        print("%7.1fs   %6.2f C   [hold gate=%d]" % (elapsed, temp, gate_state))
                        last_log = elapsed
                    time.sleep(0.25)
                set_gate(0)
                log(None, "hold", "HOLD_END")
                print("\nHold complete - gate LOW.")

            # ================= COOLDOWN (gate LOW) =================
            # Cool until temp returns to the baseline (initial) temperature, with a
            # generous time cap as a backstop. If --cooldown SEC is given, use that
            # fixed span instead.
            if do_cooldown and t_reach is not None:
                set_gate(0)
                cool_start = time.time()
                cap = cooldown_seconds if cooldown_seconds else COOLDOWN_CAP_S
                if cooldown_seconds:
                    log(None, "cooling", "COOLDOWN_START fixed %.0fs (gate LOW)" % cap)
                    print("\n>>> GATE LOW - cooldown for %.0fs\n" % cap)
                else:
                    log(None, "cooling", "COOLDOWN_START to baseline %.2f C (cap %.0fs)" % (t0, cap))
                    print("\n>>> GATE LOW - cooldown until back to baseline %.2f C (cap %.0fs)\n" % (t0, cap))
                last_log = time.time() - start
                while (time.time() - cool_start) < cap:
                    elapsed = time.time() - start
                    temp = read_temp()  # gate already LOW; a bad read is not a hazard here
                    if elapsed - last_log >= LOG_INTERVAL_S:
                        log(temp, "cooling", "" if temp is not None else "sensor_read_skip")
                        shown = ("%6.2f C" % temp) if temp is not None else "  --  "
                        print("%7.1fs   %s   [cooling]" % (elapsed, shown))
                        last_log = elapsed
                    # stop once we've returned to (or below) the starting temperature
                    if not cooldown_seconds and temp is not None and temp <= t0:
                        log(temp, "cooling", "COOLDOWN_REACHED_BASELINE")
                        print("Returned to baseline %.2f C at %.1fs." % (t0, elapsed))
                        break
                    time.sleep(0.25)
                else:
                    log(None, "cooling", "COOLDOWN_CAP_REACHED")
                    print("Cooldown time cap reached.")
                log(None, "cooling", "COOLDOWN_END")
                print("\nCooldown complete.")

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
    ap.add_argument("--target", type=float, default=None, metavar="C",
                    help="heat to C, then (hold, then) log cooldown")
    ap.add_argument("--hold", type=float, default=0.0, metavar="SEC",
                    help="hold at target for SEC seconds via bang-bang (needs --target)")
    ap.add_argument("--band", type=float, default=HOLD_BAND_C, metavar="C",
                    help="hysteresis band for the hold phase (default %.1f)" % HOLD_BAND_C)
    ap.add_argument("--cooldown", type=float, default=None, metavar="SEC",
                    help="cooldown duration in s (default = heat-up time)")
    ap.add_argument("--pulse", type=float, default=None, metavar="SEC",
                    help="functional test: gate HIGH for SEC seconds only")
    ap.add_argument("--max-temp", type=float, default=MAX_TEMP_C, metavar="C",
                    help="hard over-temp cutoff / safety backstop (default %.0f)" % MAX_TEMP_C)
    args = ap.parse_args()
    run(pulse_seconds=args.pulse, target_c=args.target, hold_seconds=args.hold,
        band_c=args.band, cooldown_seconds=args.cooldown, max_temp=args.max_temp)
