# Template Registry Schema (v0.4.0)

**Version:** 2.0 (PDF-based)
**Date:** 2025-01-08
**Status:** In Development

## Overview

The template registry (`visual-templates/template_registry.json`) defines all available device templates for SC Profile Viewer. In v0.4.0, the schema has been updated to support PDF-based templates with interactive form fields.

---

## Schema Version History

| Version | Format | Description |
|---------|--------|-------------|
| 1.0 | PNG+SVG | Original format (v0.1.0 - v0.3.0) |
| 2.0 | PDF | New PDF-based format (v0.4.0+) |

---

## JSON Structure

### Root Object

```json
{
  "schema_version": "2.0",
  "templates": [
    { /* template object */ },
    { /* template object */ },
    ...
  ]
}
```

**Fields:**
- `schema_version` (string, required): Schema version identifier
- `templates` (array, required): List of template objects

---

## Template Object (v2.0)

### Complete Example

```json
{
  "id": "vkb_gladiator_evo_right",
  "name": "VKB Gladiator EVO (Right)",
  "pdf": "vkb_gladiator_evo_right/vkb_gladiator_evo_right.pdf",
  "device_match_patterns": [
    "VKBsim Gladiator EVO R",
    "Gladiator EVO R"
  ],
  "type": "joystick",
  "manufacturer": "VKB",
  "button_count": 34,
  "axis_count": 6,
  "hat_count": 1,
  "default_joystick_index": null,
  "notes": "34 buttons, 6 axes, 1 POV hat"
}
```

### Field Definitions

#### Required Fields

**`id`** (string)
- Unique identifier for this template
- Format: lowercase, underscores, no spaces
- Examples: `vkb_gladiator_evo_right`, `vkb_f16_mfd`, `vkb_thq`

**`name`** (string)
- Human-readable display name
- Used in UI dropdowns and labels
- Examples: "VKB Gladiator EVO (Right)", "VKB F16 MFD"

**`pdf`** (string)
- Path to PDF template file (relative to `visual-templates/`)
- Format: `{device_id}/{device_id}.pdf`
- Example: `"vkb_gladiator_evo_right/vkb_gladiator_evo_right.pdf"`

**`device_match_patterns`** (array of strings)
- List of strings to match against SC profile device names
- Matching is case-insensitive substring matching
- More specific patterns should come first
- Examples:
  ```json
  [
    "VKBSim Gladiator EVO R",
    "Gladiator EVO R",
    "GEO R"
  ]
  ```

**`type`** (string)
- Device category
- Valid values:
  - `"joystick"` - Flight stick
  - `"throttle"` - Throttle quadrant
  - `"mfd"` - Multi-Function Display
  - `"pedals"` - Rudder pedals
  - `"gamepad"` - Game controller
  - `"other"` - Miscellaneous

#### Optional Fields

**`manufacturer`** (string)
- Device manufacturer name
- Examples: "VKB", "Thrustmaster", "Virpil", "Logitech"
- Used for filtering/grouping in UI

**`button_count`** (integer)
- Number of buttons on device
- Used for validation and documentation
- Example: `34` for VKB Gladiator EVO

**`axis_count`** (integer)
- Number of analog axes
- Examples: 6 (x, y, z, rotx, roty, rotz)

**`hat_count`** (integer)
- Number of hat switches (POV hats)
- Example: `1` or `2`

**`default_joystick_index`** (integer or null)
- Default joystick index for this device (1-9)
- Used when device appears alone in profile
- `null` = dynamic assignment based on profile device order
- Examples: `1` for primary stick, `2` for throttle, `null` for auto

**`notes`** (string)
- Additional information or special considerations
- Examples:
  - "34 buttons, 6 axes, 1 POV hat"
  - "Requires device splitter for SEM module"
  - "Left-hand variant"

