Photoplasm Quick Start Guide  ·  Appendix C: Pi 5 Pinout — NS-03 v8

# Appendix C: Pi 5 Pinout — NS-03 v8

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 8  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

## **Document Metadata**

| **Project** | Photoplasm |
| --- | --- |
| **Subsystem** | Hardware / Pin Assignment |
| **Version** | v8 |
| **Status** | PWM channels separated; heater PWM1 paper-assigned (not yet bench-tested) |
| **Date** | 2026-05-17 |
| **Supersedes** | NS-03 v7 (Apr 2026) |
| **Repository** | github.com/ericview-dev/photoplasm |
| **Author** | Eric Schneider |

Canonical hardware reference for the Photoplasm optogenetics exposure unit (Raspberry Pi 5, hostname eyepi, user ericview). This document is the authoritative pin assignment source; any code, schematic, or chapter that references pin numbers must reconcile to this file.

## **Test Status Legend**

| **Symbol** | **Meaning** |
| --- | --- |
| **✅ ACTIVE** | Wired, code-verified, bench-confirmed |
| **⚠️ ASSIGNED** | Pin reserved in software/docs; NOT yet bench-tested |
| 🔒 RESERVED | Held for future use; no current consumer |
| — | Power, ground, or no-connect |

## **Group A — Hardware PWM**

Pi 5 exposes two independent hardware PWM channels. Each channel can route to one of two GPIOs; the channels are independent of each other and require no mutex or time-multiplexing in software.

| **Channel** | **GPIO** | **Pin** | **Consumer** | **Driver** | **Status** |
| --- | --- | --- | --- | --- | --- |
| **PWM0** | GPIO18 | **12** | LED ring (470 nm, 9× via IRLZ44N) | lgpio.tx_pwm | **✅ ACTIVE** |
| **PWM1** | GPIO13 | **33** | Heater MOSFET (PTC element, Board B) | lgpio.tx_pwm | **⚠️ NOT YET TESTED** |

**PWM0 alternate (unused): **GPIO12 / Pin 32 — conflicts with GPIO18 if enabled.

**PWM1 alternate (blocked): **GPIO19 / Pin 35 — occupied by OLED SPI block.

### **Heater PWM1 bench-test gate**

Before promoting Pin 33 / GPIO13 to ✅ ACTIVE, complete:

**1. **lgpio claim GPIO13 as output, tx_pwm at 10 % duty, low frequency (1–10 Hz appropriate for thermal mass).

**2. **Confirm PWM waveform on MOSFET gate via scope or indirect LED-on-gate visual check.

**3. **Run LED PWM0 (GPIO18) and heater PWM1 (GPIO13) simultaneously; confirm no cross-channel interference.

**4. **Confirm DS18B20 reads valid temperature while heater duty cycles.

**5. **Document chosen PWM frequency in code comments and update this file to v9.

*Until those five steps are complete, Ch. 8 Flask UI must treat the heater endpoint as simulation-only (no actual GPIO13 output) or behind an explicit --enable-heater-pwm flag.*

## **Group B — Communication Buses**

| **Bus** | **Pins** | **GPIOs** | **Consumer** | **Address / CS** | **Status** |
| --- | --- | --- | --- | --- | --- |
| I²C | 3, 5 | GPIO2 (SDA), GPIO3 (SCL) | AS7341 spectral sensor | 0x39 | ✅ ACTIVE |
| SPI | 19, 21, 23, 24 | GPIO10 (MOSI), GPIO9 (MISO), GPIO11 (SCLK), GPIO8 (CE0) | OLED SSD1309 image mask | CE0 | ✅ ACTIVE |
| OLED control | 13, 17, 22 | GPIO27 (DC), GPIO11/shared, GPIO25 (RST) | OLED SSD1309 control lines | — | ✅ ACTIVE |
| 1-Wire | 7 | GPIO4 | DS18B20 temperature sensor | — | ✅ ACTIVE |

**Note on Pin 13 vs GPIO13 confusion: **Pin 13 is GPIO27 (in the OLED block). GPIO13 is Pin 33 (the new heater PWM1). Always use the Pin/GPIO pair when discussing assignments.

## **Group C — Discrete GPIO**

| **GPIO** | **Pin** | **Consumer** | **Mode** | **Status** |
| --- | --- | --- | --- | --- |
| GPIO21 | 40 | Shutdown button | Input, momentary, pull-up | ✅ ACTIVE |

## **Group D — Power ****&**** Ground**

