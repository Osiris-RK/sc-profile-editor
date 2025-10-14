# Star Citizen Profile Viewer

A desktop application for converting Star Citizen control profile XML files into human-readable formats (PDF, Word, CSV) with annotated device graphics.

## Features

- Import Star Citizen XML control profiles
- Generate human-readable control mapping tables
- Create annotated device graphics (VKB, Thrustmaster, etc.)
- Export to multiple formats: PDF, Word, CSV
- Edit control labels for personalization
- Support for keyboard, mouse, and HOTAS devices

## Project Structure

```
sc-profile-viewer/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── gui/               # GUI components
│   ├── parser/            # XML parsing and label generation
│   ├── exporters/         # Export modules (PDF, Word, CSV, Graphics)
│   ├── models/            # Data models
│   └── resources/         # Device templates and assets
├── example-profiles/      # Sample SC profile XML files
├── visual-templates/      # Device reference images
├── tests/                 # Unit tests
└── build_scripts/         # PyInstaller build scripts
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python src/main.py
```

## Building Executable

```bash
pyinstaller --onefile --windowed --name "SC Profile Viewer" src/main.py
```

## Development Status

Currently in Phase 1: Project structure setup complete. See PLAN.md for full development roadmap.

## Technology Stack

- **Python 3.12+**
- **PyQt6** - GUI framework
- **python-docx** - Word document generation
- **reportlab** - PDF generation
- **Pillow** - Image processing
- **PyInstaller** - Executable packaging

## License

TBD
