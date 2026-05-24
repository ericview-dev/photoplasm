Photoplasm Quick Start Guide  ·  Chapter 8 — GUI / Flask Web Interface

# Chapter 8 — GUI / Flask Web Interface

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-05-17  ·  github.com/ericview-dev/photoplasm

---

# 1. Introduction

This chapter describes the **operator-facing graphical interface** for Photoplasm: a Flask web application that controls the device's LED ring, OLED image mask, AS7341 spectral sensor, and incubation heater through a touch-friendly browser UI.

The chapter is **forward-looking**. At the time of this draft, no GUI code has been written. The interface's functional scope is documented in **Appendix B — Feature Specification** under the GUI category (features GUI-01 through GUI-11). This chapter provides the chapter-shaped context that Appendix B's registry rows can't carry: the design rationale, the architectural intent, the operator-experience considerations, and the accessibility principles that should guide implementation.

When the GUI is eventually built in its dedicated implementation session, this chapter will be updated to v1.0.0 and will gain the parts inventory, code listings, wiring details, and experiment records that the published chapters (Ch. 4 LED Ring, Ch. 6 Heater Perfboard) carry. Until then, the chapter serves as the **design brief** the implementation will be measured against.

## Relationship to Other Chapters and Appendices

The GUI sits at the top of Photoplasm's software stack. Reading order for the chapter to be meaningful:

| **Chapter / Appendix** | **Role** | **Status** |
| --- | --- | --- |
| Ch. 4 — LED Ring | LED PWM control, the GUI's primary actuator | ✅ Published v1.0.0 |
| Ch. 5 — OLED Digital Image Mask | Mask projection, the GUI's image surface | 🟢 Draft 2 (v0.2.0) |
| Ch. 6 — Incubation Heater Perfboard | Heater control, the GUI's environment regulator | ✅ Published v1.0.0 |
| Ch. 7 — System Integration | The control layer the GUI sits on top of | 🟢 Draft 1 (v0.1.0) |
| Ch. 8 — GUI / Flask | This chapter | 🟢 Draft 1 (v0.1.0) |
| App. B — Feature Specification | Cross-cutting feature registry; GUI category scopes this chapter | 🟢 Working draft v0.18 |
| App. C — Pi Pinout (NS-03 v8) | Pin assignments referenced by all hardware | 🟢 Working draft |

A reader landing here should already understand the device's hardware subsystems (Ch. 4, 5, 6), have read the system integration logic that ties them together (Ch. 7), and be prepared to consult Appendix B for specific feature definitions as the chapter references them.

## Audience and Prerequisites

This chapter is written for:

**• ****Eric Schneider** as the primary builder and operator **• ****MakerSpace Charlotte BioArt Studio participants** who may operate the device after hand-off **• ****Future collaborators** at Genspace, HTGAA, or other community bio venues who may extend the work **• ****Future Claude Code sessions** that will implement the GUI based on this design brief The chapter assumes familiarity with Python and basic Flask concepts, comfort with a Raspberry Pi 5 running Linux, and access to the BioLight project's overall context (visible in the chapter-and-appendix series listed above). It does not assume prior experience with optogenetic workflows, kiosk-mode browser configuration, or HTML/CSS — those concepts are introduced as the chapter encounters them.

# 2. High-Level Intent

The Photoplasm GUI exists to make a complex piece of laboratory equipment **operable by a non-engineer in a working laboratory environment**.

That sentence does most of the work in this chapter. Each clause matters:

**"****Complex piece of laboratory equipment.****"**** **Photoplasm is a multi-subsystem device with concurrent processes: a PWM-driven LED ring, an SPI-bus OLED image mask, an I²C-bus spectral sensor logging at high rate, a 1-Wire temperature sensor, a closed-loop heater controller. None of those subsystems is operator-visible in a useful way through the underlying CLI. The GUI's job is to *aggregate, simplify, and present* the device's state in a way an operator can act on without needing to understand the underlying architecture.

