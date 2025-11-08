# SC Profile Viewer - Project Context

This document provides context for AI assistants working on this project.

## Project Overview

SC Profile Viewer is a desktop application for Star Citizen players to view, customize, and export their control profiles in human-readable formats. It generates visual diagrams of controller layouts and exports bindings to PDF, Word, CSV, and graphical formats.

## Current Status

**Version:** 0.2.1 (released October 28, 2025)
**Current Branch:** v0.3.0-more-device-support (active development)
**Status:** Stable release with expanded device support
**Platform:** Windows (PyInstaller executable)

## Implemented Features

### Core Functionality
- ✅ Import Star Citizen XML control profiles
- ✅ Parse and display control bindings in sortable, filterable table
- ✅ Two view modes: Default (3 columns) and Detailed (6 columns)
- ✅ Custom label editing with persistent override system
- ✅ Auto-load last opened profile on startup

### Export Capabilities
- ✅ Export to CSV (spreadsheet format)
- ✅ Export to PDF (formatted document)
- ✅ Export to Word (.docx)
- ✅ Export device graphics with annotations (PNG/PDF)

### Device Graphics
- ✅ SVG-based template system for device visualization
- ✅ Template overlay generation with custom labels
- ✅ Automatic label mapping to device buttons/controls
- ✅ Supported devices (8 templates):
  - VKB Gladiator EVO (Right & Left)
  - VKB Space Sim Module (SEM)
  - VKB F16 MFD
  - VKB Throttle Quadrant (THQ)
  - VKB Gunfighter MCG Ultimate
  - VPC MongoosT-50CM3 (Right)
  - Thrustmaster TWCS Throttle
- ✅ Device splitter utility for composite devices (e.g., stick + SEM module)

### Label System
- ✅ Three-tier label priority: Custom > Global > Auto-generated
- ✅ 72 pre-configured global label overrides
- ✅ Per-user custom label storage in AppData
- ✅ Real-time label updates across table and graphics

### UI/UX
- ✅ PyQt6-based modern GUI
- ✅ Filter by search text, device, action map
- ✅ Hide unmapped keys option
- ✅ Auto-select text when editing labels
- ✅ Persistent window geometry and settings
- ✅ In-app help with USER_GUIDE.md display
- ✅ Version display in window title and headers

### Version Management
- ✅ Semantic versioning (MAJOR.MINOR.PATCH)
- ✅ VERSION.TXT file for version tracking
- ✅ Build scripts with automatic version incrementing
- ✅ CHANGELOG.md for tracking changes

### Template Development Tools
- ✅ Comprehensive template creation documentation
  - `CREATING_DEVICE_TEMPLATES.md` - Step-by-step guide
  - `OVERLAY_CONVERSION.md` - SVG conversion guide
  - `DEVICE_STATUS.md` - Template progress tracking
- ✅ Utility scripts for template development:
  - `device_splitter.py` - Handle composite devices
  - `convert_inkscape_overlay.py` - Convert Inkscape SVG to template format
  - `embed_image_in_svg.py` - Embed device images in SVG overlays
  - `rescale_overlay.py` - Rescale overlay coordinates
  - `detect_button_coordinates.py` - Auto-detect button positions (OCR)

## Architecture

### Technology Stack
- **Python 3.12+** - Core language
- **PyQt6** - GUI framework
- **python-docx** - Word document generation
- **reportlab** - PDF generation
- **Pillow** - Image processing
- **PyInstaller** - Executable packaging

### Project Structure
```
src/
├── main.py                 # Application entry point
├── gui/                    # PyQt6 GUI components
│   ├── main_window.py     # Main window with tabs and exports
│   └── device_graphics.py # Device visualization widget
├── parser/                 # XML parsing and label generation
│   ├── xml_parser.py      # SC profile XML parser
│   └── label_generator.py # Human-readable label generator
├── exporters/              # Export modules (CSV, PDF, Word)
├── graphics/               # Template management and SVG rendering
├── models/                 # Data models for profiles and bindings
└── utils/                  # Utilities (settings, overrides, version)

visual-templates/           # Device template resources
├── template_registry.json  # Template configuration
└── [device_id]/            # Per-device folders
    ├── *.png               # Device image
    └── *_overlay.svg       # Button overlay template

scripts/
├── build/                  # Build scripts (exe generation)
└── template_dev/           # Template development utilities
    ├── device_splitter.py
    ├── convert_inkscape_overlay.py
    ├── embed_image_in_svg.py
    ├── rescale_overlay.py
    └── detect_button_coordinates.py

docs/
├── CREATING_DEVICE_TEMPLATES.md
├── OVERLAY_CONVERSION.md
└── DEVICE_STATUS.md
```

