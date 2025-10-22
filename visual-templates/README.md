# Visual Templates Directory

This directory contains device template images and their overlay files for the Star Citizen Profile Viewer.

## Directory Structure

```
visual-templates/
├── <device_full_name>/                 # Device subdirectory
│   ├── <device_full_name>_template.png # Template image with {{ }} tags
│   ├── <device_full_name>_clean.png    # Clean image without tags
│   └── <device_full_name>_overlay.svg  # SVG overlay file
├── template_registry.json              # Registry of all templates
└── README.md                           # This file
```

Example:
```
visual-templates/
├── vkb_gladiator_evo_right/
│   ├── vkb_gladiator_evo_right_template.png
│   ├── vkb_gladiator_evo_right_clean.png
│   └── vkb_gladiator_evo_right_overlay.svg
├── template_registry.json
└── README.md
```

## Naming Convention

All files for a device are stored in a subdirectory named `<device_full_name>/`:
- Use lowercase with underscores for spaces
- Example: `vkb_gladiator_evo_right/`

### Template Images (with tags)
- Format: `<device_full_name>/<device_full_name>_template.<ext>`
- Extension: `.png` or `.jpg`
- Contains visible `{{ Button X }}` template tags
- Used for reference and SVG overlay generation

Examples:
- `vkb_gladiator_evo_right/vkb_gladiator_evo_right_template.png`
- `vkb_gladiator_evo_left/vkb_gladiator_evo_left_template.png`
- `thrustmaster_t16000m/thrustmaster_t16000m_template.png`

### Clean Display Images (without tags)
- Format: `<device_full_name>/<device_full_name>_clean.<ext>`
- Extension: `.png` or `.jpg`
- Same as template but with template tags manually removed
- Used for display and export

Examples:
- `vkb_gladiator_evo_right/vkb_gladiator_evo_right_clean.png`
- `vkb_gladiator_evo_left/vkb_gladiator_evo_left_clean.png`
- `thrustmaster_t16000m/thrustmaster_t16000m_clean.png`

### Overlay Files
- Format: `<device_full_name>/<device_full_name>_overlay.svg`
- Generated from template image using OCR
- Stored in the same device subdirectory

Examples:
- `vkb_gladiator_evo_right/vkb_gladiator_evo_right_overlay.svg`
- `vkb_gladiator_evo_left/vkb_gladiator_evo_left_overlay.svg`
- `thrustmaster_t16000m/thrustmaster_t16000m_overlay.svg`

## Adding a New Device Template

### Step 1: Create Device Directory
```bash
mkdir visual-templates/<device_full_name>
```

Example: `mkdir visual-templates/thrustmaster_t16000m`

### Step 2: Prepare the Template Image
1. Find or create a high-quality image of the device
2. Add template tags to the image in the format `{{ Button X }}`, `{{ Hat 1 Up }}`, etc.
3. Use clear, readable font (Arial 10pt recommended)
4. Save as `visual-templates/<device_full_name>/<device_full_name>_template.png`

### Step 3: Generate the SVG Overlay
Run the SVG generator tool:
```bash
python generate_svg_overlay.py visual-templates/<device_full_name>/<device_full_name>_template.png
```

This will:
- Use OCR to detect all template tags in the image
- Generate `visual-templates/<device_full_name>/<device_full_name>_template_overlay.svg`
- Capture position and size constraints for each tag

### Step 4: Rename SVG Overlay
```bash
mv visual-templates/<device_full_name>/<device_full_name>_template_overlay.svg visual-templates/<device_full_name>/<device_full_name>_overlay.svg
```

### Step 5: Manual Refinement (Optional)
Edit the generated SVG file to adjust:
- Text positions (`x`, `y` attributes)
- Font size (`font-size` attribute)
- Text color (`fill` attribute)
- Max dimensions (`data-max-width`, `data-max-height`)

### Step 6: Create Clean Version
Create a clean version of the image without template tags:
- Open `<device_full_name>/<device_full_name>_template.png` in an image editor
- Erase or paint over all `{{ Button X }}` tags
- Save as `<device_full_name>/<device_full_name>_clean.png`

### Step 7: Register the Template
Add an entry to `template_registry.json`:
```json
{
  "id": "<device_id>",
  "name": "<Human Readable Name>",
  "image": "<device_full_name>/<device_full_name>_clean.png",
  "template_image": "<device_full_name>/<device_full_name>_template.png",
  "overlay": "<device_full_name>/<device_full_name>_overlay.svg",
  "device_match_patterns": [
    "Device Name Pattern 1",
    "Device Name Pattern 2"
  ],
  "type": "joystick",
  "buttons": {}
}
```

## Template Tag Format

Template tags are placeholders that get replaced with actual control bindings:

### Supported Formats:
- `{{ Button 1 }}` - Primary fire button
- `{{ Button 2 }}` - Secondary button
- `{{ Hat 1 Up }}` - Hat switch direction
- `{{ Hat 1 Down }}` - Hat switch direction
- `{{ Hat 1 Left }}` - Hat switch direction
- `{{ Hat 1 Right }}` - Hat switch direction

### Tag Requirements:
- Must be wrapped in double curly braces: `{{ }}`
- Can include spaces
- Case-insensitive
- Font size and width don't matter (OCR detects them all)

## SVG Overlay Format

Generated SVG overlays contain text elements with data attributes:

```xml
<text x="711.5" y="1846.5"
      font-family="Arial" font-size="10"
      fill="black" text-anchor="middle"
      data-confidence="0.78"
      data-max-width="255.0" data-max-height="53.0">
  {{ Button 1 }}
</text>
```

### Attributes:
- `x`, `y` - Text position (center point)
- `font-family` - Font to use
- `font-size` - Base font size (will auto-scale if needed)
- `fill` - Text color
- `text-anchor` - Alignment (usually "middle")
- `data-confidence` - OCR confidence score (0-1)
- `data-max-width`, `data-max-height` - Size constraints for text

## How It Works

1. **User loads a profile** → App detects VKB Gladiator EVO device
2. **App loads clean image** → Displays `vkb_gladiator_evo_right/vkb_gladiator_evo_right_clean.png`
3. **App loads overlay** → Reads `vkb_gladiator_evo_right/vkb_gladiator_evo_right_overlay.svg`
4. **App processes tags** → Replaces `{{ Button 1 }}` with user's action (e.g., "Primary Fire")
5. **App renders** → Shows device image with custom bindings overlaid (transparent background)

## Troubleshooting

### OCR Not Detecting Tags
- Ensure tags are in format `{{ Button X }}`
- Use clear, high-contrast text
- Avoid overly stylized fonts
- Make sure text is not rotated

### Text Overlapping or Misaligned
- Edit the SVG file manually
- Adjust `x` and `y` coordinates
- Increase `font-size` if too small
- Adjust `data-max-width` to constrain long text

### Template Not Loading
- Check `template_registry.json` syntax
- Verify file paths are correct
- Ensure device_match_patterns are accurate
- Check that image file exists

## Tips for Best Results

1. **High Resolution**: Use high-quality images (1920px+ width recommended)
2. **Clear Tags**: Make template tags easily readable
3. **Consistent Naming**: Follow the naming convention strictly
4. **Test OCR**: Run the generator and check results before manual editing
5. **Transparent Text**: SVG text is always transparent - no need to add backgrounds