**`deprecated`** (boolean, default: false)
- Mark template as deprecated (won't be used for new matches)
- Existing configurations still work
- Example: `true` for old template versions

**`indesign_source`** (string)
- Path to InDesign source file (.indd) for template maintenance
- Example: `"vkb_gladiator_evo_right/vkb_gladiator_evo_right.indd"`

---

## Complete Example Registry (v2.0)

```json
{
  "schema_version": "2.0",
  "templates": [
    {
      "id": "vkb_gladiator_evo_right",
      "name": "VKB Gladiator EVO (Right)",
      "pdf": "vkb_gladiator_evo_right/vkb_gladiator_evo_right.pdf",
      "device_match_patterns": [
        "VKBsim Gladiator EVO R",
        "Gladiator EVO R"
      ],
      "type": "joystick",
      "manufacturer": "VKB",
      "button_count": 34,
      "axis_count": 6,
      "hat_count": 1,
      "default_joystick_index": null,
      "notes": "Right-hand premium joystick with Kosmosima grip"
    },
    {
      "id": "vkb_f16_mfd",
      "name": "VKB F16 MFD",
      "pdf": "vkb_f16_mfd/vkb_f16_mfd.pdf",
      "device_match_patterns": [
        "F16 MFD",
        "VKB F16 MFD",
        "F-16 MFD"
      ],
      "type": "mfd",
      "manufacturer": "VKB",
      "button_count": 22,
      "axis_count": 0,
      "hat_count": 0,
      "default_joystick_index": null,
      "notes": "Multi-function display with 22 programmable buttons"
    },
    {
      "id": "vkb_thq",
      "name": "VKB Throttle Quadrant THQ",
      "pdf": "vkb_thq/vkb_thq.pdf",
      "device_match_patterns": [
        "VKB THQ",
        "VKB Throttle Quadrant",
        "Throttle Quadrant THQ",
        "GNX-THQ"
      ],
      "type": "throttle",
      "manufacturer": "VKB",
      "button_count": 8,
      "axis_count": 3,
      "hat_count": 1,
      "default_joystick_index": 2,
      "notes": "Throttle quadrant with 3 axes and 8 buttons"
    }
  ]
}
```

---

## Migration from v1.0 to v2.0

### Changes

**Removed Fields:**
- `image` - Replaced by PDF (image now embedded in PDF)
- `overlay` - Replaced by PDF form fields
- `buttons` - No longer needed (buttons defined by PDF field names)
- `button_range` - Replaced by `button_count`
- `template_image` - Deprecated

**Added Fields:**
- `schema_version` - Root level version identifier
- `pdf` - Path to PDF template
- `manufacturer` - Device manufacturer
- `button_count`, `axis_count`, `hat_count` - Input counts
- `default_joystick_index` - Default JS index
- `notes` - Additional information
- `deprecated` - Deprecation flag
- `indesign_source` - Source file path

**Unchanged Fields:**
- `id` - Same format
- `name` - Same format
- `device_match_patterns` - Same format
- `type` - Same format

### Migration Script

A migration script could convert v1.0 to v2.0:

```python
def migrate_v1_to_v2(old_registry):
    """Migrate template registry from v1.0 to v2.0"""
    new_registry = {
        "schema_version": "2.0",
        "templates": []
    }

    for template in old_registry["templates"]:
        new_template = {
            "id": template["id"],
            "name": template["name"],
            "pdf": f"{template['id']}/{template['id']}.pdf",  # Assumes PDF exists
            "device_match_patterns": template["device_match_patterns"],
            "type": template["type"],
            "manufacturer": extract_manufacturer(template["name"]),
            "button_count": extract_button_count(template.get("button_range")),
            "axis_count": None,  # Must be filled manually
            "hat_count": None,  # Must be filled manually
            "default_joystick_index": None,
            "notes": ""
        }

        new_registry["templates"].append(new_template)

    return new_registry
```

---

## Validation

### JSON Schema Validation

The registry can be validated using JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schema_version", "templates"],
  "properties": {
    "schema_version": {
      "type": "string",
      "enum": ["2.0"]
    },
    "templates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "pdf", "device_match_patterns", "type"],
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^[a-z0-9_]+$"
          },
          "name": {
            "type": "string",
            "minLength": 1
          },
          "pdf": {
            "type": "string",
            "pattern": "^[a-z0-9_/]+\\.pdf$"
          },
          "device_match_patterns": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1
            },
            "minItems": 1
          },
          "type": {
            "type": "string",
            "enum": ["joystick", "throttle", "mfd", "pedals", "gamepad", "other"]
          },
          "manufacturer": {
            "type": "string"
          },
          "button_count": {
            "type": "integer",
            "minimum": 0
          },
          "axis_count": {
            "type": "integer",
            "minimum": 0
          },
          "hat_count": {
            "type": "integer",
            "minimum": 0
          },
          "default_joystick_index": {
            "oneOf": [
              {"type": "integer", "minimum": 1, "maximum": 9},
              {"type": "null"}
            ]
          },
          "notes": {
            "type": "string"
          },
          "deprecated": {
            "type": "boolean"
          },
          "indesign_source": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

