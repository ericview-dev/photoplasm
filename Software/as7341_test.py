#!/usr/bin/env python3
"""
AS7341 Spectral Sensor Test
BioLight Project - BioArt Studio
Tests all 10 channels and confirms I2C comms on 0x39
Revised: uses smbus2 direct bus access — works via SSH and interactive
"""

import time
import smbus2
import sys
sys.stdout.reconfigure(line_buffering=True)

# ── Config ─────────────────────────────────────────────────────────────────────
I2C_BUS     = 1        # Confirmed bus on Pi 5 after SDA resolder
AS7341_ADDR = 0x39     # Fixed I2C address

# AS7341 channel register pairs (low byte address, high byte = reg+1)
CHANNELS = [
    ("415nm  (Violet)", 0x95),
    ("445nm  (Indigo)", 0x97),
    ("480nm  (Blue)  ", 0x99),
    ("515nm  (Cyan)  ", 0x9B),
    ("555nm  (Green) ", 0x9D),
    ("590nm  (Yellow)", 0x9F),
    ("630nm  (Orange)", 0xA1),
    ("680nm  (Red)   ", 0xA3),
    ("Clear          ", 0xA5),
    ("NIR            ", 0xA7),
]

# ── Init ───────────────────────────────────────────────────────────────────────
bus = smbus2.SMBus(I2C_BUS)

# Verify sensor identity via WHO_AM_I register
who = bus.read_byte_data(AS7341_ADDR, 0x92)
print(f"\n=== AS7341 Spectral Sensor Test ===")
print(f"Bus:      {I2C_BUS}")
print(f"Address:  0x{AS7341_ADDR:02X}")
print(f"WHO_AM_I: 0x{who:02X} {'OK' if who == 0x24 else 'WARNING unexpected value'}")
print("=" * 38)

# ── Read loop ──────────────────────────────────────────────────────────────────
try:
    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}]")
        for label, reg in CHANNELS:
            low  = bus.read_byte_data(AS7341_ADDR, reg)
            high = bus.read_byte_data(AS7341_ADDR, reg + 1)
            value = (high << 8) | low
            bar = "█" * min(int(value / 500), 40)
            print(f"  {label}: {value:6d}  {bar}")
        time.sleep(1.0)

except KeyboardInterrupt:
    bus.close()
    print("\nTest stopped.")