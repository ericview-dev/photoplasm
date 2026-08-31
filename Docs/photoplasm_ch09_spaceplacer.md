Photoplasm Quick Start Guide  ·  Chapter 9 — SpacePlacer

# Chapter 9 — SpacePlacer

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 0.1.0  ·  2026-05-18  ·  github.com/ericview-dev/photoplasm

---

## **Overview**

SpacePlacer is a minimalist perfboard layout tool designed for reproducible circuit builds in community makerspaces and educational lab settings. It separates **display layer** (visual grid, component placement UI) from **circuit metadata** (JSON data model), enabling version control, automated validation, and export of build-ready inventory lists.

The tool emerged from the Heater Perfboard design session — a need to document component placement in a format that could be shared via GitHub, validated before soldering, and reconstructed by independent builders without ambiguity.

**Repository:** github.com/ericview-dev/spaceplacer

## **Design Philosophy**

### **The Problem**

Traditional perfboard layouts are documented as:

- Hand-drawn schematics (hard to version-control, ambiguous hole references)

- Photographs of completed builds (can't extract coordinate data, can't validate before building)

- Fritzing breadboard views (proprietary format, heavy software, export limitations)

None of these formats separate **what the circuit is** (component placement, net connectivity) from **how it****'****s displayed** (colors, labels, zoom level). This makes automated validation impossible and GitHub diffs unreadable.

### **The Solution**

SpacePlacer treats the circuit layout as **structured data** (JSON) and the visual interface as a **rendering layer** that reads/writes that data. The JSON file is the source of truth — version-controlled, diff-friendly, tool-agnostic.

**Key principles:**

- **Grid coordinates are absolute** — Column A–T, Row 1–30 (configurable). No pixel positions, no relative placement.

- **Components own holes** — Each component (resistor, MOSFET, IC) reserves specific grid coordinates. No ambiguous "near the middle."

- **Nets are explicit** — A trace connecting holes is a named entity with color, start/end coordinates, and direction.

- **Validation before build** — DRC (Design Rule Check) engine flags overloaded holes, unconnected traces, and missing external wire destinations before soldering.

- **Inventory is derived** — Component BOM and wire list are auto-generated from metadata, not manually curated.

## **Architecture**

### **Three-Layer Model**

┌─────────────────────────────────────┐
│  Display Layer                      │  ← Browser canvas or Tkinter GUI
│  (HTML/JS or Python/PyQt)           │     User interaction, rendering
├─────────────────────────────────────┤
│  JSON Data Model                    │  ← Source of truth
│  (circuit_name.json)                │     Components, nets, externals
├─────────────────────────────────────┤
│  Validation Engine                  │  ← DRC rules, inventory export
│  (Python or JS)                     │     Pre-build checks, wire lists
└─────────────────────────────────────┘

**Display layer** — Reads JSON, renders grid, handles mouse clicks for component placement. Writes updated JSON on save. Display preferences (zoom, grid lines, hole labels) live in UI state, not in JSON.

**JSON data model** — Stores:

- Components: `{id, type, label, holes: [grid coordinates], color}`

- Nets: `{id, label, color, from: coordinate, to: coordinate, trace_index}`

- Externals: `{eid, label, hole: coordinate, direction, destination}`

- Board metadata: `{board_type, dimensions, date_modified}`

**Validation engine** — Reads JSON, applies DRC rules, outputs:

- Hole occupancy report (flags overloaded holes)

- Trace continuity check (flags unassigned or orphan holes)

- External wire destinations (flags missing labels)

- Component inventory (BOM with quantities)

- Wire list (location → destination table with wire colors)

## **JSON Data Model**

### **Structure**