### Validation Checklist

- [ ] `schema_version` is "2.0"
- [ ] All required fields present for each template
- [ ] Template IDs are unique
- [ ] PDF files exist at specified paths
- [ ] PDF files have valid form fields (run validation script)
- [ ] Device match patterns are not empty
- [ ] Type is valid enum value
- [ ] Button/axis/hat counts are non-negative integers
- [ ] Default joystick index is 1-9 or null

---

## Device Matching Algorithm

### Matching Process

1. **Get device name from SC profile**
   - Example: `"VKBSim Gladiator EVO R"`

2. **Normalize device name**
   - Convert to lowercase
   - Trim whitespace

3. **Iterate through templates**
   - For each template, check `device_match_patterns`

4. **Match using substring search**
   - If any pattern (lowercase) is substring of device name (lowercase), match found

5. **Return first match**
   - Templates earlier in list have priority

### Example Matching

**Device Name:** `"VKBSim Gladiator EVO R"`

**Template Patterns:**
```json
{
  "device_match_patterns": [
    "VKBSim Gladiator EVO R",
    "Gladiator EVO R"
  ]
}
```

**Result:** Match! (exact match on first pattern)

**Device Name:** `"gladiator evo r"`

**Result:** Match! (case-insensitive substring match)

---

## Best Practices

### Pattern Ordering

**Good:**
```json
{
  "device_match_patterns": [
    "VKBSim Gladiator EVO R Omni",  // Most specific first
    "VKBSim Gladiator EVO R",
    "Gladiator EVO R",
    "GEO R"  // Least specific last
  ]
}
```

**Bad:**
```json
{
  "device_match_patterns": [
    "GEO",  // Too generic, matches many devices
    "VKBSim Gladiator EVO R"  // More specific pattern after generic
  ]
}
```

### Template Organization

**Group by manufacturer:**
```json
{
  "templates": [
    // VKB devices
    { "id": "vkb_gladiator_evo_right", ... },
    { "id": "vkb_gladiator_evo_left", ... },
    { "id": "vkb_f16_mfd", ... },
    { "id": "vkb_thq", ... },
    // Virpil devices
    { "id": "vpc_mt50cm3_right", ... },
    // Thrustmaster devices
    { "id": "thrustmaster_twcs_throttle", ... }
  ]
}
```

### Documentation

**Always include notes:**
```json
{
  "notes": "34 buttons (including hat), 6 axes (x/y/z/rotx/roty/rotz), 1 POV hat"
}
```

---

## Appendix

### Example Template Directory Structure

```
visual-templates/
├── template_registry.json          # Registry file (v2.0 schema)
├── vkb_gladiator_evo_right/
│   ├── vkb_gladiator_evo_right.pdf      # PDF template
│   └── vkb_gladiator_evo_right.indd     # InDesign source (optional)
├── vkb_f16_mfd/
│   ├── vkb_f16_mfd.pdf
│   └── vkb_f16_mfd.indd
└── vkb_thq/
    ├── vkb_thq.pdf
    └── vkb_thq.indd
```

### Schema Version History Details

**v1.0 (PNG+SVG):**
- Used separate PNG image and SVG overlay files
- SVG had template tags like `{{ Button 1 }}`
- Regex replacement for label population
- Complex template generation process

**v2.0 (PDF):**
- Single PDF file with embedded image
- Interactive form fields with SC-compatible names
- Direct field value assignment
- Simpler workflow using InDesign

---

## Version History

- **v2.0 (2025-01-08):** PDF-based schema for v0.4.0
  - Replaced PNG+SVG with PDF
  - Added schema_version field
  - Added manufacturer, button_count, axis_count, hat_count
  - Added default_joystick_index
  - Removed deprecated fields

- **v1.0 (2024-10-23):** Original PNG+SVG schema (v0.1.0 - v0.3.0)
  - Separate image and overlay files
  - Button ranges and manual mapping
