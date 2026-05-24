Photoplasm Quick Start Guide  ·  Chapter 3 — Wavelength Sensor (AS7341)

# Chapter 3 — Wavelength Sensor (AS7341)

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-04-26  ·  github.com/ericview-dev/photoplasm

---

## 3.1  Hardware — AS7341 Sensor

The Godiyes AS7341 is an Arduino-style breakout board with 6 pins. For Photoplasm only 4 are used — INT and LDR are left unconnected.

| Color | Signal | Pi Pin | GPIO |
|---|---|---|---|
| Red | VCC (3.3V) | Pin 1 | 3.3V |
| Green | GND | Pin 14 | GND |
| Blue | SDA | Pin 3 | GPIO2 |
| Yellow | SCL | Pin 5 | GPIO3 |

Final configuration: direct interface — 4 dupont wires only, no external pull-up resistors. Pi 5 internal pull-ups on GPIO2/GPIO3 are sufficient once the SDA solder joint on the Godiyes board was corrected. External 4.7kΩ pull-up resistors were tested during bring-up but removed — the root cause of all read failures was a cold solder joint on SDA, not missing pull-ups.

## 3.2  I2C Bus Discovery

The Pi 5 maps GPIO I2C differently than earlier Pi models. Use this sequence to identify the correct bus:

```bash
# List all I2C buses
ls /dev/i2c*

# Identify each bus
for i in $(ls /sys/bus/i2c/devices/); do
  echo "$i: $(cat /sys/bus/i2c/devices/$i/name 2>/dev/null)"
done

# Scan for sensor on each bus
sudo i2cdetect -y 1
sudo i2cdetect -y 13
sudo i2cdetect -y 14
```

> **CONFIRMED** — Bus 1 = Synopsys DesignWare — GPIO pins 3/5 — AS7341 confirmed at 0x39. Bus 13/14 = internal system buses.

Verify sensor identity:

```bash
python3 -c "import smbus2; bus = smbus2.SMBus(1); print(hex(bus.read_byte_data(0x39, 0x92)))"
# Expected: 0x24
```

## 3.3  Software — `as7341_adafruit_test.py`

The confirmed working script uses the Adafruit CircuitPython library with a `BLINKA_FORCEBOARD` environment variable fix for SSH compatibility.

### Why BLINKA_FORCEBOARD is Required

The Adafruit library uses `board.SCL` and `board.SDA` which rely on environment variables only available in an interactive Pi session. When called via SSH from Mac, these variables are not set and the script hangs silently. Setting `BLINKA_FORCEBOARD=RASPBERRY_PI_5` forces platform detection and resolves the hang in all execution contexts.

```python
import os
os.environ['BLINKA_FORCEBOARD'] = 'RASPBERRY_PI_5'
```

### Why Adafruit Library Over smbus2

Direct smbus2 register reads skip the AS7341 SMUX configuration — the internal routing of photodiodes to the ADC. Without SMUX init, gain settings have no effect, channel reads return stale data, and the 680nm channel reads a fixed erroneous value of 59,392–63,488 regardless of light conditions. The Adafruit library handles SMUX, PON, SP_EN, and AVALID polling automatically.

### stdout Buffering Fix

Python buffers stdout by default. Over SSH, output is held in a buffer and never reaches the Mac terminal. Fix applied at top of every script:

```python
import sys
sys.stdout.reconfigure(line_buffering=True)
```

### Channel Map

| Channel | Wavelength | Notes |
|---|---|---|
| F1 | 415nm Violet | Low response to 470nm source |
| F2 | 445nm Indigo | Rising — LED emission edge |
| F3 | 480nm Blue | PRIMARY — 470nm LED monitoring channel |
| F4 | 515nm Cyan | Adjacent bleed |
| F5 | 555nm Green | Elevated — phosphor component |
| F6 | 590nm Yellow | Tapering |
| F7 | 630nm Orange | Minimal response |
| F8 | 680nm Red | Confirmed working with Adafruit lib |
| Clear | Broadband | Integrated luminosity reference |
| NIR | Near Infrared | Tracks ~2× the 480nm count |

## 3.4  Gain Sweep Results

Test conditions: Adafruit library, ATIME=100, ASTEP=999, LEDs on, sensor in direct proximity (~1 inch). Linear scaling confirmed across all gain levels. No saturation at any level.

