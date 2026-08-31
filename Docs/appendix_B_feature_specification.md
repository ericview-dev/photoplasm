Photoplasm Quick Start Guide  ·  Appendix B: Feature Specification **Photoplasm**

**Appendix B: Feature Specification**

**Version: **v0.18 (working draft)

**Status: **Working functional specification — locks at release milestone **Date: **2026-05-17 **Repository: **github.com/ericview-dev/photoplasm **Author: **Eric Schneider

# About This Document

This appendix is the functional specification for Photoplasm, the Raspberry Pi-based optogenetic exposure unit at the heart of the BioLight project. It catalogs every feature of the device — hardware subsystems, software components, mechanical assemblies, and platform infrastructure — and tracks each feature's design intent, implementation status, and supporting build assets.

The specification is organized as a registry rather than a narrative. Each feature has a permanent identifier (such as LED-01 or CAM-01.2), a category grouping, and a row in the registry table. Detailed specifications for each feature follow the registry in the appendix body. The registry serves as the index; the body provides the depth.

## Working Document, Locked at Release

This is a working functional specification. It evolves as features are designed, scoped, built, and tested. Entries are added, statuses change, sub-features are decomposed, and upgrade paths emerge throughout development. Internal revision history is tracked at the end of this appendix; it captures the document's own evolution and is intended for working reference, not publication.

When Photoplasm reaches a release milestone, the specification is locked: statuses are reconciled, the working revision history is archived, and a final published version is produced. Until then, the specification is a living document, and the registry reflects the current state of the project rather than any single committed plan.

# Legend

## Category Codes

| **Code** | **Category** | **Scope** |
| --- | --- | --- |
| **SYS** | System & Lifecycle | Boot, shutdown, services, power management, platform-level concerns |
| **GUI** | Operator Interface | Flask web UI, kiosk panel, CLI, all user-facing controls |
| **LED** | Light Generation (EBOOT-based) | Current prototype: 9× 470 nm through-hole LEDs |
| **CRE** | Light Generation (Cree XP-E2) | Upgrade lightring: high-output star LEDs with heatsink, diffuser, fan |
| **MSK** | Image Mask | Variable-density image layer between light and sample |
| **WAV** | Spectral Measurement | Wavelength-based sensing of the light source; calibration, characteristic curves |
| **HTR** | Thermal Subsystem | Heater element, MOSFET driver, temperature sensing, control loop |
| **OPT** | Optical Isolation | Dark chamber, frustum, baffles, sample stage, passive optics |
| **CAM** | Imaging & Machine Vision | Camera-based observation of the sample; image acquisition, analysis pipelines |

## Status Lifecycle

| **Status** | **Meaning** |
| --- | --- |
| **🔵 Proposed** | Identified, rationale captured, not yet scoped |
| **🟡 Scoped** | Implementation path defined, parts listed, awaiting build |
| **🟢 In Progress** | Active development; hardware wiring, code, or both underway |
| **🧪 Tested** | Built and bench-verified; awaiting integration into chapter spec |
| **✅ Complete** | Fully specified, built, tested, operational |
| **🗄️ Deferred** | Was active; now paused, superseded, or migrated to another category |
| **⛔ Rejected** | Considered and declined; rationale preserved |

## Upgrade Path Notation

Succession: → FEATURE-ID (superseded) or → FEATURE-ID.x (gains a sub-variant).

Gating: Gates FEATURE-ID — milestone dependency. A feature in the gating role typically defines a pass/fail criterion in its Brief Description.

# Feature Specification Registry

