Photoplasm Quick Start Guide  ·  Table of Contents

# Table of Contents

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.1  ·  2026-05-18  ·  github.com/ericview-dev/photoplasm

---

## About This Document

This Table of Contents is the canonical inventory for the Photoplasm Quick Start Guide. It lists every chapter and appendix in the book, with the current version, date, status, and a one-line summary of scope. When a chapter or appendix is added, renumbered, or version-bumped, this document is updated as part of the same commit.

The book is organized as **nine chapters** (build sequence) and **three appendices** (reference material). Chapters follow the device build from first connection through final integration. Appendices hold cross-cutting reference material that is invoked by multiple chapters: calibration protocol, feature specification registry, and pin assignments.

---

## Chapters

| # | Title | Version | Date | Status | Filename |
|---|---|---|---|---|---|
| 1 | SSH Setup & VS Code Remote Development | 1.0.0 | 2026-04-28 | published | `photoplasm_ch01_ssh.md` |
| 2 | GitHub & Version Control | 1.0.0 | 2026-04-28 | published | `photoplasm_ch02_github.md` |
| 3 | Wavelength Sensor (AS7341) | 0.1.0 | 2026-04-26 | draft | `photoplasm_ch03_wavelength_sensor.md` |
| 4 | LED Ring · 470nm PWM Control | 1.0.0 | 2026-05-17 | published | `photoplasm_ch04_led_ring.md` |
| 5 | OLED Digital Image Mask | 0.2.0 | 2026-05-17 | draft | `photoplasm_ch05_oled_mask.md` |
| 6 | Incubation Heater Perfboard | 1.0.0 | 2026-05-17 | published | `photoplasm_ch06_heater_perfboard.md` |
| 7 | System Integration | 0.1.0 | 2026-05-17 | draft | `photoplasm_ch07_system_integration.md` |
| 8 | GUI / Flask Web Interface | 0.1.0 | 2026-05-17 | draft | `photoplasm_ch08_gui_flask.md` |
| 9 | SpacePlacer | 0.1.0 | 2026-05-18 | draft | `photoplasm_ch09_spaceplacer.md` |
| 10 | Camera Module (Pi Camera · Machine Vision) | 0.1.0 | 2026-05-18 | placeholder | `photoplasm_ch10_camera_module.md` |

## Appendices

| # | Title | Version | Date | Status | Filename |
|---|---|---|---|---|---|
| A | Calibration Protocol | 0.1.0 | 2026-05-17 | draft | `appendix_A_calibration_protocol.md` |
| B | Feature Specification | 0.18 | 2026-05-17 | working draft | `appendix_B_feature_specification.md` |
| C | Pi 5 Pinout — NS-03 v8 | v8 | 2026-05-17 | working draft | `appendix_C_pinout_NS-03_v8.md` |

---

## Chapter Scope Summaries

### Chapter 1 — SSH Setup & VS Code Remote Development
Establishes passwordless SSH from Mac to Raspberry Pi 5 (`eyepi`) and connects VS Code Remote-SSH for development against the running hardware. Covers key generation, `~/.ssh/config` aliases, and the end-to-end verification that proves the Mac → Pi development loop works.

### Chapter 2 — GitHub & Version Control
Brings the photoplasm repository under version control with the Mac → GitHub → Pi three-way sync architecture. Covers Personal Access Tokens, branch strategy (`main` / `dev` / `feature/*`), daily workflow, commit message conventions, and the promotion path from `dev` to `main`.

### Chapter 3 — Wavelength Sensor (AS7341)
The first hardware build chapter. Wires the Godiyes AS7341 spectral sensor to the Pi over I²C, resolves the BLINKA platform-detection hang for non-interactive SSH execution, and characterizes the sensor's gain response (0.5× through 512×) plus dark-chamber noise floor and signal-to-noise. The sensor's spectral channel output feeds every downstream calibration and integration measurement.

