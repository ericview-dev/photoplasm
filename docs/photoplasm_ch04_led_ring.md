Photoplasm Quick Start Guide  ·  Chapter 4 — LED Ring · 470nm PWM Control

# **Chapter 4 — LED Ring · 470nm PWM Control**

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

## **Introduction**

The LED ring is the primary light source of the Photoplasm exposure unit. It delivers 470nm blue light to the agar substrate, driving the RsLOV photoreceptor in BioLightV5 to modulate sfGFP expression in the bacterial lawn. This chapter covers hardware design, circuit configuration, PWM control, and the critical irradiance analysis that defines the operating window for biological exposure.

The LED ring operates on a 12V rail switched by an IRLZ44N logic-level MOSFET, controlled by Raspberry Pi 5 GPIO18 (PWM0). PWM duty cycle is the primary software control of delivered irradiance — the relationship between duty cycle and λex (excitation proxy) is characterised in Appendix A: Calibration Protocol.

Understanding the irradiance requirements of BioLightV5 is not optional — the LED hardware must deliver photon dose within a specific window for any biological response to occur. This is the central engineering constraint of the entire Photoplasm system.

## **Parts Inventory**

| **Component** | **Specification** | **Qty** | **Notes** |
| --- | --- | --- | --- |
| Blue LEDs | EBOOT LN0986 ~470nm | 9 | Aim 1 · pending XP-E2 upgrade (Aim 2) |
| MOSFET | IRLZ44N TO-220 | 1 | Logic-level · 55V/47A · 3.3V gate compatible |
| Gate pull-down resistor | 10kΩ | 1 | Prevents floating gate on startup |
| Gate series resistor | 470Ω | 1 | Gate current limiting |
| String current resistors | 120Ω | 3 | One per string · 3 strings of 3 LEDs |
| Breadboard | Full size | 1 | MOSFET control board |
| LED breakout board | 30-row half size | 1 | LED array board |
| Jumper wires | Dupont M-M M-F | assorted | Colour-coded per NS-03 v7 |
| 12V power supply | DC barrel jack | 1 | Shared rail with MOSFET drain |
| JST connectors | PH 2.0mm | 3 | One per LED string · pin 1 positive |
| Cree XP-E2 3-up star | 470nm · 350mA rated | 1 | Aim 2 ordered · awaiting delivery |
| Resistor Aim 2 | 6.8Ω 2W | 1 | Current limit at 12V for XP-E2 |

## **Design Considerations**

### **Why 470nm**

The RsLOV LOV-domain chromophore (FMN) in BioLightV5 has peak absorption at 460–475nm. Photons at this wavelength drive the conformational change in the RsLOV domain that controls LexRO binding to the pColE408 operator. All LED selection, spectral calibration, and irradiance measurement in Photoplasm targets 470nm specifically.

### **Why IRLZ44N**

The IRLZ44N is a logic-level N-channel MOSFET with a gate threshold of 1–2V, meaning it switches fully ON at 3.3V from the Raspberry Pi GPIO without a level shifter. Rds(on) of 22mΩ produces negligible heat at LED array currents. The device is rated to 47A — massively overspec for this application, which means it operates well within its safe operating area and requires no heatsink.

### **Topology — 3 parallel strings of 3 series LEDs**

Nine LEDs arranged in three parallel strings of three series LEDs each. Per string:

+12V → 120Ω → LED(+)→LED(-)→LED(+)→LED(-)→LED(+)→LED(-) → MOSFET Drain Each 470nm LED has Vf ≈ 3.2V. Three in series = 9.6V. Voltage across the 120Ω resistor = 12V − 9.6V = 2.4V. Current per string = 2.4V / 120Ω = 20mA. Total array current = 3 × 20mA = 60mA at full brightness.

### **Ring geometry**

Nine LEDs edge-coupled into a 146mm diameter cast opal acrylic disc (6mm minimum thickness, 9.5mm preferred). Three strings of three form 120° arcs — LEDs at 40° intervals within each arc. The disc acts as a light guide, mixing 51mm LED pitch into a uniform diffuse field at the agar surface. Laser cut at Makerspace Charlotte; kerf compensation ~0.5mm on cut diameter.

## **Irradiance Requirements — RsLOV / eLightOn**

This section defines the photon dose window required to drive meaningful biological response in BioLightV5. All exposure planning, calibration, and hardware selection decisions in Photoplasm trace back to these numbers.

