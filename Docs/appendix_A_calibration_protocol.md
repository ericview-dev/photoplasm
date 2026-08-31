Photoplasm Quick Start Guide  ·  Appendix A: Calibration Protocol

# Appendix A: Calibration Protocol

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm *Stepwedge Calibration, Light-Dose Quantification, and Incremental Exposure Protocols for Bacterial Reporter Systems using BioLight V5 (derived from eLightOn)*

> **DRAFT — Working Appendix.** This appendix is in active development. Section headings, protocol parameters, and figures are subject to revision as calibration data are collected. Placeholder values are indicated with `[TBD]`.

---

## **Overview**

Optogenetic control of gene expression in living bacterial cells requires a precise and reproducible relationship between the physical properties of the illumination source and the resulting biological output — in this case, measurable fluorescent protein expression. Without that relationship firmly established, any image, pattern, or dose delivered to a cell culture is an uncontrolled variable, and the experiment yields ambiguous data at best.

The concept of Photoplasm — the light-sensitive biological emulsion at the heart of the BioLight project — draws a deliberate analogy to photographic chemistry. A photographic emulsion responds to light exposure in a predictable, quantifiable way: the H&D (Hurter-Driffield) curve maps exposure to density, and every serious darkroom begins with a step-wedge calibration to characterize that curve before any image is committed to film. Photoplasm operates by the same logic. BioLight V5 is our optogenetic plasmid construct, developed from the eLightOn system — a blue-light–inducible transcription platform that established the core LOV-domain photosensory architecture we build upon. The bacterial reporter layer encoding BioLight V5 must be characterized before it can serve as a medium for biological imaging.

This appendix describes the stepwedge calibration protocol: a systematic, incremental exposure series applied to a uniform bacterial lawn under controlled conditions. The output is a biological dose-response curve — the Photoplasm equivalent of the H&D curve — which quantifies the relationship between light dose (irradiance × time, expressed as J/cm²) and normalized reporter output (relative fluorescence units, RFU, or optical density of colorimetric product). All subsequent imaging experiments depend on the valid operating range defined by this calibration.

## **1.  The Stepwedge: Concept and Rationale**

In classical photography, a stepwedge (also called a step tablet or neutral-density step wedge) is a series of optical density values arranged in discrete, evenly-spaced increments. When contact-printed onto photosensitive material, each step delivers a known, incrementally different exposure to the emulsion, producing a characteristic curve of response versus dose. The stepwedge is not an image — it is a measurement instrument.

In the BioLight context, the stepwedge is implemented as a spatial light modulator (SLM) pattern: a series of discrete rectangular zones, each programmed to transmit a defined fraction of total illumination intensity from the 470 nm LED array. The zones span from minimum to maximum exposure in consistent logarithmic steps. The biological emulsion — plated bacterial cells expressing BioLight V5 — is exposed beneath this pattern for a defined duration. After incubation and reporter development, each zone is imaged and its fluorescence output is quantified.

### **1.1  Why discrete steps rather than a continuous gradient**

Discrete steps are preferable to a continuous gradient for the calibration phase for three reasons. First, discrete zones allow independent statistical treatment of each exposure level. Second, the sharp edges between zones create unambiguous boundaries that facilitate automated image segmentation. Third, discrete steps map directly onto the digitally-controlled PWM (pulse-width modulation) output of the BioLight hardware: each step corresponds to a specific duty cycle setting, making conditions exactly reproducible in future experiments.

### **1.2  Relationship to device calibration**

The stepwedge protocol does not replace device calibration — it depends on it. Before any biological exposure is attempted, the BioLight illumination hardware must be characterized: the 470 nm LED array must deliver a known, spatially uniform irradiance (mW/cm²) at the substrate plane, and the PWM controller must translate duty cycle settings into delivered irradiance with a characterized response. This physical calibration is performed with a calibrated photodetector or spectrometer prior to any biological use.

Only after the device has been physically characterized does the stepwedge protocol begin. At that point, each step can be assigned a precise light dose in J/cm² (irradiance × exposure time), and the biological response can be plotted against a physically meaningful, absolute x-axis — not merely an arbitrary PWM setting.

| **Key Principle: Absolute Dose Units** All BioLight calibration data are recorded in J/cm² (joules per square centimeter). This ensures that calibration results are portable — comparable across hardware versions, labs, and setups — as long as the device has been characterized with a calibrated reference instrument. Never report calibration results in PWM duty cycle alone. |
| --- |