### Chapter 4 — LED Ring · 470nm PWM Control
The primary illumination source. Builds the 9-LED 470nm ring with IRLZ44N MOSFET PWM switching off GPIO18 (PWM0), characterizes irradiance versus RsLOV/eLightOn detection thresholds, and documents the upgrade path to Cree XP-E2 (Aim 2, scoped in Appendix B's CRE category).

### Chapter 5 — OLED Digital Image Mask
The spatial light modulator. Loads the Waveshare SSD1309 128×64 OLED for digital mask projection over the LED ring, characterizes the OLED's additive 470nm self-emission as a calibration offset (Δ_oled), and scopes the planned ILI9341 transmissive LCD upgrade.

### Chapter 6 — Incubation Heater Perfboard
The thermal control subsystem. Designs and documents the perfboard build for the PTC heater + DS18B20 temperature sensor stack, with circuit layout produced via SpacePlacer (Chapter 9). Establishes the 37°C incubation envelope for post-exposure bacterial growth.

### Chapter 7 — System Integration
Combines all four hardware subsystems (LED ring, OLED mask, AS7341 sensor, heater) into a unified control sequence. Covers GPIO pin sharing, I²C bus coexistence, timing constraints, and the smoke-test sequence that validates the full stack before biological exposures.

### Chapter 8 — GUI / Flask Web Interface
The operator interface. Forward-looking design brief for the Flask-based browser UI that exposes the integrated device to the operator. Scope is held in Appendix B's GUI category (GUI-01 through GUI-11); this chapter carries the design rationale, architectural intent, and accessibility principles.

### Chapter 9 — SpacePlacer
The perfboard layout tool used to design the Heater Perfboard (and future boards). Browser-based JSON-backed grid layout with DRC, version control, and build-ready inventory export.

### Chapter 10 — Camera Module (Pi Camera · Machine Vision)
The imaging stage. Introduces the Raspberry Pi Camera Module for three roles: monitoring real-time light exposure on the substrate plane, time-lapse capture of bacterial plate growth, and machine-vision-based bacteriographic image quantification (OpenCV pipeline). Placeholder pending camera stage build.

---

## Appendix Scope Summaries

### Appendix A: Calibration Protocol
Defines the biological calibration methodology — stepwedge exposure series, dose-response curve construction, H&D curve interpretation, and the conditions under which a calibration run is considered valid. Establishes the operating envelope for all subsequent imaging experiments. Hosts the Kc coefficient that maps AS7341 raw counts to absolute irradiance in µW/cm².

### Appendix B: Feature Specification
The registry of every feature in Photoplasm. Each feature has a permanent identifier (LED-01, WAV-02.1, GUI-04, etc.), a category grouping, a target chapter, a status, and a supporting code or asset reference. The CRE category scopes the Cree XP-E2 Aim 2 upgrade. The Methodology Notes section covers the irradiance calculation provenance.

### Appendix C: Pi 5 Pinout — NS-03 v8
The authoritative pin assignment reference for the Raspberry Pi 5. All chapters, schematics, and code reconcile to this document. Tracks PWM channel assignments, I²C buses, 1-Wire connections, and reserved pins; supersedes NS-03 v7.

---

## Status Legend

| Marker | Meaning |
|---|---|
| **published** | Working hardware/software, validated, complete. Reference-grade. |
| **draft** | Working content, hardware partially or fully built, but still subject to revision. |
| **working draft** | Living document. Updates expected with every revision of the underlying subject. |
| **placeholder** | Chapter slot reserved, introductory content only. Body content pending build/test. |

---

## Version Conventions

| Version pattern | Meaning |
|---|---|
| **v0.1.0** | Initial draft. Outline and introductory content; partial body. |
| **v0.X.0** | Working draft. Body content present, some sections incomplete or `[TBD]`. |
| **v1.0.0** | Published. Fully validated, reference-grade. |
| **v0.18** (no patch) | Used for registry/spec documents (App. B). Increments freely with content. |
| **v8** (no semver) | Used for hardware revision documents (App. C). Tracks hardware reality. |

---

## Cross-Reference Conventions

| Form | Use case |
|---|---|
| `Ch. N` / `Chapter N` | Short and long form of chapter references |
| `App. X` / `Appendix X` | Short and long form of appendix references |
| `Appendix X: Title` | First introduction of an appendix in a passage — uses full title with colon |
| `Chapter N — Title` | First introduction of a chapter in a passage — uses full title with em dash |

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.1  ·  2026-05-18  ·  published
