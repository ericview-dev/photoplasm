#!/usr/bin/env python3
"""
photoplasm_cal01.py
═══════════════════════════════════════════════════════════════════
BioLight Calibration Script — Protophotoplasm platform
Part of the BioLight optogenetic bacteriography exposure unit.
HTGAA 2026 · Makerspace Charlotte BioArt Studio
═══════════════════════════════════════════════════════════════════

PURPOSE
-------
Runs a clean, repeatable 16-step sensitometric calibration cycle.
Each step projects a cumulative pie-wedge mask through the OLED
onto the substrate below, while the AS7341 spectral sensor measures
the actual delivered irradiance at 470nm per step. Results are
written to a timestamped CSV for H&D curve construction.

This is the optical equivalent of a Stouffer step wedge — wedge 1
receives 16× the base exposure, wedge 16 receives 1×. After all
16 steps the plate holds a full logarithmic dose gradient, readable
as a sensitometric curve once sfGFP fluorescence is imaged.

CYCLE SEQUENCE
--------------
  1. LEDs ON  — GPIO18 PWM at PWM_DUTY_PCT% via IRLZ44N MOSFET gate
  2. Warm-up  — allow LED output to stabilise before first measurement
  3. Wedge loop (16 steps):
       a. Render cumulative wedge frame → push to OLED via SPI
       b. Settle 300ms for OLED pixel stabilisation
       c. Read all AS7341 channels; compute F2+F3 as 470nm proxy
       d. Stamp step metadata; append row to log buffer
       e. Hold dwell remainder for biological exposure
  4. OLED OFF — send display-off command (0xAE), screen goes dark
  5. LEDs OFF — PWM duty to 0, MOSFET gate pulled low
  6. CSV write — flush all rows to timestamped file in OUTPUT_DIR
  7. Summary  — print F2+F3 ramp ratio; warn on saturation or noise floor

GAIN ADVISORY (AS7341_GAIN = "16X" default)
--------------------------------------------
  F2+F3 step 16 > 60000  →  saturating, drop to 8X
  F2+F3 step  1 <   500  →  noise floor, raise to 32X

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
  pip3 install adafruit-circuitpython-as7341 --break-system-packages

CLI USAGE
---------
  sudo python3 photoplasm_cal01.py [options]

  Options (all optional — defaults from CONFIG block apply if omitted):
    --dwell N       Dwell time in seconds per wedge step  (default: 5.0)
    --pwm N         LED PWM duty cycle 0–100%             (default: 100)
    --gain Nx       AS7341 gain setting                   (default: 16X)
                    choices: 0_5X 1X 2X 4X 8X 16X 32X 64X 128X 256X
    --dry-run       Skip all hardware; use synthetic sensor data.
                    Useful for validating CSV output and timing on bench.

  Examples:
    sudo python3 photoplasm_cal01.py
    sudo python3 photoplasm_cal01.py --dwell 10
    sudo python3 photoplasm_cal01.py --pwm 75 --gain 8X
    sudo python3 photoplasm_cal01.py --dwell 2 --pwm 50 --gain 32X
    python3 photoplasm_cal01.py --dry-run

  Ctrl+C aborts the cycle cleanly — LEDs and OLED are powered off
  by the finally block before the process exits.
"""

import argparse        # CLI argument parsing
import lgpio          # Pi 5 GPIO library (replaces deprecated RPi.GPIO)
import spidev         # SPI bus access for OLED
import time
import csv
import os
from datetime import datetime
from PIL import Image, ImageDraw   # wedge frame rendering

# ── AS7341 import with graceful dry-run fallback ──────────────────
# If the sensor is not wired the script still runs, using synthetic
# ramp data so the OLED wedge sequence and LED on/off can be verified
# independently. SENSOR_PRESENT flag is printed at startup.
try:
    import board
    import busio
    from adafruit_as7341 import AS7341, Gain
    _i2c = busio.I2C(board.SCL, board.SDA)
    sensor = AS7341(_i2c)
    SENSOR_PRESENT = True
    print("[AS7341] sensor found")
except Exception as e:
    sensor = None
    Gain   = None
    SENSOR_PRESENT = False
    print(f"[AS7341] not found ({e}) — running in dry-run mode")


