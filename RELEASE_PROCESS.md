# Release Process

This document outlines the standard process for creating a new release of SC Profile Viewer.

## Pre-Release Checklist

- [ ] All features for the release are complete and merged
- [ ] Tests pass (if applicable)
- [ ] Documentation is updated (USER_GUIDE.md, README.md)
- [ ] CHANGELOG.md has entries for all changes

## Release Steps

### 1. Prepare Release Branch

If working on a feature branch:
```bash
# Ensure branch is up to date
git checkout <feature-branch>
git pull origin <feature-branch>
```

### 2. Update Version Files

Update the following files with the new version number:

- `VERSION.TXT` - Update to new version (e.g., `0.2.0`)
- `CHANGELOG.md` - Move unreleased items to new version section with date
- `installer.iss` - Update `#define MyAppVersion "X.Y.Z"`

### 3. Clean Up Repository

- Remove temporary/scratch files and directories
- Update `.gitignore` if needed
- Stage documentation and utility files for commit

### 4. Build the Executable

```bash
.venv\Scripts\python.exe scripts/build/build_exe.py
```

Verify the build:
```bash
# Check that dist/SCProfileViewer.exe exists
dir dist\SCProfileViewer.exe
```

### 5. Create Release Commit

On the feature branch, commit all version updates:
```bash
git add VERSION.TXT CHANGELOG.md installer.iss [other-files]
git commit -m "Release vX.Y.Z - <Brief Description>"
```

### 6. Merge to Main

**Option A: Pull Request (Recommended)**
```bash
git push origin <feature-branch>
# Create PR on GitHub to merge into main
# After PR is approved and merged, proceed to step 7
```

**Option B: Direct Merge**
```bash
git checkout main
git merge <feature-branch>
git push origin main
```

### 7. Create Version Commit on Main

After merging, ensure version files are correct on main:
```bash
git checkout main
git pull origin main

# Verify VERSION.TXT, CHANGELOG.md, installer.iss are at correct version
# If not, update them and commit:
git add VERSION.TXT CHANGELOG.md installer.iss
git commit -m "Update version to X.Y.Z"
git push origin main
```

### 8. Create Git Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z - <Brief Description>"
git push origin vX.Y.Z
```

### 9. Build Installer (Optional)

```bash
cmd /c build_all.bat
```

This creates: `installer_output/SCProfileViewer-vX.Y.Z-Setup.exe`

### 10. Create GitHub Release

1. **Go to GitHub Release Page:**
   ```
   https://github.com/Osiris-RK/sc-profile-viewer/releases/new?tag=vX.Y.Z
   ```

2. **Fill in Release Information:**
   - **Tag:** vX.Y.Z (should be auto-selected)
   - **Release Title:** `SC Profile Viewer vX.Y.Z - <Brief Description>`
   - **Description:** Use the CHANGELOG.md content for this version (see template below)

3. **Attach Build Artifacts:**
   - Upload `installer_output/SCProfileViewer-vX.Y.Z-Setup.exe`
   - Upload `dist/SCProfileViewer.exe` (optional, as standalone)

4. **Publish Release**

## GitHub Release Notes Template

```markdown
# SC Profile Viewer vX.Y.Z - <Brief Description>

[1-2 sentence summary of the release]

## 🆕 What's New

### Added
- Feature 1
- Feature 2

### Changed
- Change 1
- Change 2

### Fixed
- Fix 1
- Fix 2

## 📥 Downloads

- **Installer:** [SCProfileViewer-vX.Y.Z-Setup.exe](link) - Recommended for most users
- **Standalone:** [SCProfileViewer.exe](link) - Portable version (no installation required)

## 📋 System Requirements

- Windows 10 or later (64-bit)
- No additional dependencies required

## 🐛 Known Issues

[List any known issues or limitations]

## 📝 Full Changelog

See [CHANGELOG.md](https://github.com/Osiris-RK/sc-profile-viewer/blob/main/CHANGELOG.md) for complete version history.

---

**First time using SC Profile Viewer?** Check out the [User Guide](https://github.com/Osiris-RK/sc-profile-viewer/blob/main/USER_GUIDE.md) to get started!
```

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0) - Incompatible API changes or major feature overhauls
- **MINOR** (0.X.0) - New functionality in a backward-compatible manner
- **PATCH** (0.0.X) - Backward-compatible bug fixes

## Post-Release

- [ ] Verify GitHub release is published
- [ ] Test installer download and installation
- [ ] Announce release (Discord, social media, etc.)
- [ ] Create new development branch for next version (if needed)
- [ ] Update CHANGELOG.md with new `[Unreleased]` section

## Troubleshooting

### Tag Already Exists
```bash
# Delete local tag
git tag -d vX.Y.Z

# Delete remote tag
git push --delete origin vX.Y.Z

# Recreate tag
git tag -a vX.Y.Z -m "Release vX.Y.Z - <Description>"
git push origin vX.Y.Z
```

### Version Mismatch
If version files don't match after merge, update them on main and create a new commit before tagging.

### Build Fails
Check `build\SCProfileViewer\warn-SCProfileViewer.txt` for warnings and errors.
