Photoplasm Quick Start Guide  ·  Chapter 10 — Camera Module (Pi Camera · Machine Vision)

# Chapter 10 — Camera Module (Pi Camera · Machine Vision)

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-05-18  ·  github.com/ericview-dev/photoplasm

> **PLACEHOLDER — Chapter Pending Build/Test.** This chapter is a scoping document only. The Camera stage of the Photoplasm device has not yet been built, wired, or characterized. Body sections — parts inventory, wiring diagrams, OpenCV pipelines, experiment records — will be added as the Camera stage progresses from design through bench validation. For the current authoritative feature scope, see Appendix B: Feature Specification under the CAM category.

---

## 10.1  Introduction

The Camera Module is the imaging stage of the Photoplasm device. While Chapter 3 (Wavelength Sensor) provides quantitative spectral measurement at a single point in the optical path, the Camera Module provides spatial imaging across the entire substrate plane — capturing what the device's optics, masks, and biology actually produce as a 2D image.

The Photoplasm Camera Module uses the **Raspberry Pi Camera Module** (model TBD — Camera Module 3 is the current candidate based on its higher dynamic range and autofocus support) mounted into the Stage 0 dark chamber. The camera observes the agar plate substrate from either an oblique angle or under-plate position, depending on the optical access available after the LED ring and OLED mask stages are seated.

This chapter introduces three distinct roles the camera plays in the Photoplasm workflow, each with its own data product and acceptance criteria. They share the same hardware but are implemented as separate software pipelines so each can be validated independently.

## 10.2  The Three Roles of the Camera Module

### Role 1 — Light Exposure Monitoring

The camera provides a spatial complement to the AS7341 single-point spectral measurement. While the AS7341 reports counts at one position in the optical path, the camera records the **spatial distribution** of light reaching the substrate. This matters because the LED ring's irradiance is not perfectly uniform across the plate area — corners, edges, and central regions receive measurably different doses, and the OLED mask introduces additional spatial structure that the AS7341 cannot resolve.

Camera-based exposure monitoring is intended to answer questions the AS7341 cannot:

- Is the LED ring's irradiance uniform across the substrate, or does it fall off toward the edges?
- Does the OLED mask render the intended pattern at the substrate plane, or is the image distorted, defocused, or partially occluded?
- What is the actual delivered exposure pattern, in dose-per-pixel, for any given calibration setting?

This role consumes the calibration coefficient established in Appendix A: Calibration Protocol to translate camera pixel intensities into delivered dose values (µW·s/cm² per pixel). The output is a spatially-resolved dose map for each exposure session.

### Role 2 — Bacterial Plate Growth Time-Lapse

After exposure, the plate is moved to incubation conditions (Chapter 6 — Incubation Heater Perfboard). During incubation, the camera captures **time-lapse images** at scheduled intervals, building a record of how the bacterial lawn responds to the delivered exposure pattern over time.

Time-lapse imaging answers different questions than single-point exposure monitoring:

- How quickly does the reporter signal develop in exposed zones versus dark-control zones?
- Does the spatial pattern of reporter expression match the exposure pattern, or do diffusion, growth, or experimental artifacts distort the image?
- At what timepoint does the reporter signal peak, and how does that timepoint depend on exposure dose?

These data feed back into Appendix A's calibration model: the time-lapse provides the temporal dimension that the stepwedge protocol's single endpoint measurement does not capture. The output is a time-stamped image series per plate, with each image registered against the exposure pattern.

### Role 3 — Bacteriographic Imaging (Machine Vision via OpenCV)

The third role is the scientific endpoint of the device: producing **bacteriographic images** that document the result of an exposure session as a permanent, quantitative image. This is where the photographic analogy at the heart of Photoplasm comes full circle — the bacterial lawn is the emulsion, the LED ring + OLED mask is the enlarger, and the camera is the contact-printing record of what the system produced.

This role uses **OpenCV** as the image-processing library. Planned pipeline stages:

- **Acquisition** — calibrated raw capture from the Pi Camera with locked exposure, gain, and white balance to ensure session-to-session comparability
- **Segmentation** — identify the substrate region, mask out plate edges and chamber artifacts
- **Registration** — align the captured image to the known exposure mask coordinates for direct dose-response analysis
- **Quantification** — measure reporter intensity per region (per stepwedge zone, per pattern feature, per arbitrary ROI) with statistical error bars
- **Documentation** — generate the publication-grade bacteriographic image with calibration metadata embedded

