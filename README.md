# Photoplasm

**Optogenetic bacteriography exposure unit — HTGAA 2026 Final Project**

*Eric Schneider · Makerspace Charlotte · BioArt Studio*

---

## What It Is

Photoplasm is a Raspberry Pi 5-based optogenetic exposure unit designed for bacteriographic imaging — using spatially-patterned 470 nm light to control gene expression in engineered bacteria. A 128×64 OLED acts as a programmable digital photomask, projecting custom grayscale patterns onto a bacterial culture plate through a 470 nm LED ring. An AS7341 spectral sensor measures delivered irradiance at the substrate plane in real time.

The result is a benchtop instrument capable of exposing a bacterial plate to a calibrated, spatially-defined light pattern — the optical equivalent of an enlarger in photographic darkroom practice, but for living cells.

---

## Hardware

| Component | Role |
|---|---|
| Raspberry Pi 5 | Host compute, GPIO, SPI, I²C, PWM |
| Waveshare SSD1309 128×64 OLED (SPI) | Digital photomask — spatial light modulator |
| 9× 470 nm LED ring | Primary illumination source |
| IRLZ44N MOSFET | PWM gate driver for LED ring (GPIO18) |
| Godiyes AS7341 spectral sensor (I²C) | 10-channel irradiance measurement at substrate |
| PTC heater + DS18B20 (1-Wire) | 37°C incubation thermal control |
| Raspberry Pi Camera Module | Sample imaging and machine vision (planned) |

Pin assignments: [`docs/appendix_C_pinout_NS-03_v8.md`](docs/appendix_C_pinout_NS-03_v8.md)

---

## Scripts

| Script | Purpose |
|---|---|
| [`photoplasm_densitometer.py`](photoplasm_densitometer.py) | 16-step Bayer dither transmission densitometer — characterises OLED optical neutrality at 470 nm |
| [`photoplasm_cal01.py`](photoplasm_cal01.py) | 16-step sensitometric calibration sweep using cumulative pie-wedge masks (Stouffer step wedge equivalent) |
| [`photoplasm_cal02.py`](photoplasm_cal02.py) | Three-state irradiance calibration (display off / display on / all-white) |

### Quick start — densitometer

```bash
# Install dependencies
sudo apt install python3-lgpio python3-spidev python3-smbus2 python3-pil
sudo pip3 install adafruit-circuitpython-as7341 --break-system-packages

# Run (requires hardware)
sudo python3 photoplasm_densitometer.py

# Dry run — no hardware required
python3 photoplasm_densitometer.py --dry-run

# Options
sudo python3 photoplasm_densitometer.py --gain 128X --settle 2.0 --pwm 80
```

Output: timestamped CSV in `cal_logs/` with per-step spectral channel readings and regression summary printed to stdout.

---

## Documentation

Full build and operation guide in [`docs/`](docs/):

| # | Chapter | Status |
|---|---|---|
| 1 | [SSH Setup & VS Code Remote Development](docs/photoplasm_ch01_ssh.md) | published |
| 2 | [GitHub & Version Control](docs/photoplasm_ch02_github.md) | published |
| 3 | [Wavelength Sensor — AS7341](docs/photoplasm_ch03_wavelength_sensor.md) | draft |
| 4 | [LED Ring · 470nm PWM Control](docs/photoplasm_ch04_led_ring.md) | published |
| 5 | [OLED Digital Image Mask](docs/photoplasm_ch05_oled_mask.md) | draft |
| 6 | [Incubation Heater Perfboard](docs/photoplasm_ch06_heater_perfboard.md) | published |
| 7 | [System Integration](docs/photoplasm_ch07_system_integration.md) | draft |
| 8 | [GUI / Flask Web Interface](docs/photoplasm_ch08_gui_flask.md) | draft |
| 9 | [SpacePlacer — Perfboard Layout Tool](docs/photoplasm_ch09_spaceplacer.md) | draft |
| 10 | [Camera Module](docs/photoplasm_ch10_camera_module.md) | placeholder |
| A | [Calibration Protocol](docs/appendix_A_calibration_protocol.md) | draft |
| B | [Feature Specification](docs/appendix_B_feature_specification.md) | working draft |
| C | [Pinout — NS-03 v8](docs/appendix_C_pinout_NS-03_v8.md) | working draft |

---

## Project Status

Active development on the `dev` branch. Hardware subsystems operational: LED ring, OLED mask, AS7341 sensor, incubation heater. Calibration scripts validated. Flask GUI and camera module in scope.

---

## License

MIT — see [`LICENSE`](LICENSE)