| Gain | 480nm | Clear | NIR |
|---|---|---|---|
| 0.5x | 0 | 1 | 2 |
| 1x | 2 | 2 | 4 |
| 2x | 4 | 4 | 5 |
| 4x | 5 | 5 | 10 |
| 8x | 18 | 18 | 34 |
| 16x | 28 | 30 | 58 |
| 32x | 47 | 50 | 97 |
| 64x | 74 | 148 | 279 |
| 128x | 243 | 274 | 514 |
| 256x | 409 | 462 | 869 |
| 512x (max) | 675 | 729 | 1,430 |

## 3.5  Dark Chamber Calibration — Test Matrix

Stage 0 dark enclosure built — frustum cone shape with stackable spacer ring, adjustable throw distance in ~1 inch increments.

| Test | LEDs | OLED | Ambient | 480nm | Note |
|---|---|---|---|---|---|
| T1 | ON | — | Room light | 2,404 | Ambient dominated |
| T2 | OFF | — | Room light | 2,313 | Ambient baseline |
| T3 | ON | Glass off | Dark | 3–4 | OLED blocking |
| T4 | ON | None | Dark | 3–4 | Too far from LEDs |
| T5 | ON | None | Dark proximity | 41–46 | Signal detected |
| T6 | ON | None | Dark Adafruit 256x | 25–27 | 680nm resolved |
| T7 | ON | None | Dark chamber 512x | 49 | Current baseline |
| T12 | OFF | OFF | Dark chamber | 0–1 | True noise floor |

Dark chamber result at 512x, 10 inch throw: 480nm = 49 counts. True noise floor = 0–1 counts. Signal-to-noise ratio = ~49:1.

## 3.6  Remaining Calibration Tests (T8–T11)

| Test | Condition | Purpose |
|---|---|---|
| T8 | Dark + LEDs on + OLED present, off | OLED glass attenuation at 470nm |
| T9 | Dark + LEDs on + OLED full white | OLED active transmission range |
| T10 | Dark + LEDs on + OLED test pattern | Spatial modulation effect on sensor |
| T11 | Dark + LEDs off + OLED white | OLED self-emission contribution |

## 3.7  Known Issues & Resolutions

| Issue | Cause | Resolution | Status |
|---|---|---|---|
| Script hangs via SSH | Adafruit `board.SCL/SDA` not in non-interactive SSH | `BLINKA_FORCEBOARD=RASPBERRY_PI_5` | Closed |
| No output via SSH | Python stdout buffered | `sys.stdout.reconfigure(line_buffering=True)` | Closed |
| Remote I/O error | Cold solder joint on SDA pin | Resoldered SDA — sensor at 0x39 | Closed |
| SDA/SCL swapped | Godiyes pin order differs from Adafruit | Blue=SDA Pin 3, Yellow=SCL Pin 5 | Closed |
| 680nm saturated 59k+ | smbus2 missing SMUX init | Switched to Adafruit library | Closed |
| Gain had no effect | smbus2 skips PON/SP_EN init | Adafruit handles init correctly | Closed |
| I2C crash on 2nd sample | SMUX reconfiguration at default baud | Reduced I2C baud to 50kHz | Closed |
| 480nm low at 10 inch throw | Inverse square law — 7% of proximity signal | Spacer ring adjustment needed | Open |

## 3.8  GitHub Workflow Used

Two feature branches used this session:

```
feature/as7341-smbus2-fix         # initial SSH hang fix via smbus2
feature/as7341-adafruit-restore   # restored Adafruit library with BLINKA fix
```

Key lessons: Always push feature branch to GitHub before pulling to Pi. Use `2>&1` when running scripts via SSH. Use `sys.stdout.reconfigure(line_buffering=True)` for SSH-compatible output. The Adafruit library is the correct approach for AS7341 — handles SMUX, AVALID, and gain correctly. `BLINKA_FORCEBOARD` resolves SSH platform detection hang.

## 3.9  Next Steps

- Complete T8–T11 OLED test matrix
- Adjust spacer ring — find optimal throw distance for 20,000–40,000 counts at 480nm
- Update `sensor.py` module with Adafruit + `BLINKA_FORCEBOARD`
- Merge feature branch to dev → promote to main
- Integrate with Chapter 4 (LED Ring) and Chapter 7 (System Integration); feed counts into the Appendix A calibration model

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-04-26  ·  draft
