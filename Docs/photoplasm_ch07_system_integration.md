Photoplasm Quick Start Guide  ·  Chapter 7 — System Integration

# **Chapter 7 — System Integration**

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

## **Introduction**

This chapter brings together all four Photoplasm hardware subsystems for the first time and validates that they operate correctly as a single integrated unit. Each subsystem has been individually verified in its own chapter — the purpose here is to confirm they work together without interference, establish the correct operational sequence, and produce a first combined exposure run.

The integration order follows the physical stack from top to bottom:

┌─────────────────────────────────┐

│  LED Ring · 470nm               │  ← light source (top)

│  GPIO18 · PWM0 · 12V            │    Chapter 4

├─────────────────────────────────┤

│  OLED Digital Image Mask        │  ← spatial light modulator

│  SSD1309 · SPI · GPIO8/10/11    │    Chapter 5

│            /22/23/24/25/27      │

├─────────────────────────────────┤

│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐   │

│    Agar Plate · 84mm          │  ← culture surface

│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘   │

├─────────────────────────────────┤

│  AS7341 Wavelength Monitor      │  ← irradiance measurement (plate level)

│  I²C · 0x39 · GPIO2/3          │    Chapter 3 / Chapter 4

├─────────────────────────────────┤

│  Heater Perfboard               │  ← thermal control (below plate)

│  PTC · DS18B20 · GPIO13/4       │    Chapter 6

└─────────────────────────────────┘

This layered architecture means every photon delivered to the culture has been spatially defined by the OLED mask, measured in real time by the AS7341, and delivered to a culture maintained at the correct biological operating temperature by the heater. All four must work reliably together before biological exposure experiments can begin.

## **Bus and Pin Summary**

A key integration requirement is that four subsystems share a single Raspberry Pi 5 without bus conflicts. The design deliberately separates each subsystem onto a different interface:

| **Subsystem** | **Interface** | **Pi pins** | **Notes** |
| --- | --- | --- | --- |
| LED Ring | PWM (GPIO18) | Pin 12 | Hardware PWM0 — dedicated |
| OLED Mask | SPI0 | Pins 9/13/17/19/22/23/24 | SPI bus exclusive to OLED |
| AS7341 | I²C (addr 0x39) | Pins 1/3/5/14 | I²C bus shared (0x39 only) |
| Heater PTC | PWM (GPIO13) | Pin 33 | Hardware PWM1 — dedicated |
| DS18B20 | 1-Wire (GPIO4) | Pin 7 | 1-Wire bus separate from I²C |
| Shutdown button | GPIO21 | Pin 40 | Momentary pull-up |

**No bus conflicts exist by design.** PWM0 and PWM1 are independent hardware channels. SPI and I²C are separate buses. 1-Wire is a distinct protocol on its own GPIO pin. The AS7341 at 0x39 and the OLED SSD1309 do not share an I²C address — the SSD1309 uses SPI, not I²C.

The only shared resource is the 3.3V AUX-Power rail (Pin 17), which distributes to the OLED VCC, AS7341 VCC, and DS18B20 VDD via the LED Breadboard. Total 3.3V draw from these subsystems is well within the Pi 5's 3.3V rail capacity.

## **Integration Prerequisites**

Before running the combined integration test, confirm each subsystem passes its individual smoke test:

| **Subsystem** | **Smoke test** | **Expected result** |
| --- | --- | --- |
| LED Ring | `led_pwm.py 50` | LEDs illuminate at ~50% brightness |
| OLED Mask | `oled_smoke_test.py` | Crosshair visible on OLED |
| AS7341 | `i2cdetect -y 1` → `0x39` | Sensor detected |
| Heater PTC | `ls /sys/bus/w1/devices/` → `28-xxxx` | DS18B20 detected |
| Temperature | Read script returns ~20–25°C (ambient) | Correct ambient reading |

All five must pass before proceeding. Any failure here is a wiring or library issue in the individual subsystem — resolve using the relevant chapter before continuing.

## **Subsystem Integration — Top to Bottom**

### **1 · LED Ring (top · light source)**

The LED ring is the first element in the optical path. It is also the source of the 470nm photons that drive the RsLOV photoreceptor in BioLightV5. In the integrated system, the LED ring operates under PWM control from the exposure script — duty cycle and duration define the dose.

