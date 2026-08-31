# Heater Calibration Run — Validation Guide

**Photoplasm Incubation Heater · Stage 4 · First deliberate heat — characterize cold→max**
*Board: SpacePlacer v0.6 layout + V8 incoming routing*

---

## What this validates & who it's for

This is the **first time the heater is deliberately energized.** The goal is twofold: confirm the heater actually heats on command and the sensor tracks it, then **characterize the thermal response** — log DS18B20 temperature vs. time from cold up to plateau, producing the cold→max curve and a stored CSV. That data is what the closed-loop setpoint control is built on.

You need the prior stages passed, the Pi with the scripts loaded, and to be **present the entire time** — this stage produces real heat and must not run unattended on its first characterization.

**What changes here:** every stage until now proved the heater stays *off*. This one turns it *on*. So the safety model shifts from "confirm dormant" to "heat within bounds, with a hard cutoff and a human watching."

## Where this fits in the sequence

| | Document | Gate |
|---|---|---|
| ← before | Heater 12 V Power-On — Validation | **PASSED** (12 V held, heater off) |
| **▶ you are here** | **Heater Calibration Run** | heats on command, sensor tracks, curve + CSV captured, cools down |
| → next | Heater Closed-Loop Control | setpoint + hysteresis, interval logging |

---

## Safety measures

**The new hazard is uncontrolled heating.** Three layers guard against it:

1. **The PTC is self-limiting.** A PTC ceramic element's resistance rises sharply near its Curie point, so it naturally plateaus at its design temperature rather than running away like a resistance-wire heater. This is inherent, not software.
2. **Hard software over-temp cutoff.** `heater_calibration.py` forces the gate LOW the instant the sensor reads ≥ `MAX_TEMP_C` (default 50 °C). It also fails safe on any sensor read/CRC failure, on a runtime cap, on Ctrl-C, and on exit — the script cannot leave the heater on.
3. **You, watching.** First heat is attended. The cutoff is a backstop, not a babysitter.

> ### ⚠️ Sensor lag — the element is hotter than the reading
> The DS18B20 measures the chamber, not the PTC surface, and it lags. When the sensor reads 40 °C, the element is hotter. So keep the first run short, start with a conservative cutoff, and don't let the sensor number lull you — a hand near the supply switch beats any threshold.

**Abort (kill 12 V / Ctrl-C) if:**
- Temperature climbs far faster than expected, or overshoots the cutoff without the gate dropping
- Any smell, discoloration, or the board/PTC gets hotter than the sensor suggests
- The sensor reads erratically (the script should already cut the gate on a bad read)
- Anything unexpected — stop first, diagnose after

---

## What you need

- **12 V Power-On Validation: PASSED.** 12 V live, gate holding the heater off, grounds unified.
- Scripts on the Pi (in `~/photoplasm_git/heater/`): `heater_calibration.py`, `plot_calibration.py`.
- matplotlib for plotting: `pip install matplotlib --break-system-packages`
- Sensor confirmed reading (`28-33e70087fda7`). Meter handy (DC volts) for spot-checks.
- **Present and attending the whole run.**

### Behavior reference (low-side switch)
- Gate LOW → MOSFET off → no current → drain (T-6) floats ~12 V → **heater OFF**
- Gate HIGH → MOSFET on → drain pulled ~0 V → current through PTC → **heater ON, heating**
- The script confirms the transition by the temperature *rising*; you can spot-check the drain dropping toward 0 V when it's ON.

---

## Procedure

Run attended, one phase at a time. **Do the pulse test before the full run.**

### Step 0 — Entry state
- [ ] 12 V Power-On passed; 12 V live; gate low; board cool.
- [ ] `cat /sys/bus/w1/devices/28-33e70087fda7/w1_slave` → valid read, sane ambient temp.
- [ ] Scripts present; you're at the bench, hand near the supply switch.

### Step 1 — Functional pulse test (first heat, short)
Confirms the heater heats and the sensor tracks — *before* any sustained run.
- [ ] Run a short pulse (30 s):
      ```bash
      python3 heater_calibration.py --pulse 30
      ```
