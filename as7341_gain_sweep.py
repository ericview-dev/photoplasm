#!/usr/bin/env python3
"""
as7341_gain_sweep.py
AS7341 Gain Sweep Test — finds optimal gain for 470nm LED ring
BioArt Studio | Photoplasm | HTGAA 2026
"""

import os
os.environ['BLINKA_FORCEBOARD'] = 'RASPBERRY_PI_5'

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
import board
import busio
from adafruit_as7341 import AS7341, Gain

i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7341(i2c)
sensor.atime = 100
sensor.astep = 999

GAINS = [
    (Gain.GAIN_0_5X,  "0.5x"),
    (Gain.GAIN_1X,    "1x"),
    (Gain.GAIN_2X,    "2x"),
    (Gain.GAIN_4X,    "4x"),
    (Gain.GAIN_8X,    "8x"),
    (Gain.GAIN_16X,   "16x"),
    (Gain.GAIN_32X,   "32x"),
    (Gain.GAIN_64X,   "64x"),
    (Gain.GAIN_128X,  "128x"),
    (Gain.GAIN_256X,  "256x"),
    (Gain.GAIN_512X,  "512x"),
]

print("\n=== AS7341 Gain Sweep — 470nm LED Ring ===")
print(f"ATIME: {sensor.atime}  ASTEP: {sensor.astep}")
print(f"{'Gain':8s} {'480nm':>8s} {'Clear':>8s} {'NIR':>8s}  Bar")
print("=" * 55)

for gain_val, gain_label in GAINS:
    sensor.gain = gain_val
    time.sleep(0.3)
    b480  = sensor.channel_480nm
    clear = sensor.channel_clear
    nir   = sensor.channel_nir
    bar   = "█" * min(int(b480 / 200), 40)
    sat   = " SATURATED" if b480 >= 65000 else ""
    print(f"  {gain_label:6s}  {b480:8d} {clear:8d} {nir:8d}  {bar}{sat}")

print("\nDone.")