**Integration check:** With all other subsystems powered and the OLED displaying a full-white mask, run the LED at 50% duty cycle and confirm the AS7341 λex proxy (F2 + F3 channels) reads above the dark baseline. This confirms the optical path from source through mask to sensor is intact.

**Known integration behaviour:** The SSD1309 OLED emits additive 470nm light from its lit pixels. When the LED ring is running, the combined λex reading includes both sources. Record the OLED-only λex (LED off, OLED white) as Δ_oled. This offset is subtracted from all combined readings in the calibration model (Appendix A).

### **2 · OLED Digital Image Mask (middle · spatial modulator)**

The OLED sits below the LED ring in the optical path, defining the spatial pattern of light that reaches the plate. In integration, the OLED is loaded with the exposure mask before the LED is activated — the sequence matters.

**Integration sequence (OLED):**

- Load mask bitmap onto OLED (`oled_mask.py pattern.png`)

- Confirm crosshair or mask pattern is visible on OLED

- Activate LED ring — exposure begins

- At exposure end: extinguish LED first, then clear OLED

**Integration check:** With OLED displaying a half-black / half-white test pattern, confirm AS7341 λex reading is higher when sensor is positioned under the white half than the black half. This validates that the mask is spatially modulating the 470nm dose as expected.

**Known integration issue — Δ_oled offset:** Until Experiment 1 in Chapter 5 is run, the exact additive contribution of the SSD1309 pixels to λex is unquantified. For integration testing purposes, note whether OLED-on vs OLED-off produces a measurable λex difference at the AS7341. Record both values.

### **3 · AS7341 Wavelength Monitor (plate level · irradiance reference)**

The AS7341 sits at plate level — the same optical plane as the agar surface.

Its role in the integrated system is to provide real-time λex measurement during every exposure, confirming dose delivery and flagging any drift.

**Integration check:** With LED ring and OLED both running at steady state, the AS7341 should return stable λex readings with low variance over 10 seconds (CV < 5% between consecutive readings). Instability here indicates mechanical vibration, loose connections on the I²C bus, or ambient light leakage into the dark chamber.

**Integration behaviour — I²C and SPI coexistence:** I²C (AS7341) and SPI (OLED) operate on separate buses and do not interfere. This was verified in the April 2026 integration session. No timing delays or bus arbitration are needed between AS7341 reads and OLED writes.

**AS7341 gain setting in integration:** Use 256× gain for all Aim 1 integration runs. The Kc calibration coefficient (Appendix A) maps 256× gain counts to absolute irradiance once the XP-E2 upgrade is installed. Until then, λex counts are relative units.

### **4 · Heater Perfboard (below plate · thermal control)**

The Heater Perfboard operates as a background process — it maintains culture temperature at 37°C throughout the exposure run without interrupting the optical subsystems. The DS18B20 temperature probe mounts in the culture stage wall, reading culture-zone air temperature rather than heater surface temperature.

**Integration check:** Before loading any culture, run the heater loop to 37°C and confirm the DS18B20 reads stable temperature (±0.5°C over 2 minutes) at setpoint. This confirms the PTC heater, MOSFET drive circuit, and 1-Wire temperature readback are all functioning.

**Integration behaviour — thermal and optical independence:** GPIO13 (heater PWM1) and GPIO18 (LED PWM0) are independent hardware PWM channels with no cross-talk. DS18B20 1-Wire (GPIO4) and AS7341 I²C (GPIO2/3) operate on separate buses. The heater can be running at any duty cycle without affecting LED intensity, AS7341 readings, or OLED display.

**Thermal settling time:** Allow 5–10 minutes for the heater to reach 37°C setpoint and stabilise before loading a culture plate. Run the DS18B20 read loop in a terminal window during this warm-up period to confirm stable temperature.

**Temperature during exposure:** The heater control loop should run continuously throughout the exposure. A temperature drop of more than 2°C during an exposure run is a flag — check PTC element connection and 12V supply rail.

## **Operational Sequence — Full Integrated Exposure**

The correct order of operations for a combined Photoplasm exposure run:

1.  POWER ON          12V supply · Pi boot · SSH connect

2.  HEATER START      python3 heater.py --setpoint 37

                      → wait for DS18B20 to read 37°C ± 0.5°C

                      → allow 5–10 min thermal settling

