#!/usr/bin/env python3
"""
photoplasm_densitometer.py
═══════════════════════════════════════════════════════════════════
BioLight Transmission Densitometer — Protophotoplasm platform
Part of the BioLight optogenetic bacteriography exposure unit.
HTGAA 2026 · Makerspace Charlotte BioArt Studio
Eric Schneider 
═══════════════════════════════════════════════════════════════════

PURPOSE
-------
Characterises the OLED as a variable neutral density filter by
sweeping pixel density from 0% (display off, glass only) to 100%
(all pixels fully lit, maximum block) in 100 discrete steps.

At each step the AS7341 spectral sensor measures delivered irradiance
at the substrate plane. The resulting 100-point curve answers the
question: does OLED pixel density linearly attenuate 470nm light,
and by how much per step?

This is the optical equivalent of a densitometer sensitometric sweep
— the same principle used in photographic film characterisation.
If the OLED attenuates 470nm proportionally to pixel density, the
F2+F3 vs density curve will be linear. If it is flat (as the
cal02 three-state test suggested), that confirms the OLED is
optically neutral at 470nm regardless of pixel state.

WHAT EACH STEP DOES
-------------------
  Step 0   — OLED display off (0xAE) — glass only, no pixels
  Step 1   — 1% of pixels lit (1/100 of OLED area white)
  Step 2   — 2% of pixels lit
  ...
  Step 100 — all pixels lit (fully white — maximum block state)

Pixel density is rendered as horizontal bands filling the OLED
from top to bottom. At step N, the top N% of rows are white,
the remainder are black. This gives a clean, repeatable density
ramp that is independent of wedge geometry.

CYCLE SEQUENCE
--------------
  1. Hardware init — GPIO, SPI (OLED), I2C (AS7341)
  2. LEDs ON at 100% PWM via IRLZ44N / GPIO18
  3. Warm-up settle (WARMUP_SEC)
  4. Step 0: OLED off → settle → AS7341 read → log
  5. Steps 1–100: render density frame → settle → read → log
  6. OLED OFF (display-off command)
  7. LEDs OFF (PWM 0 + explicit gpio_write low)
  8. Compute and print density response curve summary
  9. Write timestamped CSV

DENSITY FRAME GEOMETRY
-----------------------
  OLED is 128×64 pixels. At step N (1–100):
    lit_rows = round(64 × N / 100)
    Top lit_rows rows = white (1)
    Remaining rows    = black (0)
  Step 0: display-off command — no pixels active at all.
  Step 100: all 64 rows white = fully lit = same as cal02 State 2.

  This horizontal band approach avoids the wedge geometry problem
  identified in the cal01 step-wedge tests — the sensor sees the
  integrated field, not individual geometric sectors.

EXPECTED RESULTS
----------------
  If OLED is optically neutral at 470nm (as cal02 suggested):
    F2+F3 will be flat across all 100 steps — slope ≈ 0
    All steps ≈ Step 0 baseline

  If OLED attenuates 470nm proportionally:
    F2+F3 will decrease as step increases — negative slope
    Step 100 will be measurably lower than Step 0

  The slope of the F2+F3 vs step regression line is the key metric.
  A slope of 0 confirms optical neutrality.
  A non-zero slope quantifies attenuation per 1% pixel density.

PIN ASSIGNMENTS — NS-03 v6 Pi 5
---------------------------------
  PWM / MOSFET gate:
    Pin  1  3.3V            (logic reference)
    Pin  6  GND
    Pin 12  GPIO18 PWM0  →  IRLZ44N gate (470Ω series, 10kΩ pull-down)

  OLED SPI (SSD1309 128×64):
    Pin  9  GND
    Pin 13  GPIO27  RST
    Pin 17  3.3V    VCC
    Pin 19  GPIO10  MOSI / DIN
    Pin 22  GPIO25  DC
    Pin 23  GPIO11  SCLK
    Pin 24  GPIO8   CE0 / CS

  AS7341 spectral sensor (I2C, addr 0x39):
    Pin  1  3.3V    (shared)
    Pin  3  GPIO2   SDA
    Pin  5  GPIO3   SCL
    Pin 14  GND

DEPENDENCIES
------------
  sudo apt install python3-lgpio python3-spidev python3-smbus2 python3-pil
  sudo pip3 install adafruit-circuitpython-as7341 --break-system-packages

CLI USAGE
---------
  sudo python3 photoplasm_densitometer.py [options]

  Options:
    --gain Nx     AS7341 gain setting          (default: 256X)
                  choices: 0_5X 1X 2X 4X 8X 16X 32X 64X 128X 256X
    --settle N    Settle time in seconds per step (default: 0.5)
    --pwm N       LED PWM duty cycle 0–100%    (default: 100)
    --dry-run     No hardware — synthetic data for bench validation

  Examples:
    sudo python3 photoplasm_densitometer.py
    sudo python3 photoplasm_densitometer.py --gain 128X
    sudo python3 photoplasm_densitometer.py --settle 1.0
    python3 photoplasm_densitometer.py --dry-run

  Total run time ≈ (100 × SETTLE_SEC) + warmup + overhead
  Default: ~55 seconds at 0.5s settle per step.

  Ctrl+C exits cleanly — LEDs and OLED powered off by finally block.
"""