# ══════════════════════════════════════════════════════════════════
# CLI ARGUMENT PARSING
# argparse processes sys.argv at import time so CLI flags are
# available before the CONFIG constants are referenced. Each flag
# maps directly to one CONFIG constant; the parsed value overrides
# the file default when supplied. Omitted flags fall back to the
# CONFIG defaults unchanged.
# ══════════════════════════════════════════════════════════════════
VALID_GAINS = ["0_5X","1X","2X","4X","8X","16X","32X","64X","128X","256X"]

_parser = argparse.ArgumentParser(
    prog="photoplasm_cal01",
    description="BioLight sensitometric calibration cycle — 16-step pie-wedge exposure.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=(
        "examples:\n"
        "  sudo python3 photoplasm_cal01.py\n"
        "  sudo python3 photoplasm_cal01.py --dwell 10\n"
        "  sudo python3 photoplasm_cal01.py --pwm 75 --gain 8X\n"
        "  sudo python3 photoplasm_cal01.py --dwell 2 --pwm 50 --gain 32X\n"
        "  python3 photoplasm_cal01.py --dry-run\n"
    )
)
_parser.add_argument(
    "--dwell", type=float, default=None, metavar="N",
    help="dwell time in seconds per wedge step (default: 5.0)"
)
_parser.add_argument(
    "--pwm", type=int, default=None, metavar="N",
    help="LED PWM duty cycle 0–100 percent (default: 100)"
)
_parser.add_argument(
    "--gain", type=str, default=None, choices=VALID_GAINS, metavar="Nx",
    help=f"AS7341 gain — one of: {' '.join(VALID_GAINS)} (default: 16X)"
)
_parser.add_argument(
    "--dry-run", action="store_true", dest="dry_run",
    help="skip all hardware; use synthetic sensor data (no sudo required)"
)
_args = _parser.parse_args()

# ══════════════════════════════════════════════════════════════════
# CONFIG — file defaults; CLI flags override at runtime
# ══════════════════════════════════════════════════════════════════
DWELL_SEC    = 5.0    # seconds each wedge step is held on the OLED
                      # this is your base exposure unit — wedge 1
                      # accumulates 16 × DWELL_SEC total

WARMUP_SEC   = 2.0    # settle time after LEDs energise before step 1
                      # allows thermal stabilisation of LED output

PWM_FREQ_HZ  = 1000   # MOSFET gate switching frequency in Hz
                      # 1 kHz is well above flicker threshold and
                      # below any interference with I2C or SPI buses

PWM_DUTY_PCT = 100    # LED brightness 0–100%
                      # 100 = full rated current via 6.8Ω / 2W resistor
                      # reduce here (not in hardware) for lower-dose runs

WEDGES       = 16     # number of cumulative exposure steps
                      # each step opens one additional 22.5° pie wedge
                      # 16 steps × 22.5° = full 360° circle at step 16

OUTPUT_DIR   = "/home/ericview/cal_logs"
                      # timestamped CSVs are written here
                      # directory is created automatically if absent

AS7341_GAIN  = "16X"  # spectral sensor gain setting
                      # mid-range starting point for ring light
                      # options: 0_5X  1X  2X  4X  8X  16X
                      #          32X  64X  128X  256X
                      # see GAIN ADVISORY in module docstring above

# ── Apply CLI overrides (flags take priority over file defaults) ──
if _args.dwell    is not None: DWELL_SEC    = _args.dwell
if _args.pwm      is not None: PWM_DUTY_PCT = _args.pwm
if _args.gain     is not None: AS7341_GAIN  = _args.gain
if _args.dry_run:               SENSOR_PRESENT = False   # force dry-run mode
# ══════════════════════════════════════════════════════════════════


# ── GPIO / SPI pin constants (from NS-03 v6 table — do not edit) ──
GPIO_PWM = 18    # hardware PWM0 → IRLZ44N gate
GPIO_RST = 27    # OLED hard reset line
GPIO_DC  = 25    # OLED data / command select

# ── OLED display dimensions ────────────────────────────────────────
OLED_W = 128     # pixels wide
OLED_H = 64      # pixels tall

# ── SSD1309 power control command bytes ───────────────────────────
CMD_DISPLAY_OFF = 0xAE   # blank screen, preserve RAM
CMD_DISPLAY_ON  = 0xAF   # restore display from RAM


