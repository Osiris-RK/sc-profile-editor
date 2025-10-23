# Star Citizen Profile Viewer - User Guide

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Main Features](#main-features)
- [Control Table Views](#control-table-views)
- [Customizing Labels](#customizing-labels)
- [Device Graphics](#device-graphics)
- [Exporting Your Profile](#exporting-your-profile)
- [Filters and Search](#filters-and-search)
- [Tips and Tricks](#tips-and-tricks)

---

## Introduction

The Star Citizen Profile Viewer is a tool that helps you view, customize, and export your Star Citizen control profiles in a human-readable format. It can generate visual diagrams of your controller layouts and export your bindings to various formats.

---

## Getting Started

### Importing a Profile

1. **Launch the application**
2. Click the **"Import Profile XML"** button (green button in the top-right)
3. Navigate to your Star Citizen profiles folder (usually `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Profiles\default`)
4. Select your exported profile XML file
5. Click **Open**

The application will automatically load the last profile you opened when you start it again.

### First Look

After importing a profile, you'll see:
- **Profile Summary**: Basic information about your profile in the top section
- **Control Table**: A detailed table of all your keybindings
- **Device Graphics Tab**: Visual representations of your controllers with labeled buttons

---

## Main Features

### Two Viewing Modes

The application offers two ways to view your control bindings:

#### Default View (Simplified)
- Shows only essential information: **Action Map**, **Action**, and **Device**
- Perfect for quick reference and printing
- Cleaner, more compact display

#### Detailed View (Complete)
- Shows all information including:
  - **Action Map**: The category of the action (e.g., "Spaceship Movement")
  - **Action (Original)**: The auto-generated action name
  - **Action (Override)**: Your custom label (if you've set one)
  - **Input Code**: The raw input code (e.g., "js1_button5")
  - **Input Label**: Human-readable input (e.g., "Joystick 1: Button 5")
  - **Device**: The device name

**To toggle between views:** Check/uncheck the **"Show Detailed"** checkbox in the Filters section.

---

## Control Table Views

### Understanding the Table

The control table displays all your keybindings organized by action map. Each row represents one binding.

**Default Columns:**
- **Action Map**: Category like "Spaceship Movement", "Spaceship Weapons", etc.
- **Action**: What the button does (e.g., "Fire", "Afterburner")
- **Device**: Which controller (e.g., "Keyboard", "Joystick 1")

**Detailed Columns (when "Show Detailed" is checked):**
- All default columns plus:
- **Action (Original)**: The auto-generated name from the game
- **Action (Override)**: Your custom short name
- **Input Code**: Technical identifier (e.g., "js1_button1")
- **Input Label**: Formatted input name (e.g., "Joystick 1: Button 1")

### Sorting

Click any column header to sort by that column. Click again to reverse the sort order.

---

## Customizing Labels

One of the most powerful features is the ability to create custom, shorter labels for actions to make your graphics more readable.

### How to Edit Labels

1. **Find the action** you want to rename in the Control Table
2. **Double-click** the cell in the "Action" column (or "Action (Override)" if in detailed view)
3. The text will be selected automatically
4. **Type your new label** (e.g., change "Missile Launch" to "ML")
5. Press **Enter** or click outside the cell to save

**Examples:**
- "Fire" → "F"
- "Afterburner" → "AB"
- "Target Cycle All Forward" → "Next Tgt"
- "Shield Raise Level Forward" → "Shld Fwd"

### Reverting Custom Labels

To remove a custom label and return to the auto-generated one:

1. **Double-click** the action label cell
2. **Select all text** (Ctrl+A) and **delete** it (or just press Delete since text is auto-selected)
3. Press **Enter**

The label will revert to either:
- The global default label (if one exists in `label_overrides.json`)
- The auto-generated label

### How Label Overrides Work

The application uses a two-tier label system:

1. **Global Defaults** (`label_overrides.json`)
   - Pre-configured short labels for 72 common Star Citizen actions
   - Shipped with the application
   - Examples: "v_attack1" → "Fire", "v_afterburner" → "Afterburner"

2. **Custom Overrides** (`label_overrides_custom.json`)
   - Your personal customizations
   - Created automatically when you edit your first label
   - Takes priority over global defaults
   - Not tracked in version control (your personal file)

**Priority Order:**
1. Your custom label (if you've edited it)
2. Global default label (if defined)
3. Auto-generated label (from the action name)

---

## Device Graphics

The **Device Graphics** tab shows visual representations of your controllers with your bindings labeled on them.

### Available Device Templates

The application includes templates for:
- VKB Gladiator EVO (Right Hand)
- VPC MongoosT-50CM3 Throttle (Right Hand)
- Keyboard layouts
- Mouse layouts
- And more...

### How Graphics Work

1. Switch to the **"Device Graphics"** tab
2. Select your device from the dropdown
3. The graphic will show:
   - Button/axis labels
   - Your custom action labels (if you've set them)
   - Color-coded legends

**Graphics automatically update** when you edit labels in the Control Table!

### Using Graphics

- **Zoom**: Use your mouse wheel to zoom in/out
- **Pan**: Click and drag to move around
- **Export**: Right-click on the graphic to save as an image

---

## Exporting Your Profile

You can export your profile in three formats:

### Export to CSV

**Best for:** Spreadsheets, further data processing

1. Click **"Export CSV"** button
2. Choose a location and filename
3. Click **Save**

The CSV will contain all visible rows from your current view (default or detailed).

**Opens in:** Excel, Google Sheets, LibreOffice Calc

### Export to PDF

**Best for:** Printing, sharing, archiving

1. Click **"Export PDF"** button
2. Choose a location and filename
3. Click **Save**

The PDF includes:
- Profile information
- Device list
- Full table of bindings (formatted for landscape orientation)

**Features:**
- Professional formatting
- Alternating row colors for readability
- Automatic page breaks

### Export to Word Document

**Best for:** Editing, custom formatting, documentation

1. Click **"Export Word"** button
2. Choose a location and filename
3. Click **Save**

The Word document includes:
- Title page with profile name
- Device information
- Formatted table of bindings
- Easy to customize and edit

**Opens in:** Microsoft Word, Google Docs, LibreOffice Writer

### Export Modes

All export formats respect the **"Show Detailed"** checkbox:
- **Unchecked**: Exports simplified view (3 columns)
- **Checked**: Exports detailed view (6 columns)

---

## Filters and Search

### Search Box

Type in the **Search** box to filter bindings by any text:
- Action names
- Device names
- Input labels
- Action maps

**Example searches:**
- "fire" - Shows all fire-related actions
- "joystick 1" - Shows all Joystick 1 bindings
- "shield" - Shows all shield controls

### Device Filter

Select a device from the **Device** dropdown to show only bindings for that device:
- All Devices (default)
- Keyboard
- Mouse
- Joystick 1
- Joystick 2
- etc.

### Action Map Filter

Filter by category using the **Action Map** dropdown:
- All Action Maps (default)
- Spaceship Movement
- Spaceship Weapons
- Spaceship Targeting
- Spaceship Mining
- etc.

### Hide Unmapped Keys

Check **"Hide Unmapped Keys"** to hide any inputs that don't have bindings assigned.

### Clear Filters

Click **"Clear Filters"** to reset all filters and show everything.

---

## Tips and Tricks

### Creating a Reference Card

1. **Customize labels** for your most important actions with short names
2. Switch to **Default View** (uncheck "Show Detailed")
3. **Filter** to show only one device (e.g., "Joystick 1")
4. **Export to PDF**
5. Print and keep next to your controller!

### Quick Label Editing

- Labels are **auto-selected** when you double-click, so you can immediately start typing
- Press **Delete** to clear a label completely (reverts to default)
- Press **Escape** while editing to cancel changes

### Understanding Your Setup

Use **Detailed View** to see:
- Which physical buttons are mapped (Input Code + Input Label)
- Original action names vs. your custom labels
- Device assignments at a glance

### Graphics Workflow

1. **First pass**: Use default labels to see what's mapped
2. **Customize**: Edit labels to short versions that fit in graphics
3. **Export graphics**: Switch to Device Graphics tab and export images
4. **Print**: Create a physical reference sheet

### Managing Multiple Profiles

The application remembers your last loaded profile and automatically opens it on startup. To switch profiles:
1. Click **"Import Profile XML"**
2. Select a different profile
3. Your custom labels are **saved globally** and will apply to matching actions in any profile

### Backup Your Custom Labels

Your custom labels are stored in `label_overrides_custom.json` in the application directory. To backup:
1. Locate the file in the application folder
2. Copy it to a safe location
3. To restore, just copy it back

---

## Example Workflow

### Scenario: Creating a HOTAS Reference Card

1. **Import** your Star Citizen profile
2. **Filter** to show only "Joystick 1" in the Device filter
3. **Edit labels** to create short versions:
   - "Target Cycle All Forward" → "Next"
   - "Target Cycle All Back" → "Prev"
   - "Missile Launch" → "MSL"
   - "Shield Raise Level Forward" → "Shld F"
4. **Switch to Device Graphics** tab
5. **Select** your joystick model
6. **Verify** the labels look good on the graphic
7. **Export** the graphic as an image
8. **Return to Control Table** and export to PDF
9. **Print** both the graphic and the PDF for reference

---

## Troubleshooting

### Table doesn't show after importing

- Toggle any checkbox (like "Show Detailed") to refresh the view
- This is a known issue that will be fixed in the next update

### Custom labels not appearing in graphics

- Make sure you pressed Enter after editing the label
- Switch tabs and back to refresh the graphics

### Can't edit a cell

- Make sure you're double-clicking the "Action" or "Action (Override)" column (column 2)
- Other columns are read-only

### Export buttons are disabled

- Make sure you've imported a profile first
- The buttons enable after a successful profile load

---

## Keyboard Shortcuts

Currently, the application uses standard Qt shortcuts:
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste (when editing)
- **Escape**: Cancel editing
- **Enter**: Save edit

---

## Getting Help

For issues, feature requests, or contributions:
- Visit: https://github.com/anthropics/claude-code/issues
- Report bugs with steps to reproduce
- Request new device templates
- Suggest improvements

---

## Version Information

This guide is for Star Citizen Profile Viewer v0.2

**New in v0.2:**
- Custom label override system
- Show Detailed view toggle
- Improved table editing with clean visual feedback
- Global and custom label override files
- Enhanced export formats with view mode support

---

**Happy Flying, Citizen!** o7
