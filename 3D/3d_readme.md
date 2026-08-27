# 3D Printed Parts

Printable mechanical components for the Photoplasm optogenetic exposure unit.

Binary STL exported from Fusion 360. Source CAD is not tracked here.

> ## ⚠ PETG — every part, no exceptions
>
> **Print the entire device in PETG.** Not "PETG where it gets hot" — PETG throughout. Two reasons,
> and the second is the one that is easy to miss.
>
> ### 1. PLA cannot survive the light or heater paths
>
> | | Glass transition | Against |
> |---|---|---|
> | **PLA** | **≈ 55–60 °C** | ⛔ **at or below the operating ceiling** |
> | **PETG** | **≈ 80 °C** | ✅ ~25 °C of margin |
>
> The heater's **KSD9700 opens at 55 °C** — that is the designed fault ceiling, so chamber parts are
> *expected* to reach it. **PLA is at its glass transition at exactly that temperature**: it softens,
> creeps under load, and a snap or friction fit lets go. On the light side the Cree heat sink sheds
> **~3.3 W** continuously into whatever carries it.
>
> Parts in these paths: **01, 06, 09, 10, 11** (heater column) and **04, 05, 13** (light/optical
> path). But see below — do not treat that as a permission list for the others.
>
> ### 2. Mixed filament breaks the interference fits — this is the real argument
>
> This stack holds itself together by **fit**, not fasteners: part 11 snaps inside part 06's bore,
> part 13 grips the light spacer by friction, every ring nests on a register lip, and the spacer
> tolerances run to tenths of a millimetre.
>
> **Different polymers have different thermal expansion and different creep rates.** Print two mating
> parts in different filaments and their interference stops being a constant — it drifts with
> temperature, and the two halves relax at different rates under sustained load. A fit dialled in on
> the bench then changes at 37 °C incubation.
>
> **One filament across the whole device keeps every fit predictable.** That is why the rule is *all
> parts consistently PETG*, including the ones that never get warm.
>
> **Also:** PETG takes the **M2/M3 heat-set inserts** at a 230–250 °C iron, and accepts the optional
> **UV-resin sterilisation coating** on part 01. Both are PETG-specific and neither is a
> print-it-in-anything property.


| ID | Part | File | Feature |
|---|---|---|---|
| 01 | Plate Holder | [`Plate_Holder.stl`](Plate_Holder.stl) | OPT-03 |
| 02 | Lower Stage Sensor Mount | [`lower_stage_sensor.stl`](lower_stage_sensor.stl) | Ch. 3 |
| 03 | LCD Carrier | [`LCD_Carrier_1.1_CF.stl`](LCD_Carrier_1.1_CF.stl) | MSK-01.3 |
| 04 | Cone | [`Cone.stl`](Cone.stl) | OPT-01.1 |
| 05 | Cone Spacer, 1 in | [`Cone_Spacer_1in.stl`](Cone_Spacer_1in.stl) | OPT-01.2 |
| 06 | Heater Spacer | [`HeaterSpacer.stl`](HeaterSpacer.stl) | HTR |
| 07 | Pi 5 Mount | [`pi5mount.stl`](pi5mount.stl) | — |
| 08 | GPIO Breakout Mount | [`gpio_breakout_mount.stl`](gpio_breakout_mount.stl) | — |
| 09 | Heater Mount | [`my_heater_base_3holes.stl`](my_heater_base_3holes.stl) | HTR |
| 10 | Heater Circuit Holder | [`Heater_DFR0457.stl`](Heater_DFR0457.stl) | HTR |
| 11 | Temp Cutoff Ring | [`tempcut_combined_holder.stl`](tempcut_combined_holder.stl) | HTR |
| 12 | Switch Box | [`switchbox.stl`](switchbox.stl) | ☐ |
| 13 | Light Spacer Lower Ring | [`lightspacer_lower_ring_draft.stl`](lightspacer_lower_ring_draft.stl) | OPT |
| 14 | Cree Light Ring | [`Cree_lightring.stl`](Cree_lightring.stl) | OPT-LED |
| 15 | Light Spacer, Large | [`lightspacer_large.stl`](lightspacer_large.stl) | OPT |
| 16 | Light Circuit Hat | [`light_circuit_hat.stl`](light_circuit_hat.stl) | OPT-CTL |

IDs are stable labels assigned in order of addition, not assembly order.

### Also in this folder, not a numbered part

| File | What it is | Status |
|---|---|---|
| `lightspacer_lower_ring.3mf` | Bambu Studio project for **part 13** | ✅ Keep — a print-ready source artefact, which part 11 conspicuously lacks |
| `thermalcut_sensorholder.3mf` | Bambu Studio project for the **superseded** two-file part 11 workflow | ☐ **Review** — D-11 previously recorded this as deleted; it is still here. It is scaffolding for the merge-at-slice-time method that `tempcut_combined_holder.stl` replaced, so it is probably a delete — but it is also the only remaining artefact carrying part 11's pre-merge geometry (see the source-CAD warning in [D-11](#d-11-temp-cutoff-ring)) |

## Stack order

Bottom to top. Confirmed 2026-08-18 against the Fusion coordinates still carried in the STLs.

| | Part | Role |
|---|---|---|
| ▲ top | **03** LCD Carrier | mask carrier |
| | **04** Cone | dark chamber |
| | **05** Cone Spacer, 1 in | throw adjustment, stackable |
| | **01** Plate Holder | dish / sample stage |
| | **06** Heater Spacer | spacer between heater and dish holder — **11** nests inside it |
| | **09** Heater Mount | PTC heating element + DS18B20 insert |
| ▼ base | **10** Heater Circuit Holder | DFR0457 driver — the essential heater circuit, at the base |

Part **11** (temp cutoff ring) is not a stack layer: it snaps *inside* the bore of part 06.
Parts **02**, **07** and **08** are not in the column at all.

Parts 09 and 10 are both current and both part of the heater layer — 09 carries the PTC element, 10 carries the DFR0457 driver. The pre-rebuild heater circuit board mount is obsolete and not tracked here.

---

## 01 — Plate Holder

`Plate_Holder.stl` · 113.1 × 113.0 × 31.8 mm

Sample stage at the base of the frustum. Holds the agar plate at the focal plane.