# ══════════════════════════════════════════════════════════════════
# OLED DRIVER
# Minimal SPI driver for the SSD1309 128×64 OLED.
# Uses lgpio for GPIO control (Pi 5 / Bookworm compatible).
# ══════════════════════════════════════════════════════════════════
class OLED:
    def __init__(self, h, spi):
        """
        h   — lgpio chip handle (from lgpio.gpiochip_open)
        spi — spidev SpiDev instance (bus 0, device 0)
        """
        self.h   = h
        self.spi = spi

    def _cmd(self, c):
        """Send a single command byte. DC low = command mode."""
        lgpio.gpio_write(self.h, GPIO_DC, 0)
        self.spi.xfer2([c])

    def _data(self, buf):
        """
        Send pixel data buffer. DC high = data mode.
        Chunked at 4096 bytes to stay within spidev transfer limits.
        """
        lgpio.gpio_write(self.h, GPIO_DC, 1)
        for i in range(0, len(buf), 4096):
            self.spi.xfer2(buf[i:i + 4096])

    def reset(self):
        """
        Hardware reset pulse: RST high → low → high with 10ms holds.
        Required on power-up to initialise the SSD1309 controller.
        """
        lgpio.gpio_write(self.h, GPIO_RST, 1); time.sleep(0.01)
        lgpio.gpio_write(self.h, GPIO_RST, 0); time.sleep(0.01)
        lgpio.gpio_write(self.h, GPIO_RST, 1); time.sleep(0.01)

    def init(self):
        """
        Full SSD1309 initialisation sequence.
        Sets clock, multiplex ratio, addressing mode, contrast, and
        charge pump before turning the display on. Values are fixed
        for the Waveshare 128×64 SPI OLED module.
        """
        self.reset()
        for c in [
            0xAE,       # display off during init
            0xD5, 0x80, # oscillator frequency / clock divide ratio
            0xA8, 0x3F, # multiplex ratio = 64 rows
            0xD3, 0x00, # display offset = 0 (no vertical shift)
            0x40,       # display start line = 0
            0x8D, 0x14, # charge pump enabled (required — no external Vcc)
            0x20, 0x00, # horizontal addressing mode
                        # auto-increments column then page — suits row-by-row push
            0xA1,       # segment re-map: col 127 → SEG0 (mirror horizontally)
            0xC8,       # COM scan direction: remapped (flip vertically)
            0xDA, 0x12, # COM pins hardware config: alt, no remap
            0x81, 0xCF, # contrast = 0xCF (bright; reduce if too intense)
            0xD9, 0xF1, # pre-charge period: phase1=1, phase2=15
            0xDB, 0x40, # VCOMH deselect level = 0.77 × Vcc
            0xA4,       # display follows RAM (not all-on)
            0xA6,       # normal polarity (1 = lit pixel)
            0xAF,       # display on
        ]:
            self._cmd(c)

    def show(self, img: Image.Image):
        """
        Push a PIL image to the OLED framebuffer.

        The SSD1309 stores pixels as vertical 8-pixel pages across
        128 columns. Each byte in the buffer represents 8 vertically
        stacked pixels in one column of one page (bit 0 = top row).

        Process:
          - Convert image to 1-bit (black/white)
          - Walk 8 pages × 128 columns
          - Pack 8 vertical pixels per column into one byte
          - Set column (0x21) and page (0x22) address windows
          - Send packed buffer as data
        """
        bw  = img.convert("1")
        buf = []
        for page in range(8):             # 8 pages × 8 rows = 64 rows total
            for col in range(OLED_W):     # 128 columns
                byte = 0
                for bit in range(8):
                    row = page * 8 + bit  # absolute pixel row
                    px  = bw.getpixel((col, row))
                    if px:
                        byte |= (1 << bit)   # set bit; bit 0 = topmost row in page
                buf.append(byte)
        self._cmd(0x21); self._cmd(0); self._cmd(127)   # column address 0–127
        self._cmd(0x22); self._cmd(0); self._cmd(7)     # page address 0–7
        self._data(buf)

    def off(self):
        """Blank the display. Pixel RAM is preserved — on() restores it."""
        self._cmd(CMD_DISPLAY_OFF)

    def on(self):
        """Restore display from RAM after off()."""
        self._cmd(CMD_DISPLAY_ON)


