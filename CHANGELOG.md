# Changelog

All notable changes to SC Profile Viewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Device template directories for expanded HOTAS support:
  - VKB Gladiator EVO Left (with Space Sim Module)
  - Thrustmaster TWCS Throttle
  - Virpil MongoosT-50CM3 Left and Right sticks
- DEVICE_STATUS.md to track template development progress

### In Progress
- Creating device templates for v0.2.0 release

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
