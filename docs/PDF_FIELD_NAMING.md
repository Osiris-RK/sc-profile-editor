# PDF Form Field Naming Convention

**Version:** v0.4.0
**Date:** 2025-01-08
**Status:** Standard for PDF-based device templates

## Overview

This document defines the standard naming convention for form fields in PDF device templates. Consistent field naming is critical because the application uses field names to map Star Citizen button/axis bindings to PDF form fields.

## Field Naming Format

### Standard Format

```
{js_id}_{input_type}{number}[_{direction}]
```

**Components:**
- `{js_id}`: Joystick index (js1, js2, js3, etc.)
- `{input_type}`: Type of input (button, hat, x, y, z, etc.)
- `{number}`: Button/axis number (1, 2, 3, etc.)
- `{direction}`: Optional direction for hat switches (up, down, left, right)

### Rules
- All lowercase
- No spaces
- Underscores separate components
- Numbers are sequential starting from 1

---

## Input Types and Examples

### Buttons

**Format:** `js{N}_button{M}`

**Examples:**
```
js1_button1     -> First button on joystick 1
js1_button2     -> Second button on joystick 1
js2_button15    -> 15th button on joystick 2
js3_button40    -> 40th button on joystick 3
```

**Star Citizen XML:**
```xml
<rebind input="js1_button1"/>
<rebind input="js2_button15"/>
```

**Usage:** Most common input type. Used for triggers, pushbuttons, toggles.

---

### Axes

**Format:** `js{N}_{axis_name}`

**Axis Names:**
- `x` - X-axis (horizontal)
- `y` - Y-axis (vertical)
- `z` - Z-axis (throttle/twist)
- `rotx` - Rotation X
- `roty` - Rotation Y
- `rotz` - Rotation Z

**Examples:**
```
js1_x       -> X-axis on joystick 1
js1_y       -> Y-axis on joystick 1
js1_z       -> Z-axis (throttle) on joystick 1
js1_rotx    -> Rotation X on joystick 1
js2_x       -> X-axis on joystick 2
```

**Star Citizen XML:**
```xml
<rebind input="js1_x"/>
<rebind input="js1_y"/>
<rebind input="js2_z"/>
```

**Usage:** Analog controls like stick movement, throttle, twist.

---

### Hat Switches

**Format:** `js{N}_hat{M}_{direction}`

**Directions:**
- `up`
- `down`
- `left`
- `right`

**Examples:**
```
js1_hat1_up      -> Hat 1 up on joystick 1
js1_hat1_down    -> Hat 1 down on joystick 1
js1_hat1_left    -> Hat 1 left on joystick 1
js1_hat1_right   -> Hat 1 right on joystick 1
js1_hat2_up      -> Hat 2 up on joystick 1
js2_hat1_up      -> Hat 1 up on joystick 2
```

**Star Citizen XML:**
```xml
<rebind input="js1_hat1_up"/>
<rebind input="js1_hat1_down"/>
```

**Usage:** POV hat/D-pad controls. Most devices have 1-2 hat switches.

---

### Sliders

**Format:** `js{N}_slider{M}`

**Examples:**
```
js1_slider1     -> First slider on joystick 1
js1_slider2     -> Second slider on joystick 1
js2_slider1     -> First slider on joystick 2
```

**Star Citizen XML:**
```xml
<rebind input="js1_slider1"/>
```

**Usage:** Linear analog controls (less common than axes).

---

## Complete Example: VKB Gladiator EVO

### Device Overview
- 34 buttons (button1 - button34)
- 6 axes (x, y, z, rotx, roty, rotz)
- 1 hat switch (hat1: up, down, left, right)

### All Field Names (if device is js1)

**Buttons:**
```
js1_button1, js1_button2, js1_button3, ..., js1_button34
```

**Axes:**
```
js1_x
js1_y
js1_z
js1_rotx
js1_roty
js1_rotz
```

**Hat Switch:**
```
js1_hat1_up
js1_hat1_down
js1_hat1_left
js1_hat1_right
```

**Total Fields:** 44 form fields

---

## Joystick Index Assignment

