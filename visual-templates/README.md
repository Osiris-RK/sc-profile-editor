# Visual Templates Directory

This directory contains device templates for displaying controller/joystick graphics with labeled controls in the SC Profile Viewer.

## Quick Start

**Creating a new device template:**

1. Place device PNG image in `YOUR_DEVICE_ID/your_device_id.png`
2. Create editable overlay:
   ```bash
   python visual-templates/embed_image_in_svg.py \
       visual-templates/YOUR_DEVICE_ID/your_device_id.png \
       visual-templates/YOUR_DEVICE_ID/your_device_id_overlay.svg
   ```
3. Open overlay in IDE and add button labels
4. Add entry to `template_registry.json`
5. Test in app

**See [CREATING_DEVICE_TEMPLATES.md](CREATING_DEVICE_TEMPLATES.md) for detailed instructions.**

## Directory Structure

```
visual-templates/
├── README.md                           # This file
├── CREATING_DEVICE_TEMPLATES.md       # Complete guide for creating templates
├── OVERLAY_CONVERSION.md              # Deprecated conversion workflow (kept for reference)
├── template_registry.json             # Device template configuration
├── embed_image_in_svg.py              # Script: Create editable SVG with embedded PNG
├── convert_inkscape_overlay.py        # Script: Convert Inkscape SVG (deprecated)
├── rescale_overlay.py                 # Script: Rescale SVG dimensions
├── vkb_gladiator_evo_left/           # VKB Gladiator EVO Left stick template
│   ├── vkb_gladiator_evo_left.png
│   └── vkb_gladiator_evo_left_overlay.svg
├── vkb_gladiator_evo_right/          # VKB Gladiator EVO Right stick template
│   ├── vkb_gladiator_evo_right.png
│   └── vkb_gladiator_evo_right_overlay.svg
├── vkb_sem/                           # VKB SEM module template
│   ├── vkb_sem.png
│   └── vkb_sem_overlay.svg
└── vpc_mt50cm3_right/                # VPC MongoosT-50CM3 throttle template
    ├── vpc_mt50cm3_right.png
    └── vpc_mt50cm3_right_template_overlay.svg
```

## Template Components

Each device template consists of:

1. **PNG Image** (`device_id.png`)
   - Photo or render of the device
   - Shows button/control locations
   - Recommended: 3000+ pixels wide

2. **SVG Overlay** (`device_id_overlay.svg`)
   - Text labels positioned over buttons
   - Contains embedded PNG for easy editing in IDEs
   - Template tags: `{{ Button 1 }}`, `{{ Hat Up }}`, etc.
   - File size: ~3-5 MB (due to embedded image)

3. **Registry Entry** (in `template_registry.json`)
   - Links device to its files
   - Defines device match patterns
   - Specifies button ranges for split devices

## Template Registry

The `template_registry.json` file contains configuration for all device templates:

```json
{
  "templates": [
    {
      "id": "device_id",
      "name": "Display Name",
      "image": "device_id/device_id.png",
      "template_image": "device_id/device_id.png",
      "overlay": "device_id/device_id_overlay.svg",
      "device_match_patterns": ["Device Name Pattern"],
      "type": "joystick",
      "buttons": {},
      "button_range": [1, 32]
    }
  ]
}
```

## SVG Overlay Format

Overlays use embedded PNG images for editing convenience. The app automatically:
- Loads the PNG separately as background
- Extracts `<rect>` and `<text>` elements from the SVG
- Ignores the embedded `<image>` element

**Template tag format:**
```xml
<g>
    <rect x="100" y="200" width="400" height="60"
          fill="white" fill-opacity="0"
          stroke="black" stroke-width="2" />
    <text x="105" y="240" font-size="46"
          fill="black" stroke="white" stroke-width="2">{{ Button 1 }}</text>
</g>
```

**Supported template tags:**
- Buttons: `{{ Button N }}`
- HAT switches: `{{ Hat 1 Up }}`, `{{ Hat 1 Down }}`, etc.
- Axes: `{{ X Axis }}`, `{{ Y Axis }}`, `{{ Z Rotation }}`
- Sliders: `{{ Slider 1 }}`

## Scripts

### embed_image_in_svg.py

Creates an editable SVG with embedded PNG image.