**"****Operable by a non-engineer.****"**** **The eventual users of Photoplasm at the BioArt Studio are makers, artists, and life-science learners — not embedded systems engineers. The interface should not assume Python literacy, command-line comfort, or knowledge of GPIO pin assignments. It should present *biological-and-photographic* affordances (exposure time, mask image, sample plate, temperature setpoint), not *electronic* affordances (PWM duty cycle, register value, GPIO state).

**"****In a working laboratory environment.****"**** **The deployment context is not a developer's desk. It's a working laboratory with these characteristics:

**• ****Variable lighting**: safelight-only (deep red), standard lab fluorescent, or mixed **• ****Hands occupied**: gloves on, sample plates in hand, pipettes in use **• ****Eyes on the sample**: the operator is often looking at the device, not the screen **• ****Interruptions**: timed protocols (incubation, exposure) run in the background while the operator does other work **• ****Two-person workflows possible**: one person prepares samples while another monitors device state **• ****Cleanability**: surfaces may need to be wiped with isopropanol; the kiosk display will be touched by gloved hands The GUI's design must accommodate all of those operational realities. It is not a developer dashboard; it is a laboratory instrument's control panel.

## Two Surfaces, One Codebase

The GUI deploys in two configurations:

**Mode 1 — Browser (Remote Access)**

The operator runs the device from a separate computer or tablet on the same network as the Pi. They navigate to http://eyepi.local:5000 in any standard browser. This mode is for setup, mask uploads, schedule planning, and monitoring exposures from a desk while the device runs in a darkroom or enclosed space.

**Mode 2 — Kiosk (Local Touch Panel)**