{
  "board_type": "half_perfboard",
  "dimensions": {
    "columns": 20,
    "rows": 30
  },
  "date_modified": "2026-05-18T10:30:00Z",
  "components": [
    {
      "id": "R1",
      "type": "resistor",
      "label": "470Ω gate protection",
      "value": "470",
      "holes": ["C7", "D7", "E7"],
      "color": "#FFA500"
    },
    {
      "id": "Q1",
      "type": "mosfet_to220",
      "label": "IRLZ44N",
      "holes": ["E7", "F7", "G7"],
      "pins": {
        "E7": "gate",
        "F7": "drain",
        "G7": "source"
      },
      "color": "#000000"
    }
  ],
  "nets": [
    {
      "id": "net_gnd",
      "label": "GND",
      "color": "#000000",
      "traces": [
        {"from": "G7", "to": "A1", "trace_index": 1}
      ]
    },
    {
      "id": "net_12v",
      "label": "12V",
      "color": "#FF0000",
      "traces": [
        {"from": "A14", "to": "F14", "trace_index": 2}
      ]
    }
  ],
  "externals": [
    {
      "eid": "ext_gpio13",
      "label": "Pi Pin 33 (GPIO13)",
      "hole": "C7",
      "direction": "input",
      "destination": "Raspberry Pi header",
      "wire_color": "#FFA500"
    },
    {
      "eid": "ext_ptc_pos",
      "label": "PTC element (+)",
      "hole": "T4",
      "direction": "output",
      "destination": "JST J1",
      "wire_color": "#FF0000"
    }
  ]
}

### **Key Design Decisions**

**Hole coordinates are strings** — "C7" not {col: 3, row: 7}. Easier to read, diffs show "moved from C7 to D8" instead of col: 3 → 4.

**Components own holes, not vice versa** — The resistor knows it occupies C7–D7–E7. Holes don't store "I'm occupied by R1." This makes hole lookups O(n) but simplifies JSON structure.

**Trace index prevents double-counting** — A solder bridge across E7→D7→C7 is one trace with trace_index: 1. Three separate wires E7→D7, D7→C7, C7→? would be three traces with trace_index: 1, 2, 3. The DRC counts wires per hole using trace index, not coordinate presence.

**Externals have direction** — input (wire arrives from outside, e.g., Pi GPIO13) vs output (wire leaves board, e.g., to PTC element). Direction matters for wire list generation: inputs list "FROM external → TO board hole," outputs list "FROM board hole → TO external."

**Wire color is optional but recommended** — If present, inventory export includes a "recommended wire color" column for BOM ordering.

## **Feature Set**

### **Core Features (v0.1)**

| **Feature** | **Description** | **Status** |
| --- | --- | --- |
| **Grid-based coordinate system** | Columns A–T (or custom), rows 1–30 (or custom). Hole coordinates like "C7" reference absolute grid positions. | ✅ Implemented |
| **Component library** | Resistors (2-lead, 3-lead vertical), MOSFETs (TO-220), ICs (DIP-8/14/16), JST connectors, generic footprints. | ✅ Implemented |
| **Net (trace) tracking** | Named nets (e.g., "GND", "12V", "GPIO13") with color coding, start/end coordinates, and trace index for multi-hop routes. | ✅ Implemented |
| **External wire management** | Input/output designation, destination labels (e.g., "Pi Pin 33"), wire color recommendations. | ✅ Implemented |
| **JSON import/export** | Save/load layouts as `.json` files. Human-readable diffs in Git. | ✅ Implemented |
| **DRC (Design Rule Check)** | 10 validation rules: hole overload, orphan traces, unassigned holes, missing external destinations, etc. | ✅ Implemented |
| **Component inventory export** | Auto-generated BOM with quantities, values, and part numbers. CSV or Markdown table output. | ✅ Implemented |
| **Wire list export** | Location-to-destination table with wire colors and checkboxes for build tracking. CSV or Markdown output. | ✅ Implemented |
| **Browser (HTML/JS) version** | Runs in any modern browser, no install required. Interactive grid with drag-and-drop placement. | ✅ Implemented |
| **Python (Tkinter) version** | Standalone desktop app, same JSON format. Cross-platform (Windows/Mac/Linux). | ✅ Implemented |
| **SVG export** | Printable reference diagram for bench use. Hole labels, component outlines, wire routes. | ✅ Implemented |

### **Planned Features (Beta milestone)**

