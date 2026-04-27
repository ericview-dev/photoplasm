#!/usr/bin/env python3
"""
as7341_adafruit_test.py
AS7341 Spectral Sensor Test — Adafruit library with BLINKA_FORCEBOARD fix
Tests SSH execution with forced Pi 5 platform detection
BioArt Studio | Photoplasm | HTGAA 2026
"""

import os
os.environ['BLINKA_FORCEBOARD'] = 'RASPBERRY_PI_5'

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
import board
import busio
from adafruit_as7341 import AS7341

# Init I2C and sensor
print("Initializing I2C...")
i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7341(i2c)
print("Sensor connected OK")

# Tuning
from adafruit_as7341 import AS7341, Gain
sensor.gain = Gain.GAIN_256X
sensor.atime = 100
sensor.astep = 999

print(f"\n=== AS7341 Spectral Sensor Test (Adafruit) ===")
print(f"Gain:     {sensor.gain}x")
print(f"ATIME:    {sensor.atime}")
print(f"ASTEP:    {sensor.astep}")
print("=" * 46)

CHANNELS = [
    ("415nm  (Violet)", "channel_415nm"),
    ("445nm  (Indigo)", "channel_445nm"),
    ("480nm  (Blue)  ", "channel_480nm"),
    ("515nm  (Cyan)  ", "channel_515nm"),
    ("555nm  (Green) ", "channel_555nm"),
    ("590nm  (Yellow)", "channel_590nm"),
    ("630nm  (Orange)", "channel_630nm"),
    ("680nm  (Red)   ", "channel_680nm"),
    ("Clear          ", "channel_clear"),
    ("NIR            ", "channel_nir"),
]

try:
    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}]")
        for label, attr in CHANNELS:
            value = getattr(sensor, attr)
            bar = "█" * min(int(value / 500), 40)
            print(f"  {label}: {value:6d}  {bar}")
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nTest stopped.")