### **What the system requires**

BioLightV5 uses the eLightOn optogenetic system (Li et al., 2020), in which the RsLOV photoreceptor domain from *Rhodobacter sphaeroides* drives repression of sfGFP expression in response to 470nm blue light. The dose-response relationship between irradiance and biological output defines three operating zones — illustrated in **Figure 4.1** below.

{{< figure src="/images/chapters/fig4-1-irradiance-zones.svg" alt="RsLOV / eLightOn irradiance activation zones — 470nm log-scale infographic showing sub-threshold, linear response, and saturation zones with EBOOT and XP-E2 hardware positions" caption="**Figure 4.1** — RsLOV / eLightOn irradiance activation zones. 470nm · BioLightV5 · Li et al. 2020, PMC7102963 · SD37 configuration." class="figure-irradiance"

>}} The three zones represent what blue light dose means for this project:

**Sub-threshold (below 10 µW/cm²):** Too few photons reach the RsLOV chromophore to drive meaningful conformational change. The bacterial culture behaves as though in darkness regardless of whether the LED is on. At this irradiance, no biological image can be written into the lawn — there is no dose-response to exploit. The current EBOOT LED array at ~2.0 µW/cm² sits entirely within this zone.

**Linear response zone (10–500 µW/cm²):** Irradiance in this range produces graded repression of sfGFP expression that is proportional to photon dose. This is the H&D characterisation window — the region where different exposure levels produce distinguishable biological outputs, enabling tonal bacteriography. The half-maximal response point (k½ = 59 µW/cm²) sits in the middle of this zone, marking the steepest part of the dose-response curve and the point of maximum image contrast.

The Cree XP-E2 upgrade is predicted to deliver 100–500 µW/cm², placing the system squarely within this window.

**Saturation (above 500 µW/cm²):** Irradiance beyond this threshold drives maximum repression but produces no additional biological change. Additional photons are wasted. Tonal range collapses — exposures in this zone produce binary output only (fully repressed or not), which eliminates the gradation needed for bacteriographic image detail. Extended operation here risks UV stress artefacts in the bacterial culture.

### **Threshold values (Li 2020, SD37 configuration)**

| **Parameter** | **Symbol** | **Value** | **Units** | **Notes** |
| --- | --- | --- | --- | --- |
| Detection threshold | T_det | ~10 | µW/cm² | Fold-repression first detectable |
| Half-maximal response | k½ | 59 | µW/cm² | 0.059 mW/cm² at 460–465nm |
| Saturation threshold | T_sat | ~500 | µW/cm² | Lower bound; extends to ~1000 |
| Usable H&D window | T_det → T_sat | 10–500 | µW/cm² | ~2 log units of useful range |

### **What this means for the project**

The EBOOT LN0986 LEDs, measured at approximately 2.0 µW/cm² at the plate surface (AS7341, April 2026), sit roughly 50× below the detection threshold. Running biological exposures with the current hardware will produce no detectable optogenetic response — the culture will express sfGFP uniformly regardless of whether a mask pattern is applied, because the light dose never reaches the biological operating window.

This makes the Cree XP-E2 upgrade (Appendix B: Feature Specification, CRE category, Aim 2) the prerequisite for any wet lab exposure work. The XP-E2 at 350–700mA drive current is predicted to deliver 100–500 µW/cm² at the plate surface — spanning the full usable H&D window and bracketing k½ at 59 µW/cm². Appendix A: Calibration Protocol will establish the precise Kc coefficient that maps AS7341 λex readings to actual irradiance at the plate, allowing PWM duty cycle to be dialled to a specific biological dose rather than an arbitrary percentage.

Until the XP-E2 is installed and Kc is characterised, the LED ring chapter covers hardware that is verified electrically but not yet biologically active.

The OLED Digital Image Mask (Chapter 5) introduces an additional optical consideration: the SSD1309 OLED emits additive 470nm light from lit pixels, adding an uncontrolled dose offset (Δ_oled) to whatever the LED array delivers.

At the sub-threshold irradiance of the current EBOOT hardware, this offset is irrelevant — but once the XP-E2 brings the system into the linear zone, Δ_oled must be quantified and incorporated into the calibration model before patterned exposures can be trusted.

## **Wiring**

### **MOSFET control board (breadboard)**