## 1. SYS — System & Lifecycle

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **SYS-01** | Shutdown Button | GPIO21 momentary pull-up, graceful shutdown trigger | Ch. 7 | ✅ Complete | ✅ sys_01_shutdown.py | → SYS-03.2 |
| **SYS-02** | System Endpoints | /api/system/{shutdown,reboot,status} + signal handlers | Ch. 8 | 🟡 Scoped | 📝 sys_02_endpoints.py | → SYS-03 |
| **SYS-03** | Power Module | On/off/reboot module: hard switch, soft buttons, wake control | Ch. 8 | 🔵 Proposed | 📝 sys_03_power.py | — |
| **SYS-03.1** | Hard Power Switch | SPST rocker, 5V interrupt | Ch. 8 | 🔵 Proposed | ⬜ N/A | — |
| **SYS-03.2** | Soft Shutdown Button | Momentary, GPIO-triggered graceful shutdown (replaces SYS-01) | Ch. 8 | 🔵 Proposed | 📝 sys_03_2_soft_shutdown.py | — |
| **SYS-03.3** | Wake Button | Momentary on Pi 5 PWR_BTN header for wake-from-shutdown | Ch. 8 | 🔵 Proposed | ⬜ N/A | — |
| **SYS-03.4** | Reboot Control | Separate button or long-press gesture for reboot vs shutdown | Ch. 8 | 🔵 Proposed | 📝 sys_03_4_reboot.py | — |
| **SYS-04** | Battery Backup / UPS | Li-ion UPS HAT for graceful shutdown on power loss | Ch. 8 | 🔵 Proposed | 📝 sys_04_ups.py | — |
| **SYS-05** | Status LED Indicators | Front-panel LED stack | Ch. 8 | 🔵 Proposed | 📝 sys_05_status_leds.py | — |
| **SYS-05.1** | Pi Powered LED | Tied to 3V3 rail, lights when Pi has power | Ch. 8 | 🔵 Proposed | ⬜ N/A | — |
| **SYS-05.2** | System Ready LED | GPIO-driven, lights when Flask /health returns 200 | Ch. 8 | 🔵 Proposed | 📝 sys_05_2_ready_led.py | — |
| **SYS-05.3** | Shutdown In Progress LED | Blinks during graceful shutdown sequence | Ch. 8 | 🔵 Proposed | 📝 sys_05_3_shutdown_led.py | — |
| **SYS-06** | Battery-Backed RTC | Pi 5 onboard RTC with CR2032 cell for timestamp persistence | Ch. 8 | 🔵 Proposed | ⬜ N/A | — |
| **SYS-07** | Audible Status Cues | Piezo buzzer for shutdown, exposure complete, error states | Ch. 8 | 🔵 Proposed | 📝 sys_07_buzzer.py | — |
| **SYS-08** | Logging Infrastructure | Timestamped CSV writer shared across calibration + Flask | App. A / Ch. 7 | ✅ Complete | 🚧 sys_08_logger.py | — |
| **SYS-09** | lgpio Handle Pool | Shared GPIO claim/release management | Ch. 7 | ✅ Complete | 🚧 sys_09_gpio_pool.py | — |
| **SYS-10** | systemd Service Definition | Flask service unit for boot-time start | Ch. 8 | 🟡 Scoped | 📝 sys_10_photoplasm.service | Gates GUI-01, GUI-02 |
| **SYS-11** | Headless Pi 5 Configuration | OS install, hostname eyepi, user ericview, SSH, GPIO permissions | Ch. 7 | ✅ Complete | ⬜ N/A | — |
| **SYS-12** | Repo Sync Workflow | Three-way Mac ↔ GitHub ↔ Pi sync with HTTPS auth | Ch. 7 | ✅ Complete | ⬜ N/A | — |