3.  OLED INIT         python3 oled_smoke_test.py

                      → confirm crosshair visible

                      → load exposure mask: python3 oled_mask.py mask.png

4.  AS7341 DARK       python3 as7341_read.py --duration 10

                      → record dark baseline λex (all lights off)

                      → target: F2+F3 < 10 counts at 256× gain

5.  LED VERIFY        python3 led_pwm.py 10

                      → confirm AS7341 λex rises above dark baseline

                      → LED off: python3 led_pwm.py 0

6.  LOAD CULTURE      place agar plate on culture stage

                      → confirm plate seated correctly

7.  CONFIRM TEMP      DS18B20 reading must be 37°C ± 0.5°C before exposure

8.  EXPOSE            python3 led_expose.py <duty> <seconds>

                      → AS7341 logs λex throughout exposure

                      → DS18B20 monitors temperature throughout

9.  EXTINGUISH        LED off → OLED clear → log exposure parameters

10. INCUBATE          remove plate to dark incubator

                      → heater continues running if extended incubation

                      → log: duty cycle · duration · λex mean · temp mean

11. SHUTDOWN          python3 oled_off.py

                      → heater setpoint to 0

                      → gpio cleanup

## **Combined Integration Test Script**

The script below runs all four subsystems in sequence, performs the dark baseline check, runs a 10-second verification exposure, and logs the key metrics to a timestamped CSV. This is the minimum viable integration test — run it before every biological exposure session.

#!/usr/bin/env python3

# photoplasm_integration_test.py

# Validates all four subsystems in sequence before a biological exposure run.

# Logs: temp, dark_lx, expose_lx, delta_lx, oled_offset to timestamped CSV.

import lgpio, time, glob, csv, datetime from luma.core.interface.serial import spi as luma_spi from luma.oled.device import ssd1309 from PIL import Image, ImageDraw

# ── pin assignments (NS-03 v7) ──────────────────────────────────────────────

LED_PIN    = 18   # GPIO18 PWM0 HEAT_PIN   = 13   # GPIO13 PWM1 TEMP_PIN   = 4    # GPIO4  1-Wire (read via /sys/bus)

OLED_DC    = 25   # GPIO25 OLED_RST   = 27   # GPIO27 PWM_FREQ   = 1000 # Hz

# ── helpers ──────────────────────────────────────────────────────────────────

def read_temp():

    devs = glob.glob('/sys/bus/w1/devices/28*')

    if not devs:

        return None

    with open(devs[0] + '/w1_slave') as f:

        lines = f.readlines()

    if 'YES' in lines[0]:

        return float(lines[1].split('t=')[1]) / 1000.0

    return None

def read_as7341_lx():

    """Read λex proxy — F2+F3 counts. Returns (f2, f3, lx)."""

    try:

        import board, busio, adafruit_as7341

        i2c = busio.I2C(board.SCL, board.SDA)

        sensor = adafruit_as7341.AS7341(i2c)

        sensor.gain = adafruit_as7341.Gain.GAIN_256X

        time.sleep(0.1)

        f2 = sensor.channel_445nm

        f3 = sensor.channel_480nm

        return f2, f3, f2 + f3

    except Exception as e:

        print(f"[AS7341] Read error: {e}")

        return 0, 0, 0

# ── main integration test ────────────────────────────────────────────────────