| **Rail** | **Pin** | **Destination** | **Notes** |
| --- | --- | --- | --- |
| 3V3 | 1 | AS7341 only | Dedicated to sensor — keeps noise off LED rail |
| 3V3 | 17 | LED board right rail (+) | Logic-level supply; OLED + Heater Board tap I10 / H8 off this rail |
| GND | 6 | LED board right rail (−) | Common ground reference |

*12 V rail for LED drive and heater PTC is external (not from Pi headers). GPIO PWM controls IRLZ44N MOSFETs that switch the 12 V rail.*

## **Group E — DS18B20 JST Pin Mapping (Sensor Side)**

Wire colors follow the OEM cable convention (where applicable, vendor-dependent).

| **JST Pin** | **Function** | **Wire Color (OEM)** | **Pi Connection** |
| --- | --- | --- | --- |
| **J3** | Data | Orange / Yellow | Pin 7 / GPIO4 (1-Wire) |
| **J4** | GND | Gray / Black | Pi GND |
| **J5** | VDD | Blue / Red | Pi 3V3 |

## **Group F — Heater PTC Element JST Mapping (Board B)**

| **JST Pin** | **Function** | **Connection** |
| --- | --- | --- |
| **J1** | PTC+ | 12 V rail (MOSFET drain side) |
| **J2** | PTC− | GND via IRLZ44N source |

Heater MOSFET gate is driven by GPIO13 / Pin 33 (PWM1) via Heater Board's gate resistor network. **Not yet bench-verified — see Group A test gate.**

## **Pinout Index (Pin Number → Function)**

| **Pin** | **GPIO** | **Function** | **Status** |
| --- | --- | --- | --- |
| 1 | — | 3V3 → AS7341 | ✅ |
| 3 | GPIO2 | I²C SDA → AS7341 | ✅ |
| 5 | GPIO3 | I²C SCL → AS7341 | ✅ |
| 6 | — | GND → LED rail (−) | ✅ |
| 7 | GPIO4 | 1-Wire → DS18B20 Data | ✅ |
| 9 | — | SPI block (OLED) | ✅ |
| **12** | **GPIO18** | **PWM0 → LED MOSFET gate** | **✅** |
| 13 | GPIO27 | SPI block (OLED control) | ✅ |
| 14 | — | GND (AS7341 / I²C) | ✅ |
| 17 | — | 3V3 → LED rail (+) | ✅ |
| 19 | GPIO10 | SPI MOSI (OLED) | ✅ |
| 21 | GPIO9 | SPI MISO (OLED) | ✅ |
| 22 | GPIO25 | OLED RST | ✅ |
| 23 | GPIO11 | SPI SCLK (OLED) | ✅ |
| 24 | GPIO8 | SPI CE0 (OLED) | ✅ |
| **33** | **GPIO13** | **PWM1 → Heater MOSFET gate** | **⚠️ NOT YET TESTED** |
| 40 | GPIO21 | Shutdown button | ✅ |

*All other pins: unused / no-connect. Available for future expansion (camera module, additional sensors, Aim 2 transmissive LCD upgrade).*

## **Change Log**

### **v8 — 2026-05-17**

• Promoted heater PWM: Pin 33 / GPIO13 moved from 🔒 RESERVED to ⚠️ ASSIGNED (PWM1 channel).

• Reclassified DS18B20: Pin 7 / GPIO4 explicitly listed as ✅ ACTIVE 1-Wire (was implicit under "reserved temp/bed" in v7).

• Resolved PWM contention: LED and heater now on independent hardware PWM channels (PWM0 and PWM1); no time-multiplexing required.

• Added test-gate criteria for promoting GPIO13 from ⚠️ to ✅.

• Added pin-number → GPIO-number disambiguation note (Pin 13 ≠ GPIO13).

### **v7 — Apr 2026**

• LED PWM0 verified at GPIO18.

• OLED SPI block locked.

• AS7341 I²C confirmed at 0x39.

• DS18B20 JST color mapping documented.

• Heater pins (7, 33) marked reserved pending Board B design.

## **References**

• Board B (Heater Board) circuit design: SpacePlacer v0.1 export, github.com/ericview-dev/spaceplacer • LED PWM build notes: github.com/ericview-dev/photoplasm, dev branch, photoplasm_cal02.py • HTGAA 2026 final project Section 4 (Protocol Design 2): AS7341 calibration + duty cycle reference • Chapter 7 (System Integration) of the Photoplasm Guide: full hardware stack context • Chapter 8 (Flask UI) of the Photoplasm Guide: consumer of this pin table — to be drafted in dedicated session

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v8  ·  2026-05-17  ·  working draft