## 2. GUI — Operator Interface

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **GUI-01** | Flask UI — Mode 1 (Browser) | Browser-based control at http://eyepi.local:5000, systemd-managed | Ch. 8 | 🟡 Scoped | 📝 gui_01_browser.py | — |
| **GUI-02** | Flask UI — Mode 2 (Kiosk) | Chromium kiosk on Micro HDMI touchscreen, shares Mode 1 codebase | Ch. 8 | 🟡 Scoped | 📝 gui_02_kiosk.py | — |
| **GUI-02.1** | Chromium Launch Script | Kiosk-mode browser invocation with localhost target | Ch. 8 | 🟡 Scoped | 📝 gui_02_1_chromium_launch.sh | — |
| **GUI-02.2** | Touchscreen Hardware | 5-7" capacitive HDMI/DSI panel (specific model TBD) | Ch. 8 | 🔵 Proposed | ⬜ N/A | — |
| **GUI-03** | Click CLI Layer | flask photoplasm <subcommand> — unified CLI/web control path | Ch. 8 | 🟡 Scoped | 📝 gui_03_cli.py | — |
| **GUI-04** | Exposure Scheduling | Scheduled runs with duration, intensity, mask, incubation params | Ch. 8 | 🟡 Scoped | 📝 gui_04_scheduler.py | — |
| **GUI-05** | Mask Upload & Library | PNG/SVG upload to mask buffer with re-usable mask library | Ch. 8 | 🟡 Scoped | 📝 gui_05_mask_library.py | — |
| **GUI-06** | Live Sensor Dashboard | Real-time AS7341 + DS18B20 stream via SSE/WebSocket | Ch. 8 | 🟡 Scoped | 📝 gui_06_dashboard.py | — |
| **GUI-07** | Session Logging UI | Per-session timestamped CSV, downloadable from UI | Ch. 8 | 🟡 Scoped | 📝 gui_07_session_log.py | — |
| **GUI-08** | Touch-First UI Conventions | ≥64 px tap targets, bold typography, single stylesheet | Ch. 8 | 🟡 Scoped | 📝 gui_08_styles.css | — |
| **GUI-09** | Safelight-Aware Color Palette | Cool-tone primary chrome, red reserved for safelight-invisible states | Ch. 8 | 🟡 Scoped | 📝 gui_09_colors.css | — |
| **GUI-10** | Error State Handling | UI surfaces for hardware fault, sensor disconnect, mid-exposure failures | Ch. 8 | 🟡 Scoped | 📝 gui_10_errors.py | — |
| **GUI-11** | Multi-Client Concurrency | SSE/WebSocket fan-out for simultaneous browser + kiosk sessions | Ch. 8 | 🟡 Scoped | 📝 gui_11_realtime.py | — |

## 3. LED — Light Generation (EBOOT-based Lightring)

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **LED-01** | LED Subsystem (Parent, EBOOT-based) | Variable-intensity 470 nm lightring; current prototype implementation | Ch. 4 | ✅ Complete | ✅ led_01_driver.py | → CRE-01 |
| **LED-01.1** | Breadboard/Protoboard Breakout | 9× 470 nm EBOOT LEDs, 3 strings of 3 series, 3×120Ω, 30-row protoboard | Ch. 4 | ✅ Complete | ✅ Present | → CRE-01 |
| **LED-01.2** | LED Matrix Board (alpha_01) | 120×120×2mm PETG, 9×9 diagonal RGB interleave, designed not built | Ch. 4 | 🟡 Scoped | 🚧 led_3D_01_2_matrix | → CRE-02 |
| **LED-01.3** | IRLZ44N PWM Gate Circuit | IRLZ44N at I15/I16/I17, 10kΩ G17-F20→GND, 3.3V gate at H17 | Ch. 4 | ✅ Complete | ✅ Present | — |
| **LED-03** | PWM Frequency Selection | LED PWM frequency (kHz) vs heater PWM (1-10 Hz) calibration | Ch. 4/7 | ✅ Complete | ✅ in led_01_driver.py | — |
| **LED-04** | Irradiance Measurement (EBOOT) | ~2.0 µW/cm² at 445nm; ~50× below 100 µW/cm² uncalibrated threshold² for blue-light optogenetic activation. Insufficient for eLightOn; drives CRE upgrade | Ch. 3 | ✅ Complete | ⬜ N/A | — |

