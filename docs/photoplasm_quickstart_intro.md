# Photoplasm
### A light and pattern projector for biosensor-driven spatial imaging.

&nbsp;

**photo** (light) — the energy that drives the system.

**plasma** (formed living matter) — the substance of cells.

---

**Photoplasm** is a coined term that carries two simultaneous meanings, both accurate. At the substrate level, it describes any light-responsive biological material — living cells or cell-free systems — that records a spatially patterned light exposure and produces a measurable output: fluorescence, pigment, enzymatic activity, or any biosensor-driven response. At the molecular level, it describes the light-responsive circuits within those systems: with any light-responsive synthetic biological platform, including those engineered specifically to calibrate and test the device in the most optimized and controlled manner. The instrument that delivers, patterns, and measures that light takes its name from both meanings.

---

## A Quick Start Guide Introduction

Photoplasm is a biological imaging platform — a device that uses patterned light to activate spatially resolved biosensor responses in a biological substrate, the way a darkroom enlarger uses patterned light to expose photographic paper. If you have ever held a photographic negative up to a light source and watched an image appear, you already understand the fundamental concept. The difference is that instead of silver halide crystals suspended in gelatin, Photoplasm exposes a living bacterial lawn embedded in an agarose slab — or a cell-free biosensor system in a compatible substrate. Instead of silver reacting to photons, a biosensor circuit responds to blue light, producing a spatially resolved output that can be read, measured, and archived. The result is a bacteriograph: a biological image produced not by chemistry but by gene expression.

This is not a metaphor. It is an engineering decision, grounded in the same sensitometric principles that Hurter and Driffield used to characterize photographic film in 1890. The Photoplasm device is a repurposed darkroom enlarger — a Bogen column optical projector — with its original lamphouse replaced by a 470 nm blue LED array, and its negative carrier replaced by an OLED digital image mask. Any darkroom enlarger can serve as the optical platform with appropriate modifications and adaptation; the Bogen is the reference implementation documented in this guide. The baseboard remains exactly as it was, serving its original function as the stable base platform on which the plate stage, heater module, and sensor assembly sit. Everything else — the condenser lens, the focusing lens, the column, the spacer rings — is exactly as it was. The instrument already existed. The substrate is what changed.

---

## The Stages of Photoplasm

### Stage 1 — The Light Source

The light source is a Cree XP-E2 LED array emitting at 470 nm — blue light, the activation wavelength of the eLightOn optogenetic system and the primary excitation wavelength of the Photoplasm platform in its current configuration. This is not a simple on/off illuminator. The LED array is driven by a PWM (pulse-width modulation) circuit controlled by the device's central compute unit, which allows the light intensity to be set across a calibrated range of 16 standardized steps. This range — from minimum to maximum irradiance — defines the exposure envelope of the device, the same way a photographic enlarger's f-stop and timer define its exposure envelope. Each LED is paired with a Carclo polycarbonate diffuser optic that spreads and softens the point-source output before it reaches the condenser below, ensuring even distribution across the full field. The Cree array is mounted above the condenser lens system with a heat sink and active cooling fan to maintain stable, consistent output across extended exposure runs. The 470 nm wavelength is the first implementation — the modular light ring interface is designed to accept future rings at any wavelength, opening the platform to the full range of characterized optogenetic and biosensor systems.

### Stage 2 — The Condenser Lens System

The condenser lens system is inherited directly from the Bogen enlarger. Its job is to take the diffused blue light from the LED array and transform it into a uniform, parallel field of illumination — an even plane of light with no hot spots, no falloff, no variation across the full substrate plane. This is the same function a darkroom condenser performs for a photographic enlarger: collimating the light so that every point on the image mask receives the same intensity. Without it, the projected image would be brighter in the center and darker at the edges, producing uneven biosensor activation across the substrate. The condenser is the reason the Photoplasm projection is sharp and uniform rather than diffuse and gradient — it is the optical foundation on which spatial precision depends.

### Stage 3 — The OLED Digital Image Mask

Where a darkroom enlarger holds a photographic negative, Photoplasm holds an OLED digital image mask — a Waveshare SSD1309 128×64 pixel display mounted in the negative carrier position. The OLED works differently from a true optical mask: pixels that are off are transparent, allowing the blue LED light to pass through freely to the substrate below; pixels that are on become emissive, adding their own 470 nm light on top of the LED array light already passing through. This makes the OLED an additive mask rather than a subtractive one — bright areas of the image receive more total irradiance, while dark areas receive only the baseline LED irradiance. A calibration discovery confirmed that the OLED's own 470 nm emission contributes +58.7% additional irradiance across the full pixel density range — a meaningful and measurable effect that is accounted for in the exposure model. The planned upgrade to an ILI9341 transmissive LCD addresses this directly: the LCD uses a physical shutter layer that genuinely blocks light in dark regions rather than simply emitting less, making it a true subtractive mask analogous to a photographic negative. The mask carrier is a sliding sled — the same negative carrier mechanism as the original enlarger — meaning any future masking element can be introduced by sliding out the old carrier and sliding in the new one.

