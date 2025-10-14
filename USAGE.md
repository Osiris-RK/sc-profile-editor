# Star Citizen Profile Viewer - Usage Guide

## Getting Started

### First Time Setup
1. Open a terminal in the project directory
2. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

### Importing a Profile
1. Click the **"Import Profile XML"** button in the top-right corner
2. Navigate to your Star Citizen profile location:
   - Default location: `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Controls\Mappings`
   - Or use the example profiles in the `example-profiles/` folder
3. Select your exported profile XML file (e.g., `layout_YourName_exported.xml`)
4. Click **"Open"**

### Understanding the Display

#### Profile Summary (Top Section)
Shows an overview of your profile:
- Profile name
- Number and types of devices detected
- Total number of action maps and bindings
- Categories defined in the profile

#### Controls Table (Main Section)
Displays all your control bindings with the following columns:

- **Action Map**: The category of actions (e.g., "Spaceship Movement", "Player Choice")
- **Action**: The specific action (e.g., "View Pitch", "Afterburner")
- **Input Code**: The raw technical input code from the XML (e.g., `kb1_down`, `js1_button5`)
- **Input Label**: Human-readable translation (e.g., "Keyboard: Down Arrow", "Joystick 1: Button 5")
- **Device**: The specific device name (e.g., "VKBsim Gladiator EVO R", "Keyboard", "Mouse")

### Navigating the Table

**Scroll**: Use mouse wheel or scrollbar to browse all bindings

**Resize Columns**: Drag column separators in the header

**Select Rows**: Click to select individual bindings

**Native Features** (PyQt6 provides these automatically):
- Click and drag to select multiple rows
- Ctrl+C to copy selected rows
- Ctrl+F to search (if enabled in future updates)

## Example Profiles

The project includes 15 example profiles in `example-profiles/`:
- Various VKB Gladiator EVO configurations
- BLANK profile (template with no bindings)
- Different gameplay-focused setups (Nav, Combat, Salvage)

Try importing these to see how the tool works!

## Tips

### Finding Your Star Citizen Profiles
1. In Star Citizen, go to Options > Keybindings
2. Make changes to your controls
3. Click **"Control Profiles"** at the bottom
4. Click **"Export Control Settings"**
5. Your profile is now in: `USER\Client\0\Controls\Mappings\`

### Understanding Input Codes

**Keyboard Format**: `kb1_[key]`
- Example: `kb1_space` = Spacebar
- Example: `kb1_f1` = F1 key
- Example: `kb1_lshift` = Left Shift

**Joystick Format**: `js[instance]_[input]`
- Example: `js1_button5` = Joystick 1, Button 5
- Example: `js1_hat1_up` = Joystick 1, Hat 1, Up direction
- Example: `js2_button12` = Joystick 2, Button 12

**Mouse Format**: `kb1_mouse[button]`
- Example: `kb1_mouse1` = Left mouse button
- Example: `kb1_mouse4` = Mouse button 4 (side button)

### Device Detection

The tool automatically:
- Identifies VKB Gladiator EVOs by product ID
- Differentiates between left and right sticks
- Shows human-readable device names in the table
- Groups bindings by device type

## Troubleshooting

### "Failed to parse XML file"
- Make sure you're selecting a valid Star Citizen profile XML
- Check that the file isn't corrupted
- Try exporting a fresh profile from Star Citizen

### "File not found"
- Verify the file path is correct
- Make sure the file wasn't moved or deleted
- Check file permissions

### Application won't start
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.12+)

### Empty table after import
- This is normal if your profile has no custom bindings yet
- Try importing a different profile
- Check the Profile Summary to confirm the file was read correctly

## Coming Soon

- Label editing to customize action names
- Table filtering by device or action map
- Export to PDF, Word, and CSV
- Graphical device maps with annotations
- Searchable control table

## Getting Help

- Check PROJECT_STATUS.md for current features and limitations
- Review PLAN.md for the development roadmap
- Report issues on GitHub (if published)