## 4. CRE — Light Generation (Cree XP-E2 Lightring) — Priority 2 Upgrade

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **CRE-01** | Cree Lightring Subsystem (Parent) | High-output Cree XP-E2 3-up star LED lightring; supersedes LED-01 at full integration | Ch. 4 | 🟡 Scoped (P2) | 📝 cre_01_driver.py | — |
| **CRE-01.1** | XP-E2 3-Up Star LEDs | 3× Cree XP-E2 3-up star modules (9 emitters total at 470 nm) — ordered | Ch. 4 | 🟡 Scoped (P2) | ⬜ N/A | — |
| **CRE-01.2** | 6.8Ω 2W Current-Limiting Resistors | Drive current resistors at 12V rail for rated XP-E2 forward current | Ch. 4 | 🟡 Scoped (P2) | ⬜ N/A | — |
| **CRE-01.3** | Passive Heatsink | Thermal management for star LED substrate, continuous-duty sized | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_3D_01_3_heatsink | — |
| **CRE-01.4** | Active Cooling Fan | Forced airflow over heatsink for sustained high-drive operation | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_01_4_fan.py | — |
| **CRE-01.5** | Light Diffuser | Optical diffuser to spread point-source emission for uniform exposure plane | Ch. 4/6 | 🔵 Proposed (P2) | 📝 cre_3D_01_5_diffuser | — |
| **CRE-02** | CRE Lightring Protoboard Design¹ | New SpacePlacer JSON sidecar; produced by existing SpacePlacer tool, no tool changes required | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_lightring_alpha_01.json | — |
| **CRE-02.1** | CRE Layout JSON Artifact | cre_lightring_alpha_01.json — versioned design file in spaceplacer repo | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_lightring_alpha_01.json | — |
| **CRE-02.2** | Heatsink Mounting Cutouts | Layout features for thermal contact between star LED substrate and heatsink | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_3D_02_2_cutouts | — |
| **CRE-02.3** | Fan Mounting Provisions | Mechanical and electrical layout provisions for active cooling fan | Ch. 4 | 🔵 Proposed (P2) | 📝 cre_3D_02_3_fan_mount | — |
| **CRE-03** | CRE PWM Driver Adaptation | IRLZ44N driver verification at XP-E2 drive current; may require different gate scheme | Ch. 4 | 🔵 Proposed (P2) | 📝 in cre_01_driver.py | Gates CRE-01 |
| **CRE-04** | CRE Irradiance Measurement (Migration Gate) | AS7341 calibration of CRE at 470nm. Pass if ≥100 µW/cm²² (uncalibrated threshold). Fail if <100 µW/cm² (returns to engineering revision) | App. A | 🔵 Proposed (P2) | 📝 cre_04_irradiance.py | Gates CRE-06 |
| **CRE-05** | CRE Integration with Frustum Optics | Mounting and alignment of CRE assembly to existing OPT-01 dark chamber | Ch. 6 | 🔵 Proposed (P2) | 📝 cre_3D_05_frustum_adapter | — |
| **CRE-06** | CRE Migration & Cutover Plan | Procedure for swapping LED-01 → CRE-01 in operational unit | Ch. 4/7 | 🔵 Proposed (P2) | ⬜ N/A | — |

## 5. MSK — Image Mask

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **MSK-01** | Image Mask Subsystem (Parent) | Variable-density image layer between LightRing and sample | Ch. 4/7 | ✅ Complete | ✅ msk_01_mask.py | — |
| **MSK-01.1** | OLED Implementation (SSD1309) | SPI transmissive mask — currently active, has 470 nm self-emission limitation | Ch. 4/7 | ✅ Complete | ✅ msk_01_1_oled.py | → MSK-01.2 |
| **MSK-01.2** | LCD Implementation (ILI9341) | Transmissive LCD backlit by LED array; eliminates self-emission | Ch. 4 | 🔵 Proposed | 📝 msk_01_2_lcd.py | — |
| **MSK-01.3** | Mask Mounting Hardware | Physical mount between LED rail and image mask layer | Ch. 6 | ✅ Complete | 🚧 msk_3D_01_3_mount | — |
| **MSK-02** | Bayer Dither Mask Generation | 16-step density gradient mask generation for densitometer sweeps | App. A | ✅ Complete | ✅ in wav_03_densitometer.py | — |