### Dynamic Mapping

Joystick indices (js1, js2, etc.) are assigned **dynamically** based on device order in the Star Citizen profile. The same physical device may be `js1` in one profile and `js3` in another.

### Example Profile

```xml
<devices>
  <joystick instance="1"/>  <!-- js1 -->
  <joystick instance="2"/>  <!-- js2 -->
  <joystick instance="3"/>  <!-- js3 -->
</devices>
<options type="joystick" instance="1" Product="VKBSim Gladiator EVO R"/>
<options type="joystick" instance="2" Product="VKB THQ"/>
<options type="joystick" instance="3" Product="VPC MT-50CM3"/>
```

**Result:**
- VKBSim Gladiator EVO R = **js1**
- VKB THQ = **js2**
- VPC MT-50CM3 = **js3**

### Device Mapper

The `DeviceJoystickMapper` utility class handles this dynamic mapping:

```python
from src.utils.device_joystick_mapper import DeviceJoystickMapper

mapper = DeviceJoystickMapper(profile)
js_index = mapper.get_js_index_for_device("VKBSim Gladiator EVO R")
# Returns: "js1" (in this profile)
```

---

## Creating PDF Templates in InDesign

### Step-by-Step Process

1. **Import Device Image**
   - Place device photo as background layer
   - Lock the layer

2. **Create Form Fields Layer**
   - New layer for text fields
   - One text field per button/control

3. **Position Fields**
   - Place text field over each button
   - Align to button center
   - Size appropriately for label text

4. **Name Fields**
   - Follow naming convention exactly
   - Use text field properties panel
   - Example: `js1_button1`

5. **Verify Field Names**
   - Use validation script (see below)
   - Check for typos/missing fields
   - Ensure all buttons covered

6. **Export as Interactive PDF**
   - File → Export → Adobe PDF (Interactive)
   - Enable: "Create Tagged PDF"
   - Enable: "Forms and Media: Include All"
   - Compression: High Quality

### Field Naming in InDesign

**Text Field Properties:**
- Name: `js1_button1` (exactly as shown)
- Value: (leave empty)
- Read Only: No
- Required: No
- Font: Embedded (Arial or Helvetica)
- Size: 8-10pt
- Alignment: Center

---

## Validation

### Field Naming Validation Script

Use the validation script to check PDF field names:

```bash
python scripts/validation/validate_pdf_fields.py template.pdf
```

**Checks:**
- Field names match convention
- No typos or case errors
- All expected fields present
- No duplicate field names
- Valid joystick index (js1-js9)
- Valid input types

### Common Mistakes

❌ **Wrong:**
```
JS1_button1      # Uppercase
js1_Button1      # Mixed case
js1-button1      # Hyphen instead of underscore
js1button1       # Missing underscore
js1_btn1         # Abbreviated
j1_button1       # Missing 's'
js_button1       # Missing number
button1          # Missing js prefix
```

✅ **Correct:**
```
js1_button1      # All lowercase, underscores, complete
```

---

## Template Development Workflow

### 1. Research Device

- Identify all physical buttons/controls
- Count buttons (button1 - buttonN)
- Identify axes (x, y, z, rotx, roty, rotz)
- Identify hat switches (hat1, hat2, etc.)
- Check manufacturer documentation

### 2. Create Field List

```
js1_button1
js1_button2
js1_button3
...
js1_x
js1_y
js1_hat1_up
```

### 3. Create PDF in InDesign

- Import device image
- Create text fields
- Name according to convention
- Position accurately

### 4. Validate

```bash
python scripts/validation/validate_pdf_fields.py my_device.pdf
```

### 5. Test

- Load in SC Profile Viewer
- Verify button labels appear correctly
- Test inline editing
- Check all buttons mapped

---

## Advanced Topics

### Multi-Instance Devices

Some devices appear multiple times in a profile (e.g., two VKB Gladiators):

```xml
<joystick instance="1" Product="VKBSim Gladiator EVO R"/>
<joystick instance="2" Product="VKBSim Gladiator EVO L"/>
```