### Stage 4 — The Focusing Lens

The focusing lens — also inherited from the Bogen enlarger — sits below the image mask and projects the patterned light onto the biological substrate at the focal plane. The lens is set to f/8, which is the optimal balance between image sharpness and depth of field for this application. A wider aperture (lower f-number) produces a shallower depth of field — which risks blurring across the variable surface topology of an agarose slab or cell-free substrate. A narrower aperture (higher f-number) increases depth of field but reduces the irradiance reaching the substrate, requiring longer exposure times. At f/8, with the Cree LED upgrade delivering ≥100 µW/cm² at the plate plane, Photoplasm operates well within the eLightOn activation threshold across the full substrate surface. A 515 nm long-pass filter sits below the focusing lens during imaging — blocking the 470 nm excitation light and passing only the sfGFP emission at 510–530 nm — allowing the spectral sensor and camera to read biosensor response without excitation bleed-through.

### Stage 5 — The AS7341 Spectral Sensor

The AS7341 is an 11-channel spectral sensor deployed at plate height — the actual biological substrate plane — to measure the irradiance that the biosensor system will receive, not the irradiance at the source. This distinction matters: what happens at the source is irrelevant; what happens at the substrate is the experiment. The AS7341 reads across multiple wavelength channels simultaneously, and the F2+F3 channel sum (445 nm + 480 nm) is used as the 470 nm dose proxy — the closest available channels to the current platform activation wavelength. During calibration, the sensor sweeps a 16-step Bayer dither pattern to produce the optical H&D curve of the device: the logarithmic relationship between projected pixel density and measured irradiance at the substrate plane. This curve is the sensitometric fingerprint of Photoplasm — equivalent to the characteristic curve of a photographic emulsion — and it must be established before any biological exposure begins. The sensor is a modular element: it clips into the plate stage for calibration runs, characterizes the full optical stack at substrate level, and is then physically removed before the biological substrate is placed into the plate holder for exposure. In for calibration, out for exposure — the swap takes seconds.

### Stage 6 — The Plate Stage and Incubation Heater

The plate stage sits at the base of the Bogen column, at the calibrated focal plane of the focusing lens. It holds the 90 mm petri dish or compatible substrate vessel containing the biosensor material. Embedded beneath the stage is a PTCYIDU PTC heating element controlled by a DS18B20 temperature probe and an IRLZ44N MOSFET driver, maintaining the substrate at a tunable setpoint of 37°C — optimal growth temperature for *E. coli* DH5α and compatible with most cell-free protein synthesis systems. The heater is what eliminates the need for a separate incubator — the substrate maintains optimal temperature inside the dark chamber throughout the full exposure run, whether that run is a single continuous dose or a multi-cycle duty cycle sequence. The heater element nests directly on top of its own control circuitry board as a self-contained thermal module, removable and serviceable independently of the rest of the stack. The plate holder itself is designed to be removed and sterilized between runs — an essential feature for any biological substrate handled under aseptic conditions.

### Stage 7 — The Raspberry Pi 5 and Control Software

The Raspberry Pi 5 is the nervous system of the Photoplasm device. It controls the LED array via PWM on GPIO18, reads the AS7341 sensor via I2C, drives the OLED digital image mask via SPI, manages the heater via a second PWM channel on GPIO13, and — in the Aim 2 configuration — receives real-time machine vision feedback from the Raspberry Pi Camera Module mounted inside the dark chamber. All of these systems are coordinated by Python scripts running on Raspberry Pi OS Bookworm, with calibration data logged to CSV for export, analysis, and publication. The Raspberry Pi mounts directly onto the LED light ring — so when a future light ring is introduced for a different excitation wavelength, the Pi remounts onto the new ring without any other changes to the system. The control software is open-source, version-controlled on GitHub under MIT License, and designed to be modified. If you want to change the exposure protocol, the duty cycle timing, the step-wedge parameters, the image mask format, or the biosensor readout channel — you do it in code.

### Stage 8 — The Dark Chamber