## 6. WAV — Spectral Measurement & Calibration

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **WAV-01** | AS7341 Sensor | 10-channel I²C sensor at 0x39, drives calibration pipeline | Ch. 3 | ✅ Complete | ✅ wav_01_as7341.py | — |
| **WAV-01.1** | F1-F8 Spectral Channel Mapping | 415/445/480/515/555/590/630/680 nm channel definitions | Ch. 3 | ✅ Complete | ✅ in wav_01_as7341.py | — |
| **WAV-02** | Calibration Pipeline (Current) | Three-state irradiance, λex proxy, CSV logging | App. A | ✅ Complete | ✅ wav_02_calibration.py | — |
| **WAV-02.1** | Three-State Irradiance Method | Off / OLED-only / full exposure measurement methodology | App. A | ✅ Complete | ✅ in wav_02_calibration.py | — |
| **WAV-02.2** | λex Excitation Proxy | F2₄₄₅ + F3₄₈₀ summed-channel proxy for 470 nm excitation | App. A | ✅ Complete | ✅ in wav_02_calibration.py | — |
| **WAV-03** | Densitometer / H&D Sweep | 16-step Bayer dither, characteristic curves | App. A | ✅ Complete | ✅ wav_03_densitometer.py | — |
| **WAV-04** | (migrated to CAM-01) | Pi Camera Module — was tracked here under WAV when imaging was treated as a spectral concern; migrated to CAM category v0.14 | — | 🗄️ Deferred | — | → CAM-01 |
| **WAV-05** | Kc Coefficient Integration | Holds the irradiance coefficient (Kc) used to convert AS7341 raw counts to absolute µW/cm². Value derived externally through BioLight calibration protocol; Photoplasm consumes as configuration parameter | App. A | 🔵 Proposed | 📝 wav_05_kc_integration.py | — |
| **WAV-06** | Luminosity Reference (Clear Channel) | AS7341 clear channel for total flux measurement | App. A | ✅ Complete | ✅ in wav_02_calibration.py | — |

## 7. HTR — Thermal Subsystem

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **HTR-01** | DS18B20 Temperature Sensor | 1-Wire sensor on GPIO4 (Pin 7), feeds heater control loop | Ch. 4/7 | ✅ Complete | ✅ htr_01_ds18b20.py | — |
| **HTR-01.1** | DS18B20 JST Wiring | T7=Data(orange/yellow), T8=GND(gray/black), T9=VDD(blue/red) | Ch. 4 | ✅ Complete | ⬜ N/A | — |
| **HTR-02** | PTC Element & Driver (Board B) | PTC via IRLZ44N on GPIO13/PWM1, closed loop with DS18B20 feedback | Ch. 4/7 | 🟡 Scoped | 📝 htr_02_controller.py | — |
| **HTR-02.1** | PTC Heating Element | Self-regulating positive-temperature-coefficient element | Ch. 4 | 🟡 Scoped | ⬜ N/A | — |
| **HTR-02.2** | IRLZ44N MOSFET Driver | Gate-driven from GPIO13/PWM1, switches 12V to PTC | Ch. 4 | 🟡 Scoped | ⬜ N/A | — |
| **HTR-02.3** | Heater PTC JST Connector | T4=PTC+, T5=PTC- | Ch. 4 | 🟡 Scoped | ⬜ N/A | — |
| **HTR-02.4** | Heater Board Layout (SpacePlacer) | Perfboard layout designed in github.com/ericview-dev/spaceplacer | Ch. 4 | 🟡 Scoped | 🚧 Board B JSON (spaceplacer) | — |
| **HTR-03** | PWM Bench Test Sequence | Independent verification of GPIO13/PWM1 before integration | Ch. 7 | 🟡 Scoped | 📝 htr_03_pwm_test.py | Gates HTR-02 |
| **HTR-04** | PID Control Loop | Temperature setpoint hold for 37 °C incubation | Ch. 8 | 🔵 Proposed | 📝 htr_04_pid.py | — |
| **HTR-05** | Heater Board Chamber | Physical enclosure subsection for Board B | Ch. 6 | 🔵 Proposed | 📝 htr_3D_05_chamber | — |