# ══════════════════════════════════════════════════════════════════
# WEDGE FRAME GENERATOR
# Produces the cumulative pie-wedge exposure masks displayed on the
# OLED at each step of the calibration cycle.
# ══════════════════════════════════════════════════════════════════
def make_wedge_frame(step: int, total: int = 16) -> Image.Image:
    """
    Generate a 128×64 1-bit PIL image for calibration step N.

    The image is WHITE (opaque mask) except for N cumulative dark pie
    wedge cutouts. Light passes through the dark sectors only — the
    white areas block the LED output entirely.

    Biological meaning:
      Step  1 → 1 dark wedge cut   → that zone gets 1 exposure unit
      Step  2 → 2 dark wedges cut  → zone 1 gets 2 units, zone 2 gets 1
      Step 16 → all wedges cut     → zone 1 has 16 units, zone 16 has 1
    After all 16 steps the plate holds a full logarithmic dose gradient.

    Geometry:
      Circle inscribed in OLED height (radius = 31px, centred at 64,32).
      Area outside the circle remains white (fully masked) at all steps.

    Args:
      step  — current step number (1–total), controls how many wedges open
      total — total number of wedges (default 16)

    Returns:
      PIL Image, mode "1", size 128×64
    """
    # MASK LOGIC (corrected):
    # OLED starts fully WHITE — the entire screen blocks light (opaque mask).
    # Each step cuts a DARK wedge out of the mask — dark = transparent = light passes.
    # Result: light only reaches the substrate through the dark wedge cutouts.
    # Step 1 = one dark wedge open (1 exposure unit to that zone).
    # Step 16 = all dark wedges open (full circle exposed, zone 1 has 16 units).
    # This is the correct Stouffer step-wedge geometry for cumulative exposure.
    img    = Image.new("1", (OLED_W, OLED_H), 1)   # start fully white (opaque mask)
    draw   = ImageDraw.Draw(img)

    cx, cy        = OLED_W // 2, OLED_H // 2        # centre = (64, 32)
    r             = OLED_H // 2 - 1                 # radius = 31px (1px margin)
    deg_per_wedge = 360.0 / total                   # 22.5° per wedge at 16 steps
    start_angle   = -90.0                           # 0° at 12 o'clock (PIL uses 3 o'clock = 0°)

    for w in range(step):
        a0 = start_angle + w * deg_per_wedge        # wedge start angle
        a1 = a0 + deg_per_wedge                     # wedge end angle
        draw.pieslice(
            [cx - r, cy - r, cx + r, cy + r],       # bounding box of circle
            start=a0, end=a1, fill=0                 # fill=0 = dark = light passes through
        )
    return img


# ══════════════════════════════════════════════════════════════════
# AS7341 SPECTRAL MEASUREMENT
# Reads all 10 channels plus a computed 470nm proxy (F2+F3 sum).
# ══════════════════════════════════════════════════════════════════
def read_as7341() -> dict:
    """
    Read all AS7341 spectral channels and return as a flat dict.

    470nm proxy — F2 (445nm) + F3 (480nm):
      The AS7341 has no channel centred on 470nm. The 470nm EL222
      absorption peak falls in the gap between F2 and F3. Summing
      both channels gives a stable dose proxy across runs; use the
      same gain setting for all runs in a series so values are
      directly comparable.

    Gain is applied fresh each call from AS7341_GAIN config constant.
    This is safe because gain takes effect immediately and the sensor
    has no persistent state between calls.

    Dry-run mode (SENSOR_PRESENT = False):
      Returns a static synthetic reading so the rest of the cycle
      (OLED wedges, LED control, CSV write) can be validated without
      the sensor connected.

    Returns:
      dict with keys: f1_415nm … f8_680nm, clear, nir, f2_f3_sum
    """
    if not SENSOR_PRESENT:
        # Synthetic values — proportional to a mid-range real reading.
        # Enough to confirm CSV structure and summary math without sensor.
        return {
            "f1_415nm":  0,  "f2_445nm": 100, "f3_480nm": 120,
            "f4_515nm": 50,  "f5_555nm":  30, "f6_590nm":  20,
            "f7_630nm": 15,  "f8_680nm":  10, "clear":    300,
            "nir":       5,  "f2_f3_sum": 220
        }

    # Apply gain from config — mid-range 16X default for ring light
    sensor.gain = getattr(Gain, f"GAIN_{AS7341_GAIN}")

    ch = {
        "f1_415nm" : sensor.channel_415nm,   # violet
        "f2_445nm" : sensor.channel_445nm,   # deep blue  ← EL222 lower bound
        "f3_480nm" : sensor.channel_480nm,   # blue       ← EL222 upper bound
        "f4_515nm" : sensor.channel_515nm,   # cyan
        "f5_555nm" : sensor.channel_555nm,   # green
        "f6_590nm" : sensor.channel_590nm,   # yellow-green
        "f7_630nm" : sensor.channel_630nm,   # orange-red
        "f8_680nm" : sensor.channel_680nm,   # red
        "clear"    : sensor.channel_clear,   # broadband (no filter)
        "nir"      : sensor.channel_nir,     # near-infrared
    }
    ch["f2_f3_sum"] = ch["f2_445nm"] + ch["f3_480nm"]   # 470nm proxy
    return ch