import argparse
import lgpio
import spidev
import time
import csv
import os
import math
from datetime import datetime
from PIL import Image, ImageDraw


# ── AS7341 import with graceful dry-run fallback ──────────────────
try:
    import board
    import busio
    from adafruit_as7341 import AS7341, Gain
    _i2c   = busio.I2C(board.SCL, board.SDA)
    sensor = AS7341(_i2c)
    SENSOR_PRESENT = True
    print("[AS7341] sensor found")
except Exception as e:
    sensor = None
    Gain   = None
    SENSOR_PRESENT = False
    print(f"[AS7341] not found ({e}) — dry-run mode")


# ══════════════════════════════════════════════════════════════════
# CLI ARGUMENT PARSING
# ══════════════════════════════════════════════════════════════════
VALID_GAINS = ["0_5X","1X","2X","4X","8X","16X","32X","64X","128X","256X"]

_parser = argparse.ArgumentParser(
    prog="photoplasm_densitometer",
    description="BioLight OLED transmission densitometer — 100-step pixel density sweep.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=(
        "examples:\n"
        "  sudo python3 photoplasm_densitometer.py\n"
        "  sudo python3 photoplasm_densitometer.py --gain 128X\n"
        "  sudo python3 photoplasm_densitometer.py --settle 1.0\n"
        "  python3 photoplasm_densitometer.py --dry-run\n"
    )
)
_parser.add_argument("--gain",    type=str,   default=None, choices=VALID_GAINS, metavar="Nx",
    help=f"AS7341 gain — one of: {' '.join(VALID_GAINS)} (default: 256X)")
_parser.add_argument("--settle",  type=float, default=None, metavar="N",
    help="settle time in seconds per step (default: 0.5)")
_parser.add_argument("--pwm",     type=int,   default=None, metavar="N",
    help="LED PWM duty cycle 0–100 (default: 100)")
_parser.add_argument("--dry-run", action="store_true", dest="dry_run",
    help="skip all hardware, use synthetic data")
_args = _parser.parse_args()


# ══════════════════════════════════════════════════════════════════
# CONFIG — file defaults; CLI flags override at runtime
# ══════════════════════════════════════════════════════════════════
PWM_DUTY_PCT = 100      # LED brightness — keep at 100% for densitometer
PWM_FREQ_HZ  = 1000     # MOSFET gate switching frequency
WARMUP_SEC   = 2.0      # LED warm-up settle after power on
SETTLE_SEC   = 0.5      # settle per step — 0.5s × 100 steps = ~55s total
AS7341_GAIN  = "256X"   # maximum gain — ring light at substrate is dim
STEPS        = 100      # number of density steps (0–100)
OUTPUT_DIR   = "/home/ericview/cal_logs"

# ── Apply CLI overrides ───────────────────────────────────────────
if _args.gain   is not None: AS7341_GAIN  = _args.gain
if _args.settle is not None: SETTLE_SEC   = _args.settle
if _args.pwm    is not None: PWM_DUTY_PCT = _args.pwm
if _args.dry_run:             SENSOR_PRESENT = False
# ══════════════════════════════════════════════════════════════════


# ── GPIO / SPI pin constants (NS-03 v6 — do not edit) ─────────────
GPIO_PWM = 18
GPIO_RST = 27
GPIO_DC  = 25

