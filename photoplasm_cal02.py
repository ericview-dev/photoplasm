#!/usr/bin/env python3
"""
photoplasm_cal02.py
═══════════════════════════════════════════════════════════════════
BioLight Irradiance Calibration — Protophotoplasm platform
Part of the BioLight optogenetic bacteriography exposure unit.
HTGAA 2026 · Makerspace Charlotte BioArt Studio
Eric Schneider + Karen Ingram
═══════════════════════════════════════════════════════════════════

PURPOSE
-------
Measures actual delivered irradiance at agar base height across
three optical states. Establishes the calibrated baseline for all
subsequent biological exposure runs.

This script contains NO step wedge logic. The step wedge is a
biological exposure tool (protophotoplasm.py) and runs only after
calibration is complete and gain/PWM values are confirmed.

CALIBRATION STATES
------------------
  State 1 — LED ON, no OLED (maximum possible irradiance)
    Sensor reads full unobstructed LED field at agar plane.
    This is the optical ceiling — nothing can exceed this value.

  State 2 — LED ON, OLED fully WHITE (maximum block)
    OLED glass + pixel layer at full white attenuates the beam.
    Measures the transmission loss of the OLED substrate itself.
    White pixels on SSD1309 = pixels ON = OLED emitting = blocking
    the 470nm LED light passing through from below.

  State 3 — LED ON, OLED fully OFF (display dark, glass only)
    Display command 0xAE blanks all pixels but glass remains.
    Measures glass-only transmission loss with no pixel attenuation.
    This is the working irradiance for biological exposure runs.

DERIVED METRICS
---------------
  oled_transmission   = state2_f2f3 / state1_f2f3
    How much light passes through the full OLED (white pixels + glass)
    as a fraction of unobstructed LED output. Typically 60–80%.

  glass_transmission  = state3_f2f3 / state1_f2f3
    How much light passes through the OLED glass alone (pixels off).
    Typically 85–95%.

  pixel_attenuation   = state3_f2f3 / state2_f2f3
    How much additional blocking the lit pixels add over glass alone.
    Useful for understanding OLED contrast ratio in the optical path.

  irradiance_uwcm2    = f2_f3_sum × k_factor
    Estimated irradiance in µW/cm² at the sensor plane.
    k_factor must be established by comparison with a calibrated
    reference meter. Default k=1.0 until measured.

SENSOR PLACEMENT
----------------
  AS7341 at agar base height, in transmission geometry directly
  under the OLED projection zone. This measures the actual photon
  flux delivered to the biological substrate plane — the ground
  truth for EL222 activation dose.

  Sensor must remain at this fixed position for all calibration
  and exposure runs so readings are directly comparable.

CYCLE SEQUENCE
--------------
  1. Hardware init — GPIO, SPI, I2C
  2. LEDs ON at PWM_DUTY_PCT%
  3. Warm-up settle (WARMUP_SEC)
  4. State 1: OLED absent/off → read AS7341 → log
  5. State 2: OLED white (full block) → settle → read AS7341 → log
  6. State 3: OLED display off (glass only) → settle → read AS7341 → log
  7. LEDs OFF
  8. OLED OFF
  9. Compute and print transmission ratios
  10. Write CSV

GAIN ADVISORY
-------------
  F2+F3 > 60000  →  saturating, drop gain
  F2+F3 <   500  →  noise floor, raise gain
  Starting point: 256X for current ring light at agar base height.
  Adjust --gain flag until state 1 reads 1000–50000 counts.

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
    Pin  1  3.3V    (shared with OLED VCC)
    Pin  3  GPIO2   SDA
    Pin  5  GPIO3   SCL
    Pin 14  GND

DEPENDENCIES
------------
  sudo apt install python3-lgpio python3-spidev python3-smbus2 python3-pil
  sudo pip3 install adafruit-circuitpython-as7341 --break-system-packages

CLI USAGE
---------
  sudo python3 photoplasm_cal02.py [options]

  Options:
    --pwm N       LED PWM duty cycle 0–100%   (default: 100)
    --gain Nx     AS7341 gain setting          (default: 256X)
                  choices: 0_5X 1X 2X 4X 8X 16X 32X 64X 128X 256X
    --settle N    Settle time in seconds between states (default: 2.0)
    --k N         k_factor for µW/cm² estimate (default: 1.0)
    --dry-run     No hardware — synthetic data for bench validation

  Examples:
    sudo python3 photoplasm_cal02.py
    sudo python3 photoplasm_cal02.py --gain 128X
    sudo python3 photoplasm_cal02.py --pwm 75 --gain 256X
    python3 photoplasm_cal02.py --dry-run

  Ctrl+C exits cleanly — LEDs and OLED powered off by finally block.
"""