# ══════════════════════════════════════════════════════════════════
# LED PWM HELPERS
# Thin wrappers around lgpio hardware PWM on GPIO18.
# The IRLZ44N MOSFET switches the 12V LED rail; the Pi never
# carries LED current directly.
# ══════════════════════════════════════════════════════════════════
def leds_on(h, duty_pct: int = 100):
    """
    Start hardware PWM on GPIO18 at duty_pct% (0–100).
    Clamped to valid range. Drives IRLZ44N gate, switching 12V LED rail.
    """
    duty = max(0, min(100, duty_pct))
    lgpio.tx_pwm(h, GPIO_PWM, PWM_FREQ_HZ, duty)
    print(f"[LED] ON — {duty}% duty cycle")


def leds_off(h):
    """
    Turn LEDs off — two-step for reliability:
      1. tx_pwm duty to 0 stops the PWM signal
      2. gpio_write pulls the gate pin explicitly low
    The explicit gpio_write is necessary because lgpio's tx_pwm
    at 0% duty can leave the pin in an indeterminate state on some
    Pi 5 / Bookworm combinations, keeping the MOSFET partially on.
    Explicit low guarantees the gate is pulled to GND.
    """
    lgpio.tx_pwm(h, GPIO_PWM, PWM_FREQ_HZ, 0)     # stop PWM
    lgpio.gpio_write(h, GPIO_PWM, 0)               # pull gate explicitly low
    print("[LED] OFF")