OLED_W = 128
OLED_H = 64

CMD_DISPLAY_OFF = 0xAE
CMD_DISPLAY_ON  = 0xAF


# ══════════════════════════════════════════════════════════════════
# OLED DRIVER (SPI, SSD1309, lgpio)
# ══════════════════════════════════════════════════════════════════
class OLED:
    def __init__(self, h, spi):
        self.h   = h
        self.spi = spi

    def _cmd(self, c):
        """Send command byte — DC low."""
        lgpio.gpio_write(self.h, GPIO_DC, 0)
        self.spi.xfer2([c])

    def _data(self, buf):
        """Send pixel data — DC high, chunked at 4096 bytes."""
        lgpio.gpio_write(self.h, GPIO_DC, 1)
        for i in range(0, len(buf), 4096):
            self.spi.xfer2(buf[i:i + 4096])

    def reset(self):
        """Hardware reset pulse."""
        lgpio.gpio_write(self.h, GPIO_RST, 1); time.sleep(0.01)
        lgpio.gpio_write(self.h, GPIO_RST, 0); time.sleep(0.01)
        lgpio.gpio_write(self.h, GPIO_RST, 1); time.sleep(0.01)

    def init(self):
        """Full SSD1309 init sequence for Waveshare 128×64 SPI module."""
        self.reset()
        for c in [
            0xAE,       # display off during init
            0xD5, 0x80, # clock divide
            0xA8, 0x3F, # multiplex 64
            0xD3, 0x00, # display offset 0
            0x40,       # start line 0
            0x8D, 0x14, # charge pump on
            0x20, 0x00, # horizontal addressing
            0xA1,       # seg remap
            0xC8,       # com scan dec
            0xDA, 0x12, # com pins
            0x81, 0xCF, # contrast
            0xD9, 0xF1, # precharge
            0xDB, 0x40, # vcom detect
            0xA4,       # follow RAM
            0xA6,       # normal polarity
            0xAF,       # display on
        ]:
            self._cmd(c)

    def show(self, img: Image.Image):
        """Push a 128×64 1-bit PIL image to the OLED framebuffer."""
        bw  = img.convert("1")
        buf = []
        for page in range(8):
            for col in range(OLED_W):
                byte = 0
                for bit in range(8):
                    if bw.getpixel((col, page * 8 + bit)):
                        byte |= (1 << bit)
                buf.append(byte)
        self._cmd(0x21); self._cmd(0); self._cmd(127)
        self._cmd(0x22); self._cmd(0); self._cmd(7)
        self._data(buf)

    def density(self, pct: int):
        """
        Render a horizontal band density frame at pct% (1–100).
        Top pct% of rows are white (lit), remainder black.
        At pct=100 all rows are white — same as full white mask.
        At pct=0 use off() instead — no pixels active.
        """
        img      = Image.new("1", (OLED_W, OLED_H), 0)
        lit_rows = max(0, min(OLED_H, round(OLED_H * pct / 100)))
        if lit_rows > 0:
            draw = ImageDraw.Draw(img)
            draw.rectangle([0, 0, OLED_W - 1, lit_rows - 1], fill=1)
        self.show(img)

    def off(self):
        """Display off — pixels blank, glass remains in path."""
        self._cmd(CMD_DISPLAY_OFF)

    def on(self):
        """Restore display from RAM."""
        self._cmd(CMD_DISPLAY_ON)