## **2.  Baseline Calibration Criteria**

Before the biological stepwedge experiment is run, the following baseline calibration criteria must be met and documented. Failure to meet any criterion should trigger re-calibration of the hardware before proceeding.

### **2.1  Hardware acceptance criteria**

| **Parameter** | **Value / Range** | **Notes** |
| --- | --- | --- |
| Peak irradiance at substrate | ≥ 0.5 mW/cm² | Measured at center of illumination field with calibrated sensor |
| Spatial uniformity | ≤ ±15% COV | Coefficient of variation across 9-point grid measurement |
| Spectral peak | 470 nm ± 5 nm | Verified by spectrometer or calibrated photodetector with bandpass filter |
| PWM linearity | R² ≥ 0.97 | Irradiance vs. duty cycle linear regression over 10–90% range |
| Temporal stability | < 5% drift over 60 min | Measured at fixed duty cycle; illumination source thermally stabilized |
| Dark chamber leakage | < 0.001 mW/cm² | At substrate plane with all LEDs off; ambient light excluded |

The hardware calibration record (device ID, date, operator, instrument serial number, and all measured values) must be appended to the experimental logbook before any biological experiment proceeds.

### **2.2  Biological baseline criteria**

The bacterial reporter system must also meet baseline performance criteria before calibration data are considered valid. These criteria are established using dark-control plates — cultures of the same BioLight V5 strain, prepared identically, but kept in complete darkness throughout the incubation period.

| **Parameter** | **Value / Range** | **Notes** |
| --- | --- | --- |
| Dark-control fluorescence (sfGFP) | < 50 RFU (normalized) | Leaky expression from uninduced promoter; establish per-batch |
| Dark-control melanin (tyrosinase) | OD₄₀₀ < 0.05 | Background pigmentation in unexposed zones |
| Colony density uniformity | ≤ 20% COV | Non-uniform lawns disqualify the plate |
| Agar surface clarity | No condensation | Condensation scatters light; allow plates to equilibrate before use |
| Incubation temperature | 37 °C ± 0.5 °C | For E. coli; temperature shifts alter expression kinetics |
| Post-exposure incubation | [TBD] hours | Time for full reporter maturation after illumination ends |

## **3.  Stepwedge Exposure Protocol**

### **3.1  Wedge design parameters**

The standard BioLight calibration stepwedge consists of ten discrete exposure zones arranged in a linear sequence across the illumination field. Zones span from 0% to 100% of maximum delivered dose in equal logarithmic steps, following photographic step-tablet convention (each step representing approximately a 0.30 log unit increase in exposure — a 2× doubling of dose).

| **Parameter** | **Value / Range** | **Notes** |
| --- | --- | --- |
| Number of steps | 10 | Zones 0–9; Zone 0 = minimum, Zone 9 = maximum |
| Step interval | ~0.30 log₁₀ units | Each step doubles the dose of the previous |
| Zone dimensions | [TBD] mm × [TBD] mm | Must contain ≥ 50 colony-forming units per zone |
| Illumination wavelength | 470 nm | Matches BioLight V5 / eLightOn LOV domain absorption peak |
| Dose range | [TBD] – [TBD] J/cm² | Spans sub-threshold to saturation; set from device calibration |
| Exposure duration | [TBD] minutes | Fixed for all zones; dose variation achieved by PWM irradiance control |
| Spatial light modulator | ILI9341 TN LCD | BL/LED pin to GND; 470 nm transilluminator as sole source |

### **3.2  Step-by-step protocol**

The following protocol assumes that hardware calibration criteria (§2.1) have been verified and logged, and that a fresh batch of BioLight V5 reporter plates has met biological baseline criteria (§2.2).

- Prepare the bacterial emulsion layer: inoculate LB-agar plates with the BioLight V5 reporter strain to a uniform lawn density. Use a calibrated cell-spreading protocol (100 µL of OD₆₀₀ = 0.1 suspension spread to confluence). Allow plates to dry in the dark at room temperature for 20–30 minutes before use.

- Equilibrate the dark chamber: bring the BioLight enclosure to operating temperature. Verify that the frustum cone is seated correctly and that the spacer ring stack is set to the validated working distance.