def run():

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file  = f"integration_test_{timestamp}.csv"

    results   = {}

    print("\n=== PHOTOPLASM INTEGRATION TEST ===")

    print(f"Timestamp: {timestamp}\n")

    # Step 1 — Temperature check

    print("[1/5] Heater + DS18B20 check")

    temp = read_temp()

    if temp is None:

        print("  FAIL — DS18B20 not detected. Check 1-Wire wiring.")

        return

    print(f"  Current temperature: {temp:.2f}°C")

    results['temp_c'] = round(temp, 2)

    if temp < 35 or temp > 39:

        print(f"  WARNING — temperature outside 37°C ± 2°C target")

    # Step 2 — OLED check

    print("[2/5] OLED initialisation")

    try:

        serial  = luma_spi(device=0, port=0, bus_speed_hz=8000000,

                           gpio_DC=OLED_DC, gpio_RST=OLED_RST)

        display = ssd1309(serial, width=128, height=64, rotate=0)

        img     = Image.new("1", (128, 64), "black")

        draw    = ImageDraw.Draw(img)

        draw.line([(64, 0), (64, 64)], fill="white", width=1)

        draw.line([(0, 32), (128, 32)], fill="white", width=1)

        display.display(img)

        print("  OLED crosshair displayed — check visually")

        results['oled'] = 'ok'

    except Exception as e:

        print(f"  FAIL — OLED error: {e}")

        results['oled'] = 'fail'

        return

    # Step 3 — AS7341 dark baseline

    print("[3/5] AS7341 dark baseline (10s)")

    time.sleep(1)

    f2, f3, dark_lx = read_as7341_lx()

    print(f"  Dark baseline — F2: {f2}  F3: {f3}  λex: {dark_lx}")

    results['dark_lx'] = dark_lx

    if dark_lx > 50:

        print("  WARNING — dark baseline above 50 counts. Check ambient light sealing.")

    # Step 4 — LED ring at 10% duty, read λex

    print("[4/5] LED ring verification (10% duty · 3s)")

    chip = lgpio.gpiochip_open(0)

    lgpio.gpio_claim_output(chip, LED_PIN)

    lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, 10.0)

    time.sleep(1)

    f2, f3, expose_lx = read_as7341_lx()

    lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, 0)

    lgpio.gpio_write(chip, LED_PIN, 0)

    lgpio.gpiochip_close(chip)

    delta = expose_lx - dark_lx

    print(f"  LED-on λex: {expose_lx}  delta: {delta}")

    results['expose_lx']  = expose_lx

    results['delta_lx']   = delta

    if delta < 10:

        print("  WARNING — LED delta < 10 counts. Check LED wiring and MOSFET.")

    # Step 5 — OLED off / measure offset

    print("[5/5] OLED additive offset (Δ_oled measurement)")

    img_white = Image.new("1", (128, 64), "white")

    display.display(img_white)

    time.sleep(0.5)

    _, _, oled_on_lx  = read_as7341_lx()

    img_black = Image.new("1", (128, 64), "black")

    display.display(img_black)

    time.sleep(0.5)

    _, _, oled_off_lx = read_as7341_lx()

    oled_offset = oled_on_lx - oled_off_lx

    print(f"  OLED white λex: {oled_on_lx}  OLED black λex: {oled_off_lx}  Δ_oled: {oled_offset}")

    results['oled_offset'] = oled_offset

    display.cleanup()

    # Summary

    print("\n=== RESULTS ===")

    passed = (results.get('oled') == 'ok'

              and results.get('delta_lx', 0) >= 10

              and read_temp() is not None)

    print(f"  Temperature:      {results.get('temp_c')}°C")

    print(f"  Dark baseline:    {results.get('dark_lx')} counts")

    print(f"  LED delta:        {results.get('delta_lx')} counts")

    print(f"  Δ_oled:           {results.get('oled_offset')} counts")

    print(f"  Overall:          {'PASS' if passed else 'FAIL'}")

    # Log to CSV

    with open(log_file, 'w', newline='') as f:

        w = csv.DictWriter(f, fieldnames=results.keys())

        w.writeheader()

        w.writerow(results)

    print(f"\nLogged to {log_file}")

if __name__ == '__main__':

    run()

## **Experiments**

### **Experiment 1 — Bus isolation verification**

**Goal:** Confirm that all four subsystems can run simultaneously without interfering with each other's readings or control signals.

**Procedure:**

- Start heater loop in background — target 37°C

- Display OLED crosshair

- Run LED ring at 50% duty

- Read AS7341 continuously for 30 seconds — log λex every second

- During the 30 seconds, toggle OLED between black and white at 5s intervals

- Confirm λex changes cleanly with OLED state, with no artefacts from heater

**Success criteria:**

- AS7341 CV < 5% within each OLED state

- OLED toggle produces clean step change in λex (no ringing or drift)

- Temperature stable ± 0.5°C throughout

- No I²C errors, no SPI errors, no PWM glitches in Pi system log

**Status:** [TBD — bench test]

### **Experiment 2 — Thermal stability during exposure**

**Goal:** Confirm heater maintains 37°C setpoint throughout a 30-minute simulated exposure run while all other subsystems are active.

**Procedure:**

- Bring heater to 37°C and confirm stable

- Start LED ring at 50% duty + OLED mask + AS7341 read loop

- Log temperature every 60 seconds for 30 minutes

