# Button Remapping Feature Guide

## Overview

The SC Profile Editor now includes full button remapping functionality, allowing you to not only edit display labels but also remap controls to different buttons/inputs and export modified profiles for use in Star Citizen.

## New Features

### 1. Button Remapping
- Remap any action to a different button, axis, hat, or key
- Change activation modes (press, hold, double_tap, etc.)
- Support for all input types: joystick buttons, axes, hats, keyboard keys, mouse buttons

### 2. Input Detection
- "Listen for Input" feature detects button presses automatically
- Simply press the button you want to bind and it's detected instantly
- Works with joysticks, keyboards, and mice

### 3. XML Profile Export
- Save modified profiles as new XML files
- Choose "Save" to overwrite original or "Save As" for a new file
- Exported profiles can be used directly in Star Citizen

### 4. Conflict Detection
- Warns you if an input is already bound to another action
- Shows all existing bindings for that input
- Lets you proceed anyway (Star Citizen supports multiple actions per button)

## How to Use

### Method 1: Device View (PDF Click)

1. **Open the Device View tab**
   - Load a profile
   - Select a device from the dropdown
   - The PDF diagram shows all controls

2. **Click a button/control on the PDF**
   - A dialog appears with both label editing and remapping options

3. **Edit the Label** (optional)
   - Type a custom label in the "Custom Label" field
   - Or leave empty to use the default

4. **Remap the Button**
   - **Option A: Use Dropdowns**
     - Select Device Type (Joystick/Keyboard/Mouse)
     - Select Device Instance (1, 2, 3...)
     - Select Input Type (Button/Axis/Hat/Key)
     - Select Input Number
     - For Hats: Select Direction (up/down/left/right)

   - **Option B: Listen for Input**
     - Click "🎮 Listen for Input..."
     - Press the button/key you want to bind
     - The system automatically detects and fills in the values

5. **Set Activation Mode** (optional)
   - Choose press, hold, double_tap, tap, or (none)

6. **Click OK**
   - The binding is updated in memory
   - The PDF refreshes with the new label
   - A "💾 Save Profile" button appears

### Method 2: Controls Table (Right-Click)

1. **Go to the Controls Table tab**

2. **Right-click on any row**
   - Context menu appears

3. **Choose an option:**
   - **"🎮 Remap Button..."** - Opens full remapping dialog
   - **"✏️ Edit Label..."** - Quick label edit only

4. **Follow the same steps as Device View**

### Saving Your Changes

When you make any changes (remapping or label edits), the window title shows an asterisk (*) and a blue "💾 Save Profile" button appears.

1. **Click "💾 Save Profile"**

2. **Choose Save Method:**
   - **Save** - Overwrites the original XML file
   - **Save As** - Creates a new XML file with your changes
   - **Cancel** - Don't save

3. **Success!**
   - Profile is saved to disk
   - The asterisk (*) disappears from the title
   - Your changes are preserved

## Features in Detail

### Input Types Supported

- **Joystick Buttons**: `js1_button1`, `js2_button32`, etc.
- **Joystick Axes**: `js1_x`, `js1_y`, `js1_z`, `js1_rotx`, `js1_roty`, `js1_rotz`, `js1_slider1`, etc.
- **Joystick Hats**: `js1_hat1_up`, `js1_hat1_down`, `js1_hat1_left`, `js1_hat1_right`
- **Keyboard Keys**: `kb1_space`, `kb1_lshift`, `kb1_a`, etc.
- **Mouse Buttons**: `mouse1`, `mouse2`, `mouse3`
- **Mouse Wheel**: `mwheel_up`, `mwheel_down`
- **Unbound**: Remove a binding completely

### Activation Modes

- **press** - Activate on button press (default)
- **release** - Activate on button release
- **hold** - Activate while button is held
- **double_tap** - Activate on double-tap
- **tap** - Activate on quick tap
- **(none)** - No specific activation mode

### Conflict Handling

When you remap to an input that's already in use, you'll see a warning:

```
The input 'js1_button10' is already bound to:

  • Fire Weapon (spaceship_weapons)
  • Drop Cargo (spaceship_general)

Do you want to continue anyway?
```

- **Yes** - Proceed with the remapping (both actions will be on the same button)
- **No** - Cancel and choose a different input

This is intentional - Star Citizen supports multiple actions per button, which is useful for context-sensitive controls.

## Technical Details

### Files Added/Modified

**New Files:**
- `src/utils/input_detector.py` - Input detection using pygame
- `src/utils/input_validator.py` - Input code validation and parsing
- `src/gui/remap_dialog.py` - Remapping dialog UI
- `src/exporters/xml_exporter.py` - XML profile writer