| **Feature** | **Description** | **Status** |
| --- | --- | --- |
| **xAPI learning analytics** | Emit xAPI statements on save/validate: verb "designed", object circuit, extensions: net_count, component_count, board_type, wire_count. | 🔄 Planned |
| **Multi-board projects** | Link multiple JSON files (e.g., LED Breadboard + Heater Perfboard) with inter-board trace validation. | 🔄 Planned |
| **Schematic auto-layout** | Generate schematic diagram from JSON (not just perfboard grid view). | 🔄 Planned |
| **Component rotation** | 90°/180°/270° rotation for ICs, connectors. Currently components are fixed orientation. | 🔄 Planned |
| **Interactive DRC in UI** | Highlight rule violations in red on the grid as user places components (live validation). | 🔄 Planned |
| **Gerber export** | Convert perfboard layout to Gerber files for PCB fabrication (Aim 3 scaling). | 🔄 Planned |

## **DRC (Design Rule Check) Engine**

### **10 Validation Rules**

| **Rule #** | **Name** | **Description** | **Severity** |
| --- | --- | --- | --- |
| **1** | **Hole overload** | A hole occupied by >1 component (excluding solder bridges). Example: Two resistor leads in the same hole. | ❌ Error |
| **2** | **Unassigned trace holes** | A net trace references a hole not occupied by any component. Example: Trace "C7→D8" but D8 is empty. | ⚠️ Warning |
| **3** | **Orphan holes** | A component hole has no net trace connecting it. Example: Resistor at C7–D7–E7 but no trace from E7. | ⚠️ Warning |
| **4** | **External destination missing** | An external wire has no `destination` label. Build checklist incomplete. | ❌ Error |
| **5** | **Wire count exceeds limit** | A hole has >1 wire (non-bridge trace). Example: Two jumper wires soldered to same hole. | ⚠️ Warning |
| **6** | **Net name conflict** | Two nets have the same label but different colors or non-overlapping traces. Example: Two "GND" nets with different colors. | ⚠️ Warning |
| **7** | **Component overlap** | Two components reserve overlapping holes (excluding intentional shared nodes like power rails). | ❌ Error |
| **8** | **Out-of-bounds coordinates** | A hole coordinate exceeds board dimensions. Example: "Z99" on a 20×30 grid. | ❌ Error |
| **9** | **Floating component** | A component has no net traces on any of its holes (not connected to anything). | ⚠️ Warning |
| **10** | **Missing component value** | A resistor or capacitor has no `value` field. BOM generation incomplete. | ℹ️ Info |

**Severity levels:**

- **Error (❌):** Build cannot proceed. Fix required before exporting wire list.

- **Warning (⚠️):** Likely mistake but may be intentional. Review before proceeding.

- **Info (ℹ️):** Non-critical, improves documentation completeness.

### **Running DRC**

**Browser version:**

// In browser console or via UI button
validateCircuit(); **Python version:** from spaceplacer import DRC circuit = DRC.load_json('heater_perfboard_v1.json')
report = circuit.validate()
print(report.summary())

**Output format:**

DRC Report — heater_perfboard_v1.json
Generated: 2026-05-18 10:30:00 ✅ PASS: Rule 1 (Hole overload) — 0 violations
⚠️  WARN: Rule 3 (Orphan holes) — 1 violation
   - Hole K10 (4.7kΩ pull-up resistor) has no outgoing trace
✅ PASS: Rule 4 (External destination missing) — 0 violations
...

Summary: 1 warning, 0 errors. Build can proceed with review.

## **Inventory Export**

### **Component BOM**

Auto-generated from components[] array in JSON. Groups by type and value, counts quantities.

**Example output (Markdown table):**

| **Component** | **Value** | **Quantity** | **Reference Designators** | **Notes** |
| --- | --- | --- | --- | --- |
| Resistor | 470Ω | 1 | R1 | Yellow-Violet-Brown-Gold |
| Resistor | 10kΩ | 1 | R2 | Brown-Black-Orange-Gold |
| Resistor | 4.7kΩ | 1 | R3 | Yellow-Violet-Red-Gold |
| MOSFET | IRLZ44N | 1 | Q1 | TO-220 package |
| JST Connector | XH 6-pin | 1 | J1 | 2.5mm pitch |

**CSV export:**

Component,Value,Quantity,Reference Designators,Notes
Resistor,470Ω,1,R1,Yellow-Violet-Brown-Gold
Resistor,10kΩ,1,R2,Brown-Black-Orange-Gold
...

### **Wire List**