| Spec | Value |
|---|---|
| Material | PETG — as with **every** part on this device; part 01 additionally needs it for the UV-resin sterilisation coating |
| Dish size | 90 mm or less |
| Seating | Raised off the bottom grid |
| Grid | Airflow passes under and around the dish for even passive heating |
| Air passage | Extends to the base of the model — **prints without supports** (rev 2026-08-17) |
| Volume | **64.35 cm³** — thickened to reach Z = 0; do not lighten (see [D-01](#d-01-plate-holder)) |
| Finish | Optional UV resin coating (PETG-specific) to seal print voids for sterilization |

[More details → D-01](#d-01-plate-holder)

---

## 02 — Lower Stage Sensor Mount

`lower_stage_sensor.stl` · 86.4 × 86.4 × 36.0 mm

Holds the AS7341 spectral sensor at substrate height for calibration runs.

| Spec | Value |
|---|---|
| Sensor seating | Sits on the protruding pin |
| Cable routing | Routes under the lower bar |
| Fasteners | None |

[More details → D-02](#d-02-lower-stage-sensor-mount)

---

## 03 — LCD Carrier

`LCD_Carrier_1.1_CF.stl` · 107.0 × 135.0 × 14.7 mm

Image mask carrier — sliding sled in the negative-carrier position. Revision 1.1.

> ⚠ **The file here is the single-piece rev 1.1.** The design has since been **split into two parts**
> — a **carrier body** and a **bezel plate** — refined for the 1.1″ T4 screen and CFA10110 mounting.
> **Neither of the two-part files is in this folder.** See the
> [LCD readme](../../spaceplacer_repo/projects/imaging/spaceplacer_lcd_display_readme.md).

**Two independent fastener systems** — do not conflate them:

| | Fastener | Into | Notes |
|---|---|---|---|
| **Bezel plate → carrier body** | **M2 × 5 mm** | **M2 heat-set inserts** in the print | ⏸ **PARKED 2026-08-22** — fastener resolved, but the bezel itself is on hold (see below) |
| **Carrier → CFA10110 driver** | **2 × #2-56 flat head, 3/16″** | The driver board's own standoffs | ✅ **Confirmed 2026-08-22 — countersunk heads clear the bottom.** Flat head required; no inserts, clearance holes only |

### ⏸ Bezel plate parked 2026-08-22

The bezel **still does not fit** the negative-carrier slot and the thickness tolerances are too tight
to keep iterating on the two-part geometry — **a simplified design is to be considered** instead. The
fastener numbers below are settled and stay on file for whatever replaces it.

**The driver mounting is unaffected and proceeds:** the #2-56 flat heads seat in their countersinks
and clear the bottom, so the CFA10110 can be mounted now. The two fastener systems are independent.

### Bezel fastener — resolved 2026-08-22

| Measured | Value |
|---|---|
| Bezel plate thickness | **2.61 mm** |
| M2 insert depth | **2.86 mm** |

```
M2 × 5 mm → 5.00 − 2.61 = 2.39 mm engaged  ≈ 1.2×D · 0.47 mm clear of bottom   ✅
M2 × 6 mm → 6.00 − 2.61 = 3.39 mm          BOTTOMS OUT by 0.53 mm              ⛔
M2 × 4 mm → 4.00 − 2.61 = 1.39 mm          = 0.7×D — too thin                  ⚠
```

A bottoming screw **pushes the insert out of the boss** rather than clamping the bezel — the same
failure [D-09](#d-09-heater-mount) flags for M3 × 6 mm in a 4 mm insert.

**Iron temperature for the M2 inserts: 240 °C**, same PETG working band (230–250 °C) as every other
insert on the device. Press with the guide tool — **never freehand**; a skewed insert cracks the
carrier and mis-seats the glass.

[More details → D-03](#d-03-lcd-carrier)

---

## 04 — Cone

`Cone.stl` · 104.5 × 104.5 × 152.4 mm

Dark chamber frustum. Light-tight envelope over the optical path.

| Spec | Value |
|---|---|
| Height | 152.4 mm (6 in) |
| Base | 104.5 mm OD / 100.5 mm ID |
| Top | 50.8 mm OD / 46.7 mm ID |
| Wall | 2.0 mm |

[More details → D-04](#d-04-cone)

---

## 05 — Cone Spacer, 1 in

`Cone_Spacer_1in.stl` · 108.5 × 108.5 × 31.8 mm

Stackable spacer ring. Adjusts throw distance between lens and substrate plane in 1 in increments.

| Spec | Value |
|---|---|
| Outside diameter | 108.5 mm |
| Inside diameter | 100.5 mm |
| Wall | 2.0 mm |
| Height | 31.8 mm overall; 25.4 mm (1 in) added throw |
| Register lip | 6.4 mm, nests over the cone base |

[More details → D-05](#d-05-cone-spacer-1-in)

---

## 06 — Heater Spacer

`HeaterSpacer.stl` · 113.1 × 113.1 × 30.5 mm

Stacking ring forming the heater chamber. Plain ring — contains no heater mounting hole and no sensor insert.

| Spec | Value |
|---|---|
| Outside diameter | 113.1 mm |
| Inside diameter | 105.1 mm |
| Wall | 2.0 mm |
| Height | 30.5 mm overall; 25.4 mm (1 in) added stack height |
| Register lip | 5.1 mm, nests into the ring above |
| Heater element | **PTCYIDU** PTC plate, 12 V, **45 W**, insulated aluminium shell, **77 × 62 × 6 mm** ([ASIN B0BNZRQP5Q](https://www.amazon.com/dp/B0BNZRQP5Q)) |

The heater mount proper — the part carrying the element and the DS18B20 insert — is [part 09](#09--heater-mount). See [D-06](#d-06-heater-spacer).

[More details → D-06](#d-06-heater-spacer)

---

## 07 — Pi 5 Mount

`pi5mount.stl` · 56.0 × 65.0 × 12.7 mm

**Mounts the Raspberry Pi 5 to the inside top of the device**, board hanging beneath.

| Spec | Value |
|---|---|
| Standoffs | **4**, ~6.35 mm square, **12.7 mm tall** (6.35 mm base + 6.35 mm post) |
| **Hole pattern** | **49.0 × 58.0 mm on centres** — matches the Pi 5 spec exactly |
| Chassis fixing | **1 × Ø3.9 mm hole, dead centre** (28.0, 32.5) |
| Board overhang | Pi 5 is 85 × 56 mm; the mount is 65 mm long, so the board overhangs ~20 mm |

☐ **How does the Pi fasten to the standoffs?** The posts read **solid — no bores**. Pi 5 uses **M2.5**
holes, so this needs self-tapping screws into solid posts, or M2.5 heat-set inserts added. Record which.
☐ **Single central bolt allows rotation.** Nothing in the part keys its angle — confirm the mounting
surface provides a locating feature, or add a second fastener.

[More details → D-07](#d-07-pi-5-mount)

---

## 08 — GPIO Breakout Mount

`gpio_breakout_mount.stl` · 130.4 × 25.4 × 31.8 mm

Rail mount for the **40-screw-terminal GPIO breakout**, fed by ribbon cable from the Pi 5 above.
**Sited left-front** for hand access to the terminals and short cable runs to each assembly.

| Spec | Value |
|---|---|
| Board fixing | **2 × Ø2.2 mm** (M2 clearance) at **57.15 mm** (2.25″) centres |
| Chassis fixing | **2 × Ø3.9 mm** at **103.44 mm** centres |
| Layout | All four holes in a single row |
| Terminals | 40 screw terminals — one per GPIO header pin |

**Why left-front matters:** every assembly lands here, so terminal access is the thing being optimised.
Screw terminals are re-worked far more often than soldered joints, and this is where harness changes
happen.

> ### ⚠ Orientation is the known failure mode on this part
> A **180°-reversed ribbon** once produced a complete false bring-up — every signal present, nothing
> where the pin map said it was. The mount is where that can be designed out.
>
> ☐ **Can this mount be fitted 180° out?** Its two chassis holes are symmetric about the centre, and
> its two board holes are also symmetric — so **nothing in the geometry prevents a reversed fit.**
> Add a keying feature, or mark pin 1 on the print itself (embossed, not a label).

[More details → D-08](#d-08-gpio-breakout-mount)

---

## 09 — Heater Mount

`my_heater_base_3holes.stl` · 113.0 × 113.1 × 31.8 mm

Holds the PTC heater element, carries the insert for the DS18B20 probe, and **passes all heater-zone
wiring down into the circuit module** (part 10) below.

> **Revised 2026-08-18 — `my_heater_base_v2` is superseded and deleted.** The floor now has
> **3 × Ø5 mm holes** in place of the previous two undersized slots. See [D-09](#d-09-heater-mount).

☐ **Filename does not follow the naming rule** — `my_heater_base_3holes` is a working name. Rename to
`Heater_Mount_v3.stl` when convenient.

| Spec | Value |
|---|---|
| Outside diameter | 113.1 mm; central bore Ø53.4 mm |
| Height | 31.8 mm |
| Hole pattern | 4 standoffs, 2.06 × 1.28 in on centers — **measured 52.33 × 32.51 mm** |
| Posts | Ø8.0 mm OD × 4.8 mm tall, from a 2.0 mm floor |
| Iron temperature | **240 °C** (PETG working range 230–250 °C) |
| Fasteners | 4 × M3 hex socket |
| Anchors | 4 × heat-set insert, M3 |
| Bore | 4.0 mm — provisional, allows for shrinkage; confirm once printed |
| Insert OD | 4.4 mm |
| Insert d1 (outer thread) | 3.8 mm |
| Insert thread length | 3 mm minimum |
| Insert source | FFVRVSS kit (Amazon) |
| Temp sensor | DS18B20 insert — 19.0 × 3.0 mm at the wall, rising z 2.0 → 26.6 mm |
| **Lead pass-throughs** | **3 × Ø5.0 mm** through the 2 mm floor, at y = −45.7, **11.0 mm pitch** (x = −11.0 / 0 / +11.0) |
| Wire routing | All heater-zone wiring drops through these into part 10 |

[More details → D-09](#d-09-heater-mount)

---

## 10 — Heater Circuit Holder

`Heater_DFR0457.stl` · 113.1 × 113.0 × 25.4 mm

**The essential heater circuit, at the base of the stack.** This is the holder that previously took
the soldered perfboard circuit; it now carries the DFR0457 driver on four heat-set-insert posts. The
PTC element (part 09) sits on top of it; neither supersedes the other.

| Spec | Value |
|---|---|
| Outside diameter | 113.1 mm |
| Height | 25.4 mm (1 in) |
| Floor | 2.0 mm, posts rise from it |
| Posts | 4, Ø8.0 mm OD × 4.0 mm tall (z 2.0 → 6.0 from floor) |
| Insert bore | Ø4.0 mm |
| Post pattern | **25.0 × 20.9 mm on centres**, offset from the ring axis |
| Anchors | 4 × heat-set insert, M3 — FFVRVSS kit (OD 4.4 · d1 3.8 · thread ≥ 3 mm) |
| Fasteners | 4 × M3 hex socket, 5 mm |
| Board carried | DFR0457, PCB 44 × 32 mm |
| Iron temperature | **240 °C** (PETG working range 230–250 °C) |

[More details → D-10](#d-10-heater-circuit-holder)

---

## 11 — Temp Cutoff Ring

`tempcut_combined_holder.stl` · 105.0 × 98.0 × 12.7 mm

Snap-in ring that retains the KSD9700 thermal cutoff **inside the bore of part 06**, not as a stack
layer of its own. 105.0 mm OD against the spacer's 105.1 mm ID.

> ✅ **Revised 2026-08-21 — now a single file.** `tempcut_combined_holder.stl` is the ring and the
> sensor pocket merged into one printable mesh, replacing the old load-two-files-and-merge-in-the-slicer
> workflow. **The composite caveat is retired.**
>
> 🗑 **Superseded halves deleted 2026-08-24** — `tempcut_ring.stl`, `tempcut.stl` and
> `tempcut_ring.step` are gone from the folder. They were reference only; the merged mesh is the
> single printable. ⚠ See D-11: this leaves part 11 with **no source geometry of any kind**.

| Spec | Value |
|---|---|
| Outside diameter | 105.0 mm — nests **inside** part 06's 105.1 mm bore |
| Height | 12.7 mm (0.5 in) |
| Retains | KSD9700 thermal cutoff, body ~20 × 7.75 × 3.6 mm |
| Fasteners | None — snap fit |
| Assembly | **Single mesh** — merged in CAD, not at slice time |
| Source | ⚠ **None** — the superseded halves were deleted 2026-08-24 and no STEP/F3D of the merged part exists (D-11) |

☐ **Superseded by design intent** — see D-11. A simplified spacer that holds the sensor *and* routes
its leads is planned, which would absorb this part and part 06 into one.

[More details → D-11](#d-11-temp-cutoff-ring)

---

## 12 — Switch Box

`switchbox.stl` · 96.0 × 76.0 × 70.0 mm

**Panel enclosure for the manual rail switches.** ✅ **First unit built 2026-08-21.** Measured from
the mesh: a **4 mm floor**, filleted sides, open underside (−Z ≈ 29 % solid), mostly-closed top
(+Z ≈ 66 %).

### Build notes from the first unit — 2026-08-21

| Finding | Action |
|---|---|
| **12 mm holes are too tight** for the threaded 12 mm switch bushing | **Open to Ø12.5 mm.** A 12 mm nominal thread needs clearance over its major diameter — fix in CAD, don't ream every print |
| Switch rocks in the panel | Add a **5/8″ thin locking washer** to stabilise |
| **The black/red ON-OFF plate and the red flip cap cannot both fit** the manufactured assembly | **Flip cap chosen.** Legend goes on the box instead — self-labelled |

☐ **Update the CAD to Ø12.5 mm** so the next print needs no reaming.
☐ **Record the self-label wording** for ON/OFF, and whether it is engraved, embossed, or applied.
Embossing into the print removes a label that can peel.
☐ Record the washer spec/source and the switchbox fastening scheme.

### ☐ Planned — "lighthouse" indicator mod

A raised indicator tower on top of the box, putting each power-state light next to the switch it
reports on, so switch and state read together.

| Circuit | Indicator | Means |
|---|---|---|
| **Heater** +12 V | **red** | that circuit is powered — **not** that it is heating |
| **Light** +15 V | **blue under white diffusion** | that rail is powered ⚠ **see the goggle warning in the NS-04 readme** |

Electrical specs live with each circuit — [heater readme](../../spaceplacer_repo/projects/heater_v2/spaceplacer_heater_v2_readme.md)
and [NS-04 readme](../../spaceplacer_repo/projects/cree_led/spaceplacer_ns04_blue_rail_ctrl_readme.md).

☐ Diffuser geometry, LED seat (3 mm / 5 mm / panel bezel), and lead routing down into the box.

---

## 13 — Light Spacer Lower Ring

`lightspacer_lower_ring_draft.stl` · 159.9 × 159.9 × 27.4 mm — **rev 2, drafted bore**

**Retaining ring for the light spacer** — it stops the spacer slipping down into the **enlarger
body**. **Press fit**, and **adjustable**: its height on the spacer sets how deep the spacer sits.

> ### 🔁 Rev 2 — 2026-08-24: drafted bore, because rev 1 slipped
> **Rev 1's straight Ø149.78 bore did not hold.** Against the spacer's Ø149.82 that was +0.04 mm
> diametral — 0.02 mm on radius, finer than FDM repeatability — so the fit landed wherever the print
> happened to land, and in practice it landed loose.
>
> **Rev 2 tapers the bore at a 1.00° half-angle** — Ø149.74 at the top, narrowing to **Ø148.79** at
> the bottom. Outside diameter is unchanged at Ø159.97, and the envelope is identical, so it drops
> straight into the same place.
>
> **The taper narrows downward, which is the load direction.** The spacer's weight pushes it *down*
> through the ring — into the narrowing bore — so the joint **self-tightens under exactly the load it
> exists to resist**. Rev 1 had no such behaviour: a straight bore that slips once slips further.

Measured from the mesh: 826 triangles, two Z levels, constant Ø159.97 OD, tapered bore.

| Spec | Value |
|---|---|
| Outside diameter | **159.97 mm**, constant |
| Bore — top | **Ø149.74 mm** |
| Bore — bottom | **Ø148.79 mm** |
| Bore draft | **1.00° half-angle**, narrowing downward |
| Wall | 5.12 mm (top) → 5.59 mm (bottom) |
| Height | **27.40 mm** |
| Fasteners | None — **press fit**, self-tightening under load |
| Adjustment | Ring position on the spacer sets the spacer's depth in the body |

✅ **Spacer OD resolved 2026-08-24** — it mates with [part 15](#15--light-spacer-large), whose lower
section is **Ø149.82 mm** straight. Against rev 2's tapered bore that is **+0.08 mm interference at the
ring's top, rising to +1.03 mm at its bottom** — a wedge, not a constant fit. The ring slides along **76.19 mm** of straight spacer, giving **48.79 mm** of
adjustable travel once its own 27.40 mm height is accounted for.

⏸ **That travel is the optical tuning range, in active use.** This part is currently a *tuning
fixture*: the emitter height is being set empirically for best projection convergence, and only then
will it be recorded and locked in — see [D-15](#d-15-light-spacer-large). Expect this ring to be
revised or replaced at lock-in; the fit that adjusts well is not the fit that holds permanently.

☐ **The enlarger body's opening is still unrecorded** — the 159.94 mm OD must not pass through it, or
the assembly drops and the part does nothing. That dimension lives on inherited hardware, not CAD.
**PETG**, per the device-wide rule at the top — and load-bearing here, since the retention is an interference fit that a softer filament would relax out of. ☐ Print orientation not recorded.
☐ Not placed in the stack-order table: it belongs to the light/optical path above the mask, not the
heater column.

[More details → D-13](#d-13-light-spacer-lower-ring)

---

## 14 — Cree Light Ring

`Cree_lightring.stl` · 174.6 × 174.6 × 42.9 mm

**Carrier for the Cree XP-E2 470 nm emitter array** — the lamphouse replacement that seats the light
source above the condenser. Largest part on the device.

Measured from the mesh: an outer **skirt** with a **web plate** across it, a central **hub**, and a
raised **ring** on top. 1,956 triangles, 6 distinct Z levels.

| Spec | Value |
|---|---|
| Outside diameter | **174.62 mm** |
| Skirt bore | **149.22 mm** |
| Skirt wall | **12.70 mm** — exactly 0.500 in |
| Skirt height | 32.20 mm (Z −12.70 → +19.50) |
| Web plate | **3.20 mm** thick (Z +9.80 → +13.00), spanning to the skirt bore |
| Central bore | **Ø9.97 mm** |
| Central hub | **Ø37.77 mm**, rising to Z +19.60 |
| Upper ring | Ø75.80 – Ø112.46 at Z +30.20 |
| Edge notches | 2 × ~1.76 × 3.59 mm at the plate rim, mirrored about X — ☐ purpose not recorded (cable exit? keying?) |

> ### ✅ RESOLVED 2026-08-24 — it mates with part 15
> The inferred Ø≈149 tube is real: it is [part 15](#15--light-spacer-large), added the same day. The
> skirt bore of **149.22 mm** seats on the spacer's **tapered top OD**, which passes through 149.26 mm
> at its narrowest. Both this joint and part 13's are cut to the **same +0.04 mm interference** — see
> [D-15](#d-15-light-spacer-large) for the full mating table. Nothing was wrong; the two close bores
> were two different stations on one tube.

Both this part and part 13 are walled in **exact imperial** (0.500 in and 0.200 in) while the rest of
the printed stack is metric — consistent with both being dimensioned against the inherited **Bogen
enlarger** hardware rather than the printed column.

☐ **Emitter mounting not recorded.** No mounting-hole pattern for the Cree stars, the heat sink, or
the fan was resolvable from the mesh at this level. Record how the array, sink and Carclo optics
attach, and to which surface.
☐ **Thermal path not recorded.** The Cree sink sheds **~3.3 W** into whatever carries it — see the
material rule; this part is squarely in the light path and must be PETG.

[More details → D-14](#d-14-cree-light-ring)

---

## 15 — Light Spacer, Large

`lightspacer_large.stl` · 149.7 × 149.8 × 92.1 mm

**The column that raises the Cree light ring to optical height** — setting the throw for projection
convergence. ⏸ **That height is deliberately tunable and not yet locked in:** the optimum is being
found empirically, then recorded, and the parts revised to suit. A plain tube with a **stepped/tapered outer diameter**, and it is the part that ties the
whole upper assembly together: [part 14](#14--cree-light-ring) wedges onto its top,
[part 13](#13--light-spacer-lower-ring) grips its lower section and stops it dropping into the
enlarger body.

| Spec | Value |
|---|---|
| Height | **92.07 mm** — ⏸ **provisional, tunable by design** (see [D-15](#d-15-light-spacer-large)) |
| Bore (clear aperture) | **Ø142.84 mm**, constant full height |
| Wall | **3.49 mm** |
| OD — lower, straight | **Ø149.82 mm** over **76.19 mm** |
| OD — upper, tapered | **Ø149.82 → Ø149.26** over the top **15.88 mm** (≈**1.0° half-angle**) |

### The fits — both cut to +0.04 mm

| Joint | Bore | Spacer OD | Interference |
|---|---|---|---|
| **14** Cree light ring → spacer top | Ø149.22 | Ø149.26 | **+0.04 mm** |
| **13** lower ring → spacer bottom | Ø149.78 | Ø149.82 | **+0.04 mm** |

Two joints, two stations on one tube, **the same interference at each**. The shallow top taper is a
**self-locking wedge**: the light ring starts easily at the narrow top and tightens as it is pushed
down, which both centres it on the optical axis and grips it without a fastener.

⚠ **+0.04 mm diametral is 0.02 mm radial — finer than FDM repeatability.** See
[D-15](#d-15-light-spacer-large): in practice your printer's calibration, not the model, decides
whether these come out tight, loose, or immovable.

[More details → D-15](#d-15-light-spacer-large)

---

## 16 — Light Circuit Hat

`light_circuit_hat.stl` · 149.2 × 149.2 × 42.1 mm

**Closed cap over the Cree light ring**, carrying the **NS-04 perfboard** that replaces the
breadboarded blue-rail CTRL circuit. Drops into part 14's bore as a spigot.

| Spec | Value |
|---|---|
| Outside diameter | **Ø149.23 mm** — into [part 14](#14--cree-light-ring)'s Ø149.22 bore |
| Seats on | part 14's web plate at **Z 13.00** |
| Height | **42.10 mm** (Z 13.02 → 55.12) |
| Clears | part 14's **10.66 mm** protrusion, out to Ø112.45 |
| **Wire porthole** | **Ø12.00 mm**, central — 4 wires + future wire-lock |
| **Standoffs** | 4 × **10 mm tall**, **Ø4.00 mm bore**, Ø10 → Ø13.52 flared |
| **Post pattern** | **35.00 × 55.00 mm**, centre offset **−33.20 mm in X** |
| Top plate | 4 mm (Z 51.12 → 55.12) |

### ⚠ ☐ The four standoff bores break through the top face

Verified from the mesh: the Ø4.0 bores span the full 10 mm, **Z 45.12 → 55.12**, and top-face material
starts at r = 2.00 mm around each post. **They are open.**

**That is four light leaks in the cap of a 470 nm lamphouse, pointing up at the operator.** The
[standoff standard](#heat-set-inserts--standoffs--device-standard) calls for a **6 mm blind bore with
2 mm of solid floor** — partly to avoid exactly this.

☐ **Shorten the bores to 6 mm**, leaving the 4 mm top plate solid — or plug them.
⚠ With a through-bore there is also **no bottoming limit**: a long bolt simply exits the top, so the
bolt-length table stops protecting the insert.

### ⚑ Perfboard mounting is M2 — resolved by drilling, once

The posts were modelled at **Ø4.0 for M3** before the perfboard was offered up. **Perfboard mounting
holes are M2-sized and an M3 bolt does not fit.**

**Resolved for this part by drilling the perfboard to Ø3.4 mm (M3 free fit)** rather than reprinting,
since the print was already under way. ⚠ **That is a one-off remedy, not the standard** — design new
perfboard-carrying parts to **M2 (bore Ø3.0, post Ø7.0, M2 × 5)** from the first sketch.

☐ Confirm the 35.00 × 55.00 pattern matches the board's actual holes, and that the **33.20 mm
off-axis offset** is deliberate (it keeps the board clear of the central porthole).

### ☐ Planned — wire-management cap

Two snapping halves with a fitted cable sleeve, acting as a passthrough tension manager on the Ø12
porthole. **Needed, not cosmetic:** the NS-04 build uses **male Dupont pins soldered directly into the
perfboard**, which have **no strain relief** — the solder joint itself takes any cable pull.

### Venting — deliberately not here

Vents belong in [part 15](#15--light-spacer-large), the 92 mm tall volume directly enclosing the
emitter and heat sink where heat actually accumulates. The hat sits above it and mostly sees what
rises. Decided 2026-08-26.

---

## Heat-set inserts & standoffs — device standard

Iron at **240 °C** for every insert on this device, M2 and M3 alike (PETG working band 230–250 °C).
Press **square and slow** so the melt flows rather than skins — **use the guide tool, never freehand**.

| | **M3** | **M2** |
|---|---|---|
| Source | FFVRVSS kit | ☐ measure your kit |
| Insert OD | 4.4 mm | ~3.2 mm |
| Insert d1 | 3.8 mm | ~2.8 mm |
| **Receiving bore** | **Ø4.0 mm** | **Ø3.0 mm** |
| Post OD (2 mm wall) | Ø8.0 mm | Ø7.0 mm |
| Post height / bore depth | 8 mm / 6 mm | 8 mm / 6 mm |
| Solid floor under bore | 2.0 mm | 2.0 mm |
| **Bolt for a 1.5 mm board** | **M3 × 6** | **M2 × 5** |
| Engagement | 3.0 mm = 1.0×D | 3.0 mm = 1.5×D |
| Max bolt before bottoming | 7.5 mm | 7.5 mm |

**Bore sizing rule:** sit just **above d1** so the knurl clears and enters, well **under OD** so it still
bites. Sized to OD the insert drops in and spins; far under d1 the boss splits.

⚠ **Printed bores come out undersized** — expect ~0.1–0.2 mm under nominal. Measure the first print.
**At or above 4.2 mm (M3) / 3.4 mm (M2) the inserts will spin** — tighten in CAD, do not compensate at
install.

⚠ **A bottoming bolt pushes the insert out of the boss** instead of clamping the part. Engagement is
capped by the insert's ~3 mm thread, not by bore depth: a longer bolt buys clearance, not grip.

> ### ⚑ Perfboard mounting is M2, not M3 — learned 2026-08-26
> **Perfboard mounting holes are M2-sized; an M3 bolt does not fit.** The M3 standard above is right
> for *printed-part-to-printed-part* and for module mounts (parts 09, 10), but **any standoff that
> carries a perfboard must be M2**.
>
> This surfaced on [part 16](#16--light-circuit-hat) after its posts were already modelled at Ø4.0.
> **Resolved for that part by drilling the perfboard out to Ø3.4 mm (M3 free fit)** rather than
> reprinting — the print was already under way. That is a one-off remedy, not the standard.
>
> **Design new circuit-carrying parts to M2 from the start.** When drilling out instead: back the board
> with scrap wood (FR4 breaks out on exit), step up rather than jumping to final size, deburr both
> faces, and check edge margin — a torn mounting hole near an edge is unrecoverable.

---

## Print settings

| Setting | Value |
|---|---|
| Material | **PETG — every part, no exceptions** (see the material rule at the top). PLA is not suitable anywhere on this device |
| Layer height | 0.20 mm — 0.16 mm for part 03 |
| Walls | 3+ |
| Infill | 20–30% |
| Supports | As needed, check after orienting — part 01 needs none |

Models carry their original Fusion 360 coordinates and sit below Z = 0. Drop to the build platform before slicing.

---

## Naming

`Part_Name.stl`, with a revision suffix where a part has iterated (`_1.1`) and a material suffix where the print targeted a specific filament (`_CF`). Superseded revisions are replaced — git history holds the older geometry.

---

## Related documentation

- [Chapter 3 — Wavelength Sensor](../docs/photoplasm_ch03_wavelength_sensor.md)
- [Chapter 6 — Incubation Heater Perfboard](../docs/photoplasm_ch06_heater_perfboard.md)
- [Appendix B — Feature Specification](../docs/appendix_B_feature_specification.md)
- [Quickstart Introduction](../docs/photoplasm_quickstart_intro.md)

---
---

# More Details

Rationale, reference data, and open items. Nothing here overrides the specifications above.

## D-01 Plate Holder

### Why PETG, not PLA

The holder sits in the thermal path of the incubation heater and is held at the 37 °C setpoint for the full duration of a run — hours at temperature, under the load of the dish.

PLA's glass transition is roughly 55–60 °C, and it softens and creeps under sustained load below that; it does not need to reach melting to sag. PETG's is roughly 80 °C, clearing the operating range with margin.

The margin is thinner than the setpoint suggests. The DS18B20 reads culture-zone temperature, not heater surface temperature (Ch. 6, Ch. 7), so surfaces nearer the element run hotter than the reported 37 °C.

Deformation is not cosmetic here. The holder sets the plate's position at the focal plane; a holder that sags mid-run moves the substrate out of focus and changes delivered irradiance, corrupting the exposure against its calibration. A PLA holder may survive a short run and fail on a long one — invalidating results before it visibly breaks.

### Grid and airflow

Raising the dish off the grid opens a gap that lets air pass evenly under and around the dish, so heat rising from the heater element reaches the sample from all sides rather than conducting into one contact face. This is the passive-heating path that holds the culture at 37 °C without a separate incubator.

Anything that blocks the grid apertures or closes the standoff gap defeats this — including over-thick surface coating.

### Air passage revision — 2026-08-17

**The first build needed supports, and that was the problem.** Support material printed *inside the
airflow grid* — the one place it must not be. It **clogged the airflow pattern** the grid exists to
provide, and it was **very hard to remove**: awkward to reach, and anything missed stays as a partial
blockage in the passage.

**The fix was to thicken the airflow pattern so it reaches Z = 0.** With the geometry carried down to
the build plate there is nothing to overhang, so the part prints support-free.

> ### ⚠ The revision ADDED material — do not "optimise" it back
> An earlier note here said the revision *removed* geometry. **That is wrong, and the meshes prove
> it.** Measured from the two exports (both closed and manifold, so the volumes are reliable):
>
> | | Aug 16 — pre-revision | **Aug 17 — current** |
> |---|---|---|
> | Volume | 33.27 cm³ | **64.35 cm³** |
> | Triangles | 7,836 | **7,428** |
> | Envelope | 113.05 × 113.00 × 31.75 mm | *unchanged* |
>
> **~93 % more material, in the same envelope, with fewer triangles.** The mass is not waste — it *is*
> the fix. Thicker struts running to the plate are what removed the supports, and they gave a thicker
> base as a bonus. Lightening this part reintroduces the overhangs, the supports, and the clogged
> grid. The simpler tessellation is the tell: fewer overhang features to describe.
>
> Pre-revision geometry is recoverable at `2554f8fc` — kept for reference only, **not printable
> without supports**.

Two further benefits follow. A passage open to the base has no enclosed underside to trap
contaminants, which suits the sterilization requirement below and makes the resin coating easier to
apply and inspect.

**Print this part without supports.** If a slicer proposes them here, the orientation is wrong — check
it before accepting, because supports in this grid defeat the part's function, not just its finish.

### Resin sealing

UV-cure resin formulated for PETG seals the voids and layer lines inherent to FDM printing, which would otherwise trap contaminants.

- Keep grid apertures and dish standoffs clear — pooled resin closes the airflow path.
- Coating adds thickness; confirm the dish still seats at the intended height, since seat height sets the under-dish gap.
- Cure fully before biological use. Uncured resin is a contaminant and cytotoxic.

### Sterilization limits

Sealed or not, this is PETG — glass transition roughly 80 °C, below the 121 °C of a steam autoclave. Autoclaving will deform the holder and change plate position at the focal plane. Sterilization means chemical: IPA, bleach, or a comparable cold method compatible with the cured resin.

### Open items

- Standoff height and resulting under-dish air gap not measured.
- Resin product not recorded; cure behavior and chemical resistance vary by formulation.
- Whether dishes smaller than 90 mm stay centered is unrecorded.
- Appendix B records the OPT-03 target as an 84 mm agar plate; the holder's working limit is 90 mm. One of the two should be updated.

## D-02 Lower Stage Sensor Mount

### Fastener-free by design

The sensor goes in for calibration and comes out before the biological substrate is placed, so it seats and lifts off the pin by hand between runs. See Stage 5 in the [quickstart introduction](../docs/photoplasm_quickstart_intro.md).

### Cable routing

Route the cable under the lower bar before seating the sensor, not after. Cable dressed over the bar can lift or tilt the board on its pin, changing the sensor's height and angle at the substrate plane — the exact quantity the calibration sweep measures. A sensor that shifts between runs invalidates comparison against earlier step-wedge data.

### Open items

- Pin diameter and height not recorded; needed to confirm fit against the AS7341 breakout's mounting hole.
- Whether the pin constrains rotation or only position is unrecorded.
- Sensor height relative to the plate surface — the number that makes the mount a valid substrate-plane proxy — not measured.

## D-03 LCD Carrier

### Why flat head is required

Carrier clearance inside the device is tight, so screw heads must sit flush with or below the carrier surface. A pan, button, or socket head protrudes and will foul the sled travel. Do not substitute.

Length matters in both directions. Flat head length is measured overall, head included, so 3/16 in spans carrier thickness plus thread engagement into the standoff. A longer screw either bottoms out in the standoff before the head seats — leaving the head proud, defeating the clearance requirement — or protrudes past the standoff on the far side.

### Fastener reference

#2-56 UNC: major diameter 0.086 in (2.18 mm), 56 TPI. ANSI flat head is an 82° countersink, head diameter up to 0.172 in (4.4 mm).

Metric M2 flat head (90° countersink, 3.8 mm head) is not a drop-in substitute — it will not seat flush in an 82° countersink, and the thread pitch is wrong for the standoffs.

Screws pass through the carrier into the driver board's standoffs; **for the driver mounting** nothing is tapped into the print and no inserts are involved. Carrier holes are clearance holes, not tapped: #43 (0.089 in / 2.26 mm) close fit, #38 (0.1015 in / 2.58 mm) free fit.

**Corrected 2026-08-22:** an earlier version of this line said the part uses *no* heat-set inserts at all. That is true only of the **driver** mounting. The two-part design adds **M2 heat-set inserts in the carrier body** for the bezel plate — see §03 above.

### Why the bezel exists, and why torque is different here

The bezel plate clamps the screen at its **edge/face perimeter**, so the fragile glass is never slid into a slot. That is a direct response to a screen destroyed by exactly that: sliding it into a friction slot.

Which makes the bezel screws the one fastener on this device where **the print is not the weakest part** — the glass is. **Snug by feel only.** The screen cracks long before M2 brass strips, so the "tighten until it stops" habit that is safe on a board standoff is wrong here. Tighten in a **diagonal cross pattern** in small increments so the bezel lands flat and never loads a single corner.

### Print note

The countersink is a functional feature. Check it for elephant foot or first-layer squish if the carrier prints face-down, and test-seat a screw before assembly — a head sitting even 0.5 mm proud eats the clearance budget.

The `_CF` suffix denotes the carbon-fiber-filled filament the part was designed against. It prints in plain PETG, with slightly more flex in the sled.

### Open items

- ⏸ **Bezel plate PARKED 2026-08-22** — still does not fit, tolerances too tight; consider a simplified design. Items below that concern the bezel are held with it.
- ✅ **#2-56 flat heads + countersink clear the bottom (2026-08-22)** — driver mounting good to assemble.
- ✅ Bezel thickness (2.61 mm) and M2 insert depth (2.86 mm) recorded → **M2 × 5 mm**.
- ☐ **The two-part files are not in this folder** — only the superseded single-piece rev 1.1. Upload the carrier body and bezel plate (STL + STEP/3MF).
- ☐ **Bezel screw head type** — the bezel is the sled's outward face, so a pan or button head can foul travel, the same constraint that forced flat heads on the driver screws.
- ☐ Standoff height and carrier thickness for the **2-56 driver screws** still not recorded — together they must equal the 3/16 in the screw provides.
- ☐ Insert count around the perimeter not recorded.
- Torque/seating notes pending first assembly.

## D-04 Cone

### Dimensions do not match Appendix B

Measured profile: 152.4 mm tall (6 in), 2.0 mm wall, base 104.5 mm OD / 100.5 mm ID, top 50.8 mm OD / 46.7 mm ID.

Appendix B records OPT-01.1 as a 256 mm frustum with a 51 mm top ID and 152 mm base OD. The top matches — 50.8 mm, though that is the OD, not the ID. Height and base diameter do not: 152.4 mm against 256 mm, and 104.5 mm against 152 mm.

152.4 mm is exactly 6 in, matching the lower end of the documented 6–12 in throw range, and the base nests into the spacer's register lip (part 05). That is consistent with the cone being the base segment extended by spacers, but it is an inference, not a recorded fact.

### Open items

- Reconcile against Appendix B OPT-01.1, and correct whichever record is stale.
- Confirm whether this is the complete cone or a segment.

## D-05 Cone Spacer, 1 in

### Nominal vs measured height — resolved

The file is named for a 1 in increment and measures 31.8 mm overall, which looked like a 0.25 in discrepancy. Measuring the profile resolves it: the body spans 25.4 mm exactly, and the remaining 6.35 mm is a register lip that nests into the part above rather than adding to the stack.

Each spacer therefore adds a true 1 in of throw. The name is correct and the throw-distance calculation is unaffected.

Profile: 108.5 mm OD, 100.5 mm ID, 2.0 mm wall. The lip's 52.27–54.27 mm radius band seats over the cone's 50.24–52.27 mm base — the two nest directly.

Appendix B records OPT-01.2 as a 50 mm spacer, which this is not. Either a second spacer size exists or the spec is stale.

### Open items

- Maximum stackable count not recorded.
- Reconcile against Appendix B OPT-01.2.

## D-06 Heater Spacer

### This file is not the heater mount

Measured from the mesh, `HeaterSpacer.stl` is a ring of revolution with no features at all beyond its stacking profile — every vertex falls at one of three radii (52.53, 54.53, 56.53 mm) across four Z planes. There is no heater mounting hole, no pocket for the element, and no DS18B20 insert in this geometry.

Profile: 113.1 mm OD, 105.1 mm ID, 2.0 mm wall, 30.5 mm overall, with a 5.1 mm register lip that nests into the ring above. Added stack height is 25.4 mm (1 in), matching the ~1 in modular ring described in [Chapter 6](../docs/photoplasm_ch06_heater_perfboard.md).

The heater mount carrying the element and the sensor insert is a separate part, not present in this folder.

### Heater element

**PTCYIDU PTC plate, 12 V, insulated aluminium shell** — [ASIN B0BNZRQP5Q](https://www.amazon.com/dp/B0BNZRQP5Q). Vendor spec table recorded 2026-08-18; all power/current figures carry ±20 %.

| | |
|---|---|
| Dimensions | **77 × 62 × 6 mm (±1)** |
| Max power | **45 W** → ~3.75 A |
| Power without airflow | **7 W** → ~0.58 A |
| Inrush current | **≤ 8.5 A** |
| Resistance range | 1–4 Ω |
| Surface temp, no airflow | 70 °C |
| **Chip temperature** | **TS80** — 80 °C Curie point |
| Leads | 15 cm high-temp, non-polar, tensile > 5 kg |

> **Corrected:** this file previously recorded **50 W / ~4.2 A**, taken from the listing title. The vendor spec table says **45 W**, matching the heater readme's original figure.

**The thermal margin is thinner than this file used to claim.** 70 °C is the *surface* temperature in still air, measured hung in a windless space at 24 °C ambient (±10 °C per the vendor's own note). The **chip** is TS80 — an 80 °C Curie point, which is PETG's glass transition, not 10 °C below it. Screw and heat-set insert form a metal path from element into the print ([D-09](#d-09-heater-mount)), so the plastic at each insert is the hottest plastic in the assembly. The 55 °C KSD9700 is the real bound on a runaway; do not treat the element's self-limiting as the safety layer.

It still sharpens the PLA prohibition on part 01: PLA's glass transition of 55–60 °C sits *below* the element's normal operating range, so a PLA part in the thermal path can be driven past softening by the element working exactly as designed — no fault condition required.

**Steady-state power is airflow-dependent**, from 7 W in still air to 45 W with good dissipation, so the running current in this chamber has to be measured rather than assumed. **Inrush is ≤ 8.5 A**, which is what sizes the supply — see the heater readme's [§2.1a](../../spaceplacer_repo/projects/heater_v2/spaceplacer_heater_v2_readme.md).

### Temperature sensor insert

The heater mount includes the insert for the DS18B20 probe. Chapter 6 notes the probe reads culture-zone temperature rather than heater surface temperature; the insert's position is what enforces that distinction, so it is a calibration-relevant feature rather than a convenience.

Wiring and troubleshooting for the probe: [Appendix D](../docs/appendix_D_ds18b20_troubleshooting.md).

### Open items

- The obsolete pre-rebuild heater circuit board mount is not uploaded. (The heater mount itself is part 09, `my_heater_base_v2.stl`.)
- Insert dimensions and probe retention method — friction fit, adhesive, or captive — not recorded.
- ✅ Element dimensions recorded: **77 × 62 × 6 mm**.
- **☐ The element is larger than part 09's Ø53.4 mm bore and spans it** — 77 × 62 mm plate over a 53.4 mm hole. The four M3 posts sit at r = 30.9 mm, i.e. *inside* the plate's footprint (half-extents 38.5 × 31 mm). **The vendor spec lists no mounting holes.** So either the plate has holes the listing does not mention, or the posts carry a clamp plate/bracket over the element rather than bolts through it. **Resolve before printing another mount.**
- Chapter 6 records the element as a "PTCYIDU ceramic disc, 5V–12V". Brand is right, form factor is not — the part is a 77 × 62 mm plate, 12 V only. That component-list line is stale.

## D-07 Pi 5 Mount

### Footprint is smaller than the board

The Raspberry Pi 5 board is 85 × 56 mm. This part measures 56 × 65 mm — matching the board's width but falling short of its length, so it is likely a partial bracket or a two-point mount rather than a full-footprint tray. Unconfirmed.

### Correction — this is not a partial bracket

An earlier note here read the 56 × 65 mm outline against the Pi 5's 85 × 56 mm board and inferred a
partial or two-point bracket. **Measuring the mesh disproves that:** four standoffs sit on a
**49.0 × 58.0 mm** rectangle, which is the Pi 5's full four-hole pattern. The outline is smaller than
the board simply because the board overhangs — all four mounting points are carried.

### ⚠ The inside top is the device's hot zone

The Pi hangs from the **inside top**, which is where the device's heat collects. Two sources converge
there:

- The heater's convective column **exits at the top** by design — that is the airflow path the
  chamber depends on ([D-06](#d-06-heater-spacer)).
- The Cree LED and its **DLH-3up-EH heat sink** shed ~3.3 W near the top of the optical stack.

A Pi 5 throttles around 80–85 °C junction and is not a cool part unloaded. It is now sited in the
exhaust of a 70 °C element and beside an LED heat sink.

☐ **Measure the Pi's thermals during a sustained 37 °C hold**, not just at idle — `vcgencmd
measure_temp` alongside the heater staircase run. This is cheap to check and expensive to discover
after the enclosure is closed.
☐ Confirm the mount does not block the exhaust path it sits in.
### 🔭 Cooling approach — heat sink + Pi fan *(direction set 2026-08-21)*

The enclosure fan is **deferred**; the focus is a **heat sink and the Pi's own fan** instead. That is
a much cheaper path — it needs no vents, so **no HEPA filter, no light traps, and no re-measure of the
heater's running current**, all of which an enclosure fan would have forced.

Two consequences to design around.

#### ⚠ An internal fan does not remove heat from the enclosure

It moves heat **off the SoC into the enclosure air**. In a closed box the total heat load is
unchanged — the Pi's watts still end up in the chamber the heater is regulating. Strictly, active
cooling *improves the thermal coupling* between the Pi and the chamber air, so it can deliver Pi heat
to the chamber **faster** than a passive sink would.

| Goal | Does heat sink + Pi fan achieve it? |
|---|---|
| Stop the Pi throttling | ✅ Yes — this is the right tool |
| Reduce heat reaching the 37 °C chamber | ❌ **No.** Same watts, better distributed |

So if the ambient evaluation shows the *chamber* running hot from parasitic electronics heat, this
does not fix it — only ducting, relocating, or exhausting the sources does.

#### ⛔ The official Pi 5 Active Cooler competes for this mount's holes

The Active Cooler retains itself with **spring push-pins through the Pi 5's mounting holes** — the
same **49 × 58 mm** holes this mount's four standoffs use. They cannot both occupy the same holes.

☐ **Resolve before printing another mount.** Options: an **adhesive heat sink** that does not use the
mounting holes; letting the cooler take two holes and the mount the other two (diagonal pair); or
re-working the standoffs around the cooler's pins.

☐ **Note the intake-air problem.** Mounted to the inside top, the Pi hangs component-side-down, so the
cooler sits **beneath** the board — directly in the rising exhaust of the heater column. Its intake is
then the hottest air in the enclosure, which is exactly what caps an active cooler's performance.
Worth measuring before assuming the cooler solves it.

☐ The Pi 5's 4-pin JST-SH fan header drives PWM + tach under OS control, so **no GPIO is consumed**
and nothing needs adding to the framework pin map.

#### 🔭 Option under consideration — move the Pi outside the enclosure

**Removes the watts instead of managing them**, which beats both fan options: no Pi heat in the
chamber at all, the inside-top space is freed, and the Active-Cooler hole conflict above disappears.

Costs to weigh if it is taken:

- **The 40-way ribbon has to leave the enclosure** — another pass-through, and another **light leak**
  in a light-tight envelope. Needs the same baffle treatment a vent would have needed.
- **Ribbon length hurts signal integrity.** The LCD runs **7-wire SPI** and the DS18B20 runs 1-Wire;
  both degrade on a long unshielded ribbon. Keep it as short as the placement allows and re-verify
  the LCD and probe after moving.
- **This mount (part 07) becomes obsolete or needs redesigning** for an external position.
- **Reversed-ribbon risk rises** — a longer external ribbon is easier to seat backwards, and that
  already cost a full false bring-up once. Key it (see part 08's orientation warning).

### Open items

- Standoff fastening method — posts are solid, Pi 5 needs **M2.5**.
- Single central chassis bolt permits rotation; confirm a locating feature exists.

## D-08 GPIO Breakout Mount

### Open items

- ✅ Rail-style mount confirmed; hole patterns measured.
- Breakout board make/model not recorded — only that it has **40 screw terminals**.
- Ribbon cable length/type not recorded.
- ☐ **Anti-reversal keying** — see the orientation warning above.
- ☐ Whether the chassis holes take M3 or #6 not recorded (Ø3.9 mm clearance suits either).

## D-09 Heater Mount

**The part is `my_heater_base_3holes.stl`** — identified 2026-08-18 by measuring the mesh. It
is a *different part* from part 10 (`Heater_DFR0457.stl`): 09 carries the PTC element on a
52.3 × 32.5 mm pattern, 10 carries the DFR0457 driver board on a 25.0 × 20.9 mm pattern. Both are
current; neither supersedes the other.

### Fastening scheme

The heater element is held down with M3 hex socket screws threading into heat-set inserts installed in the printed mount. This is the opposite arrangement to the LCD carrier (part 03), which threads into standoffs already on its board — here the print itself carries the threads, via brass.

Inserts are from the FFVRVSS kit: 4.4 mm OD, 3.8 mm d1 outer thread, 3 mm minimum thread length.

### Hole pattern

Four standoffs on a 2.06 × 1.28 in rectangle (52.3 × 32.5 mm) on centers. Corner-to-corner diagonal is 61.6 mm, comfortably inside the 105.1 mm bore of the heater chamber ring (part 06), so the pattern clears the chamber wall with room for the boss diameters.

**Measured from the mesh: 52.33 × 32.51 mm**, post centres at (±26.16, +16.50 / −16.01) — the spec is
confirmed in the print. Posts are Ø8.0 mm OD with a Ø4.0 mm bore, 4.82 mm tall from a 2.0 mm floor,
so there is 2.0 mm of wall around each insert.

### Boss hole sizing

Four bores, documented at 4.0 mm.

The receiving hole is the number that decides whether the inserts hold. Sized to the 4.4 mm OD, the insert drops in and spins; sized far under the 3.8 mm d1, material has nowhere to displace and the boss splits. 4.0 mm sits between the two — above d1 so the knurl has clearance to enter, under the OD so it still bites — and leaves room for the printed hole to come out under nominal, which is the usual direction for a small bore in PETG.

The figure is provisional pending a printed part. Holes this size typically print undersized, so the effective bore may land nearer 3.8–3.9 mm; that is still workable, but it is the measurement to take first. If it comes out at or above 4.2 mm, the inserts will spin and the bore wants tightening in CAD rather than compensating at install.

Boss walls need enough material around the hole to contain the melt; a 4.4 mm insert wants a boss noticeably wider than the insert itself.

### Installation

Heat-set inserts go in with a temperature-controlled iron — **set it to 240 °C** for PETG (working range 230–250 °C) — pressed square and slowly enough that the melt flows rather than skins. An insert that goes in cocked will hold the heater at an angle, which matters here because the element's contact with the mount is the thermal path.

### Lead pass-throughs — revised 2026-08-18

The floor carries **three Ø5.0 mm through-holes**, at y = −45.7 on an 11.0 mm pitch. This replaced the
previous **two** slots of roughly 3.8 × 2.8 mm. Two changes, each for its own reason:

**Enlarged to 5 mm, because the old holes damaged the wire.** The PTC leads did not pass cleanly
through the undersized slots, and forcing them **stripped the insulation**. That is not a fit problem,
it is a fault waiting in a heated chamber: the PTC draws up to 3.75 A running and ≤ 8.5 A on cold-start
inrush, and bare conductor
against another lead or against a heat-set insert is a short. The mitigation is **heat-shrink,
colour-coded** — which was the plan for identification anyway, and now does double duty as abrasion
protection.

> ⚠ **Inspect, do not merely re-sleeve.** Any lead that was already pulled through the old slots may
> be nicked under intact-looking insulation. Sleeving hides that rather than fixing it. Ring out each
> conductor and inspect the jacket over the passed length before reuse.

**A third hole, because the cutoff had nowhere to go.** The KSD9700 sits in the spacer above
([part 11](#11--temp-cutoff-ring)) and has two leads that must reach the supply. The third hole lets
it be **wired from inside the heat chamber** and dropped down. All heater-zone wiring now converges
into the circuit module (part 10) at the base, where the circuit wiring is actually made — one
termination zone instead of leads escaping the stack at several heights.

☐ **Chamfer or deburr the hole mouths.** A printed hole edge is exactly what abraded the insulation
the first time; 5 mm of clearance helps, but a sharp layer edge at the rim still cuts.
☐ **Size the clearance against the sleeved OD**, not the bare wire — heat-shrink adds diameter, and
the cutoff pair shares one hole.

### Thermal note

Screw and insert together form a metal path from the aluminum-shelled element into the print. The element self-limits at 70 °C, below PETG's ~80 °C glass transition, so the bridge is not a failure risk — but the plastic immediately around each insert is the hottest plastic in the assembly, and heat-set inserts hold by melted grip. Worth checking retention after the first sustained run at setpoint.

### Open items

- Measure the as-printed bore against the 4.0 mm nominal and confirm insert retention.
- Screw length not recorded.
- Insert overall length not recorded — only the 3 mm minimum thread.
- DS18B20 probe retention method not recorded (the insert measures 19.0 × 3.0 mm, 24.6 mm tall).
- **☐ The probe insert is at y +41.3; the three pass-throughs are at y −45.7, on the opposite side.**
  The three holes are spoken for — two PTC leads and the cutoff pair. Does the DS18B20 lead need a
  route down as well, or does it exit the module another way?
- Element outline dimensions not recorded — the hole pattern is fixed, but the element's footprint sets the clearance around it.
- Rename `my_heater_base_3holes.stl` to match the naming rule.
- Source CAD (F3D/STEP) not tracked, and the `.3mf` went with the superseded version.
- Chamfer/deburr state of the new Ø5 mm holes not recorded — see the insulation note in D-09.

## D-10 Heater Circuit Holder

### What this part is

`Heater_DFR0457.stl` is the **current heater module** — the 1 in stack ring at the heater layer,
carrying the DFR0457 driver on four heat-set-insert posts.

Part 09 (`my_heater_base_v2.stl`) is a **different, equally current** part: it carries the PTC element
and the DS18B20 insert on a 52.3 × 32.5 mm pattern. The two are not interchangeable and neither
supersedes the other — 09 holds the element, 10 holds the driver that switches it. Both take the same
M3 inserts and both have Ø8.0 mm posts with Ø4.0 mm bores.

### Measured geometry

Taken from the mesh, not from CAD:

| | Value |
|---|---|
| Envelope | 113.05 × 113.04 × 25.40 mm |
| Ring OD | 113.05 mm (radius 56.53) — matches the rest of the stack |
| Floor | 2.0 mm |
| Post OD | **8.0 mm** |
| Post height | 4.0 mm (z 2.0 → 6.0 measured from the underside) |
| Insert bore | 4.0 mm through the post |
| Post centres | (−13.14, +3.99) · (+11.87, +3.99) · (+11.87, −16.89) · (−13.14, −16.89) |
| Pattern | **25.01 × 20.88 mm** on centres |
| Pattern centre | (−0.64, −6.45) — offset from the ring axis, not concentric |

The 8.0 mm post OD leaves 2.0 mm of wall around a 4.0 mm bore, which is enough material to contain
the melt around a 4.4 mm insert — it is a light interference, so press slowly and watch for the boss
bulging rather than the insert sinking.

### Iron temperature

**240 °C**, the working figure for these PETG posts. The band is 230–250 °C: below it the plastic
does not flow and the post cracks under pressure; above it the insert sinks too fast to keep square
and the plastic degrades. Stop with the flange flush, and let it cool fully before threading a bolt —
PETG near its 80 °C Tg has no strength and an insert torqued warm spins permanently.

### Open items

- Confirm the 25.01 × 20.88 mm pattern against the DFR0457's actual mounting holes — the pattern was
  measured from the print, and DFRobot publishes board outline only.
- Measure the as-printed bore. At or above 4.2 mm the inserts spin; tighten in CAD, not at install.
- Confirm screwdriver access to the VIN / GND / VOUT terminal block with the board seated.
- Source CAD (F3D/STEP) not tracked.
- Register lip / stacking profile not characterised here.

## D-11 Temp Cutoff Ring

### Why it is a separate part

The ring exists **so the cutoff's position can be adjusted.** The KSD9700 has to sit where it will
trip on a genuine runaway but not during a normal hold at 37 °C, and that spot is found empirically —
[the heater how-to validates it at step 36](../../spaceplacer_repo/projects/heater_v2/spaceplacer_heater_v2_howto.md).
Keeping the sensor in a separate snap-in ring means moving it is a reprint of a small 0.5 in ring
rather than of the whole spacer.

### ✅ No longer a composite — resolved 2026-08-21

`tempcut_combined_holder.stl` is a **single merged mesh**: 105.03 × 97.96 × 12.70 mm, the ring plus
the sensor pocket in one file. Slice that one file and you get the whole part.

Previously the two halves were joined **in Bambu Studio at slice time**, so `tempcut_ring.stl` alone
yielded a plain ring with no sensor retention. That trap is gone.

**Folder cleaned 2026-08-21.** The 8 `(Assembly)_BodyN` exports were removed once the merged mesh
existed — they were scaffolding for a workflow the combined file replaces.

**Superseded halves deleted 2026-08-24.** `tempcut_ring.stl`, `tempcut.stl` and `tempcut_ring.step`
are no longer in the folder. They were reference only — never printables — and their exports were not
co-located anyway (the ring sat at z −1131, the pocket at z 0), so they were a standing trap for
anyone reading those coordinates as stack positions. Nothing printable was lost.

> ### ⚠ ☐ Part 11 now has NO source geometry — the merged STL is the only artefact
> This was already thin and the 2026-08-24 cleanup closed the last door. `tempcut_ring.f3d` was
> deleted earlier; the removed 3MF referenced a `tempcut_ring_parts.step` that was never in this
> folder; and `tempcut_ring.step` — the *ring alone*, not the merged geometry — has now gone too.
>
> **`tempcut_combined_holder.stl` is the whole of part 11's existence.** A revision to the merge
> starts from a mesh, not from CAD.
>
> **One hedge remains:** `thermalcut_sensorholder.3mf` is still in the folder (D-11 previously
> recorded it as deleted — it was not). As the Bambu project for the pre-merge workflow it carries the
> two halves' geometry, so it is the last thing standing between part 11 and mesh-only. **Do not
> delete it until a STEP or F3D of the combined part exists.**
>
> **Do this if the Fusion 360 design still exists in the cloud: re-export a STEP or F3D of the
> combined part.** If it does not, part 11 is mesh-only permanently — which matters because D-11
> already flags it as *superseded by design intent* (a simplified spacer absorbing parts 06 and 11),
> and that redesign would have to be modelled from scratch regardless.

### ✅ RESOLVED 2026-08-18 — the leads have an exit

The cutoff's two leads had no way out of the incubation module. Fixed at **part 09**, not here: its
floor was revised from two undersized slots to **3 × Ø5 mm holes**, the third specifically so the
cutoff can be **wired from inside the heat chamber** and dropped down into the circuit module at the
base. See [D-09](#d-09-heater-mount).

This settles the routing question for the consolidated spacer below: the wire exits do **not** have
to be designed into the spacer, because the leads leave through the floor of the part beneath it. The
consolidation is now purely about part count and sensor retention.

### ☐ Planned — consolidate 06 + 11 into one spacer

The intended fix is a **simplified spacer ring that holds the sensor and provides the wire exits**,
replacing both the plain spacer (part 06) and this ring. That would:

- **reduce the part count by one**, and
- **enable wire routing**, which the current pair does not solve at all.

Adjustability is what the split bought; the consolidated part has to preserve enough of it — either
by offering the sensor pocket at a chosen position per print, or by fixing the position once the
step-36 validation settles where it belongs. **Resolve step 36 before committing to the merged
design**, or the reprint-a-small-ring advantage is lost.

### ⛔ Print this part in PETG, not PLA — 2026-08-21

*(The slicer project that prompted this note has since been deleted. The requirement stands for
whatever project replaces it — it assigned both objects to **PLA**, slot 1, 220 °C / 55 °C bed.)*

**This part must not be PLA.** It sits inside the heater chamber holding the thermal cutoff, and
PLA's glass transition is **55–60 °C** — the KSD9700 is specified to trip at **55 °C**, so the ring is
expected to reach PLA's softening range *by design*, with no fault required. A ring that creeps or
sags moves the sensor, which changes the trip margin that
[step 36](../../spaceplacer_repo/projects/heater_v2/spaceplacer_heater_v2_howto.md) exists to validate.
This is the same PLA prohibition [D-01](#d-01-plate-holder) applies to the plate holder.

☐ **Slice this part in PETG.** Carry the requirement into the new project.

### ☐ Print settings — the deleted project deviated from this file's spec

Recorded so the same defaults do not come back:

| | That project used | This file specifies |
|---|---|---|
| Walls | **2** | **3+** |
| Infill | **15 %** | **20–30 %** |
| Layer height | 0.2 mm | 0.2 mm ✅ |
| Supports | off | as needed ✅ |

Thin walls and low infill on a **snap-fit** part are a specific risk: the snap features rely on wall
material to hold their spring. Either bring the project up to 3 walls / 20 % or record why this part
is an exception.

☐ **Leave enough lead length to reach the floor below.** The cutoff is now wired from inside the
chamber and its leads drop through part 09's floor, so the sensor's height in the spacer sets how much
slack the leads need. Moving the sensor up to satisfy step 36 lengthens that run.


## D-13 Light Spacer Lower Ring

`lightspacer_lower_ring.stl` — added 2026-08-24.

The light spacer carries the LED light ring in the **lamphouse position** of the Bogen enlarger the
device is built from. Without a stop it can slide down into the body; this ring is that stop.

### Geometry, measured from the mesh

Two Z levels (−94.07 and −66.68 in Fusion coordinates) and two radii (74.89 and 79.97 mm) — so the
part is a **plain extruded annulus**. There is no register lip, no taper, no lead-in chamfer, and no
fastener boss. Everything it does, it does by interference.

The **5.08 mm wall is exactly 0.200 in**, which suggests the ring was dimensioned in imperial against
the enlarger's own hardware rather than to the metric stack the printed parts otherwise use.

### ☐ The two numbers that matter are not recorded

Retention is a pure friction fit, so its behaviour is set entirely by clearances this file cannot
show:

| Interface | Ring dimension | Mating dimension | Status |
|---|---|---|---|
| Ring bore → light spacer OD | **149.78 mm** | ? | ☐ **not recorded** |
| Ring OD → enlarger body opening | **159.94 mm** | ? | ☐ **not recorded** |

The second is what makes it a *retaining* ring at all: the OD must exceed the body opening, or the
assembly passes straight through and the part does nothing. **Measure the enlarger body and record
it** — it is the one dimension that decides whether this design is correct, and it lives on a piece
of inherited hardware, not in CAD.

### Rev 2 — how the wedge actually engages

The spacer is a **straight** Ø149.82 tube; the ring's bore is **tapered**. So contact is not over the
full 27.40 mm — the tube enters at the ring's top and binds as the bore narrows beneath it.

| Interference reached | Depth from ring top |
|---|---|
| 0.08 mm | 0.00 mm — contact begins immediately |
| 0.10 mm | 0.57 mm |
| 0.15 mm | 2.01 mm |
| 0.20 mm | 3.44 mm |
| 0.30 mm | 6.30 mm |
| 0.50 mm | 12.03 mm |

Full-depth engagement would demand **1.03 mm** of diametral interference — far past what PETG will
take without splitting. **The joint therefore grips as a narrow band a few millimetres below the
ring's top face**, and how far the tube travels in is set by how hard it is pressed.

**That is the right behaviour for this part**, and it is what rev 1 lacked:

- **Self-tightening.** Load pushes the tube down into a narrowing bore. The harder it is loaded, the
  harder it grips.
- **Tolerant of print variation.** Rev 1 needed 0.02 mm radial accuracy to work at all. Rev 2 just
  seats at a slightly different depth if the print runs over or under — the taper converts a
  dimensional error into a **position** error, which nothing here cares about.
- **Still adjustable.** Press further for tighter, back off for looser — which keeps the tuning range
  open while the optical height is being found ([D-15](#d-15-light-spacer-large)).

☐ **Record the seating depth** once the optical height is locked in — it is the number that says how
much interference the joint actually ended up with.

### ⚠ The wall thins where the load is

Wall runs **5.59 mm at the bottom, 5.12 mm at the top** — and the top is where the wedge grips. A
press fit puts the bore in hoop tension, so the thinnest section carries the highest stress.

☐ Watch the top face for **hoop cracking** after repeated seating cycles, particularly along a layer
line. PETG is tough but layer adhesion is the weak axis, and a ring loaded in hoop tension is being
pulled exactly across its layers.

### ☐ Friction fit + sustained load

The ring holds the spacer's weight continuously, through a printed interference fit. **PETG is
mandatory here** (see the material rule at the top) — not merely preferred, because a softer filament
would relax straight out of an interference fit under a constant load. Even in PETG, expect *some*
creep: a joint that grips on assembly can settle over weeks, the same mechanism behind the
pass-through and heat-set-insert cautions elsewhere in this document.

Worth checking after the first extended run: does it still hold position, or has it settled? If it
settles, the fix is a mechanical stop rather than more interference — a screw, a lip that lands on
the body, or a split ring with a clamping screw. **Adjustability and long-term grip pull in opposite
directions**, and right now the design is entirely on the adjustable side.

☐ Record whether the adjustment is set once at assembly or re-adjusted between configurations. That
decides whether creep is a nuisance or a calibration problem.


## D-14 Cree Light Ring

`Cree_lightring.stl` — added 2026-08-24. **174.62 × 174.57 × 42.86 mm**, 1,956 triangles.

Replaces the Bogen enlarger's original lamphouse. The Cree XP-E2 470 nm array and its Carclo
diffuser optics sit here, above the condenser that collimates their output onto the mask.

### Geometry, measured from the mesh

Six distinct Z levels, all concentric on the axis (XY centre 0.00, 0.00):

| Z | r_min | r_max | Reading |
|---|---|---|---|
| −12.70 | 74.61 | 87.31 | skirt, bottom face |
| +9.80 | 5.00 | 74.61 | web plate, underside |
| +13.00 | 5.00 | 74.61 | web plate, top — **3.20 mm thick** |
| +19.50 | 74.61 | 87.31 | skirt, top face |
| +19.60 | 5.00 | 18.90 | central hub |
| +30.20 | 37.90 | 56.23 | upper ring |

The skirt runs the full height (−12.70 → +19.50) while the web plate sits high within it, so the part
has a **deep open underside** — about 22 mm of clear skirt below the plate. That volume is presumably
where the emitter, sink and optics live, firing downward.

### ☐ What the mesh cannot tell us

Three things are needed before this part can be built or reconciled, and none are derivable from an
STL:

1. **Emitter mounting.** No resolvable hole pattern for the Cree stars, the heat sink, or the cooling
   fan. Record the pattern, fastener spec, and which surface each attaches to.
2. **The Ø≈149 mm light spacer.** See the mating question in the part 14 summary — the tube that both
   this and part 13 appear to be sized around is not in this folder at all. **It is the one component
   that would confirm or break both designs, and it is undocumented.**
3. **The two edge notches** (~1.76 × 3.59 mm, mirrored about X at r ≈ 74.6). Cable exit is the obvious
   guess — the emitter needs power in — but that is a guess.

### ⚠ Thermal — PETG is load-bearing here

The Cree sink sheds **~3.3 W** continuously, and this part carries it. The device-wide
[PETG rule](#) applies with force: PLA's ~55–60 °C glass transition is a real risk against a
continuously-dissipating sink in a semi-enclosed skirt, where convection is poor by design (the
lamphouse is meant to be light-tight, not ventilated).

☐ Record the measured temperature at the sink-to-PETG interface during a sustained run. The device
guidance is to keep that interface **well below ~80 °C**; unlike the heater chamber, nothing here has
a thermal cutoff to bound it.


## D-15 Light Spacer, Large

`lightspacer_large.stl` — added 2026-08-24. **149.74 × 149.76 × 92.07 mm**, 1,002 triangles, three
distinct Z levels.

Sets the height of the Cree emitter above the condenser, which is what determines **projection
convergence** at the substrate plane. Its 92 mm is therefore an optical dimension, not a structural
one — changing it changes the throw.

### Measured profile

| Z | ID | OD | Section |
|---|---|---|---|
| 0.00 (top) | Ø142.84 | **Ø149.26** | narrow end of the taper |
| −15.88 | — | **Ø149.82** | taper meets the straight section |
| −92.07 (bottom) | Ø142.84 | **Ø149.82** | straight, full length |

Only three Z levels, so the band between 0.00 and −15.88 is a single conical surface — a true taper,
not a step. Half-angle ≈ **1.01°**.

The **Ø142.84 mm bore is constant the full height**: the clear optical aperture, unobstructed.

### Why the design works

Both mating joints are cut to **+0.04 mm interference**, but they do different jobs:

- **Top (part 14)** — the 1° taper is a **self-locking wedge**. The light ring's Ø149.22 skirt starts
  at the tube's narrowest point and tightens as it descends, centring the emitter on the optical axis
  and holding it without a fastener. Taper joints self-centre; a straight press fit does not.
- **Bottom (part 13)** — a straight Ø149.82 section **76.19 mm** long. The retaining ring is 27.40 mm
  tall, so it can be set anywhere across **48.79 mm** of travel. *That* is the adjustability: the
  height at which the spacer is stopped from entering the body.

### ⚠ 0.02 mm radial is below what FDM can hold

This is the one thing to know before printing. **+0.04 mm diametral = 0.02 mm on radius**, an order
of magnitude finer than typical FDM repeatability (~0.1–0.2 mm), and smaller than the dimensional
shift from a change of filament batch, nozzle temperature, or ambient conditions.

**So the model does not decide these fits — the printer does.** Expect to calibrate:

☐ Print a **short test coupon** of each joint — 10 mm of the top taper and 10 mm of the lower
  straight section — before committing to a 92 mm tube and a 174 mm ring.
☐ **Target the tuning phase first, not the final fit.** While the height is still being set, part 13's
  joint needs to be *movable* — a fit calibrated to hold permanently will fight every adjustment.
  Aim for firm-but-slidable now; tighten at lock-in.
☐ Record the **measured** OD you actually achieve versus the modelled 149.82 / 149.26, and the
  resulting fit (free / snug / immovable) for each joint.
☐ Decide which way to err. These joints fail in opposite directions: the **taper** tolerates being
  slightly undersize (it simply seats deeper), while the **straight friction section** does not —
  undersize there and the retaining ring will not hold the load. If a compensation is needed, bias
  toward the straight section.

### ⏸ Height is TUNABLE BY DESIGN — lock-in pending

**The 92.07 mm is provisional and intended to be.** Optimal optical height is being determined
empirically, not calculated up front: the emitter is moved until projection convergence at the
substrate plane is best, and *then* the number gets recorded.

That is what the adjustable joint is for. Part 13's **48.79 mm of travel** is not slop to be
engineered out — **it is the tuning range**, and it stays open until the optimum is found.

**Planned lock-in.** Once the optimal height is determined:

☐ **Record the number** — the measured emitter height, and the convergence result that justified it.
☐ **Then revise the parts to suit.** The outcome may be a **longer** tube, a **shorter** one, a
  **better-fitting** joint, or a fixed stop replacing the adjustment entirely. None of that is decided
  yet, and none of it should be pre-empted.

> ⚠ **The fit that tunes well is not the fit that locks well.** These are different requirements and
> the design currently has to serve both:
>
> | Phase | What part 13's joint must do |
> |---|---|
> | **Tuning (now)** | Slide, re-grip, and hold position through **repeated** adjustment |
> | **Locked (later)** | Hold one position permanently under sustained load |
>
> Repeated sliding **burnishes PETG** — each adjustment cycle wears the interface slightly, so a fit
> that grips on the first setting can be looser by the tenth. Do not tighten the fit to solve this
> during tuning; that makes adjustment harder and accelerates the wear. **Solve it at lock-in**, with
> a mechanical stop, a clamping screw, or a reprint at the final height.

### ☐ Still open

☐ **Enlarger body opening** — still the one unrecorded dimension in this sub-assembly (see
  [D-13](#d-13-light-spacer-lower-ring)). Part 13's Ø159.94 OD must exceed it.
**Height is deliberately tunable — see below.** 92.07 mm is a *starting point*, not a derived value.
☐ **PETG, per the device-wide rule** — and load-bearing twice over here: this tube carries the light
  ring's weight *and* both interference fits. Creep in the wall relaxes both joints at once.