The OpenCV pipeline is forward-looking — no code exists yet. The pipeline is scoped in Appendix B under the CAM category (CAM-01.2 — Fluorescence Analytics Pipeline) and will be implemented in its own dedicated session once the camera stage hardware is built and the acquisition path is validated.

## 10.3  Relationship to Other Chapters and Appendices

| Chapter / Appendix | Role | Status |
|---|---|---|
| Ch. 3 — Wavelength Sensor (AS7341) | Single-point spectral reference; camera provides spatial complement | 🟢 Draft 1 (v0.1.0) |
| Ch. 4 — LED Ring | Light source the camera monitors | ✅ Published v1.0.0 |
| Ch. 5 — OLED Digital Image Mask | Spatial pattern the camera records at substrate plane | 🟢 Draft 2 (v0.2.0) |
| Ch. 6 — Incubation Heater Perfboard | Time-lapse imaging occurs during heater-regulated incubation | ✅ Published v1.0.0 |
| Ch. 7 — System Integration | Camera will be added as a fifth subsystem when built | 🟢 Draft 1 (v0.1.0) |
| Ch. 8 — GUI / Flask | Browser UI will surface live preview, time-lapse playback, and quantification output | 🟢 Draft 1 (v0.1.0) |
| App. A: Calibration Protocol | Provides the irradiance coefficient used to translate camera pixel intensities to delivered dose | 🟢 Draft 1 (v0.1.0) |
| App. B: Feature Specification | CAM category scopes this chapter (CAM-01, CAM-01.1, CAM-01.2) | 🟢 Working draft v0.18 |
| App. C: Pi Pinout NS-03 v8 | Camera connector reservation (CSI-2 ribbon, not a GPIO pin) | 🟢 Working draft |

A reader landing in this chapter should already understand the device's hardware subsystems (Ch. 3, 4, 5, 6), the integration logic that ties them together (Ch. 7), and the calibration framework (Appendix A) that the camera's measurements will be evaluated against.

## 10.4  Feature Scope Reference

The Camera Module's functional scope is documented in Appendix B: Feature Specification under the CAM category. As of v0.18, three features are scoped:

| Feature | Title | Status |
|---|---|---|
| CAM-01 | Pi Camera Module (Machine Vision) | 🔵 Proposed |
| CAM-01.1 | Camera Mount (Oblique or Under-Plate) | 🔵 Proposed |
| CAM-01.2 | Fluorescence Analytics Pipeline | 🔵 Proposed |

Additional features will be added to the CAM category as the camera stage progresses through design and build. This chapter's body sections will track the registry, with each implemented feature gaining its parts inventory, wiring detail, code listing, and experiment record as it moves from 🔵 Proposed → 🟡 Scoped → ✅ Complete.

## 10.5  Next Steps

The following are required before this chapter can advance past placeholder status:

- **Hardware selection.** Lock the Pi Camera Module variant (Module 3 vs HQ Camera vs alternatives) based on dynamic range, autofocus, and CSI-2 cable length requirements for the Stage 0 dark chamber geometry.
- **Mount design.** Determine whether the camera observes the substrate from an oblique angle (above the plate, looking down at an angle through the LED ring's optical axis) or from an under-plate position (looking up through transparent plate substrate). This decision drives the entire mechanical integration.
- **Acquisition path validation.** Confirm that a basic still-capture script runs on the Pi against the camera with consistent timing and predictable output.
- **Pipeline scaffolding.** Build the minimal OpenCV pipeline (read raw, identify substrate, output ROI mean intensity) as a working baseline before adding registration, quantification, or analytics features.
- **Integration with Ch. 7 and Appendix A.** Add the camera as the fifth subsystem in Ch. 7's integration smoke test, and define how camera pixel intensity maps to Appendix A's calibration coefficient framework.

Each of these tasks is a candidate for a dedicated working session. This chapter will be advanced from `placeholder` to `draft` once the hardware path is validated and the acquisition baseline is captured.

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-05-18  ·  placeholder
