#!/usr/bin/env python3
"""
AS7341 Spectral Sensor Test
BioLight Project - BioArt Studio
Tests all 10 channels and confirms I2C comms on 0x39
"""

import time
import board
import busio
from adafruit_as7341 import AS7341

# Init I2C and sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7341(i2c)

# Optional tuning — adjust for your light levels
sensor.atime = 100       # integration time steps (0–255)
sensor.astep = 999       # step size in 2.78µs units
sensor.gain = 8          # 1x, 2x, 4x, 8x, 16x, 32x, 64x, 128x, 256x, 512x

CHANNELS = [
    ("415nm  (Violet)",  "channel_415nm"),
    ("445nm  (Violet)",  "channel_445nm"),
    ("480nm  (Blue)  ",  "channel_480nm"),
    ("515nm  (Cyan)  ",  "channel_515nm"),
    ("555nm  (Green) ",  "channel_555nm"),
    ("590nm  (Yellow)",  "channel_590nm"),
    ("630nm  (Orange)",  "channel_630nm"),
    ("680nm  (Red)   ",  "channel_680nm"),
    ("Clear          ",  "channel_clear"),
    ("NIR            ",  "channel_nir"),
]

print("\n=== AS7341 Spectral Sensor Test ===")
print(f"Address:  0x39")
print(f"ATIME:    {sensor.atime}")
print(f"ASTEP:    {sensor.astep}")
print(f"GAIN:     {sensor.gain}x")
print("=" * 38)

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