A small touchscreen (5–7" capacitive HDMI/DSI panel) is connected directly to the Pi 5's Micro HDMI port. Chromium launches in kiosk mode at boot, displaying the same Flask app at http://localhost:5000. The operator interacts with the device hands-on, at the workbench, in the actual laboratory environment.

**Both modes use the same Flask codebase. **This is a deliberate architectural choice. The kiosk display is not a separate application; it is the same web app served to a locally-running browser. This means:

**• **One feature added = both surfaces gain the feature **• **One bug fixed = both surfaces are fixed **• **One UI design = one set of style decisions to maintain **• **Multi-client concurrency is supported by default: a remote browser session and a local kiosk session can both be active at once, both showing live state The cost of this approach is a slightly heavier kiosk session than a native UI would be. The benefit is a single codebase whose surface area is the same regardless of where it's running. For a one-developer project, that's an unambiguous trade.

## Why Flask

Flask was chosen as the web framework for four reasons:

**1. ****Python-native.** Photoplasm's hardware control code is Python (using `lgpio` for GPIO, Adafruit libraries for the AS7341 and DS18B20, `luma.oled` for the SSD1309). Flask integrates with these libraries directly, sharing process memory and execution context. No inter-process communication, no serialization boundaries, no message queues.

**2. ****Lightweight.** Flask runs comfortably on the Pi 5 alongside the hardware control processes. A larger framework (Django, FastAPI with full async stack) would consume more memory and add complexity that isn't justified for a single-device, single-operator interface.

**3. ****Single-file deployable.** The Flask app can ship as a single Python file with a templates folder. No build pipeline, no compilation step, no separate frontend bundler. Edit the file, restart the service, the change is live.

**4. ****Mature SSE/WebSocket story.** Real-time sensor streaming (the live AS7341 readings, the heater temperature loop) needs server-to-client push. Flask supports both Server-Sent Events (simple) and WebSockets (via Flask-SocketIO if needed) without architectural gymnastics.

The alternative considered was **FastAPI** for its async-first design. Rejected because Photoplasm's hardware libraries are synchronous; an async framework would just be wrapping sync calls in run_in_executor boilerplate, which is friction for no benefit at this scale.

## Boundaries: What the GUI Is and Is Not

The GUI is responsible for **operator interaction**. It is *not* responsible for hardware control logic.

Hardware control lives in dedicated modules per subsystem, documented in Ch. 4, 5, 6, and 7. The GUI calls into those modules through clear interfaces. This separation matters: if the GUI crashes, a long-running exposure does not abort; the underlying hardware control continues until completion. If the hardware control encounters an error, the GUI surfaces the error but does not need to handle the underlying recovery (the hardware modules do that).

A useful frame: **the GUI is the operator****'****s instrument; the device control stack is the device.** The GUI lets the operator see and steer the device; the device runs itself.

# 3. Design Considerations

## Operator Context

The Photoplasm operator at any given moment is in one of several states:

| **Operator State** | **Interface Need** |
| --- | --- |
| Setting up an exposure | Mask selection, duration entry, plate placement guidance |
| Mid-exposure (running) | Live progress, sensor readings, abort affordance |
| Mid-incubation (heating) | Temperature display, time remaining, abort affordance |
| Reviewing results | Recent session log, exported CSV, plate image (when CAM-01 lands) |
| Maintenance / calibration | Manual subsystem controls, AS7341 calibration runs, OLED test patterns |
| Idle / between runs | Quick start affordance, recent session glance |

The UI should make each of these states *the obvious next thing* when the operator is in it. A heavy mode-switching navigation pattern (deep menus, tab bars) makes the operator hunt for what's relevant. A state-aware home screen presents the right affordance for the moment without hunting.

## Safelight-Aware Visual Design

Photoplasm operates in a darkroom or enclosed light-isolation environment when actively exposing biological samples. The ambient lighting is often **safelight only** — deep red illumination (around 660 nm) that does not activate the eLightOn optogenetic system (470 nm).

The kiosk display itself becomes a light source. If the kiosk uses a bright white-on-dark UI, it adds blue light to the chamber. If it uses primarily reds and dark grays, it preserves safelight conditions.

Design implications:

**• ****Default chrome is cool-toned but dim.** Slate grays, dark blues, soft cyans. Not pure black (which makes the screen look broken), but very low overall luminance.

**• ****Red is reserved for safelight-visible UI elements.** Counterintuitively, red is the *most* visible color under safelight conditions, so it's used for critical state indicators — exposure-in-progress, error states, abort buttons. The operator can see red even when the rest of the screen looks dim.

**• ****Critical state indicators do not require white backgrounds or high-luminance accents.** A dim red "EXPOSING" indicator against a dim chrome is sufficient and preserves the safelight environment.

**• ****Brightness control is a first-class feature.** The kiosk should have a software brightness slider, and ideally a hardware-button equivalent for gloved operation.

This is the **Safelight-Aware Color Palette** scoped as GUI-09 in App. B.

## Touch-First Interaction

The kiosk display is a capacitive HDMI/DSI panel operated by gloved hands. Interaction implications:

**• ****Minimum 64-pixel touch targets.** Standard 44px iOS targets are too small for nitrile-gloved fingers; 64px gives reliable hit rates.

**• ****Generous spacing between targets.** Touch targets should have at least 8–12 px of dead space between them to prevent fat-finger errors.

**• ****No hover states.** Hover does not exist on touch. Any UI behavior that depends on hover is broken on the kiosk.

**• ****No right-click / context menus.** Same reason.

**• ****No multi-touch gestures.** Pinch-zoom, two-finger swipe, etc. are not used. Standard tap and scroll only.

**• ****Visible-when-relevant inputs.** Form fields hidden in collapsed panels mean the operator has to tap to discover them. Critical inputs (exposure duration, mask selection) should be visible at the top of their relevant view.

This is the **Touch-First UI Conventions** scoped as GUI-08 in App. B.

## State Persistence and Recovery

Photoplasm runs unattended for periods of minutes (short exposures) to hours (overnight incubation). The GUI must survive page reloads, browser tab switches, and even short Pi reboots without losing operator state.

Persistence layers:

**• ****Session state (per browser session)**: held in a server-side session store, keyed by browser cookie or kiosk client ID. Survives page reloads.

**• ****Run state (per exposure run)**: written to disk in ~/.photoplasm/logs/ as a session CSV. Survives Pi reboots; can be resumed if the device crashes mid-exposure (controlled subsystem rollback, not "where did we stop").

**• ****Device state (continuous)**: the underlying hardware control modules maintain their own state. If a heater is mid-incubation when the GUI crashes, the heater keeps heating. The GUI reconnects on restart and resumes display.

The design rule: **the operator never has to remember what state the device was in.** The UI reads device state on every load and presents it.

## Multi-Client Concurrency

Two operators may interact with Photoplasm simultaneously — one on the kiosk panel, one in a remote browser. Both must see live state and be able to issue commands. Conflict resolution is straightforward for read operations (both see the same data) and important for write operations (who can start an exposure when one is already running?).

Design rules:

**• ****Sensor data is broadcast.** Every connected client receives the same live AS7341 / DS18B20 stream via SSE. No polling.

**• ****Control commands are gated.** If an exposure is running, the "Start Exposure" button is disabled on all clients. The first client to claim control of a setup screen indicates that to other clients ("Currently being configured by operator at kiosk").

**• ****Abort is always available to any client.** Safety overrides social niceties: any operator can stop a running exposure from any client.

This is the **Multi-Client Concurrency** feature scoped as GUI-11 in App. B.

# 4. Architecture Overview

The GUI architecture has four concentric layers:

┌─────────────────────────────────────────────────┐

│  Operator (touchscreen or remote browser)       │

└──────────────────┬──────────────────────────────┘

                   │ HTTP + SSE

┌──────────────────▼──────────────────────────────┐

│  Flask Web App (Python)                         │

│   ├─ Routes (HTML pages, JSON endpoints)        │

│   ├─ Templates (Jinja2 + Tailwind-ish CSS)      │

│   └─ Session state                              │

└──────────────────┬──────────────────────────────┘

                   │ Direct Python calls

┌──────────────────▼──────────────────────────────┐

│  Click CLI Layer (`flask photoplasm <cmd>`)     │

│   └─ Shared commands callable from CLI or web   │

└──────────────────┬──────────────────────────────┘

                   │ Direct Python calls

┌──────────────────▼──────────────────────────────┐

│  Hardware Control Modules                       │

│   ├─ LED PWM (Ch. 4)                            │

│   ├─ OLED mask (Ch. 5)                          │

│   ├─ AS7341 sensor (Ch. 3, Ch. 7)               │

│   ├─ Heater + DS18B20 (Ch. 6)                   │

│   └─ Pi GPIO via lgpio (App. C pinout)          │

└─────────────────────────────────────────────────┘

## Flask App + Click CLI

A deliberate architectural choice: every Flask route's underlying operation is also callable as a Click CLI subcommand. The same Python function backs both. This means:

**• **The Flask UI exists to make operations *easier* than the CLI, not to gate access to them **• **Anything the operator can do through the UI, an advanced user (or a script) can do through `flask photoplasm <subcommand>`

**• **Testing is easier: CLI commands can be exercised without browser instrumentation **• **Headless operation is supported: a Pi without a kiosk display, accessed only via SSH, is fully functional This is the **Click CLI Layer** scoped as GUI-03 in App. B.

## Real-Time Streaming

The AS7341 spectral sensor reads at 1–10 Hz during calibration runs and exposures. The DS18B20 reads every second during heating. The kiosk and any remote browsers need to see these readings live, not as poll-refreshed snapshots.

The Flask app uses **Server-Sent Events (SSE)** for one-way server-to-client streaming. The browser opens a long-lived HTTP connection to /api/stream/sensors, and the server pushes JSON-formatted sensor readings as they arrive. The browser JavaScript appends each reading to a live chart and updates UI elements.

SSE was chosen over WebSockets because:

**• **Sensor data is one-way (server → client). Bidirectional WS adds complexity without benefit.

**• **SSE works through proxies, firewalls, and ad-blockers more reliably than WS.

**• **SSE reconnection is built into the browser EventSource API.

Two-way operations (start exposure, change setpoint) use ordinary HTTP POST. The state change is then reflected in the SSE stream that all clients see.

This is the **Live Sensor Dashboard** scoped as GUI-06 in App. B.

## Session Model

A **session** is one complete operator interaction with the device, typically:

**1. **Operator opens the UI **2. **Selects or uploads a mask **3. **Sets exposure parameters (duration, intensity, target temperature if incubating)

**4. **Starts the run **5. **Watches the run complete **6. **Reviews results Each session generates a timestamped CSV in ~/.photoplasm/logs/ containing:

**• **Session metadata (start time, operator-supplied label, mask filename, exposure parameters)

**• **Per-second sensor readings during the run **• **Event log (start, mid-run state changes, completion, errors)

Sessions are listed in a "Recent Sessions" view, downloadable as CSVs from the UI. The session log is the device's lab notebook — every exposure produces an auditable record.

This is the **Session Logging UI** scoped as GUI-07 in App. B.

## Mask Library and Upload Pipeline

Masks are images displayed on the OLED to modulate the LED ring's projected light. Masks are most often:

**• ****Step wedges** for calibration (16-step Bayer dither, see Ch. 3)

**• ****Test patterns** for OLED diagnostics **• ****Experimental images** for actual exposures (logos, photographic negatives, custom designs)

The mask upload pipeline accepts PNG, SVG, and JPEG. The Flask app converts uploads to the OLED's native bitmap format on the server, never asking the operator to think about pixel dimensions or color depth. Uploaded masks join a reusable library so the operator doesn't re-upload common patterns.

This is the **Mask Upload ****&**** Library** scoped as GUI-05 in App. B.

## systemd Integration

The Flask app launches automatically at Pi boot via a systemd service unit. The service:

**• **Starts after network is available **• **Restarts on crash (within reason)

**• **Logs to journald for centralized access **• **Runs as the ericview user, not root A separate systemd unit launches the Chromium kiosk on the local display, pointing at http://localhost:5000. The two services are independent: Flask can be running while the kiosk is not (headless mode), or the kiosk can be told to display a different URL for debugging.

This is the **systemd Service Definition** scoped as SYS-10 in App. B, with the kiosk launcher scoped as GUI-02.1.

# 5. Universal Design & Accessibility

The interface should be usable by the widest reasonable range of people, including people with vision differences, motor limitations, cognitive load constraints, or simply unfamiliarity with the device. This is not a feature added at the end of design; it is a constraint shaping design from the beginning.

## Key Principles

The interface design is informed by the **seven principles of Universal Design** (Center for Universal Design, NC State, 1997):

**1. ****Equitable use** — The interface is useful to people with diverse abilities. The same controls work for everyone; there are no "accessibility mode" alternate paths that segregate users.

**2. ****Flexibility in use** — The interface accommodates a wide range of individual preferences and abilities. The same operation can be performed via touch (kiosk), mouse (browser), keyboard (browser), or CLI.

**3. ****Simple and intuitive use** — Operation is easy to understand regardless of the user's experience, knowledge, language skills, or current concentration level. Labels are plain language; the next obvious action is visually prominent; complex configurations are progressively disclosed.

**4. ****Perceptible information** — The interface communicates necessary information effectively to the user regardless of ambient conditions or the user's sensory abilities. State changes are signaled by both color and shape/text (color-blind support); active state has both visual indication and sufficient size to be noticed peripherally.

**5. ****Tolerance for error** — The design minimizes hazards and the adverse consequences of accidental or unintended actions. Destructive operations (cancel exposure, delete session, overwrite mask) require explicit confirmation; the default action on ambiguous input is the safe one.

**6. ****Low physical effort** — The interface can be used efficiently and comfortably with minimum fatigue. Frequent operations (start exposure, abort, view live state) are accessible in one or two taps. Multi-step workflows are minimized.

**7. ****Size and space for approach and use** — Appropriate size and space is provided for approach, reach, manipulation, and use regardless of the user's body size, posture, or mobility. Touch targets are large enough for gloved fingers; the kiosk display is positioned for a standing operator at typical bench height.

## Accessibility Specifics

Standard accessibility guidelines (WCAG 2.1 AA-equivalent, adapted to a desktop-class Flask UI):

**• ****Color contrast** meets a 4.5:1 minimum for normal text, 3:1 for large text and active UI elements. Color is *never* the sole carrier of state information — text labels, icons, or shape changes always accompany color.

**• ****Keyboard navigation** is complete in browser mode. Every interactive element is reachable via Tab; visible focus indicators are present on all focusable elements.

**• ****Screen readers** are supported in browser mode through semantic HTML and ARIA labels where semantic HTML is insufficient. The kiosk mode prioritizes touch over screen-reader support, given the deployment context.

**• ****Text scaling** respects the browser's default font size setting. The UI scales gracefully from 100% to 200% without breaking layouts.

**• ****Form validation** is inline, accessible, and never blames the operator. "Duration must be at least 1 second" not "Invalid input."

## Wet-Lab Operational Accessibility

Beyond standard accessibility, Photoplasm has wet-lab-specific operational considerations that affect interface design:

**• ****Gloved operation**: nitrile or latex gloves change capacitive touch behavior. Larger targets, slower response timing, and forgiveness of glancing taps are required.

**• ****One-handed use**: the other hand may be holding a plate, pipette, or notebook. Critical operations should not require two-handed interaction.

**• ****Eyes-off operation**: the operator is often looking at the device or sample, not the screen. Audible feedback (a short tone on exposure start, on completion, on error) is valuable. Visual changes that occur without auditory accompaniment may be missed.

**• ****Cognitive load under time pressure**: timed protocols mean the operator may be doing multiple things at once. The interface should not require the operator to hold mental state — the screen should show the state.

## Empirical Validation

The above principles establish the design intent. Validation requires actual testing under deployment conditions:

**• **Test under safelight only **• **Test with gloved hands **• **Test with the operator's attention split (sample in hand, timer running)

**• **Test with first-time users who haven't read this chapter **• **Test with the operator at various distances from the kiosk (bench-level, reaching across the room)

Empirical validation is scoped as a post-implementation step. The principles in this section are the *design target*; the validation is the *quality check*.

*[Eric**'**s personal statement on Universal Design will be added here in a future revision.]*

# 6. Operational Sequence

A typical operator interaction with Photoplasm proceeds:

**Boot phase **(automatic, no operator action required)

**1. **Pi 5 powers on, OS boots, network comes up **2. **systemd starts the Photoplasm Flask service **3. **systemd starts the Chromium kiosk (if connected)

**4. **Flask app initializes hardware control modules **5. **Kiosk displays the "Ready" home screen **Setup phase **(operator interaction begins)

**6. **Operator selects mask from library *or* uploads new mask **7. **Operator sets exposure parameters (duration, intensity)

**8. **Operator (optional) sets temperature setpoint for incubation **9. **Operator places sample plate in dark chamber **10. **Operator closes chamber door (or simply darkens the room)

**Exposure phase **(operator monitors, device executes)

**11. **Operator presses "Start Exposure"

**12. **Confirmation modal: parameters summary, "Start" or "Cancel"

**13. **Exposure begins: LED PWM active, OLED mask displayed **14. **UI shows live timer, AS7341 readings, heater temperature (if incubating)

**15. **Audio tone on start, optional intermediate tones, tone on completion **16. **UI updates to "Complete" state **Review phase**

**17. **Operator reviews session log **18. **Optionally exports session CSV **19. **Returns to home screen for next session **Background tasks **(running concurrently throughout)

**• **Sensor data streaming to all connected clients **• **CSV log writing **• **systemd service health checks This sequence is the **operator****'****s workflow**. The internal architectural sequence (the order in which subsystems are initialized, the order in which sensor reads are scheduled, etc.) is the implementation's concern, not the operator's. The interface design's job is to make this nine-step sequence feel like five-step sequence: the operator should not perceive boot phase or background tasks as work they're doing.

# 7. Current State

At the time of this draft (May 17, 2026), the GUI exists only as this design brief.

What does exist:

**• ****App. B feature spec entries** (GUI-01 through GUI-11, 13 features)

**• ****Hardware subsystems the GUI will sit on top of** (LED ring, OLED mask, AS7341, heater) — operational and documented in Ch. 4, 5, 6 **• ****The system integration layer** (Ch. 7) — drafting at v0.1.0 **• ****The Pi 5 host** — operational with hostname `eyepi`, user `ericview`, SSH/VS Code remote access (Ch. 1)

**• ****Repository version control** — GitHub repo `github.com/ericview-dev/photoplasm` (Ch. 2)

What does not yet exist:

**• **The Flask application itself (no Python files written)

**• **The Chromium kiosk configuration **• **The systemd service units **• **The touchscreen hardware (specific 5–7" capacitive panel not yet selected or ordered)

**• **The Click CLI layer **• **The mask library **• **The session logging UI **• **The brightness control **• **Any code referenced as `gui_*.py` in App. B's Asset column This chapter is **the design brief for the implementation session that will produce the code**. That session is anticipated as a dedicated Claude Code working session, opening with this chapter and Ch. 7's markdown as context. The session's output will be working Flask code committed to the photoplasm repository, with this chapter updated to v1.0.0 to reflect the implemented state.

# 8. Future State

Looking beyond v1.0.0 of the GUI, several extensions are anticipated:

## Multi-User, Multi-Device

The current design assumes one Photoplasm device with one or two simultaneous operators. The BioLight Aim 3 vision (high-availability distribution of BioLight consumables at scale, analogous to Kodak's standardization of film) implies multiple Photoplasm devices in the field, each running its own Flask instance. A future evolution may add:

**• **A cloud-side aggregator that collects session data from multiple devices **• **Cross-device mask library synchronization **• **Operator accounts spanning multiple devices

## Remote Monitoring

A wet-lab protocol that runs overnight should be observable without the operator physically returning to the lab. Future versions may add:

**• **Mobile-friendly summary views (read-only)

**• **Push notifications on completion or error **• **Auto-pause / safe-state on detected anomalies

## Data Analysis Integration

Session CSVs accumulate over time. A future analysis layer may:

**• **Compare exposures across sessions (densitometer sweeps, dose-response curves)

**• **Surface drift in AS7341 readings as a calibration trigger **• **Track Kc coefficient stability across re-calibrations

## Mask Library Sharing

Once multiple Photoplasm users exist (per Aim 3), mask libraries become shareable assets. The interface may evolve to support:

**• **Export / import of mask packages **• **Community-sourced calibration patterns **• **Reusable protocol templates (mask + parameters + incubation profile)

These are explicitly **post-v1.0** features. They are noted here so the v1.0 implementation does not paint itself into corners that prevent these directions. Specifically: the session model should accommodate future cross-session analysis; the mask file format should be inspectable and portable; the Flask app should be configurable for a future external API consumer.

# CHANGELOG

## v0.1.0 — 2026-05-17 (Draft 1)

**• **Initial draft. Chapter scope established as informational overview, not feature registry (registry lives in App. B).

**• **Eight sections: Introduction, High-Level Intent, Design Considerations, Architecture Overview, Universal Design & Accessibility, Operational Sequence, Current State, Future State.

**• **Universal Design section uses the seven principles framework (NC State, 1997) at high level; placeholder for personal statement included.

**• **Cross-references established to Ch. 4 (LED Ring), Ch. 5 (OLED Mask), Ch. 6 (Heater), Ch. 7 (System Integration), App. B (Feature Specification GUI category), App. C (Pinout NS-03 v8).

**• **Audience explicitly named: Eric Schneider, BioArt Studio participants, future collaborators, future Claude Code sessions.

**• **Implementation is forward-looking — no code yet exists; chapter is the design brief the implementation will be measured against.

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-05-17  ·  draft