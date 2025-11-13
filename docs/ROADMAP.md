# SC Profile Editor - Roadmap

This document outlines the planned development roadmap for SC Profile Editor, organized by version milestones.

## Current Version: 0.4.0

Released: 2025-11-12

**Focus:** Interactive PDF-based device templates, expanded VKB device support, documentation restructure

See [CHANGELOG.md](CHANGELOG.md) for full release notes.

---

## Upcoming Releases

### Version 0.4.x Series - VKB Refinement & Bug Fixes

**Status:** In Planning
**Focus:** Completing VKB device support, bug fixes, and UI improvements

#### Planned Work

- **VKB Field Mapping Completion**
  - Complete field mappings for all VKB device PDF templates
  - Verify button ranges and input codes for all VKB devices
  - Add any missing VKB device variants

- **Bug Fixes**
  - Address issues discovered in v0.4.0 release
  - Fix any PDF template rendering issues
  - Resolve label mapping edge cases

- **UI Updates**
  - Improve user experience based on feedback
  - Polish existing features
  - Enhance error messages and user guidance

#### Target Devices (VKB)
- All Gladiator variants (EVO, SCG, OTA)
- All Gunfighter variants (MCG, SCG, OTA)
- All STECS components (base, STEM, ATEM, grips)
- All THQ variants (standard, V, WW2)
- SEM and SEM-V modules
- F16 MFD

---

### Version 0.5.0 - Virpil Device Support

**Status:** Planned
**Focus:** Adding comprehensive Virpil device template support

#### Planned Work

- **Virpil PDF Templates**
  - Create PDF templates for major Virpil devices
  - Implement field mappings for Virpil devices
  - Add Virpil device detection and matching

- **Template System Enhancements**
  - Improve template registry for multi-manufacturer support
  - Enhance device name pattern matching
  - Optimize PDF rendering for varied template layouts

#### Target Devices (Virpil)
- MongoosT-50CM3 (Left and Right) - *Stubs exist, need completion*
- VPC Constellation ALPHA
- VPC WarBRD
- VPC Throttle (MT-50CM3)
- VPC Control Panel #1
- VPC Control Panel #2
- Other popular Virpil devices based on community feedback

---

### Version 0.5.x Series - Virpil Refinement & Bug Fixes

**Status:** Planned
**Focus:** Bug fixes and improvements for Virpil device support

#### Planned Work

- **Bug Fixes**
  - Address Virpil-specific issues
  - Fix template rendering problems
  - Resolve device detection edge cases

- **Field Mapping Refinement**
  - Complete any missing Virpil field mappings
  - Verify button ranges for all Virpil devices
  - Add support for additional Virpil variants

- **Documentation**
  - Update user guide with Virpil device usage
  - Add Virpil-specific examples and workflows

---

### Version 0.6.0 - Thrustmaster Device Support

**Status:** Planned
**Focus:** Adding comprehensive Thrustmaster device template support

#### Planned Work

- **Thrustmaster PDF Templates**
  - Create PDF templates for popular Thrustmaster devices
  - Implement field mappings for Thrustmaster devices
  - Add Thrustmaster device detection and matching

- **Template System Enhancements**
  - Support for Thrustmaster naming conventions
  - Handle Thrustmaster-specific button layouts
  - Optimize for diverse Thrustmaster product line

#### Target Devices (Thrustmaster)
- TWCS Throttle - *Stub exists, needs completion*
- T.16000M FCS HOTAS
- Warthog HOTAS (Stick and Throttle)
- T.Flight HOTAS X/4
- TCA Sidestick Airbus Edition
- TCA Quadrant Airbus Edition
- Other popular Thrustmaster devices

---

### Version 0.6.x Series - Thrustmaster Refinement & Bug Fixes

**Status:** Planned
**Focus:** Bug fixes and improvements for Thrustmaster device support

#### Planned Work

- **Bug Fixes**
  - Address Thrustmaster-specific issues
  - Fix template rendering problems
  - Resolve device detection edge cases

- **Field Mapping Refinement**
  - Complete any missing Thrustmaster field mappings
  - Verify button ranges for all Thrustmaster devices
  - Add support for additional Thrustmaster variants

- **Documentation**
  - Update user guide with Thrustmaster device usage
  - Add Thrustmaster-specific examples and workflows

---

## Future Considerations (Post 0.6.x)

These items are under consideration but not yet scheduled for specific versions:

### Additional Manufacturer Support
- Logitech devices (X52, X56, etc.)
- CH Products
- Honeycomb Aeronautical
- Other manufacturers based on community demand

### Feature Enhancements
- Profile comparison tool
- Import/export custom label sets
- Auto-update mechanism
- Linux/macOS support
- Multi-language support
- Cloud profile storage/sharing

### Advanced Features
- Profile conflict detection
- Duplicate binding warnings
- Recommended bindings for ship types
- Integration with Star Citizen API (if available)
- Custom device template creator (GUI tool)

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **0.X.0** - New device manufacturer support, major features
- **0.X.Y** - Bug fixes, refinements, minor features

### Patch Versions (.x)
Bug fixes, template completions, UI refinements, and other minor improvements that don't introduce new device manufacturers or breaking changes.

### Minor Versions (.X.0)
New device manufacturer support (VKB → Virpil → Thrustmaster), significant new features, or major UI overhauls.

### Major Versions (1.0.0+)
Reserved for production-ready release with comprehensive device support, stable API, and feature-complete status.

---

## Contributing to the Roadmap

Have suggestions for the roadmap? We welcome community input!

- **Device Requests:** Request support for specific devices via GitHub Issues
- **Feature Ideas:** Share your feature suggestions in our Discord community
- **Template Contributions:** Help create device templates for your hardware

Join our [Discord community](https://discord.gg/NRnFJCjZke) to participate in roadmap discussions!

---

## Roadmap Updates

This roadmap is a living document and will be updated as development progresses. Check back regularly for updates, or watch the repository for changes.

**Last Updated:** 2025-11-12
**Current Version:** 0.4.0