import argparse
import lgpio
import spidev
import time
import csv
import os
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
    prog="photoplasm_cal02",
    description="BioLight irradiance calibration — three-state optical baseline.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=(
        "examples:\n"
        "  sudo python3 photoplasm_cal02.py\n"
        "  sudo python3 photoplasm_cal02.py --gain 128X\n"
        "  sudo python3 photoplasm_cal02.py --pwm 75 --gain 256X\n"
        "  python3 photoplasm_cal02.py --dry-run\n"
    )
)
_parser.add_argument("--pwm",     type=int,   default=None, metavar="N",
    help="LED PWM duty cycle 0–100 (default: 100)")
_parser.add_argument("--gain",    type=str,   default=None, choices=VALID_GAINS, metavar="Nx",
    help=f"AS7341 gain — one of: {' '.join(VALID_GAINS)} (default: 256X)")
_parser.add_argument("--settle",  type=float, default=None, metavar="N",
    help="settle time in seconds between states (default: 2.0)")
_parser.add_argument("--k",       type=float, default=None, metavar="N",
    help="k_factor for µW/cm² estimate (default: 1.0)")
_parser.add_argument("--dry-run", action="store_true", dest="dry_run",
    help="skip all hardware, use synthetic data")
_args = _parser.parse_args()


# ══════════════════════════════════════════════════════════════════
# CONFIG — edit these defaults; CLI flags override at runtime
# ══════════════════════════════════════════════════════════════════
PWM_DUTY_PCT = 100      # LED brightness 0–100%
PWM_FREQ_HZ  = 1000     # MOSFET gate switching frequency
WARMUP_SEC   = 2.0      # LED warm-up settle after power on
SETTLE_SEC   = 2.0      # settle between state changes
AS7341_GAIN  = "256X"   # high gain — ring light at agar base is dim
                         # adjust until state 1 reads 1000–50000 counts
K_FACTOR     = 1.0      # µW/cm² per count — set after reference measurement
OUTPUT_DIR   = "/home/ericview/cal_logs"

# ── Apply CLI overrides ───────────────────────────────────────────
if _args.pwm    is not None: PWM_DUTY_PCT = _args.pwm
if _args.gain   is not None: AS7341_GAIN  = _args.gain
if _args.settle is not None: SETTLE_SEC   = _args.settle
if _args.k      is not None: K_FACTOR     = _args.k
if _args.dry_run:             SENSOR_PRESENT = False
# ══════════════════════════════════════════════════════════════════


# ── GPIO / SPI pin constants (NS-03 v6 — do not edit) ─────────────
GPIO_PWM = 18    # hardware PWM0 → IRLZ44N gate
GPIO_RST = 27    # OLED hard reset
GPIO_DC  = 25    # OLED data/command select

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
        """Hardware reset pulse — required on power-up."""
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

    def white(self):
        """Fill OLED fully white — maximum pixel block state."""
        img = Image.new("1", (OLED_W, OLED_H), 1)
        self.show(img)

    def off(self):
        """Display off — pixels blank, glass remains in path."""
        self._cmd(CMD_DISPLAY_OFF)

    def on(self):
        """Display on — restore from RAM."""
        self._cmd(CMD_DISPLAY_ON)