### Key Design Decisions

1. **Label Override System**
   - Global defaults (`label_overrides.json`) bundled with app
   - User customs (`label_overrides_custom.json`) in AppData
   - Priority: Custom > Global > Auto-generated
   - Real-time updates across table and device graphics

2. **Device Template System**
   - SVG-based overlays with embedded device images
   - JSON registry (`template_registry.json`) for device matching
   - Pattern-based device name matching (supports multiple patterns per device)
   - Automatic button range detection and mapping
   - Composite device support via device splitter utility

3. **Build Configuration**
   - Standard build: Excludes OCR (faster, smaller) - recommended for users
   - OCR build: Includes EasyOCR for template development
   - Both support version incrementing via `--increment` flag
   - PyInstaller for Windows executable generation

4. **Data Flow**
   - Import XML → Parse → Generate labels → Display in table
   - Edit labels → Save to custom overrides → Update graphics
   - Export → Apply current filters and view mode → Generate output
   - Device matching → Load template → Render overlay with labels

## Development Guidelines

### Making Changes

1. **New Features**: Add to `[Unreleased]` in CHANGELOG.md
2. **Bug Fixes**: Document in CHANGELOG.md
3. **UI Changes**: Update USER_GUIDE.md if user-facing
4. **Build Changes**: Update README.md build section

### Version Increments

- **Patch** (0.1.0 → 0.1.1): Bug fixes, minor UI tweaks
- **Minor** (0.1.0 → 0.2.0): New features, device support
- **Major** (0.1.0 → 1.0.0): Breaking changes, major rewrites

### Building

```bash
# Standard build (recommended)
python scripts/build/build_exe.py --increment patch

# OCR build (for template developers)
python scripts/build/build_exe_with_ocr.py
```

## Known Issues & Limitations

- Device templates available for 8 devices (primarily VKB, some VPC and Thrustmaster)
  - Many popular devices still need templates (more Thrustmaster, Logitech, Virpil, etc.)
- No Linux/macOS support yet (Windows only)
- No installer package (standalone .exe only)
- Buttons with multiple device mappings are supported as of v0.2.1

## Future Enhancements

- More device templates (additional Thrustmaster models, Logitech, more Virpil, etc.)
- Installer packages (NSIS, Inno Setup) for easier distribution
- Import/export custom label sets for sharing configurations
- Profile comparison tool to see differences between profiles
- Auto-update mechanism for easier version management
- Linux/macOS support (PyInstaller cross-platform builds)

## Important Files

### Core Documentation
- **VERSION.TXT** - Current version number
- **CHANGELOG.md** - Version history and release notes
- **README.md** - Developer documentation and build instructions
- **USER_GUIDE.md** - End-user documentation (displayed in app)
- **FILE_LOCATIONS.md** - File storage documentation

### Configuration Files
- **label_overrides.json** - Global label defaults (bundled)
- **label_overrides_custom.json** - User custom labels (AppData)
- **visual-templates/template_registry.json** - Device template definitions

### Template Development
- **CREATING_DEVICE_TEMPLATES.md** - Complete guide for creating new device templates
- **OVERLAY_CONVERSION.md** - Guide for converting Inkscape SVG overlays
- **DEVICE_STATUS.md** - Device template development progress tracker

## When Working on This Project

### Before You Start
1. Read USER_GUIDE.md to understand user workflow
2. Check CHANGELOG.md for recent changes and current status
3. Review template_registry.json to see supported devices

### When Making Changes
4. Update CHANGELOG.md under `[Unreleased]` section
5. Update relevant documentation (USER_GUIDE.md, README.md, etc.)
6. Test both Standard and Detailed views
7. Verify exports work in all formats (CSV, PDF, Word, Graphics)
8. Test label editing and persistence
9. Check version displays correctly in window title and exports

### When Adding Device Templates
10. Follow CREATING_DEVICE_TEMPLATES.md step-by-step guide
11. Use OVERLAY_CONVERSION.md for SVG conversion from Inkscape
12. Update DEVICE_STATUS.md to track progress
13. Add device to template_registry.json
14. Test button mapping and label overlay rendering

### Recent Important Changes (v0.2.0 - v0.2.1)
- **Multi-device mapping support**: Buttons can now map to multiple devices (v0.2.1)
- **Filter persistence**: Device and action map filters preserved when toggling views (v0.2.1)
- **Device splitter**: Use `device_splitter.py` for composite devices like stick+SEM
- **Template utilities**: Full suite of tools available in `scripts/template_dev/`