# ══════════════════════════════════════════════════════════════════
# AS7341 MEASUREMENT
# ══════════════════════════════════════════════════════════════════
def read_as7341(step: int, density_pct: int) -> dict:
    """
    Read all AS7341 spectral channels and return as a flat dict.

    470nm proxy = F2 (445nm) + F3 (480nm).
    Gain applied from AS7341_GAIN config constant each call.

    In dry-run mode returns synthetic data with a small simulated
    attenuation ramp so the summary statistics are non-trivial.

    Args:
      step        — step number 0–100
      density_pct — OLED pixel density at this step (0 = off, 1–100 = %)

    Returns:
      dict with all channel readings plus metadata
    """
    if not SENSOR_PRESENT:
        # Simulate slight attenuation with density — ~0.5 count per step
        base_f2  = 100
        base_f3  = 120
        base_clr = 300
        atten    = density_pct * 0.3
        ch = {
            "f1_415nm" : 0,
            "f2_445nm" : max(0, round(base_f2  - atten * 0.4)),
            "f3_480nm" : max(0, round(base_f3  - atten * 0.5)),
            "f4_515nm" : 50,
            "f5_555nm" : 30,
            "f6_590nm" : 20,
            "f7_630nm" : 15,
            "f8_680nm" : 10,
            "clear"    : max(0, round(base_clr - atten)),
            "nir"      : 5,
        }
    else:
        sensor.gain = getattr(Gain, f"GAIN_{AS7341_GAIN}")
        ch = {
            "f1_415nm" : sensor.channel_415nm,
            "f2_445nm" : sensor.channel_445nm,
            "f3_480nm" : sensor.channel_480nm,
            "f4_515nm" : sensor.channel_515nm,
            "f5_555nm" : sensor.channel_555nm,
            "f6_590nm" : sensor.channel_590nm,
            "f7_630nm" : sensor.channel_630nm,
            "f8_680nm" : sensor.channel_680nm,
            "clear"    : sensor.channel_clear,
            "nir"      : sensor.channel_nir,
        }

    ch["f2_f3_sum"]   = ch["f2_445nm"] + ch["f3_480nm"]
    ch["step"]        = step
    ch["density_pct"] = density_pct
    ch["timestamp"]   = datetime.now().isoformat()
    ch["gain"]        = AS7341_GAIN
    ch["pwm_pct"]     = PWM_DUTY_PCT
    return ch


# ══════════════════════════════════════════════════════════════════
# LED PWM HELPERS
# ══════════════════════════════════════════════════════════════════
def leds_on(h, duty_pct: int = 100):
    """Start PWM on GPIO18 — drives IRLZ44N gate, switching 12V LED rail."""
    duty = max(0, min(100, duty_pct))
    lgpio.tx_pwm(h, GPIO_PWM, PWM_FREQ_HZ, duty)
    print(f"[LED] ON — {duty}% PWM")

def leds_off(h):
    """
    Stop PWM and pull gate explicitly low.
    Two-step ensures MOSFET fully closes on Pi 5 / Bookworm.
    """
    lgpio.tx_pwm(h, GPIO_PWM, PWM_FREQ_HZ, 0)
    lgpio.gpio_write(h, GPIO_PWM, 0)
    print("[LED] OFF")


# ══════════════════════════════════════════════════════════════════
# SUMMARY STATISTICS
# Simple linear regression on F2+F3 vs density_pct.
# Slope near 0 = OLED optically neutral.
# Negative slope = OLED attenuates 470nm proportionally.
# ══════════════════════════════════════════════════════════════════
def linear_regression(xs, ys):
    """
    Returns (slope, intercept, r_squared) for xs, ys lists.
    slope units: counts per 1% pixel density change.
    """
    n    = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    xm   = sum(xs) / n
    ym   = sum(ys) / n
    ssxy = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    ssx  = sum((x - xm) ** 2 for x in xs)
    if ssx == 0:
        return 0.0, ym, 0.0
    slope     = ssxy / ssx
    intercept = ym - slope * xm
    y_pred    = [slope * x + intercept for x in xs]
    ss_res    = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
    ss_tot    = sum((y - ym) ** 2 for y in ys)
    r_sq      = 1 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
    return round(slope, 4), round(intercept, 2), round(r_sq, 4)


