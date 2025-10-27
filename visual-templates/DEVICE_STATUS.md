# Device Template Status

This document tracks the status of all device templates in the visual-templates directory.

## Completed Templates ✅

| Device | Directory | Status | Notes |
|--------|-----------|--------|-------|
| VKB Gladiator EVO Right | `vkb_gladiator_evo_right/` | ✅ Complete | Fully functional with config.json and SVG overlay |

## In Development 🚧

| Device | Directory | Status | Priority | Notes |
|--------|-----------|--------|----------|-------|
| VKB Gladiator EVO Left (SEM) | `vkb_gladiator_evo_left/` | 🚧 Planned | High | Left-hand version with Space Sim Module |
| Thrustmaster TWCS Throttle | `thrustmaster_twcs_throttle/` | 🚧 Planned | High | Popular budget throttle option |
| Virpil MongoosT-50CM3 Right | `vpc_mt50cm3_right/` | 🚧 Partial | Medium | Directory exists, needs completion |
| Virpil MongoosT-50CM3 Left | `vpc_mt50cm3_left/` | 🚧 Partial | Medium | Directory exists, needs completion |

## Planned (No Directory Yet) 📋

| Device | Priority | Notes |
|--------|----------|-------|
| Generic Keyboard | Low | Universal keyboard layout |
| Generic Mouse | Low | Universal mouse layout |

## Device Coverage by Profile

### layout_VirpilOCT25_exported.xml
- ✅ Keyboard (generic)
- ✅ Mouse (generic)
- 🚧 RIGHT VPC Stick MT-50CM3
- 🚧 LEFT VPC Stick MT-50CM3

### layout_HOTAS_exported.xml
- ✅ Keyboard (generic)
- ✅ Mouse (generic)
- ✅ VKB Gladiator EVO R (Right)
- 🚧 TWCS Throttle

### layout_Osiris-12-30-24_exported.xml
- ✅ Keyboard (generic)
- ✅ Mouse (generic)
- ✅ VKB Gladiator EVO R (Right)
- 🚧 VKB Gladiator EVO L SEM (Left)

### layout_KnMOCT25_exported.xml
- ✅ Keyboard (generic)
- ✅ Mouse (generic)
- 🚧 RIGHT VPC Stick MT-50CM3
- 🚧 LEFT VPC Stick MT-50CM3

## How to Create a New Template

See [CONFIG_README.md](CONFIG_README.md) for detailed instructions on creating device templates.

### Quick Checklist
1. Create directory: `visual-templates/{device_name}/`
2. Add high-resolution device photo: `{device_name}_template.png`
3. Create config.json with button coordinates
4. Generate SVG overlay: `python generate_svg_overlay.py`
5. Test with the application
6. Update template_registry.json

## Template Progress Tracking

**Total Devices Identified:** 6
- **Complete:** 1 (17%)
- **In Development:** 4 (67%)
- **Planned:** 1 (17%)

**Goal for v0.2.0:** Complete all 4 in-development templates

## Last Updated
2025-10-24 - Initial status document created