- Log λex every 60 seconds

**Success criteria:**

- Temperature remains 37°C ± 1°C throughout 30-minute run

- λex drift < 5% over the same period (confirms LED stability)

- No thermal effect on AS7341 readings

**Status:** [TBD — Genspace wetlab, May 28+]

### **Experiment 3 — First combined dark-field check**

**Goal:** Confirm the frustum cone dark chamber eliminates ambient light contamination with all subsystems running.

**Procedure:**

- Assemble full Photoplasm stack with frustum cone in place

- All subsystems active — heater at 37°C, OLED black mask, LED off

- Read AS7341 for 60 seconds — log λex

- Target: λex (dark, assembled) ≈ λex (dark, bench open)

**Success criteria:** Assembled dark-field baseline within 10 counts of open-bench dark baseline. Any excess indicates light leak in the cone assembly.

**Status:** [TBD]

## **Current State**

| **Item** | **Status** |
| --- | --- |
| LED ring individual smoke test | ✅ Verified (Ch. 4) |
| OLED individual smoke test | ✅ Verified (Ch. 5) |
| AS7341 I²C at 0x39 | ✅ Verified (Ch. 3) |
| DS18B20 1-Wire detected | ✅ Verified (Ch. 6) |
| Bus isolation confirmed (I²C + SPI no conflict) | ✅ Verified Apr 2026 |
| PWM0 + PWM1 independent | ✅ Confirmed by design |
| Combined integration test script | ✅ Written — not yet run on full stack |
| Experiment 1 — bus isolation run | ⏳ Pending bench test |
| Experiment 2 — thermal stability | ⏳ Pending Genspace May 28+ |
| Experiment 3 — dark-field check | ⏳ Pending full stack assembly |
| Biological exposure readiness | ⏳ Pending XP-E2 + Kc + all experiments |

## **Readiness Checklist — Biological Exposure Gate**

All items below must be ✅ before running BioLightV5 biological exposures:

- [ ] All four subsystems pass individual smoke tests

- [ ] Integration test script runs to PASS

- [ ] DS18B20 reads 37°C ± 0.5°C at culture stage

- [ ] AS7341 dark baseline < 50 counts (dark chamber sealed)

- [ ] LED delta λex > 10 counts at 10% duty (LED + MOSFET functional)

- [ ] Δ_oled quantified and entered in calibration model

- [ ] Cree XP-E2 installed (Appendix B: Feature Specification, CRE category)

- [ ] Kc irradiance coefficient established (Appendix A)

- [ ] Irradiance confirmed within RsLOV linear zone (T_det – T_sat, Ch. 4)

- [ ] Exposure mask verified at plate surface (spatial uniformity check, Ch. 5)

## **Future State**

**Flask GUI integration (Chapter 8):** All four subsystems will be controllable from a single web UI served from the Pi. The integration test script becomes the pre-flight check accessible from the browser before an exposure session.

**Unified logging:** Temperature (DS18B20), irradiance (AS7341 λex), and exposure parameters (duty cycle, duration, mask file) will write to a single timestamped CSV per session — enabling correlation of temperature drift with biological output in post-processing.

**RPi Camera Module:** Once mounted (oblique or under-plate), the camera feeds a fluorescence analytics pipeline that completes the measurement loop from delivered dose through biological output.

## **Related Chapters**

- Chapter 3 — Wavelength Sensor (AS7341): The sensor build, gain
  characterisation, and dark-chamber test matrix this chapter depends on.

- Appendix A: Calibration Protocol — Kc coefficient and H&D curve characterisation

  depend on AS7341 integrated with the LED ring.

- Chapter 4 — LED Ring: Individual LED subsystem, irradiance thresholds,

  XP-E2 upgrade prerequisite.

- Chapter 5 — OLED Digital Image Mask: Δ_oled offset measured in this

  chapter's Experiment 1 feeds the Appendix A calibration model.

- Chapter 6 — Incubation Heater Perfboard: Full heater hardware

  documentation. This chapter assumes Ch. 6 is complete.

- Chapter 8 — GUI / Flask: Next step after integration is validated —

  wraps all four subsystems in a browser interface.

- Appendix B: Feature Specification — CRE category (Aim 2 / Cree XP-E2): Upgrade required before biological

  exposure gate can be cleared.

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-05-17  ·  draft