# ══════════════════════════════════════════════════════════════════
# MAIN CALIBRATION CYCLE
# ══════════════════════════════════════════════════════════════════
def run_cal_cycle():
    """
    Execute one complete photoplasm calibration cycle.

    Hardware is initialised, the wedge sequence runs, hardware is
    shut down cleanly, and results are written to CSV. The finally
    block guarantees LEDs and OLED are powered off even if an
    exception occurs mid-cycle — important for lab safety.
    """

    # Create output directory if it doesn't exist yet
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Timestamp used for both the CSV filename and per-row logging
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"photoplasm_cal_{ts}.csv")

    # ── Initialise GPIO chip handle ──────────────────────────────
    # lgpio requires claiming each pin before use. GPIO_PWM is
    # claimed here as an output; lgpio.tx_pwm() will take it over
    # for hardware PWM once leds_on() is called.
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, GPIO_RST)   # OLED reset
    lgpio.gpio_claim_output(h, GPIO_DC)    # OLED data/command select
    lgpio.gpio_claim_output(h, GPIO_PWM)   # LED MOSFET gate

    # ── Initialise SPI for OLED ──────────────────────────────────
    # Bus 0, device 0 (CE0, Pin 24). 8 MHz is well within SSD1309
    # spec and stable on Pi 5. Mode 0 = CPOL=0, CPHA=0.
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 8_000_000
    spi.mode = 0

    # ── Bring up OLED ────────────────────────────────────────────
    oled = OLED(h, spi)
    oled.init()   # sends full SSD1309 init sequence, turns display on

    rows = []     # accumulates one dict per step for CSV write

    try:
        # ── STEP 1: LEDs ON ──────────────────────────────────────
        # Energise the LED ring at full PWM before displaying any
        # wedge frames. Irradiance must be stable before step 1.
        print("\n── photoplasm_cal01 calibration cycle ──")
        print(f"Dwell: {DWELL_SEC}s · Steps: {WEDGES} · PWM: {PWM_DUTY_PCT}% · Gain: {AS7341_GAIN}")
        leds_on(h, PWM_DUTY_PCT)

        # ── STEP 2: Warm-up settle ───────────────────────────────
        # Allow LED junction temperature and optical output to
        # stabilise. 2s is conservative; reduce to 1s once LED
        # thermal behaviour is characterised.
        print(f"[SETTLE] warming up {WARMUP_SEC}s …")
        time.sleep(WARMUP_SEC)

        # ── STEP 3: 16-step wedge exposure sequence ───────────────
        for step in range(1, WEDGES + 1):

            # Render and push the cumulative wedge mask to OLED.
            # At step N, the OLED is white (blocking) everywhere except
            # N dark wedge cutouts — light passes only through those zones.
            frame = make_wedge_frame(step, WEDGES)
            oled.show(frame)

            # 300ms settle: allow OLED pixels to fully switch and
            # any optical transient from the frame change to decay
            # before taking the spectral measurement.
            time.sleep(0.3)

            # Read AS7341 — all 10 channels + F2+F3 470nm proxy
            reading = read_as7341()

            # Annotate reading with run metadata
            reading["step"]      = step
            reading["timestamp"] = datetime.now().isoformat()
            reading["open_pct"]  = round(step / WEDGES * 100, 1)   # % of circle open
            reading["gain"]      = AS7341_GAIN
            rows.append(reading)

            # Print live readout — F2+F3 is the primary diagnostic
            print(
                f"  step {step:02d}/{WEDGES}  "
                f"open={reading['open_pct']:5.1f}%  "
                f"F2+F3(470nm)={reading['f2_f3_sum']:6d}  "
                f"clear={reading['clear']:6d}"
            )

            # Hold for the remainder of the dwell period.
            # 0.3s settle already consumed above; subtract it so
            # total time per step = exactly DWELL_SEC.
            time.sleep(max(0, DWELL_SEC - 0.3))

        # ── STEP 4: OLED OFF ─────────────────────────────────────
        # Send display-off command. OLED goes dark; pixel RAM is
        # preserved. A subsequent oled.on() would restore the last
        # frame, but we don't need it after the calibration run.
        oled.off()
        print("[OLED] display off")
        time.sleep(0.5)   # brief settle before killing the LEDs

        # ── STEP 5: LEDs OFF ─────────────────────────────────────
        # PWM duty to 0 — MOSFET gate goes low, 12V rail disconnected
        # from LED strings. No current flows after this point.
        leds_off(h)

    finally:
        # ── Safety cleanup ────────────────────────────────────────
        # Always runs — even on keyboard interrupt or exception.
        # Ensures LEDs and OLED are never left on if the cycle fails.
        try:
            leds_off(h)
            oled.off()
        except Exception:
            pass   # hardware may already be in a failed state; ignore
        spi.close()
        lgpio.gpiochip_close(h)

    # ── STEP 6: Write CSV ─────────────────────────────────────────
    # Flush all 16 rows to a timestamped CSV. The gain value is
    # stamped per-row so logs are self-documenting across runs at
    # different gain settings.
    if rows:
        fieldnames = [
            "step", "timestamp", "open_pct", "gain",
            "f1_415nm", "f2_445nm", "f3_480nm", "f2_f3_sum",
            "f4_515nm", "f5_555nm", "f6_590nm",
            "f7_630nm", "f8_680nm", "clear", "nir"
        ]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n[CSV] saved → {csv_path}")

    # ── Summary ───────────────────────────────────────────────────
    # Print the F2+F3 ramp ratio (step1 → step16) and flag any
    # gain adjustment needed before the next run.
    print("\n── Calibration cycle complete ──")
    if rows:
        first = rows[0]["f2_f3_sum"]
        last  = rows[-1]["f2_f3_sum"]
        ratio = last / first if first > 0 else float("inf")
        print(f"  Gain:   {AS7341_GAIN}")
        print(f"  F2+F3   step 1 → step 16:  {first} → {last}  ({ratio:.1f}×)")

        # Saturation warning — if step 16 clips, readings are nonlinear
        if last > 60000:
            print("  [!] Step 16 near saturation — drop AS7341_GAIN to 8X")

        # Noise floor warning — if step 1 is in the noise, low-dose
        # wedges won't resolve and the H&D curve will be truncated
        if first < 500:
            print("  [!] Step 1 near noise floor — raise AS7341_GAIN to 32X")

        print(f"  Logs:   {csv_path}")


# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_cal_cycle()