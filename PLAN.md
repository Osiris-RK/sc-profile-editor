# Star Citizen Profile Viewer - Implementation Plan

## Overview
A Windows desktop application that reads Star Citizen control profile XML files and converts them into human-readable formats (Word, PDF, CSV) with graphical device maps.

## XML Structure Analysis
Based on example profiles, the XML contains:
- **Header**: Profile name, device list (keyboard, mouse, joysticks)
- **Action Maps**: Organized by context (spaceship_movement, spaceship_weapons, player_choice, etc.)
- **Actions**: Individual controls with rebind inputs (e.g., `kb1_down`, `kb1_mouse4`, `js1_button1`)
- **Device Info**: Product IDs for connected devices (VKB Gladiator EVOs, etc.)

---

## Technology Stack: Python + PyQt6

### Why Python + PyQt6?
1. **Fast Development**: Python's simplicity + PyQt6's powerful widgets
2. **Document Generation**: Excellent libraries for PDF, Word, CSV
3. **Graphics**: Easy image manipulation with Pillow + Qt's drawing tools
4. **Packaging**: PyInstaller creates standalone Windows executables
5. **Maintainability**: Clean, readable code
6. **Community**: Large gaming/tool-building community

### Libraries
- **GUI**: PyQt6 or PySide6
- **XML Parsing**: xml.etree.ElementTree (built-in)
- **PDF**: reportlab or fpdf2
- **Word**: python-docx
- **CSV**: csv (built-in)
- **Graphics**: PIL/Pillow + PyQt6 QPainter
- **Packaging**: PyInstaller

### Distribution
Standalone .exe or Windows installer (Inno Setup)

### Estimated Size
- **Executable**: 60-80 MB (includes Python runtime + libraries)
- **Installer version**: 70-90 MB

---

## Application Architecture

### Directory Structure

```
sc-profile-viewer/
├── src/
│   ├── main.py                 # Entry point
│   ├── gui/
│   │   ├── main_window.py      # Main application window
│   │   ├── preview_widget.py   # Preview display
│   │   ├── control_editor.py   # Label editing interface
│   │   └── device_graphics.py  # Graphical device mapper
│   ├── parser/
│   │   ├── xml_parser.py       # Parse SC XML profiles
│   │   └── label_generator.py  # Generate human-readable labels
│   ├── exporters/
│   │   ├── pdf_exporter.py     # PDF generation
│   │   ├── word_exporter.py    # Word doc generation
│   │   ├── csv_exporter.py     # CSV generation
│   │   └── graphic_exporter.py # Device graphic annotations
│   ├── models/
│   │   └── profile_model.py    # Data structures for profile
│   └── resources/
│       └── device_templates/   # SVG/PNG device templates
│           ├── keyboard.svg
│           ├── mouse.svg
│           ├── vkb_gladiator.svg
│           └── generic_joystick.svg
├── tests/
├── requirements.txt
└── build_scripts/
    └── build_exe.py            # PyInstaller script
```

---

## Feature Breakdown

### 1. File Import
- QFileDialog for XML file selection
- Parse XML with xml.etree.ElementTree
- Validate profile structure
- Extract device info, action maps, and bindings

### 2. Label Generation
- Convert action names (e.g., `v_view_pitch`) to "View Pitch"
- Map input codes to readable strings:
  - `kb1_down` → "Keyboard: Down Arrow"
  - `js1_button1` → "Joystick 1: Button 1"
  - `kb1_mouse4` → "Mouse: Button 4"
- Create lookup tables for common actions

### 3. Preview Display
- **Table View**: QTableWidget with:
  - Columns: Action Category | Action Name | Device | Input | Custom Label
  - Sortable and searchable
  - Inline editing for labels
- **Graphic View**: QGraphicsView with device template overlay

### 4. Graphical Device Mapper
- Load SVG/PNG templates for each device type
- Detect device from XML (VKB Gladiator, generic joystick, etc.)
- Overlay text labels on buttons/axes using coordinates
- Allow device-specific templates with hotspot definitions

### 5. Export Formats

**PDF** (reportlab):
- Title page with profile info
- Table of contents by category
- Action tables per category
- Device graphics on separate pages

**Word** (python-docx):
- Similar structure to PDF
- Formatted tables
- Embedded images

**CSV**:
- Flat format: `Category,Action,Device,Input,Label`
- Importable to Excel/Sheets

**Graphics** (PNG/PDF):
- Standalone device images with annotations
- High resolution for printing

### 6. Packaging
- **PyInstaller** config:
  - `--onefile` for single .exe
  - `--windowed` to hide console
  - Include device templates in bundle
  - Add icon
- **Installer** (optional): Inno Setup for professional installation experience

---

## User Workflow

1. **Launch Application** → Main window opens
2. **Import Profile** → File picker opens, select XML
3. **Preview Generation** → Automatic parsing and display
4. **Edit Labels** (optional) → Click cells in table to edit
5. **Choose Export Format** → Radio buttons or dropdown (PDF/Word/CSV/Graphics)
6. **Export** → File save dialog, generate selected format(s)

---

## Development Phases

### Phase 1: Core Parser (Week 1)
- XML parser implementation
- Data model for profiles
- Label generation logic
- Unit tests with example files

### Phase 2: GUI Foundation (Week 2)
- Main window with PyQt6
- File import dialog
- Table preview widget
- Basic label editing

### Phase 3: Exporters (Week 2-3)
- CSV exporter (simplest)
- PDF exporter with reportlab
- Word exporter with python-docx

### Phase 4: Graphics System (Week 3-4)
- Create device templates (SVG/PNG)
- Graphic overlay system
- Device detection logic
- Annotation positioning

### Phase 5: Polish & Packaging (Week 4)
- Error handling
- User settings (save last directory, etc.)
- PyInstaller build script
- Testing on clean Windows machine

---

## Device Template Strategy

### Template Files Needed:
1. **Generic Keyboard** (104-key layout)
2. **Generic Mouse** (5-button)
3. **VKB Gladiator EVO** (specific HOTAS)
4. **Generic Joystick** (fallback)

### Template Format:
- **SVG preferred**: Scalable, editable
- Include metadata JSON with button coordinates:
```json
{
  "button1": {"x": 150, "y": 200},
  "button2": {"x": 170, "y": 200},
  "hat_up": {"x": 150, "y": 180}
}
```

### Community Templates:
- Allow users to add custom templates
- Templates folder in app directory

---

## Estimated Development Time
- **Solo developer**: 3-4 weeks part-time
- **With existing Python/PyQt6 experience**: 2-3 weeks

---

## Next Steps
1. Set up Python virtual environment
2. Install required dependencies (PyQt6, python-docx, reportlab, Pillow)
3. Create project structure
4. Begin Phase 1: Core Parser implementation