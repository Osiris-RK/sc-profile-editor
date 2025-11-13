# SC Profile Editor - Project Context

This document provides context for AI assistants working on this project.

## Project Overview

SC Profile Editor is a desktop application for Star Citizen players to edit, customize, and export their control profiles in human-readable formats. It generates visual diagrams of controller layouts and exports bindings to PDF, Word, CSV, and graphical formats.

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
- ✅ Interactive PDF-based template system for device visualization
- ✅ Browser-like editing with QtWebEngine
- ✅ Automatic label mapping to device buttons/controls
- ✅ Supported devices (multiple VKB, VPC, Thrustmaster templates)
  - VKB Gladiator (EVO and SCG variants)
  - VKB Space Sim Module (SEM and variants)
  - VKB F16 MFD
  - VKB Throttle Quadrant (THQ and variants)
  - VKB Gunfighter MCG Ultimate and SCG variants
  - VKB STECS throttle and grips
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
- ✅ Three tabs: Controls Table, Device View, About
- ✅ Filter by search text, device, action map
- ✅ Hide unmapped keys option
- ✅ Auto-select text when editing labels
- ✅ Persistent window geometry and settings
- ✅ In-app help with README.md display
- ✅ Version display in window title and headers
- ✅ About tab with project info and acknowledgements

### Version Management
- ✅ Semantic versioning (MAJOR.MINOR.PATCH)
- ✅ VERSION.TXT file for version tracking
- ✅ Build scripts with automatic version incrementing
- ✅ docs/CHANGELOG.md for tracking changes

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
├── main.py                    # Application entry point
├── gui/                       # PyQt6 GUI components
│   ├── main_window.py        # Main window with tabs and exports
│   └── webengine_pdf_widget.py # Interactive PDF device viewer
├── parser/                    # XML parsing and label generation
│   ├── xml_parser.py         # SC profile XML parser
│   └── label_generator.py    # Human-readable label generator
├── exporters/                 # Export modules (CSV, PDF, Word)
├── graphics/                  # Template management and PDF rendering
│   └── pdf_template_manager.py # PDF template loader
├── models/                    # Data models for profiles and bindings
└── utils/                     # Utilities (settings, overrides, version)
    └── device_splitter.py    # Split composite devices

visual-templates/              # Device template resources
├── template_registry.json    # Template configuration
└── [device_id]/              # Per-device folders
    └── *.pdf                 # PDF template with form fields

scripts/
└── build/                    # Build scripts
    └── build_exe.py          # Standard build script

deprecated/                    # Deprecated files (SVG/PNG/OCR systems)
├── gui/                      # Old GUI widgets
├── graphics/                 # Old template managers
├── scripts/                  # Old utility scripts
└── template_files/           # Old PNG and SVG files
```

### Key Design Decisions

1. **Label Override System**
   - Global defaults (`label_overrides.json`) bundled with app
   - User customs (`label_overrides_custom.json`) in AppData
   - Priority: Custom > Global > Auto-generated
   - Real-time updates across table and device graphics

2. **Device Template System**
   - PDF-based templates with interactive form fields
   - QtWebEngine for browser-like PDF viewing and editing
   - JSON registry (`template_registry.json`) for device matching
   - Pattern-based device name matching (supports multiple patterns per device)
   - Automatic button range detection and mapping
   - Composite device support via device splitter utility

3. **Build Configuration**
   - Single standard build for all users
   - Version incrementing via `--increment` flag
   - PyInstaller for Windows executable generation

4. **Data Flow**
   - Import XML → Parse → Generate labels → Display in table
   - Edit labels → Save to custom overrides → Update Device View
   - Export → Apply current filters and view mode → Generate output
   - Device matching → Load PDF template → Populate form fields

## Development Guidelines

### Making Changes

1. **New Features**: Add to `[Unreleased]` in docs/CHANGELOG.md
2. **Bug Fixes**: Document in docs/CHANGELOG.md
3. **UI Changes**: Update README.md if user-facing
4. **Build Changes**: Update docs/DEVELOPMENT.md build section

### Version Increments

- **Patch** (0.1.0 → 0.1.1): Bug fixes, minor UI tweaks
- **Minor** (0.1.0 → 0.2.0): New features, device support
- **Major** (0.1.0 → 1.0.0): Breaking changes, major rewrites

### Building

```bash
# Standard build
python scripts/build/build_exe.py --increment patch
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
- **README.md** - End-user documentation and user guide (displayed in app)
- **docs/CHANGELOG.md** - Version history and release notes
- **docs/DEVELOPMENT.md** - Developer documentation and build instructions
- **docs/CLAUDE.md** - Project context and AI assistant instructions
- **docs/FILE_LOCATIONS.md** - File storage documentation
- **docs/RELEASE_PROCESS.md** - Release workflow and checklist

### Configuration Files
- **label_overrides.json** - Global label defaults (bundled)
- **label_overrides_custom.json** - User custom labels (AppData)
- **visual-templates/template_registry.json** - Device template definitions

## When Working on This Project

### Before You Start
1. Read README.md to understand user workflow
2. Check docs/CHANGELOG.md for recent changes and current status
3. Review template_registry.json to see supported devices
4. Read docs/DEVELOPMENT.md for development setup

### When Making Changes
5. Update docs/CHANGELOG.md under `[Unreleased]` section
6. Update relevant documentation (README.md for users, docs/DEVELOPMENT.md for developers)
6. Test both Standard and Detailed views
7. Verify exports work in all formats (CSV, PDF, Word, Graphics)
8. Test label editing and persistence
9. Check version displays correctly in window title and exports
10. Test all three tabs: Controls Table, Device View, About

### When Adding Device Templates
11. Add PDF template to appropriate directory in visual-templates/
12. Add device to template_registry.json
13. Test button mapping and form field population in Device View

### Recent Important Changes (v0.2.0 - v0.4.0)
- **Multi-device mapping support**: Buttons can now map to multiple devices (v0.2.1)
- **Filter persistence**: Device and action map filters preserved when toggling views (v0.2.1)
- **Device splitter**: Use `device_splitter.py` for composite devices like stick+SEM
- **PDF-only system**: Deprecated SVG/PNG template system in favor of interactive PDF templates (v0.4.0)
- **Simplified UI**: Consolidated to single Device View tab with About tab (v0.4.0)
- **Expanded device support**: Added 19+ new VKB device PDF templates (v0.4.0)