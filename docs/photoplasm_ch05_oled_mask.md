Photoplasm Quick Start Guide  ·  Chapter 5 — OLED Digital Image Mask

# **Chapter 5 — OLED Digital Image Mask**

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.2.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

## **Introduction**

The OLED Digital Image Mask is the spatial light modulator (SLM) component of the Photoplasm exposure unit. It sits between the 470nm LED array and the agar plate, selectively blocking or transmitting light to define the exposure pattern printed into the bacterial lawn.

In photographic terms the OLED performs the same function as a photographic negative or enlarger mask: it encodes the image geometry that the biological emulsion will record. A white pixel on the OLED transmits light to the plate below; a black pixel blocks it. The pattern is rendered digitally from a bitmap and updated between exposures without any physical darkroom manipulation.

This chapter covers the current Aim 1 implementation using the Waveshare 1.51"

Transparent OLED (SSD1309 driver, 128×64 pixels) and the planned Aim 2 upgrade to an ILI9341 transmissive LCD. Both are documented here so the chapter remains valid across hardware generations.

*Irradiance and activation threshold: The light dose delivered through the mask*

*must be sufficient to drive the RsLOV photoreceptor in BioLightV5 into its linear*

*response zone. Irradiance calculations, RsLOV threshold values (T_det, k½, T_sat),*

*and hardware comparison between EBOOT LEDs and Cree XP-E2 are covered in*

*Chapter 4 — LED Ring. This chapter covers mask optics and software control only.*

## **Design Considerations**

### **Why a transparent OLED for Aim 1**

The Waveshare SSD1309 OLED was selected for Aim 1 because it is genuinely transparent when pixels are off — the glass substrate allows 470nm light to pass through unlit areas, making it usable as an in-line mask without a separate projection path.

**Key tradeoff — additive 470nm emission:** The SSD1309 emits light at approximately 470nm from its own lit pixels. This is the same wavelength that activates the RsLOV photoreceptor in BioLightV5. Any lit (white) pixel on the OLED adds to the eLightOn repression dose rather than simply transmitting the LED array light — it is additive, not purely transmissive. In BioLightV5 / eLightOn, blue light drives repression of sfGFP expression, so any uncontrolled additive dose from the mask itself reduces output in ways that are not encoded in the mask pattern.

For Aim 1 calibration and initial pattern work this is acceptable. The additive OLED contribution is documented as a fixed offset (Δ_oled) in the calibration model (see Appendix A: Calibration Protocol), and patterns are rendered with white pixels defining the exposure zone and black pixels blocking the border.

### **Why ILI9341 for Aim 2**

The ILI9341 is a transmissive LCD — it modulates an external light source rather than emitting its own. With the onboard backlight disabled (BL pin to GND), the panel becomes a pure spatial light modulator: the 470nm LED array is the sole light source and the ILI9341 controls transmission pixel by pixel. This eliminates the additive emission problem entirely.

At 320×240 resolution (versus 128×64 on the SSD1309) the ILI9341 also increases spatial resolution approximately 10× — finer pattern edges and more image detail for bacteriographic work.

**Polarizer transmission loss:** The ILI9341 absorbs approximately 50% of incident irradiance through its polarizer stack. At the Cree XP-E2 predicted irradiance of 100–500 µW/cm², transmitted dose at the plate surface drops to 50–250 µW/cm² — still within the eLightOn linear response zone (T_det to T_sat). See Chapter 4 for the full irradiance analysis and Appendix B: Feature Specification (CRE category) for the XP-E2 upgrade details.

## **Parts Inventory**

### **Aim 1 — Current hardware**

| **Component** | **Part** | **Interface** | **Pi pins** |
| --- | --- | --- | --- |
| OLED display | Waveshare 1.51" Transparent OLED | SPI (SSD1309) | Pins 9/13/17/19/22/23/24 |
| Display driver | luma.oled + luma.core | Python library | — |
| Image library | Pillow (PIL) | Python library | — |

### **Aim 2 — Planned replacement**

| **Component** | **Part** | **Interface** | **Notes** |
| --- | --- | --- | --- |
| Transmissive LCD | ILI9341 2.4" 320×240 | SPI | BL pin to GND |
| Display driver | adafruit-circuitpython-ili9341 | Python library | Replaces luma.oled |
| Image library | Pillow (PIL) | Python library | Same API |

## **Wiring — Aim 1 (SSD1309 OLED)**

The SSD1309 uses SPI0. Pin assignments per NS-03 v7 pin table.

| **OLED pin** | **Function** | **Pi pin** | **GPIO** | **Notes** |
| --- | --- | --- | --- | --- |
| VCC | Power | 17 | 3.3V | AUX-Power rail from LED Breadboard |
| GND | Ground | 9 | GND | Shared ground |
| DIN | MOSI data | 19 | GPIO10 | SPI0 MOSI |
| SCLK | Clock | 23 | GPIO11 | SPI0 SCLK |
| CS | Chip select | 24 | GPIO8 | SPI0 CE0 |
| DC | Data / Command | 22 | GPIO25 | Cmd vs data byte select |
| RST | Reset | 13 | GPIO27 | Hardware reset line |

