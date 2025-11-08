# Changelog

All notable changes to SC Profile Viewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-01-08

### Added
- **Expanded device template support** - Added templates for additional VKB devices:
  - VKB F16 MFD (Multi-Function Display)
  - VKB Throttle Quadrant (THQ)
  - VKB Gunfighter MCG Ultimate (MCGU) joystick
- Added example profile (`example-profiles/layout_19APR2025_exported.xml`) for testing

### Changed
- Cleaned up visual-scratch directory (removed temporary development images)
- Updated .gitignore to exclude visual-scratch directory

## [0.2.1] - 2025-10-28

### Fixed
- Fixed label edit loss when toggling "Show Detailed" checkbox during active edit
  - Edits are now properly committed before view mode changes
  - Prevents confusion when reverting to default labels
- Fixed issue with device and action map filters not being preserved when toggling "Show Detailed" checkbox
- Fixed issue with label editing window text bleed-through
- Fixed issue restoring default text in label
- Support for buttons with multiple mappings

### Changed
- Updated CHANGELOG documentation to clarify device template support status (VPC MongoosT-50CM3 Left and Thrustmaster TWCS Throttle are stubs)

## [0.2.0] - 2025-10-26

### Added
- **Expanded device template support** - Added templates for additional HOTAS devices:
  - VKB Gladiator EVO Left (standalone and with Space Sim Module)
  - VKB Space Sim Module (SEM) as separate device
  - Virpil MongoosT-50CM3 Left stick stubs
  - Thrustmaster TWCS Throttle stubs
- Device splitter utility (`device_splitter.py`) for handling composite devices like VKB sticks with SEM modules
- Comprehensive device template creation documentation:
  - `CREATING_DEVICE_TEMPLATES.md` - Step-by-step guide for creating new device templates
  - `OVERLAY_CONVERSION.md` - Guide for converting Inkscape SVG overlays
- Utility scripts for template development:
  - `convert_inkscape_overlay.py` - Convert Inkscape SVG to template format
  - `embed_image_in_svg.py` - Embed device images in SVG overlays
  - `rescale_overlay.py` - Rescale overlay coordinates
- DEVICE_STATUS.md to track template development progress across devices

### Changed
- Updated .gitignore to exclude scratch/working directories and binary artifacts

## [0.1.1] - 2025-10-24

### Added
- Version management system with automatic version incrementing in build scripts
- Version display in window title, main header, and Help dialog
- CHANGELOG.md to track version history

### Changed
- Unified UI: Moved "Export Graphic" button to main header alongside other export buttons
- Export Graphic button now intelligently enables/disables based on graphic availability

### Fixed
- Fixed label edit loss when toggling "Show Detailed" checkbox during active edit
  - Edits are now properly committed before view mode changes
  - Prevents confusion when reverting to default labels
- Fixed label revert not working (deleting label text now properly reverts to global/auto-generated)
  - Removed incorrect text clearing on double-click that was interfering with revert
  - Labels now correctly fall back to global defaults or auto-generated names

### Removed
- Export Graphic button from Device Graphics tab (now in main header)
- Unused PyInstaller .spec files (now using Python build scripts exclusively)

## [0.1.0] - 2025-10-23

### Added
- Initial release of SC Profile Viewer
- Import and parse Star Citizen control profile XML files
- Display control bindings in sortable, filterable table
- Edit action labels with custom overrides
- Export profiles to CSV, PDF, and Word formats
- Device graphics visualization with SVG overlay annotations
- Support for VKB Gladiator EVO joystick templates
- Automatic template-based graphic generation
- Filter controls by:
  - Search text (action, input, device)
  - Device type
  - Action map
  - Hide unmapped keys
- Toggle between default and detailed view modes
- Persistent settings (window geometry, last opened profile)
- Auto-load last opened profile on startup
- User guide with comprehensive documentation
- PayPal donation and Discord community links

### Technical Features
- PyQt6-based GUI
- ReportLab PDF generation
- python-docx Word document export
- SVG rendering and template system
- Custom label override system with JSON storage
- Label generator for human-readable action names
- Device template manager
- Settings persistence via QSettings

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes or major feature overhauls
- **MINOR** version for new functionality in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

## How to Update This File

When making changes:

1. Add new entries under `[Unreleased]` in the appropriate category:
   - **Added** for new features
   - **Changed** for changes in existing functionality
   - **Deprecated** for soon-to-be removed features
   - **Removed** for now removed features
   - **Fixed** for any bug fixes
   - **Security** for vulnerability fixes

2. When releasing a new version:
   - Change `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
   - Add a new `[Unreleased]` section at the top
   - Update VERSION.TXT file
   - Create a git tag for the release

## Build Script Version Increment

Use the build scripts with the `--increment` flag to automatically update the version:

```bash
# Increment patch version (0.1.0 -> 0.1.1) for bug fixes
python scripts/build/build_exe.py --increment patch

# Increment minor version (0.1.0 -> 0.2.0) for new features
python scripts/build/build_exe.py --increment minor

# Increment major version (0.1.0 -> 1.0.0) for breaking changes
python scripts/build/build_exe.py --increment major
```