Auto-generated from externals[] array. Lists every wire connection with source, destination, color, and checkbox for build tracking.

**Example output (Markdown table):**

| **#** | **FROM** | **TO** | **Wire Color** | **Function** | **Done** |
| --- | --- | --- | --- | --- | --- |
| 1 | Pi Pin 33 (GPIO13) | Heater Perfboard C7 | Orange | PWM signal to gate resistor | ☐ |
| 2 | Pi Pin 7 (GPIO4) | Heater Perfboard L8 | Yellow | DS18B20 data (1-Wire) | ☐ |
| 3 | LED Breadboard 3.3V rail | Heater Perfboard J10 | Red | 3.3V power supply | ☐ |
| 4 | LED Breadboard GND rail | Heater Perfboard A2 | Black | Ground reference | ☐ |
| 5 | 12V supply (+) | Heater Perfboard Row 14 | Red | 12V power rail | ☐ |
| 6 | 12V supply (GND) | Heater Perfboard Row 1 | Black | 12V ground rail | ☐ |
| 7 | Heater Perfboard JST J1 | PTC element red wire | Red | PTC positive | ☐ |
| 8 | Heater Perfboard JST J2 | PTC element black wire | Black | PTC switched ground | ☐ |
| 9 | Heater Perfboard JST J3 | DS18B20 yellow wire | Yellow | Sensor data | ☐ |
| 10 | Heater Perfboard JST J4 | DS18B20 black wire | Black | Sensor ground | ☐ |
| 11 | Heater Perfboard JST J5 | DS18B20 red wire | Red | Sensor 3.3V | ☐ |

**CSV export:**

#,FROM,TO,Wire Color,Function,Done
1,Pi Pin 33 (GPIO13),Heater Perfboard C7,Orange,PWM signal to gate resistor,☐
2,Pi Pin 7 (GPIO4),Heater Perfboard L8,Yellow,DS18B20 data (1-Wire),☐
...

This wire list is the **build checklist** — print it, check off each connection as it's wired, verify with multimeter.

## **Use Cases**

### **1. Heater Perfboard (Completed)**

**Problem:** Document MOSFET driver circuit for PTC heater with DS18B20 sensor. Circuit needs to be reproducible by other HTGAA students building Photoplasm.

**Solution:** SpacePlacer JSON file heater_perfboard_v1.json with:

- 3 resistors (470Ω, 10kΩ, 4.7kΩ)

- 1 MOSFET (IRLZ44N)

- 1 JST connector (6-pin)

- 4 power/signal nets (12V, GND, 3.3V, GPIO13)

- 11 external wire connections

**Deliverables:**

- JSON file in Git (diffable, version-controlled)

- Component BOM (shopping list)

- Wire list with checkboxes (build guide)

- SVG printout (bench reference)

### **2. LED Breadboard (Pending Conversion to Perfboard)**

**Current state:** Breadboard prototype with 9× 470nm LEDs, AS7341 sensor, OLED display, MOSFET driver.

**Next step:** Convert breadboard layout to perfboard using SpacePlacer. JSON file will document:

- LED array traces (3×3 matrix, RGB interleave)

- AS7341 I2C connections (SDA, SCL)

- OLED SPI connections (MOSI, SCLK, CS, DC, RST)

- MOSFET gate driver (GPIO18 PWM0)

- Power distribution (AUX-Power 3.3V rail, GND rail)

**Goal:** Reproducible LED driver board for BioLight community builds.

### **3. Multi-Board Systems (Future)**

**Vision:** Link multiple JSON files (LED Breadboard + Heater Perfboard + future Camera Controller) into a single project. SpacePlacer validates inter-board trace continuity (e.g., "LED Breadboard 3.3V rail → Heater Perfboard J10" is traced as one net across two boards).

**Validation rules:**

- External wire from Board A must match external wire to Board B (color, net label)

- Power budget check across all boards (sum 3.3V current draws, verify <3A)

- Ground continuity verified (all boards share GND reference)

## **Workflow Example**

### **Step 1: Create New Layout**

**Browser version:**

- Open `spaceplacer.html` in browser

- Click "New Layout"

- Set board dimensions: 20 columns (A–T), 30 rows

- Set board type: "half_perfboard"

- Save as `my_circuit_v1.json`

