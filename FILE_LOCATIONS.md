# File Locations - SC Profile Viewer

This document explains where different files are stored when running the application.

## File Storage Locations

### When Running from .EXE (Installed/Portable)

**Read-Only Files (Bundled with Application):**
- **Location:** Same folder as `SCProfileViewer.exe`
- **Files:**
  - `VERSION.TXT` - Application version number
  - `label_overrides.json` - Global default label overrides
  - `USER_GUIDE.md` - User documentation
  - `visual-templates/` - Device graphics templates
  - `example-profiles/` - Sample profiles
  - `assets/` - Icons and images

**User-Writable Files (Custom Settings):**
- **Location:** `%APPDATA%\SCProfileViewer\`
  - Windows path: `C:\Users\[YourName]\AppData\Roaming\SCProfileViewer\`
- **Files:**
  - `label_overrides_custom.json` - Your custom label edits
  - Future: settings, preferences, etc.

### When Running from Source (Development)

**All Files:**
- **Location:** Project root directory
- **Files:**
  - `label_overrides.json` - Global defaults
  - `label_overrides_custom.json` - Custom overrides
  - All other project files

---

## Custom Label Storage

When you edit a label in the application:

1. **First edit:** The app copies `label_overrides.json` → `label_overrides_custom.json`
2. **Your edit** is saved to `label_overrides_custom.json`
3. **All future edits** update `label_overrides_custom.json`

**Priority:** Custom labels always override global defaults

**Location when running as .exe:**
```
C:\Users\[YourName]\AppData\Roaming\SCProfileViewer\label_overrides_custom.json
```

---

## Why This Approach?

### Global Overrides (label_overrides.json)
- ✅ Shipped with the application
- ✅ Read-only (in Program Files or exe folder)
- ✅ Updated with app updates
- ✅ Provides good defaults for everyone

### Custom Overrides (label_overrides_custom.json)
- ✅ Stored in user's writable AppData folder
- ✅ Persists across app updates
- ✅ User-specific customizations
- ✅ No admin rights needed to modify

---

## Finding Your Custom Labels File

**Easy Method:**
1. Press `Win + R`
2. Type: `%APPDATA%\SCProfileViewer`
3. Press Enter
4. Look for `label_overrides_custom.json`

**Alternative:**
1. Open File Explorer
2. Navigate to: `C:\Users\[YourUsername]\AppData\Roaming\SCProfileViewer\`

---

## Backing Up Your Custom Labels

To backup your custom labels:

1. Navigate to `%APPDATA%\SCProfileViewer\`
2. Copy `label_overrides_custom.json`
3. Save it somewhere safe

To restore:
1. Copy the file back to `%APPDATA%\SCProfileViewer\`
2. Restart SC Profile Viewer

---

## Sharing Custom Labels

To share your custom labels with others:

1. Find your `label_overrides_custom.json` in `%APPDATA%\SCProfileViewer\`
2. Share the file
3. Others can place it in their `%APPDATA%\SCProfileViewer\` folder

---

## Troubleshooting

### "Can't save custom labels"
- Check that `%APPDATA%\SCProfileViewer\` folder exists
- The app should create it automatically
- Make sure you have write permissions to your AppData folder

### "Custom labels disappeared after update"
- Custom labels are stored in AppData and should persist
- Check `%APPDATA%\SCProfileViewer\label_overrides_custom.json`
- If missing, you may need to restore from backup

### "Want to reset all custom labels"
- Delete `label_overrides_custom.json` from `%APPDATA%\SCProfileViewer\`
- App will use global defaults again