# ══════════════════════════════════════════════════════════════════
# AS7341 MEASUREMENT
# ══════════════════════════════════════════════════════════════════
def read_as7341(state_label: str) -> dict:
    """
    Read all AS7341 channels and return as a flat dict.

    470nm proxy = F2 (445nm) + F3 (480nm) sum.
    The 470nm EL222 peak falls between these two channels;
    summing both gives a stable dose proxy.

    k_factor converts counts to estimated µW/cm²:
      irradiance = f2_f3_sum × K_FACTOR
    K_FACTOR defaults to 1.0 until calibrated against a reference.

    Args:
      state_label — one of "no_oled", "oled_white", "oled_off"
                    stamped into the CSV row for identification

    Returns:
      dict with all channel readings plus computed fields
    """
    if not SENSOR_PRESENT:
        # Synthetic values scaled per state for dry-run validation
        synthetic = {
            "no_oled"   : {"f1_415nm": 0, "f2_445nm": 180, "f3_480nm": 210,
                           "f4_515nm": 80, "f5_555nm": 50, "f6_590nm": 30,
                           "f7_630nm": 20, "f8_680nm": 12, "clear": 520, "nir": 8},
            "oled_white": {"f1_415nm": 0, "f2_445nm": 110, "f3_480nm": 130,
                           "f4_515nm": 50, "f5_555nm": 30, "f6_590nm": 18,
                           "f7_630nm": 12, "f8_680nm":  8, "clear": 320, "nir": 5},
            "oled_off"  : {"f1_415nm": 0, "f2_445nm": 160, "f3_480nm": 190,
                           "f4_515nm": 70, "f5_555nm": 45, "f6_590nm": 27,
                           "f7_630nm": 18, "f8_680nm": 11, "clear": 470, "nir": 7},
        }
        ch = synthetic.get(state_label, synthetic["no_oled"])
    else:
        sensor.gain = getattr(Gain, f"GAIN_{AS7341_GAIN}")
        ch = {
            "f1_415nm" : sensor.channel_415nm,   # violet
            "f2_445nm" : sensor.channel_445nm,   # deep blue ← EL222 lower bound
            "f3_480nm" : sensor.channel_480nm,   # blue      ← EL222 upper bound
            "f4_515nm" : sensor.channel_515nm,   # cyan
            "f5_555nm" : sensor.channel_555nm,   # green
            "f6_590nm" : sensor.channel_590nm,   # yellow-green
            "f7_630nm" : sensor.channel_630nm,   # orange-red
            "f8_680nm" : sensor.channel_680nm,   # red
            "clear"    : sensor.channel_clear,   # broadband luminosity
            "nir"      : sensor.channel_nir,     # near-infrared
        }

    ch["f2_f3_sum"]      = ch["f2_445nm"] + ch["f3_480nm"]
    ch["irradiance_est"] = round(ch["f2_f3_sum"] * K_FACTOR, 3)
    ch["state"]          = state_label
    ch["timestamp"]      = datetime.now().isoformat()
    ch["gain"]           = AS7341_GAIN
    ch["pwm_pct"]        = PWM_DUTY_PCT
    ch["k_factor"]       = K_FACTOR
    return ch