## 8. OPT — Optical Isolation

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **OPT-01** | Dark Chamber — Frustum & Spacer Rings | Fixed cone (256mm × 51mm top × 152mm base) + stackable PETG spacers | Ch. 6 | ✅ Complete | ⬜ N/A | — |
| **OPT-01.1** | Frustum Cone | 256 mm height, 51 mm top ID, 152 mm base OD, PETG | Ch. 6 | ✅ Complete | 🚧 opt_3D_01_1_frustum | — |
| **OPT-01.2** | Spacer Ring (50 mm) | Stackable spacer for 6"-12" throw distance adjustment | Ch. 6 | ✅ Complete | 🚧 opt_3D_01_2_spacer | — |
| **OPT-02** | Modular Stacking Enclosure | PETG enclosure housing Pi, LED, mask, AS7341 | Ch. 6 | 🟢 In Progress | 🚧 opt_3D_02_enclosure | — |
| **OPT-03** | Sample Stage | Plate-holding stage at base of frustum (84 mm agar plate target) | Ch. 6 | ✅ Complete | 🚧 opt_3D_03_sample_stage | — |
| **OPT-04** | Light-Tight Sealing | Gaskets and overlap between stacked modules to prevent ambient leak | Ch. 6 | 🟡 Scoped | 📝 opt_3D_04_seals | — |

## 9. CAM — Imaging & Machine Vision

| **ID** | **Title** | **Brief Description** | **Ch.** | **Status** | **Asset** | **Upgrade** |
| --- | --- | --- | --- | --- | --- | --- |
| **CAM-01** | Pi Camera Module (Machine Vision) | RPi Camera Module for post-exposure sample imaging and fluorescence quantification | Ch. 10 | 🔵 Proposed | 📝 cam_01_capture.py | — |
| **CAM-01.1** | Camera Mount (Oblique or Under-Plate) | Physical mounting for fluorescence imaging at base of frustum | Ch. 6 | 🔵 Proposed | 📝 cam_3D_01_1_mount | — |
| **CAM-01.2** | Fluorescence Analytics Pipeline | Python image-analysis for sfGFP quantification | Ch. 10 | 🔵 Proposed | 📝 cam_01_2_fluorescence.py | — |

# Registry Footnotes

*Footnote markers are spaced superscript numerals following the relevant text (e.g., **"**µW/cm² ²**"**). The unspaced **"**²**"** in I²C elsewhere in the registry is the standard typographic rendering of the Inter-Integrated Circuit protocol name and is not a footnote reference.*

### ¹ CRE-02 SpacePlacer Note

CRE-02 is a JSON design artifact produced by SpacePlacer's existing perfboard substrate model. No SpacePlacer tool changes are required for CRE-02 to proceed. A separate concept — a proto-breadboard framework extending SpacePlacer's grid-and-component model to handle additional substrate types — has been discussed as a potential aid to future board designs, but is a SpacePlacer feature, not a Photoplasm feature. It is tracked at priority scope (P2-spaceplacer) in the SpacePlacer roadmap and does not gate CRE-02.

### ² Irradiance Calculation and Calibration

Irradiance values in this specification (LED-04, CRE-04, and any other µW/cm² references) are derived from AS7341 spectral channel readings via the calibration methodology documented in Appendix A: Calibration Protocol. The relevant features in this registry are:

WAV-02 — Calibration Pipeline (photoplasm_cal02.py)

WAV-02.1 — Three-state irradiance method (off / mask-only / full exposure)

WAV-02.2 — λex excitation proxy formula (F2₄₄₅ + F3₄₈₀ summed-channel proxy for 470 nm)

WAV-05 — Kc Coefficient Integration — applies the externally-derived Kc to convert AS7341 counts to absolute µW/cm² **Two-path measurement. Absolute irradiance can be obtained two ways: (1) direct measurement with an external calibrated photospectrometer at the plate plane, which is metrologically traceable but slow and requires wet-lab access; or (2) derived measurement through the onboard AS7341 multiplied by the Kc coefficient, which is fast and in-situ but only as accurate as the most recent Kc calibration.**

**Kc calibration is a refinement, not a prerequisite. Photoplasm delivers controlled, repeatable exposures using the onboard AS7341 in its uncalibrated state. Until a Kc value is received from BioLight****'****s calibration protocol, the 100 µW/cm² target in LED-04 and CRE-04 should be read as an uncalibrated minimum threshold rather than a metrologically traceable absolute value. The CRE-04 pass/fail migration gate can be evaluated against uncalibrated readings; metrological re-verification is a separate quality step.**