**Enable SPI:** sudo raspi-config  # Interface Options → SPI → Enable sudo reboot **Install luma.oled:** pip install luma.oled pillow

## **Wiring — Aim 2 (ILI9341 LCD)**

Same SPI0 bus and GPIO assignments as SSD1309. Critical difference:

**BL/LED pin to GND** to disable the onboard backlight.

| **ILI9341 pin** | **Function** | **Pi pin** | **GPIO** | **Notes** |
| --- | --- | --- | --- | --- |
| VCC | Power | 17 | 3.3V |  |
| GND | Ground | 9 | GND |  |
| CS | Chip select | 24 | GPIO8 | SPI0 CE0 |
| RST | Reset | 13 | GPIO27 |  |
| DC | Data / Command | 22 | GPIO25 |  |
| MOSI/SDI | Data | 19 | GPIO10 | SPI0 MOSI |
| SCK/CLK | Clock | 23 | GPIO11 | SPI0 SCLK |
| BL/LED | Backlight | — | **GND** | **Must tie to GND** |

**Install ILI9341 driver:** pip install adafruit-blinka adafruit-circuitpython-ili9341 pillow

## **Python Scripts**

### **Aim 1 — SSD1309 smoke test**

Renders a crosshair alignment pattern. Used to position the plate before loading a bitmap mask. Confirms SPI wiring and luma.oled installation.

#!/usr/bin/env python3

# oled_smoke_test.py — Photoplasm Ch5

from luma.core.interface.serial import spi from luma.oled.device import ssd1309 from PIL import Image, ImageDraw

serial  = spi(device=0, port=0, bus_speed_hz=8000000,

              gpio_DC=25, gpio_RST=27)

display = ssd1309(serial, width=128, height=64, rotate=0)

img  = Image.new("1", (128, 64), "black") draw = ImageDraw.Draw(img) draw.line([(64, 0),  (64, 64)],  fill="white", width=1) draw.line([(0,  32), (128, 32)], fill="white", width=1) draw.rectangle([0, 0, 127, 63], outline="white") draw.text((4, 2), "PHOTOPLASM", fill="white")

display.display(img) print("[OLED] Crosshair active — smoke test complete")

### **Aim 1 — Display off**

Always clear and release at end of session.

#!/usr/bin/env python3

# oled_off.py — Photoplasm Ch5

from luma.core.interface.serial import spi from luma.oled.device import ssd1309 from PIL import Image

serial  = spi(device=0, port=0, bus_speed_hz=8000000,

              gpio_DC=25, gpio_RST=27)

display = ssd1309(serial, width=128, height=64, rotate=0) display.display(Image.new("1", (128, 64), "black")) display.cleanup() print("[OLED] Display cleared and released")

### **Aim 1 — Bitmap mask loader**

Loads a 128×64 PNG and displays it as an exposure mask.

White = expose (transmit) · Black = block.

#!/usr/bin/env python3

# oled_mask.py — Photoplasm Ch5

# Usage: python3 oled_mask.py pattern.png

import sys from luma.core.interface.serial import spi from luma.oled.device import ssd1309 from PIL import Image

if len(sys.argv) < 2:

    print("Usage: python3 oled_mask.py <pattern.png>")

    sys.exit(1)

serial  = spi(device=0, port=0, bus_speed_hz=8000000,

              gpio_DC=25, gpio_RST=27)

display = ssd1309(serial, width=128, height=64, rotate=0) img = Image.open(sys.argv[1]).convert("1").resize((128, 64)) display.display(img) print(f"[OLED] Mask active: {sys.argv[1]}")

### **Aim 2 — ILI9341 circular petri mask**

Renders a circular exposure zone matching the 84mm agar plate footprint.

BL pin must be tied to GND before running.

#!/usr/bin/env python3

# ili9341_mask.py — Photoplasm Ch5 Aim 2

import board, busio, digitalio from adafruit_ili9341 import ILI9341 from PIL import Image, ImageDraw

spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI, MISO=board.MISO) cs  = digitalio.DigitalInOut(board.CE0)    # GPIO8  Pin 24 dc  = digitalio.DigitalInOut(board.D25)    # GPIO25 Pin 22 rst = digitalio.DigitalInOut(board.D27)    # GPIO27 Pin 13

display = ILI9341(spi, cs=cs, dc=dc, rst=rst, width=320, height=240)

img  = Image.new("RGB", (320, 240), "black") draw = ImageDraw.Draw(img) draw.ellipse([40, 20, 280, 220], fill="white")

display.image(img) print("[ILI9341] Circular petri mask active — 470nm source only")

## **Experiments**