**Python version:** from spaceplacer import Board board = Board(columns=20, rows=30, board_type='half_perfboard')
board.save('my_circuit_v1.json')

### **Step 2: Place Components**

**Browser version:**

- Select "Resistor" from component library

- Click grid at C7 (first hole)

- Click D7 (second hole)

- Click E7 (third hole)

- Enter label: "470Ω gate protection"

- Enter value: "470"

- Select color: Orange

- Click "Place Component"

**Python version:** board.add_component(
    id='R1',
    type='resistor',
    label='470Ω gate protection',
    value='470',
    holes=['C7', 'D7', 'E7'],
    color='#FFA500'
)

### **Step 3: Add Traces (Nets)**

**Browser version:**

- Select "New Net"

- Enter name: "GND"

- Select color: Black

- Click start hole: G7

- Click end hole: A1

- Set trace index: 1

- Click "Add Trace"

**Python version:** board.add_net(
    id='net_gnd',
    label='GND',
    color='#000000',
    traces=[
        {'from': 'G7', 'to': 'A1', 'trace_index': 1}
    ]
)

### **Step 4: Add External Wires**

**Browser version:**

- Select "External Wire"

- Click hole: C7

- Enter label: "Pi Pin 33 (GPIO13)"

- Set direction: "input"

- Enter destination: "Raspberry Pi header"

- Select wire color: Orange

- Click "Add External"

**Python version:** board.add_external(
    eid='ext_gpio13',
    label='Pi Pin 33 (GPIO13)',
    hole='C7',
    direction='input',
    destination='Raspberry Pi header',
    wire_color='#FFA500'
)

### **Step 5: Validate and Export**

**Browser version:**

- Click "Validate" button

- Review DRC report in sidebar

- Fix any errors/warnings

- Click "Export BOM" → save `bom.csv`

- Click "Export Wire List" → save `wire_list.csv`

- Click "Export SVG" → save `circuit_diagram.svg`

**Python version:** report = board.validate()
print(report.summary()) board.export_bom('bom.csv')
board.export_wire_list('wire_list.csv')
board.export_svg('circuit_diagram.svg')

### **Step 6: Version Control**

git add my_circuit_v1.json bom.csv wire_list.csv circuit_diagram.svg
git commit -m "SpacePlacer: Initial layout for heater perfboard v1.0"
git push origin main

## **GitHub Integration**

### **Repository Structure**

/hardware
  /heater-perfboard
    /spaceplacer
      heater_perfboard_v1.json       ← Source of truth
      heater_perfboard_v1_bom.csv    ← Generated BOM
      heater_perfboard_v1_wires.csv  ← Generated wire list
      heater_perfboard_v1_diagram.svg← Printable reference
    /docs
      assembly_instructions.md       ← Human-written build guide

### **Version Control Best Practices**

**Commit JSON files, not UI screenshots** — Diffs show "moved resistor from C7 to D8" not "changed 500 pixels."

**Regenerate exports on every JSON change** — BOM and wire lists are derived data. Always export fresh copies after editing JSON.

**Tag stable releases** — git tag heater-perfboard-v1.0 -m "Tested build, all DRC checks pass"

**Branch for experiments** — git checkout -b feature/add-second-mosfet for design iterations. Merge to main only after physical build validation.

## **Display Layer Independence**

### **Why Separation Matters**

The same heater_perfboard_v1.json file can be:

- Rendered in a browser (HTML/JS canvas)

- Rendered in a Python GUI (Tkinter or PyQt)

- Validated by a CLI script (no GUI, just DRC report)

- Exported to SVG (static printout)

- Converted to Gerber files (for PCB fab, future)

The JSON is **tool-agnostic**. If the browser version becomes unmaintainable, switch to Python without losing any layout data.

### **UI State vs. Circuit State**

**Stored in JSON (circuit state):**

- Component placement (C7, D7, E7)

- Net connectivity (GND trace from G7 to A1)

- External wire destinations (Pi Pin 33 → C7)

**NOT stored in JSON (UI state):**

- Zoom level (user preference)

- Grid line visibility (display preference)

- Selected component (ephemeral UI state)

- Mouse cursor position (not circuit data)