# Cross-Project References

## SpacePlacer (perfboard/PCB design tool)

| **Photoplasm Feature** | **SpacePlacer Dependency** | **Status** |
| --- | --- | --- |
| CRE-02 (CRE Lightring Protoboard Design) | Uses existing SpacePlacer perfboard model; no SpacePlacer changes required | No dependency |
| (potential future) — multi-substrate board designs | Proto-breadboard framework concept | (P2-spaceplacer) |
| HTR-02.4 (Heater Board Layout) | Uses existing SpacePlacer v0.1 perfboard model | No dependency |

## BioLight (wetware project)

**Target optogenetic system: eLightOn (RsLOV-LexA408 / pColE408, 470 nm activation, sfGFP reporter). Photoplasm****'****s light-delivery specifications — wavelength selection, irradiance targets, exposure scheduling — are calibrated for eLightOn as the sole optogenetic system across all BioLight aims.**

| **Photoplasm Feature** | **BioLight Relationship** |
| --- | --- |
| MSK-01.1 (OLED mask) | Provides image-mask substrate for BioLight Aim 1A optogenetic exposure |
| CAM-01 (Pi Camera Module) | Enables sfGFP fluorescence quantification per BioLight Aim 1A/1B protocols |
| HTR-02 (Heater) | Provides 37°C incubation for BioLight wet-lab protocols |
| LED-04 / CRE-04 (Irradiance milestones) | Verify light output meets blue-light optogenetic activation thresholds; CRE-04 gates the LED-01 → CRE-01 migration |
| WAV-05 (Kc Coefficient Integration) | BioLight owns the Kc calibration protocol. The cross-instrument calibration (Photoplasm AS7341 vs. external wet-lab photospectrometer) is wet-lab methodology — sample geometry, replicate counts, statistical derivation, validation — that lives in BioLight's experimental documentation. Photoplasm consumes the resulting Kc value as a configuration parameter. (P2-biolight scope; depends on wet-lab photospectrometer access at Genspace or equivalent.) |

*Important boundary: Kc calibration is not a prerequisite for the Photoplasm device build. The device delivers controlled, repeatable exposures using the onboard AS7341 in its uncalibrated state. Kc calibration adds metrological traceability — the ability to report irradiance in standardized µW/cm² units — but does not affect the device**'**s exposure capability, repeatability, or scientific utility for relative measurements.*

# Registry Summary

| **Category** | **Total** | **✅ Complete** | **🟢 In Progress** | **🟡 Scoped** | **🔵 Proposed** | **🗄️ Deferred** |
| --- | --- | --- | --- | --- | --- | --- |
| SYS | 19 | 5 | 0 | 2 | 12 | 0 |
| GUI | 13 | 0 | 0 | 12 | 1 | 0 |
| LED | 6 | 5 | 0 | 1 | 0 | 0 |
| CRE (P2) | 14 | 0 | 0 | 3 | 11 | 0 |
| MSK | 5 | 4 | 0 | 0 | 1 | 0 |
| WAV | 9 | 6 | 0 | 0 | 2 | 1 |
| HTR | 10 | 2 | 0 | 6 | 2 | 0 |
| OPT | 6 | 4 | 1 | 1 | 0 | 0 |
| CAM | 3 | 0 | 0 | 0 | 3 | 0 |
| **Total** | **85** | **26** | **1** | **25** | **32** | **1** |

# Per-Feature Specifications

*Detailed specifications for each feature follow. Spec sections are drafted in priority order: ✅ Complete entries back-documented first, then 🟢/🟡 entries as the primary active-development target, with 🔵 Proposed entries deferred until scoped.*

*(85 feature specification stubs awaiting drafts — to be developed in subsequent sessions.)*

# Universal Design & UI Validation

*Closing section addressing accessibility considerations, Universal Design principles, and empirical interface testing methodology under wet-lab conditions. To be developed once the functional specification body is sufficiently mature to support meaningful validation criteria.*

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.18  ·  2026-05-17  ·  working draft