The dark chamber is the physical envelope that holds it all together — a frustum cone designed in Fusion 360 and printed in gray PETG on a Bambu X1 Carbon. It is light-tight, stackable, and modular: the base cone is 256 mm tall with a 51 mm ID top aperture and a 152 mm OD base. A set of stackable spacer rings — approximately 50 mm each — adjust the throw distance between the lens and the substrate plane from 6 to 12 inches, allowing the operator to tune image magnification and irradiance at the plate. Adding or removing a ring takes seconds and requires no tools — the step-wedge calibration then maps the new geometry and establishes the updated exposure parameters. The cone is a solid structural print — not vase mode — designed for transport, handling, and repeated use in a community lab or makerspace environment. All hardware mounts, cable exits, and plate stage fixtures are designed into the print. The dark chamber is the last thing that goes on and the first thing that comes off — it is the simplest component and the one that makes everything else possible.

---

## The Modular Design Philosophy

Photoplasm is not a fixed instrument — it is a stack of interchangeable modules, each one designed to be swapped, upgraded, or replaced independently without disturbing the rest of the system. This is deliberate. The design philosophy mirrors the modular logic of the darkroom enlarger it is built from: change the negative, change the print. Change the lens, change the magnification. Change the light source, change the activation wavelength. In Photoplasm, every functional layer is a module.

From top to bottom, the stack nests as follows. The Raspberry Pi 5 mounts directly onto the LED light ring — so when a future light ring is introduced for a different excitation wavelength (green, red, or white for broadband), the Pi simply remounts onto the new ring without any other changes to the system. The LED ring itself is a swappable unit: the Cree XP-E2 470 nm array is the first implementation, but the mechanical and electrical interface is designed to accept future rings of any wavelength, opening the platform to the full range of characterized optogenetic and biosensor systems.

Below the light ring, the OLED digital image mask sits in the negative carrier position — the same sliding sled that holds a film strip in a darkroom enlarger. Swapping the OLED for the planned ILI9341 transmissive LCD is as simple as changing a negative strip: slide out the old carrier, slide in the new one, reconnect the display cable. No structural modification required. Any future masking element — a physical photographic negative, a different display technology, a custom spatial filter — can be introduced the same way.

The dark chamber cone accommodates the focal plane via stackable spacer rings. Each ring adds approximately 50 mm of throw distance, shifting the focal plane downward and adjusting the projected image size and irradiance at the plate. Adding or removing a ring takes seconds — no tools, no recalibration of the column, just a physical adjustment that the step-wedge calibration then maps to the new geometry.

At the base of the stack, the plate holder is a standalone module designed to be removed, sterilized, and replaced between exposure runs. The heater element nests directly on top of its own control circuitry board — a self-contained thermal module removable and serviceable independently of everything above it. The AS7341 spectral sensor clips into the plate stage for calibration, characterizes the full optical stack at substrate level, and is removed before the biological substrate is placed for exposure. In for calibration, out for exposure — the swap takes seconds.

Together, these modular relationships mean that Photoplasm can evolve without being rebuilt. A new wavelength, a new mask technology, a new sensor, a new substrate format — any of these can be introduced at any layer of the stack without redesigning the system from scratch. This is what makes Photoplasm a platform rather than a prototype.

---

## How It All Works Together

The relationship between these eight stages is the same relationship that exists in a photographic darkroom — sequential, calibrated, and dependent on each step being verified before the next begins. The LED array produces and diffuses the light. The condenser collimates it. The image mask patterns it. The focusing lens projects it. The AS7341 measures it at the substrate plane. The heater maintains the biological substrate at the right temperature to receive it. The Raspberry Pi orchestrates all of it. And the dark chamber keeps everything else out.

What makes Photoplasm novel is not any single one of these components — most of them existed before this project. What is novel is that they have been assembled into a coherent, calibrated, open-source platform specifically designed for biosensor-driven spatial imaging. The sensitometric H&D curve — the logarithmic relationship between light exposure and biosensor response — is the biological equivalent of a film characteristic curve, and producing it is the central deliverable of the platform's first experimental run. Everything in this Quick Start Guide is in service of that curve, and what comes after it.

---

## What Comes Next

This introduction has described what Photoplasm is and how its parts relate to each other. The Quick Start Guide that follows takes you through the process of using it — from device assembly and calibration, through biosensor preparation and substrate casting, to exposure, development, and reading the result. Each step builds on the one before it, the same way a darkroom workflow builds from chemistry to enlarger to print. By the end of the guide, you will have run your first Photoplasm exposure and produced your first biosensor spatial image.

Welcome to the platform.

---

*Photoplasm · An open platform for biosensor-driven spatial imaging.*
*MIT License · github.com/ericview-dev/photoplasm*
*BioArt Studio · MakerSpace Charlotte · Genspace NYC*
*Eric Schneider · HTGAA 2026*