- [ ] Watch the live print: baseline prints, then `GATE HIGH`, then temperature should **start rising** within the 30 s.
- [ ] *(Optional meter spot-check while it's ON)* drain (T-6) ↔ GND should now read **near 0 V** (MOSFET conducting), versus the ~8 V float when off.
- [ ] At 30 s the script prints `PULSE_END` and forces the gate LOW.
- [ ] **Confirm cooldown:** temperature stops rising and begins to fall. Heater responds to OFF.
- [ ] Board check: warmth at the PTC is expected now; the MOSFET should be only mildly warm, wiring/Wagos cool.

**Gate:** temperature rose on command and fell on release, no surprises → proceed. If it didn't heat, stop and troubleshoot (below) before the full run.

### Step 2 — Full calibration run (cold → plateau/cutoff)
- [ ] Let the chamber return near ambient first (so the curve starts cold).
- [ ] Start the run:
      ```bash
      python3 heater_calibration.py
      ```
      *(For an extra-cautious first characterization, lower the ceiling: `--max-temp 45`.)*
- [ ] Watch the live temperature print the whole time. The run ends automatically on **plateau**, **MAX_TEMP cutoff**, or the **runtime cap** — whichever comes first — and forces the gate LOW.
- [ ] It writes `heater_calibration_<timestamp>.csv`.

### Step 3 — Confirm safe shutdown & cooldown
- [ ] Gate LOW at end (script confirms "Gate LOW, GPIO released").
- [ ] Temperature falling. Board cooling.
- [ ] *(Meter)* gate ↔ GND back to ~0 V; drain back to ~floating.

### Step 4 — Plot & review the curve
- [ ] Plot it:
      ```bash
      python3 plot_calibration.py heater_calibration_<timestamp>.csv
      ```
- [ ] Review the PNG: shape of the rise, the plateau (or cutoff) value, and where **37 °C** falls on the curve (marked on the plot). Note the approximate time to reach 37 °C and the plateau temperature.

---

## What a pass looks like

- [ ] Pulse test: temperature rose on gate-HIGH, fell on gate-LOW
- [ ] Full run: logged cold→plateau/cutoff without incident; gate forced LOW at end
- [ ] Fail-safes behaved (cutoff/plateau/runtime triggered cleanly; no runaway)
- [ ] CSV written and plotted; 37 °C reachable and located on the curve
- [ ] Board within expected temps (PTC warm, MOSFET mild, wiring cool)

→ **PASS = the heater is controllable and characterized. Cleared for Closed-Loop Control.**

**Capture for the record:** baseline (cold) temp, plateau/max temp, approximate time-to-37 °C, and the cutoff used. These set the setpoint/hysteresis and expected timing for the control stage.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| No temperature rise on gate-HIGH | MOSFET not switching; gate not reaching HIGH; open in PTC path | Stop. Meter: gate should be ~3.3 V when commanded HIGH; drain should drop to ~0 V. Recheck T-5 12 V and T-6→drain path |
| `ABORT_SENSOR_START` | sensor not read at launch | Recheck the DS18B20 (address, T-8 ground); re-run Logic Power-On sensor check |
| Cuts out fast with `SENSOR_FAULT` | intermittent sensor read mid-run | Check the sensor data/ground joints; the T-8 ground especially |
| Hits `MAX_TEMP_CUTOFF` very quickly | heating faster than expected, or cutoff set low | Fine for safety; if you want the full curve, let it cool and raise `--max-temp` cautiously |
| MOSFET runs hot | high current / marginal switching | Stop; a low-side MOSFET should stay fairly cool switching a PTC — investigate before longer runs |
| Chip error on launch | wrong gpiochip number | Edit `CHIP` in the script (Pi 5 sometimes needs `4`) |

---

## Sign-off

| Field | Value |
|---|---|
| Date | __________ |
| Pulse test: temp rose / fell | __________ |
| Baseline (cold) temp (°C) | __________ |
| Plateau / max temp (°C) | __________ |
| Cutoff used (°C) | __________ |
| Approx. time to 37 °C (s) | __________ |
| CSV filename | __________ |
| MOSFET / board thermal | __________ |
| **Result** | **PASS / FAIL** |
| Tested by | __________ |

Notes: ________________________________________________________________

---

## Recommended prompt (to expedite with an assistant)

```
I'm running the Heater Calibration Run for my Photoplasm incubation heater
(Raspberry Pi 5, board: SpacePlacer v0.6 + V8 routing). Context:

- Continuity, Logic Power-On, Ground Path, and 12 V Power-On all PASSED. 12 V
  is live; the heater has been held off and is now cleared to energize.
- Low-side MOSFET (IRLZ44N: F8 gate / G8 drain / H8 source). Gate HIGH = heat.
  DS18B20 sensor 28-33e70087fda7. Scripts: heater_calibration.py (has --pulse
  SEC mode and a hard MAX_TEMP cutoff, default 50 C, fail-safe gate-LOW on
  sensor fault / runtime / exit) and plot_calibration.py.
- This is the FIRST deliberate heat. Do the --pulse 30 functional test FIRST
  (confirm temp rises then falls), then the full run to plateau/cutoff, then
  plot. The sensor lags the PTC surface, so keep it attended and conservative.

Walk me through it ONE STEP AT A TIME: a single step, wait for my result
(live temp / CSV / observation), confirm against what's expected, then
continue. Enforce the abort criteria. Start with the short pulse, not the
full run.
```

## Next step

On a clean pass, proceed to **Heater Closed-Loop Control**: use the plateau and timing from this run to set a target (37 °C) with a min/max hysteresis band that switches the gate on/off, logging sensor values at a chosen interval (≥1 s), with the hard over-temp cutoff retained as a standing guard. That's the final stage — a controllable, self-regulating incubation heater.