```bash
python visual-templates/embed_image_in_svg.py PNG_FILE OUTPUT_SVG [--overlay EXISTING_SVG]
```

**Use cases:**
- Create new overlay from scratch
- Regenerate overlay while preserving existing labels
- Create IDE-friendly editable overlays

### rescale_overlay.py

Rescales SVG dimensions to match target image size.

```bash
python visual-templates/rescale_overlay.py INPUT_SVG OUTPUT_SVG WIDTH HEIGHT
```

**Use case:** Fix dimension mismatches between overlay and image

### convert_inkscape_overlay.py (Deprecated)

Converts Inkscape SVG to simplified format. No longer needed - use embedded SVGs directly.

## Device Match Patterns

Templates are matched to devices using patterns from the Star Citizen profile XML:

```xml
<device Product="VKBsim Gladiator EVO R" ... />
```

Add multiple patterns to match variations:
```json
"device_match_patterns": [
  "VKBsim Gladiator EVO R",
  "Gladiator EVO R",
  "VKB Gladiator EVO Right"
]
```

## Split Devices

Some devices appear as one device in Star Citizen but need separate templates:

**Example: VKB Gladiator with SEM module**
- Reports as single device: "VKBsim Gladiator EVO L + SEM"
- Uses buttons 1-40 (base stick) and 41-64 (SEM module)

**Solution:** Create two templates with button ranges:
```json
{
  "id": "vkb_gladiator_evo_left",
  "button_range": [1, 40],
  ...
},
{
  "id": "vkb_sem",
  "button_range": [41, 64],
  ...
}
```

The app automatically splits bindings based on button ranges.

## Current Templates

| Device | ID | Buttons | Status |
|--------|-----|---------|--------|
| VKB Gladiator EVO Left | vkb_gladiator_evo_left | 1-40 | ✅ Complete |
| VKB SEM Module | vkb_sem | 41-64 | ✅ Complete |
| VKB Gladiator EVO Right | vkb_gladiator_evo_right | 1-40 | ✅ Complete |
| VPC MongoosT-50CM3 Right | vpc_mt50cm3_right | All | ✅ Complete |

## Adding New Templates

**Priority devices to add:**
- Thrustmaster Warthog (stick + throttle)
- Thrustmaster T.16000M
- Logitech X52/X56
- Virpil WarBRD/VPC Constellation
- MFG Crosswind pedals
- VKB Gunfighter/MCG grip variants

**Contribution workflow:**
1. Create template following [CREATING_DEVICE_TEMPLATES.md](CREATING_DEVICE_TEMPLATES.md)
2. Test with real Star Citizen profile
3. Verify all buttons/controls map correctly
4. Submit pull request with:
   - Device image (PNG)
   - Overlay with embedded image (SVG)
   - Registry entry
   - Test results

## Troubleshooting

**Device doesn't appear in dropdown:**
- Check device name in Star Citizen XML profile
- Verify `device_match_patterns` includes exact name
- Check app logs for template loading errors

**Labels mispositioned:**
- Open overlay in IDE
- Adjust `rect` and `text` x/y coordinates
- Save and restart app

**Template tags not replaced:**
- Verify tag format: `{{ Button N }}` (spaces required)
- Check tag matches app's input label format
- See `src/parser/label_generator.py` for label formats

## IDE Support

**Recommended IDEs for editing overlays:**
- ✅ Visual Studio Code (with SVG preview extension)
- ✅ PyCharm Professional (built-in SVG preview)
- ✅ Inkscape (full SVG editor)
- ✅ Any text editor with SVG preview

The embedded PNG image allows you to see button positions while editing text labels.

## Documentation

- **[CREATING_DEVICE_TEMPLATES.md](CREATING_DEVICE_TEMPLATES.md)** - Complete guide for creating new templates
- **[OVERLAY_CONVERSION.md](OVERLAY_CONVERSION.md)** - Deprecated conversion workflow (reference only)

## Related Code

- `src/graphics/template_manager.py` - Template loading and matching
- `src/gui/device_graphics.py` - SVG rendering and display
- `src/utils/device_splitter.py` - Split device logic (VKB Gladiator + SEM)
- `src/parser/label_generator.py` - Input label generation
