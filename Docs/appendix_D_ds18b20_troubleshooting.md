Photoplasm Quick Start Guide  ·  Appendix D: DS18B20 1-Wire Sensor — Wiring & Troubleshooting

# Appendix D: DS18B20 1-Wire Sensor — Wiring & Troubleshooting

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.0  ·  2026-06-12  ·  github.com/ericview-dev/photoplasm

---

## Overview

This appendix documents the correct wiring for the DS18B20 waterproof temperature sensor on the Heater Perfboard, the software setup required to activate the 1-Wire bus, and a systematic troubleshooting guide derived from the first bench build. The gotchas documented here were encountered and resolved during initial hardware bring-up.

---

## Correct Wiring

The DS18B20 uses the Dallas 1-Wire protocol on a single GPIO pin. A 4.7kΩ pull-up resistor (R2) holds the data line at 3.3V when idle. The sensor pulls the line low briefly to communicate.

```
Pi Pin 1  (3.3V) ──── R2 (4.7kΩ) ────┬──── J1 pin 3 (DS18B20 Data, orange wire)
                                       │
Pi Pin 7  (GPIO4 / 1-Wire) ───────────┘

Pi Pin 39 (GND) ────────────────────── J1 pin 4 (DS18B20 GND, gray wire)
Pi Pin 1  (3.3V) ───────────────────── J1 pin 5 (DS18B20 VDD, blue wire)
```

### The critical junction

The bottom leg of R2, J1 pin 3 (data wire), and the jumper to GPIO4 must all connect at the **same perfboard node** — same row of holes, linked by solder bridges or a jumper wire. If any one of these three is not at the same node, the pull-up will not reach the sensor and the Pi will not see the data signal.

---

## JST Connector Pinout (J1)

| Pin | Label | Function | Wire Color |
|---|---|---|---|
| 3 | T7 / J3 | DS18B20 Data | Orange |
| 4 | T8 / J4 | DS18B20 GND | Gray |
| 5 | T9 / J5 | DS18B20 VDD (3.3V) | Blue |

---

## Raspberry Pi Pin Reference

| Pi Pin | GPIO | Function |
|---|---|---|
| 1 | — | 3.3V → R2 pull-up top, DS18B20 VDD |
| 7 | GPIO4 | 1-Wire data |
| 39 | — | GND → DS18B20 GND |

**Note:** All GND pins on the Pi (6, 9, 14, 20, 25, 30, 34, 39) are electrically identical — the same ground plane. Pin 39 can be used if Pin 6 is occupied by another subsystem (e.g. the LED ring).

---

## Software Setup

Enable the 1-Wire overlay in the Pi boot config:

```bash
sudo nano /boot/firmware/config.txt
```

Add at the bottom:

```
dtoverlay=w1-gpio,gpiopin=4
```

Save and reboot:

```bash
sudo reboot
```

Verify sensor detection after reboot:

```bash
ls /sys/bus/w1/devices/
```

A working sensor shows a device starting with `28-` alongside `w1_bus_master1`. Read temperature:

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

A valid response ends with `YES` and a temperature in thousandths of a degree Celsius:

```
86 01 00 00 7f e1 3c aa d3 : crc=d3 YES
86 01 00 00 7f e1 3c aa d3 t=24375
```

`t=24375` = 24.375°C (75.9°F). `YES` confirms the CRC passed — the reading is valid.

---

## Troubleshooting

### Step 1 — Check the overlay is loaded

```bash
cat /boot/firmware/config.txt | grep w1
```

Should return: `dtoverlay=w1-gpio,gpiopin=4`

If blank, the line was not saved. Add it and reboot.

---

### Step 2 — Check the bus master appears

```bash
ls /sys/bus/w1/devices/
```

| Result | Meaning |
|---|---|
| `w1_bus_master1` only | Overlay loaded, bus active, sensor not detected |
| `28-xxxxxxxxxxxx` + bus master | Sensor detected — proceed to temperature read |
| Empty | Overlay not loaded or GPIO4 not reaching the bus |

---

### Step 3 — Measure data line voltage (Pi powered on)

Probe the data line (J1 pin 3 or the junction node on the perfboard) with a multimeter.

| Voltage | Meaning |
|---|---|
| 3.0–3.3V | Pull-up working, sensor idle — check GPIO4 connection |
| ~0.5V | Something pulling the line low — see Step 4 |
| ~0V | No pull-up reaching the data node — check R2 wiring |

---

### Step 4 — Isolate sensor vs GPIO4

If the data line reads ~0.5V with the sensor connected:

1. **Power off the Pi** (`sudo shutdown now`, unplug)
2. **Disconnect the JST connector** — remove the sensor entirely
3. **Power the Pi** and measure the data line voltage at the perfboard node

| Voltage with sensor disconnected | Meaning |
|---|---|
| Rises to 3.3V | DS18B20 is damaged — replace the sensor |
| Stays at ~0.5V | GPIO4 is being driven low by the Pi — check overlay and GPIO config |

---

### Step 5 — Continuity checks (Pi powered off)

| Check | Probe points | Expected |
|---|---|---|
| R2 in pull-up path | Sensor data wire → 3.3V rail | ~4.7kΩ (R2 resistance) |
| Data node to GPIO4 | Perfboard data junction → Pi Pin 7 | Continuity (beep / ~0Ω) |
| DS18B20 GND | J1 pin 4 → Pi GND pin | Continuity (beep / ~0Ω) |
| DS18B20 VDD | J1 pin 5 → Pi Pin 1 (3.3V) | Continuity (beep / ~0Ω) |

---

## Gotchas

**1. Damaged DS18B20 pulls data line to ~0.5V**
A failed sensor with an internally shorted open-drain transistor sinks the pull-up current and holds the data line near 0.5V. The circuit checks out perfectly — continuity is good, R2 is wired correctly, VDD is present — but the sensor never appears. Isolate by disconnecting the sensor and measuring the data line; if it rises to 3.3V, replace the sensor.

**2. VDD not connected puts sensor in parasite power mode**
If J1 pin 5 (DS18B20 VDD) is not wired to 3.3V, the sensor draws power from the data line through an internal diode — this is called parasite power mode. The data line clamps to ~0.4–0.6V and the sensor is unreliable or non-functional. Always confirm VDD reads 3.2–3.3V at the sensor.

**3. R2 not at the data junction**
R2 must connect between the 3.3V rail and the specific node shared by J1 pin 3 and the GPIO4 jumper. If R2 is placed one hole off, or its bottom leg lands on a different row, the pull-up does nothing. Verify with a resistance measurement: data node to 3.3V rail should read ~4.7kΩ.

**4. All GND pins are equivalent**
Pi Pin 6 (GND) and Pin 39 (GND) are the same ground plane. If Pin 6 is occupied by another subsystem, use any other GND pin — there is no electrical difference.

**5. The overlay must be in /boot/firmware/config.txt**
On Raspberry Pi OS Bookworm, the boot config is at `/boot/firmware/config.txt` — not `/boot/config.txt` as in older releases. Adding the overlay to the wrong file has no effect.

---

## Verified Working Configuration

| Parameter | Value |
|---|---|
| Sensor | DS18B20 waterproof probe |
| Pull-up resistor | 4.7kΩ (measured 4.17kΩ — within tolerance) |
| GPIO | GPIO4 / Pi Pin 7 |
| Overlay | `dtoverlay=w1-gpio,gpiopin=4` |
| Sensor address | `28-33e70087fda7` |
| Ambient reading at verification | 24.375°C (75.9°F) |

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.0  ·  2026-06-12  ·  published