This keeps JSON files small, diffable, and focused on circuit structure.

## **Future Directions**

### **xAPI Learning Analytics (Beta)**

SpacePlacer will emit xAPI statements when users save or validate circuits. This tracks learning progression through circuit complexity.

**Example xAPI statement:**

{
  "actor": {"name": "Eric Schneider", "mbox": "mailto:eric@example.com"},
  "verb": {"id": "http://adlnet.gov/expapi/verbs/designed"},
  "object": {
    "id": "https://github.com/ericview-dev/photoplasm/heater_perfboard_v1.json",
    "definition": {
      "type": "http://bioart.studio/xapi/activitytype/circuit",
      "name": {"en-US": "Heater Perfboard v1.0"}
    }
  },
  "result": {
    "extensions": {
      "http://bioart.studio/xapi/extensions/net_count": 4,
      "http://bioart.studio/xapi/extensions/component_count": 5,
      "http://bioart.studio/xapi/extensions/board_type": "half_perfboard",
      "http://bioart.studio/xapi/extensions/wire_count": 11,
      "http://bioart.studio/xapi/extensions/drc_errors": 0,
      "http://bioart.studio/xapi/extensions/drc_warnings": 1
    }
  }
} This data feeds into BioArt Studio learning analytics dashboards, showing progression from simple 3-component circuits to complex multi-board systems.

### **Multi-Board Projects**

Vision: A project.json file that references multiple board JSON files:

{
  "project_name": "Photoplasm BioLight System",
  "boards": [
    {"file": "led_breadboard_v1.json", "label": "LED Driver"},
    {"file": "heater_perfboard_v1.json", "label": "Heater Control"}
  ],
  "inter_board_traces": [
    {
      "from": {"board": "led_breadboard_v1.json", "hole": "3.3V rail"},
      "to": {"board": "heater_perfboard_v1.json", "hole": "J10"},
      "color": "#FF0000",
      "label": "3.3V shared power"
    }
  ]
} SpacePlacer validates that inter-board traces match on both ends (net names, colors, wire gauges).

### **Schematic Auto-Layout**

Current SpacePlacer shows **physical layout** (where components sit on the perfboard). Future: generate **schematic diagram** from the same JSON (symbolic representation, not tied to physical holes).

**Algorithm sketch:**

- Parse `components[]` and `nets[]`

- Group components by net membership

- Arrange components left-to-right by signal flow (inputs → processing → outputs)

- Draw net lines with minimal crossings (force-directed graph layout)

- Export as SVG schematic

This makes SpacePlacer a dual-purpose tool: perfboard layout AND schematic capture.

## **Installation**

### **Browser Version**

No installation required. Open spaceplacer.html in any modern browser (Chrome, Firefox, Safari, Edge).

**Files:**

- `spaceplacer.html` (UI)

- `spaceplacer.js` (logic + DRC engine)

- `spaceplacer.css` (styling)

### **Python Version**

**Requirements:**

- Python 3.8+

- Tkinter (included in most Python distributions)

- Optional: PyQt5 for enhanced UI

**Install:** git clone https://github.com/ericview-dev/spaceplacer.git
cd spaceplacer
pip install -r requirements.txt
python spaceplacer_gui.py **CLI usage (no GUI):** python spaceplacer_cli.py validate heater_perfboard_v1.json
python spaceplacer_cli.py export-bom heater_perfboard_v1.json bom.csv
python spaceplacer_cli.py export-wires heater_perfboard_v1.json wires.csv

## **References**

- **SpacePlacer GitHub Repository** — [github.com/ericview-dev/spaceplacer](https://github.com/ericview-dev/spaceplacer)

- **Heater Perfboard Example** — See Chapter 6 — Incubation Heater Perfboard

- **xAPI Specification** — [adlnet.gov/expapi](https://adlnet.gov/expapi)

- **JSON Schema** — [json-schema.org](https://json-schema.org)

## **Cross-References**

- Heater Perfboard build using SpacePlacer → See Chapter 6 — Incubation Heater Perfboard

- LED Breadboard future conversion → See Chapter: Photoplasm Hardware Overview

- BioArt Studio learning analytics → See Chapter: xAPI Integration (future)

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v0.1.0  ·  2026-05-18  ·  draft