**Same device, different instances:**
- Right stick uses `js1_*` fields
- Left stick uses `js2_*` fields

**Solution:** Create separate PDF templates or support multi-instance PDFs.

### Unmapped Buttons

Not all buttons need to be in the PDF. If a button doesn't have a form field:
- Application will skip it (no error)
- User won't see it in the visual representation
- Still visible in the table view

### Custom Field Naming

**Question:** Can I use custom names like "Trigger" instead of "js1_button1"?

**Answer:** No. Field names must match SC XML exactly. However, you can:
- Use PDF field descriptions for human-readable names
- Add static text labels near fields in PDF
- Application handles label display (not field names)

---

## Reference Tables

### Button Range by Device Type

| Device Type | Typical Button Range |
|-------------|---------------------|
| Basic Joystick | button1 - button16 |
| HOTAS Stick | button1 - button34 |
| Throttle | button1 - button40 |
| MFD Panel | button1 - button22 |
| Pedals | button1 - button8 |

### Axis Types

| Axis | Common Use | Range |
|------|-----------|-------|
| x | Stick left/right | -1.0 to 1.0 |
| y | Stick forward/back | -1.0 to 1.0 |
| z | Throttle or twist | -1.0 to 1.0 |
| rotx | Stick rotation X | -1.0 to 1.0 |
| roty | Stick rotation Y | -1.0 to 1.0 |
| rotz | Stick rotation Z | -1.0 to 1.0 |

---

## FAQs

**Q: Why not use button names like "Trigger" or "Fire"?**

A: Field names must match Star Citizen's XML format exactly. The application maps XML input codes (like `js1_button1`) to PDF fields by name.

**Q: Can I skip numbers (e.g., js1_button1, js1_button3, skip button2)?**

A: Yes. Only create fields for buttons that physically exist. Gaps are fine.

**Q: What if I make a typo in a field name?**

A: The field won't be populated. Use the validation script to catch typos.

**Q: Do I need fields for axes if the device has no analog controls?**

A: No. Only create fields for inputs that physically exist on the device.

**Q: Can one PDF support multiple joystick indices (js1, js2, etc.)?**

A: Not easily. Create separate PDFs for different joystick instances, or use field naming like `js1_button1` for the first instance.

---

## Tools and Scripts

### Validation Script

**Location:** `scripts/validation/validate_pdf_fields.py`

**Usage:**
```bash
python scripts/validation/validate_pdf_fields.py template.pdf
```

**Output:**
```
✓ Valid field name: js1_button1
✓ Valid field name: js1_button2
✗ Invalid field name: JS1_button3 (uppercase)
✗ Invalid field name: js1_btn4 (wrong format)

Summary:
  Valid fields: 38
  Invalid fields: 2
  Total fields: 40
```

### Field Name Generator

**Purpose:** Generate list of field names for a device

```python
# Example: Generate field names for VKB Gladiator EVO (js1)
buttons = [f"js1_button{i}" for i in range(1, 35)]
axes = ["js1_x", "js1_y", "js1_z", "js1_rotx", "js1_roty", "js1_rotz"]
hat = ["js1_hat1_up", "js1_hat1_down", "js1_hat1_left", "js1_hat1_right"]
all_fields = buttons + axes + hat
```

---

## Appendix

### Complete Field Name Examples

**VKB Gladiator EVO (js1):**
```
js1_button1, js1_button2, ..., js1_button34
js1_x, js1_y, js1_z, js1_rotx, js1_roty, js1_rotz
js1_hat1_up, js1_hat1_down, js1_hat1_left, js1_hat1_right
```

**VKB F16 MFD (js2):**
```
js2_button1, js2_button2, ..., js2_button22
```

**VKB THQ Throttle (js3):**
```
js3_button1, js3_button2, ..., js3_button8
js3_x, js3_y, js3_z
js3_hat1_up, js3_hat1_down, js3_hat1_left, js3_hat1_right
```

---

## Version History

- **v0.4.0 (2025-01-08):** Initial version for PDF migration
  - Defined standard field naming convention
  - Added validation guidelines
  - Included InDesign workflow
  - Created reference tables and examples