| **Connection** | **From** | **To** | **Notes** |
| --- | --- | --- | --- |
| Gate signal | Pi Pin 12 (GPIO18) | 470Ω → MOSFET Gate | PWM0 hardware PWM |
| Gate pull-down | MOSFET Gate | 10kΩ → GND | Prevents floating gate |
| Drain | 12V rail | MOSFET Drain | Switched output |
| Source | MOSFET Source | GND rail | Common ground |

### **LED array board (half-size breadboard)**

+12V

 │

 ├──[120Ω]──LED(+)─LED(+)─LED(+)──┐

 ├──[120Ω]──LED(+)─LED(+)─LED(+)──┤  → Common cathode bus

 └──[120Ω]──LED(+)─LED(+)─LED(+)──┘

                                    │

                              MOSFET Drain

IRLZ44N flat face (printed side) toward you: Gate (left) · Drain (centre) · Source (right).

### **Pi pin assignments (NS-03 v7)**

| **Pi pin** | **GPIO** | **Function** |
| --- | --- | --- |
| 12 | GPIO18 | PWM0 → MOSFET gate |
| 6 | GND | Common ground reference |

## **Python Scripts**

### **Smoke test — GPIO blink**

Confirms GPIO control before adding PWM or the MOSFET circuit.

#!/usr/bin/env python3

# blink_test.py — Photoplasm Ch4

import lgpio, time

chip = lgpio.gpiochip_open(0) lgpio.gpio_claim_output(chip, 18)

for _ in range(5):

    lgpio.gpio_write(chip, 18, 1)

    time.sleep(0.5)

    lgpio.gpio_write(chip, 18, 0)

    time.sleep(0.5)

lgpio.gpiochip_close(chip) print("Blink test complete")

### **PWM brightness control**

#!/usr/bin/env python3

# led_pwm.py — Photoplasm Ch4

# Usage: python3 led_pwm.py <duty_pct>   e.g. python3 led_pwm.py 75

import lgpio, sys, time

LED_PIN  = 18 PWM_FREQ = 1000   # Hz

duty = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0 duty = max(0.0, min(100.0, duty))

chip = lgpio.gpiochip_open(0) lgpio.gpio_claim_output(chip, LED_PIN) lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, duty) print(f"[LED] PWM active — GPIO18 · {PWM_FREQ}Hz · {duty:.1f}% duty")

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    pass

finally:

    lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, 0)

    lgpio.gpio_write(chip, LED_PIN, 0)

    lgpio.gpiochip_close(chip)

    print("[LED] Shutdown complete")

### **Timed exposure**

#!/usr/bin/env python3

# led_expose.py — Photoplasm Ch4

# Usage: python3 led_expose.py <duty_pct> <seconds>

import lgpio, sys, time

LED_PIN  = 18 PWM_FREQ = 1000

duty    = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0 seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

chip = lgpio.gpiochip_open(0) lgpio.gpio_claim_output(chip, LED_PIN)

print(f"[LED] Exposing {seconds}s at {duty:.1f}% duty") lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, duty) time.sleep(seconds) lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, 0) lgpio.gpio_write(chip, LED_PIN, 0) lgpio.gpiochip_close(chip) print("[LED] Exposure complete")

### **Gamma-corrected fade**

Perceptual smooth fade — required for visual inspection of LED uniformity.

#!/usr/bin/env python3

# led_fade.py — Photoplasm Ch4

import lgpio, time, math

LED_PIN  = 18 PWM_FREQ = 1000 STEPS    = 100 DURATION = 3.0

chip = lgpio.gpiochip_open(0) lgpio.gpio_claim_output(chip, LED_PIN)

delay = DURATION / STEPS for i in range(STEPS + 1):

    gamma = pow(i / STEPS, 2.2)

    lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, gamma * 100)

    time.sleep(delay)

lgpio.tx_pwm(chip, LED_PIN, PWM_FREQ, 0) lgpio.gpio_write(chip, LED_PIN, 0) lgpio.gpiochip_close(chip) print("[LED] Fade complete")

## **Experiments**

### **Experiment 1 — GPIO and MOSFET verification**

**Goal:** Confirm LED turns on and off cleanly under GPIO control before adding PWM.

**Procedure:**

- Wire MOSFET circuit on breadboard per wiring table above

- Run `blink_test.py`

- Observe LED blinks 5× at 0.5s intervals

**Success:** LED responds to GPIO without flicker or partial illumination.

**Status:** ✅ Verified April 2026

### **Experiment 2 — PWM dimming range**