# ══════════════════════════════════════════════════════════════════
# MAIN DENSITOMETER CYCLE
# ══════════════════════════════════════════════════════════════════
def run_densitometer():
    """
    Execute one complete OLED transmission densitometer sweep.

    Sweeps OLED pixel density from 0% (display off) to 100%
    (fully white) in 100 steps. AS7341 reads at each step.
    Linear regression on F2+F3 vs density determines whether
    the OLED meaningfully attenuates 470nm light.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"photoplasm_densitometer_{ts}.csv")

    est_time = round((STEPS + 1) * SETTLE_SEC + WARMUP_SEC + 3)
    print(f"\n── photoplasm_densitometer ──")
    print(f"Gain: {AS7341_GAIN} · PWM: {PWM_DUTY_PCT}% · "
          f"Settle: {SETTLE_SEC}s · Steps: {STEPS+1} (0–100)")
    print(f"Estimated run time: ~{est_time}s")

    # ── Hardware init ─────────────────────────────────────────────
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, GPIO_RST)
    lgpio.gpio_claim_output(h, GPIO_DC)
    lgpio.gpio_claim_output(h, GPIO_PWM)

    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 8_000_000
    spi.mode = 0

    oled = OLED(h, spi)
    oled.init()

    rows = []

    try:
        # ── LEDs ON ───────────────────────────────────────────────
        leds_on(h, PWM_DUTY_PCT)
        print(f"[WARMUP] {WARMUP_SEC}s …")
        time.sleep(WARMUP_SEC)

        # ── Step 0: OLED display off (baseline) ───────────────────
        # No pixels active — glass only in the light path.
        # This is the reference irradiance for all subsequent steps.
        oled.off()
        time.sleep(SETTLE_SEC)
        r = read_as7341(0, 0)
        rows.append(r)
        print(f"  step 000  density=  0%  "
              f"F2+F3={r['f2_f3_sum']:6d}  clear={r['clear']:6d}  [baseline]")

        # ── Steps 1–100: density sweep ────────────────────────────
        for step in range(1, STEPS + 1):

            # Render horizontal band at step% density.
            # Top step% of OLED rows are white, rest black.
            oled.density(step)

            # Settle: allow OLED pixels to stabilise before reading.
            time.sleep(SETTLE_SEC)

            r = read_as7341(step, step)
            rows.append(r)

            # Progress indicator every 10 steps
            marker = "  [max block]" if step == 100 else ""
            if step % 10 == 0 or step == 1 or step == 100:
                print(f"  step {step:03d}  density={step:3d}%  "
                      f"F2+F3={r['f2_f3_sum']:6d}  clear={r['clear']:6d}{marker}")

        # ── OLED OFF, LEDs OFF ────────────────────────────────────
        oled.off()
        print("[OLED] display off")
        time.sleep(0.3)
        leds_off(h)

    finally:
        # Safety cleanup — always runs even on Ctrl+C or exception
        try:
            leds_off(h)
            oled.off()
        except Exception:
            pass
        spi.close()
        lgpio.gpiochip_close(h)

    if not rows:
        print("[!] No data collected.")
        return

    # ── Summary statistics ────────────────────────────────────────
    baseline = rows[0]["f2_f3_sum"]
    max_step = rows[-1]["f2_f3_sum"]
    delta    = baseline - max_step
    delta_pct = round(delta / baseline * 100, 1) if baseline > 0 else 0.0

    xs = [r["density_pct"] for r in rows]
    ys = [r["f2_f3_sum"]   for r in rows]
    slope, intercept, r_sq = linear_regression(xs, ys)

    print("\n── Densitometer results ──")
    print(f"  Step 0   (OLED off)    F2+F3 = {baseline:6d}  [reference]")
    print(f"  Step 100 (OLED white)  F2+F3 = {max_step:6d}")
    print(f"  Delta                          {delta:+6d}  ({delta_pct:+.1f}%)")
    print(f"  Regression slope               {slope:+.4f} counts / 1% density")
    print(f"  R²                             {r_sq:.4f}")

    if abs(slope) < 0.05 and r_sq < 0.3:
        print("  RESULT: OLED is optically neutral at 470nm — flat response confirmed")
    elif slope < -0.05:
        print(f"  RESULT: OLED attenuates 470nm — {abs(slope):.3f} counts per 1% density")
        print(f"          Full white mask attenuates by {abs(delta_pct):.1f}% vs open")
    else:
        print("  RESULT: weak or ambiguous response — check sensor position and gain")

    if baseline < 500:
        print(f"  [!] Baseline counts low ({baseline}) — raise gain or move sensor closer")
    if baseline > 60000:
        print(f"  [!] Baseline counts high ({baseline}) — drop gain to avoid saturation")

    # ── Write CSV ─────────────────────────────────────────────────
    fieldnames = [
        "step", "density_pct", "timestamp", "gain", "pwm_pct",
        "f2_f3_sum", "clear",
        "f1_415nm", "f2_445nm", "f3_480nm",
        "f4_515nm", "f5_555nm", "f6_590nm",
        "f7_630nm", "f8_680nm", "nir",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[CSV] saved → {csv_path}")
    print(f"  {len(rows)} rows · slope={slope:+.4f} · R²={r_sq:.4f}")


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_densitometer()