- Load the stepwedge pattern: transfer the calibrated stepwedge image file to the ILI9341 display controller via the Flask/Pi pipeline. Verify that the display is rendering the correct 10-zone gradient pattern with no backlight contribution (BL pin confirmed to GND).

- Zero the exposure timer: confirm that the Pi 5 PWM output (GPIO18, PWM0) is at 0% duty cycle. Log the start time, plate ID, operator, and chamber conditions.

- Initiate exposure: set PWM duty cycle to the calibrated maximum value corresponding to the desired Zone 9 peak dose. Start the exposure timer. The SLM pattern modulates intensity spatially across the plate; the PWM controls the global illumination level.

- Maintain exposure for the defined duration (§3.1). Monitor for thermal drift using the 1-Wire temperature sensor (Pin 7, GPIO4). If temperature deviation exceeds ±1 °C, log the event; deviations >2 °C disqualify the run.

- Terminate exposure: set PWM duty cycle to 0%. Log end time and total elapsed duration. Remove plate from the dark chamber and immediately wrap in aluminum foil to prevent ambient light exposure.

- Incubate the exposed plate in darkness at 37 °C for the post-exposure incubation period defined in §2.2. This allows full maturation of the sfGFP chromophore (estimated 60–90 min for mature fluorescence) or melanin deposition ([TBD] hours for tyrosinase-dependent output).

- Image the plate: using the AS7341-WS spectral analysis module, capture fluorescence or absorbance data from each of the 10 zones. Record raw values per zone without normalizing at this stage.

- Record all data immediately in the experimental logbook: plate ID, device calibration record ID, exposure parameters, raw zone measurements, and any anomalies observed during the run.

| **Critical: One Variable at a Time** The stepwedge calibration holds all parameters constant except light dose. Never vary exposure duration, temperature, strain preparation, or media composition between zones within a single calibration run. If any of these variables must be explored, they require independent experimental series. |
| --- |

## **4.  Interpreting the Calibration Curve**

### **4.1  Constructing the Photoplasm H****&****D curve**

After imaging, plot normalized reporter output (y-axis: RFU or absorbance, normalized to Zone 9 maximum) against log₁₀ of delivered dose (x-axis: log₁₀ J/cm²) for each of the ten zones. This plot is the biological H&D curve for the current batch of Photoplasm using BioLight V5 — the foundational dataset for all downstream imaging experiments.

The curve will typically display three regions analogous to those of a photographic characteristic curve:

- Toe region (sub-threshold): zones at low dose where reporter output is indistinguishable from the dark control. Defines the minimum effective dose (MED) — the threshold below which the system does not respond.

- Linear region (dynamic range): the dose interval over which reporter output increases monotonically and approximately linearly with log dose. This is the valid operating range for biological imaging.

- Shoulder region (saturation): zones at high dose where output plateaus. Defines the maximum useful dose; exposures above this threshold produce uniformly saturated output with no tonal discrimination.

### **4.2  Defining the valid exposure range for image experiments**

For any subsequent biological imaging experiment to be interpretable, the full range of doses delivered must fall within the linear region of the calibration curve:

- The minimum dose delivered (darkest shadow region of the image) must exceed the MED established by the stepwedge.

- The maximum dose delivered (brightest highlight region of the image) must fall below the shoulder threshold.

- The dose range of the image must not exceed the dynamic range of the linear region.

These constraints are analogous to the Zone System in photography: the image must be exposed so that all tonal information falls within the linear recording range of the medium. In BioLight, this is achieved by selecting the appropriate combination of peak irradiance (PWM duty cycle) and exposure duration to place image highlights at approximately 80% of the saturation dose.

| **Design Note: Calibration Batch Dependency** The H&D calibration curve is specific to a single preparation batch of BioLight V5 reporter cells, a single agar lot, and a single device calibration state. Any change in strain, media, incubation conditions, or hardware requires a new stepwedge calibration run. Calibration data must never be transferred between batches without biological validation. |
| --- |

## **5.  Integration with the BioLight Imaging Workflow**

The stepwedge calibration occupies Stage 1 in the BioLight experimental pipeline — characterize the medium, then expose the image.