**Goal:** Confirm PWM duty cycle linearly controls LED brightness across 0–100%.

**Procedure:**

- Run `led_pwm.py` at 10%, 25%, 50%, 75%, 100%

- Record AS7341 λex proxy (F2₄₄₅ₙₘ + F3₄₈₀ₙₘ) at each step

- Plot duty cycle vs λex — expect linear relationship

**Success:** λex scales linearly with duty cycle. Gamma artefact not present (hardware PWM is linear — gamma correction applies to perception only, not dose).

**Status:** ✅ Verified — two-step off sequence confirmed (tx_pwm to 0 + gpio_write low)

### **Experiment 3 — Irradiance at plate surface (post XP-E2 upgrade)**

**Goal:** Measure actual irradiance at the agar plate surface after Cree XP-E2 installation. Establish Kc coefficient. Confirm hardware is within the RsLOV linear response zone (T_det–T_sat, 10–500 µW/cm²).

**Procedure:**

- Install Cree XP-E2 with 6.8Ω 2W resistor

- Position AS7341 at plate surface (84mm plate, operating throw distance)

- Run at 50% PWM duty, measure λex at 5-point grid

- Calculate irradiance estimate: compare against Li 2020 SD37 threshold values

- Adjust throw distance or duty cycle until centre reading corresponds to

   approximately k½ equivalent (59 µW/cm²)

**Target:** Centre grid point λex proxy corresponds to irradiance ≥ T_det (10 µW/cm²). Uniformity CV < 20% across 5-point grid.

**Status:** ⏳ Pending XP-E2 hardware delivery · Genspace wetlab May 28+

## **Current State**

| **Item** | **Status** |
| --- | --- |
| IRLZ44N MOSFET circuit | ✅ Verified on breadboard |
| GPIO18 PWM0 confirmed working | ✅ Verified |
| Two-step LED off sequence | ✅ Verified (tx_pwm 0 + gpio_write low) |
| 9× EBOOT LEDs wired 3×3 strings | ✅ Verified · 60mA total |
| AS7341 spectral measurement | ✅ λex proxy confirmed working |
| EBOOT irradiance at plate | ✅ Measured ~2.0 µW/cm² — below T_det |
| Cree XP-E2 ordered | ✅ Ordered · awaiting delivery |
| XP-E2 irradiance measurement | ⏳ Pending hardware + Genspace session |
| Kc calibration coefficient | ⏳ Pending Experiment 3 |
| Biological response confirmed | ⏳ Pending XP-E2 + wet lab |

**Known constraint — current hardware below T_det:** The EBOOT LED array at ~2.0 µW/cm² sits approximately 50× below the eLightOn detection threshold. No biological exposure experiments are possible until the Cree XP-E2 upgrade is installed and irradiance at the plate is verified within the linear response zone. All software and calibration infrastructure is in place — the constraint is purely hardware.

## **Future State — Aim 2**

The Cree XP-E2 3-up star replaces the EBOOT array with a single high-output emitter.

**Circuit changes:**

- Replace 120Ω string resistors with 6.8Ω 2W (rated current at 12V)

- Verify MOSFET duty cycle range at higher current

- Re-run Experiment 3 to establish Kc with XP-E2

**Expected improvement:**

- Irradiance: ~2.0 µW/cm² → 100–500 µW/cm² (predicted)

- Biological operating window: sub-threshold → linear response zone

- Tonal bacteriography: not possible → fully enabled

## **Related Chapters**

- Chapter 3 — Calibration: H&D curve methodology and Kc coefficient

  derivation. Kc maps AS7341 λex readings to irradiance at the plate surface.

- Chapter 5 — OLED Digital Image Mask: SSD1309 additive 470nm emission (Δ_oled)

  adds to LED dose once XP-E2 brings system into the linear zone. Must be quantified before patterned exposures.

- Appendix B: Feature Specification — CRE category (Aim 2 / Cree XP-E2): Full
  upgrade specification, wiring changes, and post-upgrade irradiance
  verification.

## **Reference**

Li X, Zhang C, Xu X, Miao J, Yao J, Liu R, Zhao Y, Chen X, Yang Y.

A single-component light sensor system allows highly tunable and direct activation of gene expression in bacterial cells. *Nucleic Acids Research.* 2020;48(6):e33. doi:10.1093/nar/gkaa044. PMID 31989175. PMC7102963.

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.0  ·  2026-05-17  ·  published