# ══════════════════════════════════════════════════════════════════
# LED PWM HELPERS
# ══════════════════════════════════════════════════════════════════
def leds_on(h, duty_pct: int = 100):
    """Start PWM on GPIO18. Drives IRLZ44N gate, switching 12V LED rail."""
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
# MAIN CALIBRATION CYCLE
# ══════════════════════════════════════════════════════════════════
def run_cal_cycle():
    """
    Execute one complete irradiance calibration cycle.

    Three optical states are measured in sequence:
      1. no_oled    — full LED field, no OLED in path
      2. oled_white — OLED fully white (maximum block)
      3. oled_off   — OLED display off (glass only)

    Transmission ratios are computed and printed at the end.
    All three readings are written to a single timestamped CSV row
    (wide format) for easy comparison across runs.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"photoplasm_cal_{ts}.csv")

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

    readings = {}   # keyed by state label

    try:
        print("\n── photoplasm_cal02 irradiance calibration ──")
        print(f"PWM: {PWM_DUTY_PCT}% · Gain: {AS7341_GAIN} · k: {K_FACTOR} · Settle: {SETTLE_SEC}s")

        # ── LEDs ON ───────────────────────────────────────────────
        leds_on(h, PWM_DUTY_PCT)
        print(f"[WARMUP] {WARMUP_SEC}s …")
        time.sleep(WARMUP_SEC)

        # ── STATE 1: no OLED ──────────────────────────────────────
        # OLED display is off (just initialised, pixels blank).
        # Measures full unobstructed LED field at agar base height.
        # This is the optical ceiling for this PWM setting.
        oled.off()
        print(f"[STATE 1] no OLED — settling {SETTLE_SEC}s …")
        time.sleep(SETTLE_SEC)
        readings["no_oled"] = read_as7341("no_oled")
        r = readings["no_oled"]
        print(f"  F2+F3={r['f2_f3_sum']:6d}  clear={r['clear']:6d}  "
              f"est={r['irradiance_est']:.1f} µW/cm²")

        # ── STATE 2: OLED fully white ─────────────────────────────
        # All pixels lit — maximum OLED attenuation.
        # Measures combined glass + pixel transmission loss.
        oled.white()
        print(f"[STATE 2] OLED white — settling {SETTLE_SEC}s …")
        time.sleep(SETTLE_SEC)
        readings["oled_white"] = read_as7341("oled_white")
        r = readings["oled_white"]
        print(f"  F2+F3={r['f2_f3_sum']:6d}  clear={r['clear']:6d}  "
              f"est={r['irradiance_est']:.1f} µW/cm²")

        # ── STATE 3: OLED display off ─────────────────────────────
        # Pixels blanked — glass substrate only in the light path.
        # This is the working irradiance for biological exposure runs.
        oled.off()
        print(f"[STATE 3] OLED off — settling {SETTLE_SEC}s …")
        time.sleep(SETTLE_SEC)
        readings["oled_off"] = read_as7341("oled_off")
        r = readings["oled_off"]
        print(f"  F2+F3={r['f2_f3_sum']:6d}  clear={r['clear']:6d}  "
              f"est={r['irradiance_est']:.1f} µW/cm²")

        # ── LEDs OFF, OLED OFF ────────────────────────────────────
        oled.off()
        leds_off(h)

    finally:
        # Safety cleanup — always runs even on exception or Ctrl+C
        try:
            leds_off(h)
            oled.off()
        except Exception:
            pass
        spi.close()
        lgpio.gpiochip_close(h)

    # ── Compute transmission ratios ───────────────────────────────
    s1 = readings["no_oled"]["f2_f3_sum"]
    s2 = readings["oled_white"]["f2_f3_sum"]
    s3 = readings["oled_off"]["f2_f3_sum"]

    oled_transmission  = round(s2 / s1 * 100, 1) if s1 > 0 else 0.0
    glass_transmission = round(s3 / s1 * 100, 1) if s1 > 0 else 0.0
    pixel_attenuation  = round(s3 / s2 * 100, 1) if s2 > 0 else 0.0

    print("\n── Calibration results ──")
    print(f"  State 1 — no OLED        F2+F3 = {s1:6d}  ({s1 * K_FACTOR:.1f} µW/cm²)")
    print(f"  State 2 — OLED white     F2+F3 = {s2:6d}  ({s2 * K_FACTOR:.1f} µW/cm²)")
    print(f"  State 3 — OLED off       F2+F3 = {s3:6d}  ({s3 * K_FACTOR:.1f} µW/cm²)")
    print(f"  OLED transmission        {oled_transmission}%  (white pixels + glass vs open)")
    print(f"  Glass transmission       {glass_transmission}%  (glass only vs open)")
    print(f"  Pixel attenuation        {pixel_attenuation}%  (off vs white — OLED contrast)")

    # Gain advisories
    if s1 > 60000:
        print(f"  [!] Counts saturating — drop gain below {AS7341_GAIN}")
    if s1 < 500:
        print(f"  [!] Counts near noise floor — raise gain above {AS7341_GAIN}")
    if K_FACTOR == 1.0:
        print(f"  [!] k_factor = 1.0 (default) — µW/cm² estimates are uncalibrated")
        print(f"      Measure with reference meter and set --k to calibrate")

    # ── Write CSV ─────────────────────────────────────────────────
    # Wide format — one row per run, all three states as columns.
    # Easy to compare across runs at different PWM/gain settings.
    fieldnames = [
        "timestamp", "pwm_pct", "gain", "k_factor",
        "s1_no_oled_f2f3",    "s1_no_oled_clear",    "s1_irradiance_est",
        "s2_oled_white_f2f3", "s2_oled_white_clear", "s2_irradiance_est",
        "s3_oled_off_f2f3",   "s3_oled_off_clear",   "s3_irradiance_est",
        "oled_transmission_pct", "glass_transmission_pct", "pixel_attenuation_pct",
        # full channel detail for state 1 (raw LED reference)
        "s1_f1_415nm","s1_f2_445nm","s1_f3_480nm","s1_f4_515nm",
        "s1_f5_555nm","s1_f6_590nm","s1_f7_630nm","s1_f8_680nm","s1_nir",
    ]

    row = {
        "timestamp"               : readings["no_oled"]["timestamp"],
        "pwm_pct"                 : PWM_DUTY_PCT,
        "gain"                    : AS7341_GAIN,
        "k_factor"                : K_FACTOR,
        "s1_no_oled_f2f3"         : readings["no_oled"]["f2_f3_sum"],
        "s1_no_oled_clear"        : readings["no_oled"]["clear"],
        "s1_irradiance_est"       : readings["no_oled"]["irradiance_est"],
        "s2_oled_white_f2f3"      : readings["oled_white"]["f2_f3_sum"],
        "s2_oled_white_clear"     : readings["oled_white"]["clear"],
        "s2_irradiance_est"       : readings["oled_white"]["irradiance_est"],
        "s3_oled_off_f2f3"        : readings["oled_off"]["f2_f3_sum"],
        "s3_oled_off_clear"       : readings["oled_off"]["clear"],
        "s3_irradiance_est"       : readings["oled_off"]["irradiance_est"],
        "oled_transmission_pct"   : oled_transmission,
        "glass_transmission_pct"  : glass_transmission,
        "pixel_attenuation_pct"   : pixel_attenuation,
        "s1_f1_415nm"             : readings["no_oled"]["f1_415nm"],
        "s1_f2_445nm"             : readings["no_oled"]["f2_445nm"],
        "s1_f3_480nm"             : readings["no_oled"]["f3_480nm"],
        "s1_f4_515nm"             : readings["no_oled"]["f4_515nm"],
        "s1_f5_555nm"             : readings["no_oled"]["f5_555nm"],
        "s1_f6_590nm"             : readings["no_oled"]["f6_590nm"],
        "s1_f7_630nm"             : readings["no_oled"]["f7_630nm"],
        "s1_f8_680nm"             : readings["no_oled"]["f8_680nm"],
        "s1_nir"                  : readings["no_oled"]["nir"],
    }

    # Append to CSV — creates header on first run, appends on subsequent runs
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"\n[CSV] saved → {csv_path}")


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_cal_cycle()