| **Stage** | **Action** | **Dependency** |
| --- | --- | --- |
| Stage 0 | Dark chamber validation — verify spatial uniformity and spectral purity | Hardware acceptance criteria (§2.1) |
| **Stage 1** | Stepwedge calibration — establish biological H&D curve for current BioLight V5 batch | This appendix |
| Stage 2 | Image exposure (Aim 1A/1B) — single-output bacteriography within valid range | Relies on Stage 1 linear region |
| Stage 2 | Dual-output exposure — two-channel BioLight V5 image; sfGFP + tyrosinase reporters | Both reporters independently calibrated |
| Stage 3 | Analysis and quantification — zone fluorescence / OD measurement, image reconstruction | AS7341-WS spectral data or widefield imaging |

The Rasterizr pipeline — which converts SVG image files into exposure pattern arrays for the SLM — operates downstream of Stage 1. Rasterizr assigns dose levels to each pixel as a fraction of the calibrated maximum dose, ensuring that translated image exposures always fall within the validated linear range. This is the biological equivalent of pre-visualization in the Ansel Adams Zone System: the image is pre-interpreted in terms of the medium's tonal response before a single cell is illuminated.

Future iterations of this workflow will incorporate closed-loop feedback between the AS7341-WS spectral sensor and the PWM controller, allowing real-time dose adjustment to compensate for batch-to-batch variability in BioLight V5 reporter sensitivity. This capability is designated Stage 4 in the BioLight development roadmap and is not described in the current chapter.

## **6.  Safety and Containment**

All experiments described in this appendix use Biosafety Level 1 (BSL-1) E. coli strains under standard laboratory containment practices. The following precautions apply specifically to the BioLight illumination setup:

- 470 nm LED arrays at the irradiances used in BioLight protocols pose a low-level blue-light hazard. Avoid direct viewing of the illuminated field. Use appropriate eye protection rated for blue-light wavelengths during hardware calibration and extended operation.

- All biological materials — exposed plates, spent cultures, and contaminated labware — must be autoclaved or chemically decontaminated before disposal per institutional biosafety protocols.

- The dark chamber frustum cone and spacer rings (PETG, Bambu-printed) are not autoclavable at standard cycle temperatures. Decontaminate all inner surfaces with 70% ethanol before and after each experimental session.

- Tyrosinase-expressing BioLight V5 cultures produce melanin as a metabolic product. Melanin-containing agar plates should be handled as potentially hazardous waste and disposed of per institutional guidelines.

## **7.  Open Items and Next Steps**

The following items are outstanding as of this draft and must be resolved before this appendix is considered complete:

- [TBD] Determine post-exposure incubation time for full sfGFP chromophore maturation at 37 °C using the BioLight V5 construct. Literature baseline for eLightOn-derived systems: 60–90 min for fast-folding sfGFP variants; empirical confirmation required for BioLight V5.

- [TBD] Determine optimal plate lawn density (CFU/cm²) for stepwedge zone resolution. Too sparse → discontinuous reporter signal; too dense → nutrient limitation artifacts.

- [TBD] Characterize dark-control baseline RFU and OD₄₀₀ for the BioLight V5 strain and current agar lot. Values in §2.2 are placeholders.

- [TBD] Define zone dimensions based on finalized ILI9341 display resolution and optical throw distance at validated spacer height.

- [TBD] Establish post-exposure incubation time for tyrosinase/melanin output — likely longer than sfGFP maturation time.

- [TBD] Integrate AS7341-WS zone measurement protocol and confirm channel-to-channel cross-talk characterization for sfGFP (peak ~510 nm) vs. melanin (broadband absorption).

## **References**

Jayaraman, P. et al. (2016). Cell-free optogenetic gene expression system. ACS Synthetic Biology, 5(12). PMC5001607.

Levskaya, A. et al. (2005). Engineering Escherichia coli to see light. Nature, 438(7067), 441–442.

Motta-Mena, L. B. et al. (2014). An optogenetic gene expression system with rapid activation and deactivation kinetics. Nature Chemical Biology, 10, 196–202. [eLightOn / EL222 foundational work]

Fernandez-Rodriguez, J. et al. (2017). Genetic encoding of a far-red fluorescent protein optimized for forward genetic screens in living cells. Nature Chemical Biology, 13, 706–708.

Li, X. et al. (2020). Two-component optogenetic toolkit for the dynamic and spatiotemporal control of gene expression. ACS Synthetic Biology. PMC7102963.

Prokaryote Playhouse (open-source enclosure design). PMC9041274.

Adams, A. (1981). The Negative. New York Graphic Society. [Zone System reference for exposure methodology analogy.]

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-05-17  ·  draft