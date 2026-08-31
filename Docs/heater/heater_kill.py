#!/usr/bin/env python3
"""
heater_kill.py - EMERGENCY: force the heater gate LOW immediately.

Independent of any running calibration script. Claims GPIO13 and drives it LOW,
turning the MOSFET (and PTC) off. Run this any time the gate must be forced off.

    python3 heater_kill.py

Note: the surest physical stop is still to cut the 12 V supply - the heater
cannot heat with no 12 V regardless of gate state. This handles the gate side.
"""
import lgpio

GATE = 13
CHIP = 0   # match your working gpiochip (some Pi 5 setups use 4)

h = lgpio.gpiochip_open(CHIP)
try:
    lgpio.gpio_claim_output(h, GATE, 0)   # claim as output, drive LOW
    lgpio.gpio_write(h, GATE, 0)
    print("GPIO13 forced LOW - heater gate OFF.")
finally:
    lgpio.gpio_free(h, GATE)
    lgpio.gpiochip_close(h)
