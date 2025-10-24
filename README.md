# Star Citizen Profile Viewer

A desktop application for converting Star Citizen control profile XML files into human-readable formats (PDF, Word, CSV) with annotated device graphics.

> **Note:** This README is for developers. For end-user documentation, see [USER_GUIDE.md](USER_GUIDE.md).

## Features

- Import Star Citizen XML control profiles
- Generate human-readable control mapping tables
- Create annotated device graphics (VKB Gladiator EVO, and more)
- Export to multiple formats: PDF, Word, CSV, PNG
- Edit control labels with persistent custom overrides
- Support for keyboard, mouse, and HOTAS devices
- SVG-based template system for device graphics
- Filter and search control bindings
- Auto-save last opened profile

## Project Structure

```
sc-profile-viewer/
├── src/                        # Source code
│   ├── main.py                # Application entry point
│   ├── gui/                   # GUI components (PyQt6)
│   │   ├── main_window.py    # Main application window
│   │   └── device_graphics.py # Device visualization widget
│   ├── parser/                # XML parsing and label generation
│   │   ├── xml_parser.py     # SC profile XML parser
│   │   └── label_generator.py # Human-readable label generator
│   ├── exporters/             # Export modules
│   │   ├── csv_exporter.py   # CSV export
│   │   ├── pdf_exporter.py   # PDF export
│   │   ├── word_exporter.py  # Word document export
│   │   └── graphic_exporter.py # Graphics export
│   ├── graphics/              # Graphics and template management
│   │   ├── template_manager.py # Device template loader
│   │   └── svg_generator.py   # SVG overlay generation
│   ├── models/                # Data models
│   │   └── profile_model.py  # Control profile data structures
│   └── utils/                 # Utilities
│       ├── settings.py       # Application settings persistence
│       ├── label_overrides.py # Custom label override manager
│       └── version.py        # Version management utilities
├── scripts/                    # Build and utility scripts
│   └── build/                 # Build scripts
│       ├── build_exe.py      # Standard build (no OCR)
│       └── build_exe_with_ocr.py # Build with OCR support
├── visual-templates/          # Device graphics templates
├── example-profiles/          # Sample SC profile XML files
├── assets/                    # Application assets (icons, images)
├── tests/                     # Unit tests
├── label_overrides.json       # Global label overrides
├── VERSION.TXT                # Current version number
├── CHANGELOG.md               # Version history and changes
└── USER_GUIDE.md              # End-user documentation
```

## Setup for Development

### Prerequisites
- Python 3.12 or higher
- Git (for version control)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sc-profile-viewer
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode
```bash
python -m src.main
```

Or directly:
```bash
python src/main.py
```

## Version Management

The project uses [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

### Current Version
The current version is stored in `VERSION.TXT` and is displayed in:
- Window title
- Main application header
- Help dialog

### Version Utilities
Located in `src/utils/version.py`:
- `get_version()` - Get current version
- `increment_version(version, type)` - Increment major/minor/patch
- `set_version(version)` - Update VERSION.TXT

### Updating the Version
You can update the version manually by editing `VERSION.TXT`, or use the build scripts with the `--increment` flag (see Building section below).

## Building Executables

The project includes two build configurations:

### 1. Standard Build (Recommended for End Users)
For most users, excludes OCR dependencies for faster startup and smaller file size.

```bash
# Build without version increment
python scripts/build/build_exe.py

# Build and increment patch version (0.1.0 -> 0.1.1)
python scripts/build/build_exe.py --increment patch

# Build and increment minor version (0.1.0 -> 0.2.0)
python scripts/build/build_exe.py --increment minor

# Build and increment major version (0.1.0 -> 1.0.0)
python scripts/build/build_exe.py --increment major
```

**Output:** `dist/SCProfileViewer.exe`

### 2. OCR-Enabled Build (For Template Developers)
Includes PyTorch, EasyOCR, and OpenCV for creating new device templates.

```bash
# Build without version increment
python scripts/build/build_exe_with_ocr.py

# Build with version increment
python scripts/build/build_exe_with_ocr.py --increment patch
```

**Output:** `dist/SCProfileViewer-WithOCR.exe`

### Version Increment Guidelines

- **Patch** (`--increment patch`): Bug fixes, minor tweaks ui tweaks, no new features
- **Minor** (`--increment minor`): New features, additional device support backward-compatible changes
- **Major** (`--increment major`): Breaking changes, major rewrites

### Build Process Details

The build scripts:
1. Display current version or increment if requested
2. Clean previous build artifacts
3. Bundle all required files (templates, assets, etc.)
4. Create standalone executable using PyInstaller
5. Place output in `dist/` directory

**Important Files Bundled:**
- `VERSION.TXT` - Version number
- `label_overrides.json` - Global label mappings
- `USER_GUIDE.md` - User documentation
- `assets/` - Icons and images
- `visual-templates/` - Device templates
- `example-profiles/` - Sample profiles

## Creating Installer Packages

> **TODO:** Document installer creation process when implemented

For distribution, you may want to create installer packages:
- Windows: Use NSIS, Inno Setup, or WiX
- macOS: Create .dmg or .pkg
- Linux: Create .deb, .rpm, or AppImage

## Testing

Run unit tests:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest --cov=src tests/
```

## Release Process

1. **Update CHANGELOG.md**
   - Move changes from `[Unreleased]` to a new version section
   - Add release date
   - Create new empty `[Unreleased]` section

2. **Build with version increment**
   ```bash
   python scripts/build/build_exe.py --increment minor
   ```

3. **Test the executable**
   - Run `dist/SCProfileViewer.exe`
   - Verify version displays correctly
   - Test all major features

4. **Create Git tag**
   ```bash
   git add VERSION.TXT CHANGELOG.md
   git commit -m "Release vX.Y.Z"
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   git push origin main --tags
   ```

5. **Publish release**
   - Create GitHub release with the tag
   - Upload executable from `dist/`
   - Copy changelog section to release notes

## Development Workflow

### Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes
3. Update tests
4. Add entry to CHANGELOG.md under `[Unreleased]`
5. Submit pull request

### Bug Fixes
1. Create bugfix branch: `git checkout -b bugfix/issue-name`
2. Fix the issue
3. Add tests to prevent regression
4. Update CHANGELOG.md
5. Submit pull request

## Technology Stack

- **Python 3.12+** - Programming language
- **PyQt6** - GUI framework
- **python-docx** - Word document generation
- **reportlab** - PDF generation
- **Pillow** - Image processing
- **PyInstaller** - Executable packaging
- **pytest** - Testing framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Update documentation
6. Submit pull request

## Troubleshooting

### Build Issues
- **Permission Error:** Close any running instances of the application
- **Import Error:** Ensure virtual environment is activated and dependencies are installed
- **Missing Files:** Check that all required assets are in the correct directories

### Development Issues
- **PyQt6 Import Error:** Reinstall PyQt6: `pip install --upgrade PyQt6`
- **Version Not Displaying:** Ensure VERSION.TXT exists in project root

## Documentation

- **USER_GUIDE.md** - End-user documentation (in-app Help)
- **CHANGELOG.md** - Version history and changes
- **CLAUDE.md** - Project context and AI assistant instructions

## License

TBD
