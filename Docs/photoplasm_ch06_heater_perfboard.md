Photoplasm Quick Start Guide  ·  Chapter 6 — Incubation Heater Perfboard

# **Chapter 6 — Incubation Heater Perfboard**

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

## **Overview**

Reliable bacteriographic imaging with the eLightOn optogenetic circuit requires *E. coli* cultures maintained at 37°C — the standard growth temperature and the condition under which the RsLOV–LexA408 repressor operates within its characterized parameters. Temperature variation during incubation introduces biological noise that obscures the dose-response relationship the H&D calibration curve depends on.

The Heater Perfboard is a dedicated half-size perfboard carrying a PTC ceramic heating element, DS18B20 temperature probe, IRLZ44N MOSFET driver, and JST 6-pin output connector. It is designed for integration into the Photoplasm stacking enclosure and controlled directly from the Raspberry Pi 5.

Circuit layout for this board was planned using SpacePlacer v0.1 — a browser-based perfboard layout tool built during the Photoplasm hardware build. See Chapter 9 — SpacePlacer for full tool documentation.

## **System Context**

The Photoplasm enclosure is a modular stacking PETG system, each ring approximately 25.4 mm (1") tall. The thermal stack from bottom to top:

[ Cone / Dark Chamber          ]  ← optical path, AS7341 sensor [ Culture Stage                ]  ← interchangeable with Calibration Stage [ PTC Heater Chamber           ]  ← heat source, DS18B20 probe [ Electronics Chamber          ]  ← Heater Perfboard, all control circuitry [ Base / Floor                 ]

Heat rises through the stack by natural convection. The electronics chamber sits at the base — the coolest zone, furthest from the heat source. The DS18B20 probe mounts in the culture stage wall, reading representative culture-zone temperature rather than heater surface temperature.

## **Component List**

| **Ref** | **Component** | **Value / Part** | **Notes** |
| --- | --- | --- | --- |
| U1 | PTC heater element | PTCYIDU ceramic disc | 5V–12V, self-limiting at Curie temp |
| Q1 | MOSFET | IRLZ44N TO-220 | Logic-level N-channel, Vgs(th) 1–2V |
| T1 | Temperature sensor | DS18B20 waterproof probe | 1-Wire, ±0.5°C accuracy at 37°C |
| R1 | Gate resistor | 470Ω ¼W | Q1 gate current limiting |
| R2 | Pull-up resistor | 4.7kΩ ¼W | DS18B20 1-Wire data line |
| J1 | Output connector | JST 6-pin 2.0mm | PTC + and −, DS18B20 data/GND/VDD, reserved |
| — | Perfboard | Half-size (14×20 holes) | PETG enclosure footprint |

## **Circuit Description**

### **PTC Heater Path**

The PTCYIDU PTC ceramic element is a self-limiting heater — its resistance rises sharply at the Curie temperature, preventing thermal runaway without a separate controller. This is the primary thermal safety mechanism.

+12V supply

    │

   PTC+ (J1 pin 1)

    │

  PTC element

    │

   PTC− (J1 pin 2)

    │

  Q1 Drain (IRLZ44N)

    │

  Q1 Source

    │

   GND Q1 Gate is driven by GPIO13 (PWM1) through R1. When PWM duty cycle is high, Q1 conducts and current flows through the PTC element. Duty cycle controls average power and therefore temperature setpoint.

### **DS18B20 Temperature Sensor**

The DS18B20 uses the Dallas 1-Wire protocol on a single GPIO pin. R2 (4.7kΩ) pulls the data line to 3.3V. Multiple DS18B20 sensors can share one bus — each is addressable by its unique 64-bit ROM ID, enabling future delta-T measurement between culture zone and heater surface.

3.3V ─── R2 (4.7kΩ) ─── DS18B20 Data ─── GPIO4 (1-Wire)

                     │

                   J1 pin 3 (data)

DS18B20 GND ─── J1 pin 4 DS18B20 VDD ─── J1 pin 5 (3.3V)

## **JST 6-Pin Connector Pinout (J1)**

| **Pin** | **Label** | **Function** | **Wire Color** |
| --- | --- | --- | --- |
| 1 | T4 / J1 | PTC + | Red |
| 2 | T5 / J2 | PTC − (switched drain) | Black |
| 3 | T7 / J3 | DS18B20 Data | Orange (yellow wire) |
| 4 | T8 / J4 | DS18B20 GND | Gray (black wire) |
| 5 | T9 / J5 | DS18B20 VDD (3.3V) | Blue (red wire) |
| 6 | — | Reserved (future delta-T) | — |

## **Raspberry Pi 5 Pin Assignment (NS-03 v7)**

| **Pi Pin** | **GPIO** | **Function** | **Connected To** |
| --- | --- | --- | --- |
| 33 | GPIO13 | PWM1 — heater control | Q1 Gate via R1 |
| 7 | GPIO4 | 1-Wire — temperature | DS18B20 data line |
| 1 | 3.3V | Logic supply | R2 pull-up, DS18B20 VDD |
| 6 | GND | Ground reference | Q1 Source, DS18B20 GND |

*Note: GPIO12 (Pin 12 / PWM0) is reserved for the 470nm LED array. GPIO13 (Pin 33 / PWM1) is dedicated to the heater to keep the two PWM channels independent.*

## **Perfboard Layout**

The Heater Perfboard uses a half-size perfboard (14 columns × 20 rows, labeled A–N / 1–20). Circuit layout was designed using SpacePlacer v0.1 (see Chapter 9). SpacePlacer provides a browser-based A–T/1–14 grid, three trace types (solder bridge, jumper wire, external connection), per-net toggle visibility, and a DRC engine — use it to verify any layout changes before soldering.

Key placement rules observed during layout:

- IRLZ44N TO-220 placed in the board center — leads span 3 rows at 2.54mm pitch (G·D·S order left to right)

- Gate resistor R1 inline between Pi header and MOSFET gate

- Pull-up resistor R2 between 3.3V rail and DS18B20 data node

- JST 6-pin connector at board edge for clean cable exit

- GND rail runs along bottom row

- 3.3V rail runs along top row

## **Python Control Script**

Enable 1-Wire in /boot/config.txt: dtoverlay=w1-gpio,gpiopin=4 Reboot, then verify sensor detection: sudo modprobe w1-gpio sudo modprobe w1-therm ls /sys/bus/w1/devices/

# should show: 28-xxxxxxxxxxxx

Basic temperature read: import lgpio import time import glob

# DS18B20 read

def read_temp():

    base = '/sys/bus/w1/devices/'

    device = glob.glob(base + '28*')[0]

    with open(device + '/w1_slave') as f:

        lines = f.readlines()

    if 'YES' in lines[0]:

        temp_c = float(lines[1].split('t=')[1]) / 1000.0

        return temp_c

    return None

# PWM heater control (GPIO13, PWM1)

chip = lgpio.gpiochip_open(0) lgpio.gpio_claim_output(chip, 13)

SETPOINT = 37.0   # °C KP = 2.0          # proportional gain (tune to your PTC)

try:

    while True:

        temp = read_temp()

        if temp is not None:

            error = SETPOINT - temp

            duty = max(0, min(100, KP * error))

            lgpio.tx_pwm(chip, 13, 100, duty)  # 100Hz PWM

            print(f"Temp: {temp:.2f}°C  Error: {error:.2f}  Duty: {duty:.1f}%")

        time.sleep(1)

finally:

    lgpio.tx_pwm(chip, 13, 100, 0)

    lgpio.gpiochip_close(chip)

*Tuning note: The proportional gain `KP` will need adjustment based on your specific PTC element wattage and enclosure thermal mass. Start low (KP=1.0) and increase. Full PID implementation is a recommended enhancement for stable long-duration exposures.*

## **Smoke Test Checklist**

Before applying 12V:

- [ ] Verify GND continuity from Q1 Source to Pi Pin 6

- [ ] Verify 3.3V continuity from R2 top to Pi Pin 1

- [ ] Verify GPIO13 reaches Q1 Gate through R1

- [ ] Verify GPIO4 reaches DS18B20 data line through R2 pull-up

- [ ] Verify JST J1 pins 1–5 match the pinout table

- [ ] Confirm PTC element is not touching any conductive surface

With 3.3V only (no 12V):

- [ ] `sudo i2cdetect -y 1` — not applicable (DS18B20 is 1-Wire, not I²C)

- [ ] `ls /sys/bus/w1/devices/` — confirm `28-xxxx` device appears

- [ ] Run temperature read script — confirm reading near ambient (~20–25°C)

Apply 12V last:

- [ ] Run heater script at 10% duty — confirm PTC element warms slightly

- [ ] Run heater script targeting 37°C — monitor temperature rise

- [ ] Confirm PTC self-limits (temperature plateaus, does not runaway)

## **Safety Notes**

- PTC elements are self-limiting but will still reach 50–70°C at the disc surface. Do not touch during operation.

- The 12V supply for the PTC must not share the Pi's GPIO 5V/3.3V rails. Use a separate supply rail.

- Always bring GPIO13 PWM to 0% duty before disconnecting the PTC leads.

- Run initial smoke tests with the Photoplasm enclosure open for visual inspection.

## **Future Enhancements**

- PID control — replace proportional-only control with full PID for tighter setpoint regulation during long exposures

- Delta-T sensor — second DS18B20 at cone exit (JST pin 6, GPIO4 1-Wire shared bus) for culture zone gradient measurement

- CSV logging — append timestamp, temp, duty cycle to `heater_log.csv` alongside exposure logs

- Safety cutoff — GPIO interrupt or watchdog timer to cut heater power if temperature exceeds 42°C threshold

*Next chapter: Chapter 7 — System Integration · LED + OLED + AS7341 + Heater*

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.0  ·  2026-05-17  ·  published