### **Experiment 1 — OLED additive emission quantification**

**Goal:** Measure the additive 470nm contribution of the SSD1309 when displaying white (transmit) state. Establish Δ_oled for the Appendix A calibration model.

**Setup:** OLED in-line between LED array and AS7341 at operating throw distance.

Run three states:

- LED array only (OLED removed from path) — baseline λex

- OLED full black — LED flux attenuated by glass only

- OLED full white — baseline + additive OLED emission

**Measure:** AS7341 λex proxy (F2₄₄₅ₙₘ + F3₄₈₀ₙₘ) for each state.

**Calculate:**

Δ_oled      = λex(full white) − λex(full black) glass_atten = λex(no OLED)   − λex(full black)

**Success criteria:** Δ_oled stable across 3 repeats (CV < 10%). Value entered into calibration model as fixed offset.

**Status:** [TBD — Genspace wetlab, May 28+]

### **Experiment 2 — Edge resolution characterization**

**Goal:** Characterize mask edge sharpness at the agar surface. Compare SSD1309 (128×64) vs ILI9341 (320×240) edge widths.

**Setup:** Display a 10-pixel vertical stripe. Scan AS7341 laterally at 1mm increments across the stripe edge.

**Measure:** λex at each position. 10%–90% rise distance = effective edge width.

**Expected result:**

- SSD1309: edge width ~2–4mm at 150mm throw

- ILI9341: edge width ~0.5–1mm (finer pixel pitch)

**Status:** [TBD]

### **Experiment 3 — Circular mask uniformity**

**Goal:** Confirm uniform transmission across the circular petri mask.

**Setup:** Display circular mask. Grid-scan AS7341 at 5mm spacing (5×5 grid within 84mm circle). Log λex at each point.

**Target:** CV < 20% across all 25 grid points.

**Status:** [TBD]

## **Current State**

| **Item** | **Status** |
| --- | --- |
| SSD1309 wired to Pi 5 (NS-03 v7) | ✅ Complete |
| luma.oled + Pillow installed | ✅ Complete |
| Smoke test (crosshair) confirmed | ✅ Verified |
| Display off script | ✅ Verified |
| Bitmap mask loader | ✅ Verified |
| Additive emission (Δ_oled) quantified | ⏳ Pending Experiment 1 |
| Mask irradiance above T_det confirmed | ⏳ Pending XP-E2 upgrade (Ch. 4 / App. B) |
| ILI9341 Aim 2 hardware ordered | ⏳ Pending |
| Integration with LED ring (Chapter 7) | ⏳ Pending |

**Known issue — additive 470nm emission:** SSD1309 lit pixels emit at ~470nm, adding to the eLightOn dose in an uncontrolled way. In BioLightV5, additional 470nm dose means additional repression — the mask is both patterning and adding unquantified biological signal. Documented as Δ_oled offset. Eliminated in Aim 2 by ILI9341 backlight disable.

**Known issue — resolution:** At 128×64, fine detail is not resolvable at the plate. Addressed in Aim 2 by ILI9341 at 320×240.

## **Future State — Aim 2**

The ILI9341 is a drop-in SPI replacement on the same GPIO assignments. Three changes:

- Hardware: Swap SSD1309 for ILI9341 · tie BL pin to GND

- Driver: Replace `luma.oled / ssd1309` with `adafruit-circuitpython-ili9341`

- Mask resolution: Scale all bitmap patterns from 128×64 → 320×240

All other system integration (Chapter 7), calibration (Appendix A), and GUI (Chapter 8) code remains unchanged.

Longer-term enhancements:

- Rasterizr pipeline integration — direct JSON coordinate-to-mask rendering

- Multi-frame exposure sequences — automated mask updates between timed dose

  intervals for gradient or zone-system exposures

- Real-time preview — render current mask in Flask web UI (Chapter 8) before

  committing to biological exposure

## **Related Chapters**

- Appendix A: Calibration Protocol: Δ_oled incorporated as calibration parameter in the

  Kc irradiance model.

- Chapter 4 — LED Ring: Full RsLOV/eLightOn irradiance analysis, T_det, k½,

  T_sat, and hardware comparison. Required reading before this chapter.

- Chapter 7 — System Integration: LED + OLED + AS7341 running in sequence,

  timing, and first combined exposure test.

- Appendix B: Feature Specification — CRE category (Aim 2 / Cree XP-E2): ILI9341 and XP-E2 are paired upgrades —

  higher irradiance compensates for ILI9341 polarizer transmission loss.

## **Reference**

Li X, Zhang C, Xu X, Miao J, Yao J, Liu R, Zhao Y, Chen X, Yang Y.

A single-component light sensor system allows highly tunable and direct activation of gene expression in bacterial cells. *Nucleic Acids Research.* 2020;48(6):e33. doi:10.1093/nar/gkaa044. PMID 31989175. PMC7102963.

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.2.0  ·  2026-05-17  ·  draft