**Modified Files:**
- `src/models/profile_model.py` - Added `is_modified` flag and `source_xml_path`
- `src/parser/xml_parser.py` - Store source XML path
- `src/gui/main_window.py` - Added context menu, save button, profile modified handler
- `src/gui/qtpdf_device_widget.py` - Use remapping dialog instead of simple input
- `requirements.txt` - Added pygame dependency

### Data Model Changes

The `ControlProfile` class now includes:
- `is_modified: bool` - Tracks unsaved changes
- `source_xml_path: str` - Path to original XML file
- `mark_modified()` - Mark as having unsaved changes
- `mark_saved()` - Mark as saved

The `ActionBinding` class uses:
- `input_code: str` - The bound input (e.g., "js1_button5")
- `activation_mode: str` - How it activates (press/hold/etc.)
- `custom_label: str` - User's custom display label

### XML Export Process

1. Load original XML file (to preserve structure)
2. Update only `<rebind>` elements with modified bindings
3. Preserve all other elements (devices, categories, options, modifiers)
4. Write formatted XML with proper indentation
5. Exported file is fully compatible with Star Citizen

### Input Detection Process

1. User clicks "Listen for Input" button
2. PyGame initializes all connected devices
3. Thread monitors for any input events (30 FPS polling)
4. First detected input is captured
5. Input code is formatted and displayed
6. Thread stops and dialog is updated

## Troubleshooting

### "No input detected" Message
- Make sure your controller is connected
- Try pressing a different button
- Check that PyGame can see your device (check logs)
- Timeout is 10 seconds - click Listen again if needed

### Exported Profile Doesn't Work in Star Citizen
- Make sure you saved to the correct location
- Star Citizen profiles are usually in: `Documents\StarCitizen\USER\Controls\Mappings`
- Backup your original profile before overwriting
- Check the log file for export errors

### Changes Not Reflected in Game
- After saving, you need to select the profile in Star Citizen settings
- Restart Star Citizen if profile doesn't appear
- Clear shader cache if experiencing issues

### Context Menu Doesn't Appear
- Make sure you're right-clicking on a table row (not empty space)
- Check that a profile is loaded
- Try clicking on different columns

## Tips and Best Practices

1. **Always Backup** - Keep a copy of your original profile before making changes

2. **Use Save As First** - When testing, use "Save As" to create a new file instead of overwriting

3. **Test in Arena Commander** - Test your new bindings in Arena Commander before using in persistent universe

4. **Document Your Changes** - Use custom labels to note what you've changed

5. **Check for Conflicts** - If something isn't working, check if the same button has multiple bindings

6. **Export Often** - Save your work frequently, especially before making major changes

7. **Use Listen for Input** - It's faster and more accurate than manually selecting from dropdowns

## Examples

### Example 1: Swap Weapon Groups

Original:
- Button 1 → Weapon Group 1
- Button 2 → Weapon Group 2

Change to:
- Button 1 → Weapon Group 2
- Button 2 → Weapon Group 1

Steps:
1. Right-click Weapon Group 1 binding → Remap Button
2. Click "Listen for Input" → Press Button 2
3. Click OK
4. Right-click Weapon Group 2 binding → Remap Button
5. Click "Listen for Input" → Press Button 1
6. Click OK
7. Click "💾 Save Profile" → Save As → `my_swapped_weapons.xml`

### Example 2: Move Landing Gear to Different Device

Original:
- Landing Gear on Joystick 1, Button 10

Change to:
- Landing Gear on Joystick 2, Button 5

Steps:
1. Find "Toggle Landing Gear" in table
2. Right-click → Remap Button
3. Change Device Instance to 2
4. Change Button Number to 5
5. Click OK
6. Save Profile

### Example 3: Add Keyboard Shortcut for Existing Joystick Binding

Note: This creates a duplicate binding (same action, multiple inputs)

Original:
- Fire Weapons on js1_button1

Add:
- Fire Weapons also on Space key

Steps:
1. Find "Fire Weapons" binding
2. Note the action name (e.g., "v_attack_group1")
3. Find another binding for the same action (or create manually)
4. Right-click → Remap Button
5. Device Type: Keyboard
6. Input Type: Key
7. Manually type: space
8. Click OK
9. Save Profile

## Dependencies

- **PyGame 2.5.0+** - Required for input detection
- **PyQt6 6.10.0+** - GUI framework
- **PyMuPDF 1.26.0+** - PDF manipulation

All dependencies are listed in `requirements.txt` and will be installed with:
```bash
pip install -r requirements.txt
```

## Support

If you encounter issues:
1. Check the log output in the terminal
2. Verify all dependencies are installed
3. Test with a fresh copy of your profile
4. Report bugs with log files and steps to reproduce
