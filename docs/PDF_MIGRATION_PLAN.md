# PDF-Based Device Template Migration Plan (v0.4.0)

## Overview

This document outlines the plan to migrate SC Profile Viewer from PNG+SVG device templates to interactive PDF templates with fillable form fields. This is a major architectural change for v0.4.0.

**Status:** Planning phase
**Branch:** `v0.4.0-pdf-templates`
**Base Version:** v0.3.0 (stable baseline)

## Vision

Users will create device templates in Adobe InDesign as PDFs with form fields. Field IDs will directly match Star Citizen's button identifiers (e.g., `js1_button1`, `js2_x`). The application will:
- Load PDF templates
- Populate form fields with action labels from XML profiles
- Display interactive PDF in the Device Graphics tab
- Support inline editing in PDF view (syncs with table)
- Support editing in table view (syncs with PDF)
- Export populated PDFs

## Key Design Decisions

### PDF Form Fields
- **Approach:** Interactive PDF with fillable form fields
- **Field naming:** Direct match to SC identifiers (e.g., `js1_button1`, `js2_hat1_up`)
- **Migration:** Replace PNG+SVG system entirely (v0.3.0 remains stable baseline)

### Bidirectional Synchronization
- Edits in PDF view → Update table
- Edits in table view → Update PDF
- Single source of truth: `Binding` objects in profile
- No full widget reloads (performance optimization)

### Device-to-Joystick Mapping
- Parse device order from SC XML profile
- Map devices to js1, js2, js3, etc. dynamically
- Fallback to manual mapping in template registry

---

## Phase 0: Release v0.3.0 ✅ COMPLETED

**Goal:** Create stable baseline before PDF migration

### Tasks Completed
- ✅ Updated CHANGELOG.md with v0.3.0 features
- ✅ Incremented version: 0.2.1 → 0.3.0
- ✅ Built executable: SCProfileViewer.exe
- ✅ Created git commit and tag v0.3.0
- ✅ Pushed to remote with tags
- ✅ Created GitHub release
- ✅ Built installer: SCProfileViewer-v0.3.0-Setup.exe
- ✅ Uploaded installer to GitHub release
- ✅ Committed installer.iss version update

**Release:** https://github.com/Osiris-RK/sc-profile-viewer/releases/tag/v0.3.0

---

## Phase 1: Infrastructure & Research (1-2 weeks)

**Goal:** Evaluate PDF libraries, create proof-of-concept, design device mapping system

### 1.1 PDF Library Selection & Prototyping

**Primary Candidate: PyMuPDF (fitz)**
- Research capabilities:
  - Reading/writing PDF form fields
  - PDF page rendering to QPixmap for Qt display
  - Form field coordinate extraction
  - Performance characteristics
- **Alternative:** pdfrw (lighter weight, form-field focused)

**Proof-of-Concept Requirements:**
- Load PDF with form fields
- Populate field values programmatically
- Render PDF page in Qt widget (QGraphicsScene or QLabel)
- Detect clicks on form field regions
- Test performance with multiple devices

**Deliverables:**
- `scripts/prototypes/pdf_poc.py` - Proof-of-concept script
- Research notes on PyMuPDF capabilities and limitations
- Performance benchmarks (load time, render time)

### 1.2 Device-to-JS Mapping System

**Template Registry Changes:**
- Add `joystick_index` field to template_registry.json
- Example:
  ```json
  {
    "id": "vkb_gladiator_evo_right",
    "joystick_index": 1,  // Maps to js1
    ...
  }
  ```
- Support dynamic mapping based on device order in profile

**New Utility Class:**
- Create `src/utils/device_joystick_mapper.py`
- `DeviceJoystickMapper` class:
  - Parse device order from SC XML profile
  - Map device names to js1/js2/js3 dynamically
  - Handle device name variations (case-insensitive, partial matching)
  - Handle split devices (e.g., VKB Gladiator + SEM module)
  - Fallback to template registry if dynamic mapping fails

**Algorithm:**
```python
# Parse profile to get device order
devices_in_profile = ["VKBsim Gladiator EVO R", "VKB THQ", "VPC MT-50CM3"]

# Map to js indices
device_to_js = {
    "VKBsim Gladiator EVO R": "js1",
    "VKB THQ": "js2",
    "VPC MT-50CM3": "js3"
}

# When populating PDF field "js1_button5":
# Look up device for js1 → "VKBsim Gladiator EVO R"
# Find template for that device
# Populate field with action label
```

**Deliverables:**
- `src/utils/device_joystick_mapper.py`
- Unit tests for mapping logic
- Updated template_registry.json schema

### 1.3 PDF Field Naming Convention

**Standard Format:** `{js_id}_{input_type}{number}`

**Examples:**
- Buttons: `js1_button1`, `js1_button2`, `js2_button15`
- Axes: `js1_x`, `js1_y`, `js1_z`, `js1_rotx`, `js1_roty`, `js1_rotz`
- Hat switches: `js1_hat1_up`, `js1_hat1_down`, `js1_hat1_left`, `js1_hat1_right`
- Sliders: `js1_slider1`, `js1_slider2`

**Validation Utility:**
- Create `scripts/validation/validate_pdf_fields.py`
- Check PDF field names match convention
- Report missing or incorrectly named fields
- Suggest corrections

**Documentation:**
- Create `docs/PDF_FIELD_NAMING.md`
- Comprehensive field naming reference
- Examples for each input type
- Guidelines for InDesign template authors

**Deliverables:**
- `docs/PDF_FIELD_NAMING.md` - Field naming specification
- `scripts/validation/validate_pdf_fields.py` - Validation tool
- Sample PDF with correctly named fields

---

## Phase 2: PDF Template Creation Workflow (2-3 weeks)

**Goal:** Document workflow, create conversion guide, convert all existing templates

### 2.1 InDesign Template Creation Guide

**Create `docs/CREATING_PDF_TEMPLATES.md`:**
- InDesign setup and configuration
  - Document size recommendations
  - Color mode (RGB vs CMYK)
  - Resolution settings
- Form field placement
  - Using InDesign's Interactive Form tools
  - Field properties and styling
  - Text field vs button field considerations
- Field naming requirements
  - Reference to PDF_FIELD_NAMING.md
  - Naming conventions enforcement
- Export settings for interactive PDFs
  - PDF/X compatibility
  - Form field preservation
  - Compression settings
- Best practices
  - Font selection (embedded vs system)
  - Field sizing for long labels
  - Color scheme for readability
  - Background vs foreground layers

**Deliverables:**
- `docs/CREATING_PDF_TEMPLATES.md`
- InDesign template file (starter template)
- Example PDF with annotations

### 2.2 Convert Existing Device Templates to PDF

**8 Devices to Convert:**
1. VKB Gladiator EVO Right
2. VKB Gladiator EVO Left
3. VKB Space Sim Module (SEM)
4. VKB F16 MFD
5. VKB Throttle Quadrant (THQ)
6. VKB Gunfighter MCG Ultimate
7. VPC MongoosT-50CM3 Right
8. Thrustmaster TWCS Throttle

**Workflow Per Device:**
1. Open InDesign, create new document
2. Import existing PNG as background layer (locked)
3. Create new layer for form fields
4. Place text form fields at each button location
   - Use existing SVG overlay as reference for positioning
5. Name fields according to SC identifier convention
   - Example: `js1_button1`, `js1_button2`, etc.
6. Style fields (font, size, alignment, border)
7. Export as interactive PDF
8. Validate with validation script
9. Test in proof-of-concept app

**Storage Location:**
- `visual-templates/{device_id}/{device_id}.pdf`
- Keep PNG files temporarily for reference
- Archive InDesign source files (.indd) in template folder

**Quality Checklist:**
- All buttons have corresponding form fields
- Field names match convention exactly
- Fields are positioned accurately over buttons
- Text fits within field boundaries
- PDF exports without errors

**Deliverables:**
- 8 PDF device templates in `visual-templates/`
- InDesign source files (.indd) for each device
- Validation report for each template

### 2.3 Update Template Registry

**Modify `template_registry.json`:**
- Replace `"image"` and `"overlay"` with single `"pdf"` field
- Add `"joystick_index"` for device-to-js mapping
- Remove `"button_range"` (now handled by PDF field names)

**Example New Format:**
```json
{
  "id": "vkb_gladiator_evo_right",
  "name": "VKB Gladiator EVO (Right)",
  "pdf": "vkb_gladiator_evo_right/vkb_gladiator_evo_right.pdf",
  "joystick_index": 1,
  "device_match_patterns": [
    "VKBsim Gladiator EVO R",
    "Gladiator EVO R"
  ],
  "type": "joystick"
}
```

**Migration Plan:**
- Keep backward compatibility flag during transition (optional)
- Document breaking change in CHANGELOG.md
- Update CLAUDE.md with new architecture

**Deliverables:**
- Updated `template_registry.json`
- JSON schema documentation
- Migration notes in CHANGELOG.md

---

## Phase 3: Core Application Changes (3-4 weeks)

**Goal:** Replace graphics system, implement PDF rendering, add bidirectional sync

### 3.1 New PDF Template Manager

**Create `src/graphics/pdf_template_manager.py`:**

**`PDFTemplateManager` Class:**
```python
class PDFTemplateManager:
    def __init__(self, registry_path: str):
        """Load template registry and initialize PDF handling"""

    def load_template(self, device_name: str) -> PDFTemplate:
        """Find and load PDF template for device"""

    def get_form_fields(self, pdf_path: str) -> Dict[str, FormField]:
        """Extract all form fields and coordinates from PDF"""

    def populate_fields(self, pdf_path: str, field_values: Dict[str, str]) -> bytes:
        """Populate PDF form fields with action labels"""

    def render_page(self, pdf_bytes: bytes, dpi: int = 150) -> QPixmap:
        """Render PDF page to QPixmap for Qt display"""
```

**Key Functionality:**
- Load PDF templates from registry
- Use PyMuPDF to extract form fields
- Map device buttons to PDF fields via DeviceJoystickMapper
- Populate fields with action labels from bindings
- Cache rendered pages for performance

**Deliverables:**
- `src/graphics/pdf_template_manager.py`
- Unit tests for template loading and field population
- Performance benchmarks

### 3.2 Replace Device Graphics Widget

**Create `src/gui/pdf_device_graphics_widget.py`:**

**`PDFDeviceGraphicsWidget` Class:**
```python
class PDFDeviceGraphicsWidget(QWidget):
    # Signals
    label_changed = pyqtSignal(str, str, str)  # device, input_code, new_label

    def __init__(self, parent=None):
        """Initialize PDF viewer widget"""

    def load_profile(self, profile: Profile):
        """Load profile and render device PDFs"""

    def select_device(self, device_name: str):
        """Switch to display a specific device"""

    def update_field(self, input_code: str, new_label: str):
        """Update specific PDF field without full reload"""

    def on_click(self, pos: QPoint):
        """Handle click events for inline editing"""
```

**Implementation Details:**
- Use QGraphicsScene to display rendered PDF
- Store form field rectangles for click detection
- Implement zoom/pan support (QGraphicsView)
- Show hover effects (highlight fields on mouse over)
- Display inline editor (QLineEdit overlay) on click
- Support keyboard shortcuts (Enter to save, Esc to cancel)

**Performance Optimizations:**
- Cache rendered PDF pages (only re-render on change)
- Lazy load devices (render only when selected)
- Background rendering for large PDFs
- Adjustable DPI (trade quality vs performance)

**Deliverables:**
- `src/gui/pdf_device_graphics_widget.py`
- Integration with main window
- User interaction tests

### 3.3 Bidirectional Synchronization: PDF ↔ Table

**Current Problem:**
- Full widget reload on every label edit (inefficient)
- No synchronization architecture

**Solution: Unified Signal Architecture**

**Create `src/utils/label_sync_manager.py`:**
```python
class LabelSyncManager(QObject):
    # Signal emitted when any label changes
    label_changed = pyqtSignal(str, str, str, str)  # device, input_code, new_label, source

    def update_label(self, device: str, input_code: str, new_label: str, source: str):
        """
        Update label in binding object and emit signal

        Args:
            device: Device name
            input_code: Button/axis identifier
            new_label: New label text
            source: "table" or "pdf" (prevents circular updates)
        """
        # Update binding.custom_label
        # Save to override file via LabelOverrideManager
        # Emit signal (subscribers ignore if source == self)
```

**Update Flow: PDF → Table**
1. User clicks field in PDF view → Show inline editor
2. User edits label → Save changes
3. Call `sync_manager.update_label(device, input_code, new_label, source="pdf")`
4. SyncManager updates binding and saves override
5. SyncManager emits `label_changed` signal
6. Table receives signal → Updates specific row (no full reload)
7. PDF receives signal but ignores (source == "pdf")

**Update Flow: Table → PDF**
1. User edits cell in table
2. Call `sync_manager.update_label(device, input_code, new_label, source="table")`
3. SyncManager updates binding and saves override
4. SyncManager emits `label_changed` signal
5. PDF receives signal → Updates specific field, re-renders page
6. Table receives signal but ignores (source == "table")

**Integration Points:**
- Main window connects table and PDF to SyncManager
- Both widgets subscribe to `label_changed` signal
- Source tracking prevents infinite loops

**Deliverables:**
- `src/utils/label_sync_manager.py`
- Integration in main_window.py
- End-to-end synchronization tests

### 3.4 Device Selection and Filtering

**Maintain Current Behavior:**
- Device filter dropdown in main window
- When device selected:
  - Load corresponding PDF template
  - Filter table to show only that device's bindings
  - Sync selection between tabs (already implemented)

**New Requirements:**
- PDF widget must respond to device filter changes
- Efficient switching between devices (no full reload)
- Remember last selected device per session

**Deliverables:**
- Updated main_window.py device filter handling
- Device switching tests

---

## Phase 4: Export Functionality (1 week)

**Goal:** Update export features for PDF-based system

### 4.1 Enhanced PDF Export

**Feature: Export Populated PDF**
- Save currently displayed PDF with all populated labels
- User chooses save location via file dialog
- Options:
  - Flatten fields (make read-only/non-editable)
  - Keep fields editable
- Add metadata:
  - Profile name
  - Device name
  - Export timestamp
  - SC Profile Viewer version
- Preserve formatting and layout from template

**Implementation:**
```python
def export_pdf(self, output_path: str, flatten: bool = False):
    """
    Export populated PDF

    Args:
        output_path: Where to save PDF
        flatten: If True, make fields read-only
    """
```

**Deliverables:**
- PDF export implementation in PDFDeviceGraphicsWidget
- Export button in main window
- File dialog for save location
- Flatten option checkbox

### 4.2 PNG Export from PDF

**Feature: Convert PDF to PNG**
- Maintain backward compatibility with PNG export
- Use PyMuPDF to render PDF at high DPI (300)
- Same file dialog and save workflow as current PNG export

**Implementation:**
```python
def export_png(self, output_path: str, dpi: int = 300):
    """
    Export PDF as high-resolution PNG

    Args:
        output_path: Where to save PNG
        dpi: Resolution (default 300 for print quality)
    """
```

**Deliverables:**
- PNG export implementation
- DPI selection option
- Quality comparison tests

### 4.3 Update Other Export Formats

**CSV Export:**
- No changes needed (uses Binding objects directly)
- Verify still works with new system

**Word Export:**
- No changes needed (uses Binding objects directly)
- Verify still works with new system

**PDF Report Export (existing):**
- May need updates if it embeds device graphics
- Test with new PDF templates

**Deliverables:**
- Verify all export formats work
- Update export dialog if needed
- Export integration tests

---

## Phase 5: Migration & Cleanup (1 week)

**Goal:** Remove deprecated code, update documentation, prepare for release

### 5.1 Remove PNG+SVG System

**Code to Delete:**
- `src/graphics/svg_generator.py` - SVGOverlayGenerator class
- Old `src/gui/device_graphics.py` - DeviceGraphicsWidget class
- `src/graphics/template_manager.py` - Old TemplateManager (if fully replaced)

**Utilities to Remove:**
- `scripts/template_dev/convert_inkscape_overlay.py`
- `scripts/template_dev/embed_image_in_svg.py`
- `scripts/template_dev/detect_button_coordinates.py` (OCR-based)
- `scripts/template_dev/rescale_overlay.py`

**Build Scripts:**
- Remove OCR build variant: `scripts/build/build_exe_with_ocr.py`
- Update `scripts/build/build_exe.py` to remove OCR dependencies

**Templates:**
- Move old PNG+SVG templates to `visual-templates/legacy/`
- Keep for reference but not included in builds
- Update .gitignore if needed

**Dependencies:**
- Review requirements.txt
- Remove unused dependencies (if any)
- Add PyMuPDF to requirements.txt

**Deliverables:**
- Cleaned up codebase
- Updated requirements.txt
- Legacy templates archived

### 5.2 Update Documentation

**USER_GUIDE.md:**
- Add section on inline PDF editing
- Update device graphics tab screenshots
- Update export instructions

**CLAUDE.md:**
- Update architecture section with PDF system
- Remove references to PNG+SVG system
- Update project structure diagram
- Update key design decisions

**README.md:**
- Update build instructions (remove OCR build)
- Update dependencies list
- Update feature list

**CHANGELOG.md:**
- Comprehensive v0.4.0 entry
- Document breaking changes
- List new features
- Migration notes for users

**CREATING_DEVICE_TEMPLATES.md:**
- Replace SVG workflow with PDF workflow
- Update all screenshots and examples
- Remove references to Inkscape

**DEVICE_STATUS.md:**
- Update template format column (PDF instead of PNG+SVG)
- Mark all 8 devices as "PDF complete"

**Deliverables:**
- All documentation updated
- Screenshots refreshed
- Comprehensive v0.4.0 CHANGELOG entry

---

## Phase 6: Testing & Release (1-2 weeks)

**Goal:** Comprehensive testing, build release, publish v0.4.0

### 6.1 Comprehensive Testing

**Template Testing:**
- Verify all 8 device PDFs load correctly
- Check field names match convention
- Validate field positioning accuracy
- Test with various label lengths (short, long, multi-word)

**Mapping Testing:**
- Test device-to-joystick mapping with various profiles
- Test single device profiles (js1 only)
- Test multi-device profiles (js1, js2, js3+)
- Test device name variations (case sensitivity, partial matches)
- Test split devices (VKB with SEM module)

**Bidirectional Sync Testing:**
- Edit label in PDF → Verify table updates immediately
- Edit label in table → Verify PDF updates immediately
- Test rapid edits (type fast, switch between PDF and table)
- Test multiple label edits in sequence
- Test undo/redo functionality (if implemented)

**Export Testing:**
- PDF export: Verify populated PDF saves correctly
- PDF export: Test flatten option (fields read-only)
- PNG export: Verify high-quality image output
- Word export: Verify still works with new system
- CSV export: Verify still works with new system

**Label Override System:**
- Custom labels persist across sessions
- Global labels still work
- Auto-generated labels as fallback
- Label revert functionality (delete custom)

**Filter/Search:**
- Device filter dropdown works
- Action map filter works
- Search text filter works
- Hide unmapped keys works
- Filters persist when switching tabs

**Performance Testing:**
- Profile load time (baseline vs new system)
- Device switching time
- PDF rendering time
- Memory usage with multiple devices
- Large profile handling (100+ bindings)

**UI/UX Testing:**
- Inline editing is intuitive
- Hover effects provide feedback
- Keyboard shortcuts work (Enter, Esc)
- Zoom/pan in PDF view works
- Tab switching is smooth

**Edge Cases:**
- Empty profile (no bindings)
- Profile with unmapped device
- Profile with unknown device
- Corrupted PDF template
- Missing form fields in PDF
- Invalid field names

**Deliverables:**
- Test plan document
- Test results report
- Bug fixes for issues found
- Performance benchmarks

### 6.2 Build and Release v0.4.0

**Pre-Release Checklist:**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md finalized
- [ ] VERSION.TXT updated to 0.4.0
- [ ] No outstanding bugs
- [ ] Performance acceptable

**Build Process:**
1. Update VERSION.TXT to 0.4.0
2. Update installer.iss to 0.4.0
3. Run build script: `python scripts/build/build_exe.py`
4. Test executable on clean Windows machine
5. Build installer: `scripts/build/build_installer.bat`
6. Test installer on clean Windows machine

**Git Release Process:**
1. Commit all final changes
2. Merge v0.4.0-pdf-templates to main (or create PR)
3. Create git tag: `git tag v0.4.0`
4. Push with tags: `git push && git push --tags`

**GitHub Release:**
1. Create release on GitHub: `gh release create v0.4.0`
2. Write comprehensive release notes
3. Upload installer: `SCProfileViewer-v0.4.0-Setup.exe`
4. Mark as pre-release if needed
5. Publish release

**Deliverables:**
- SCProfileViewer.exe (tested)
- SCProfileViewer-v0.4.0-Setup.exe (tested)
- Git tag v0.4.0
- GitHub release published
- Release announcement

---

## Technical Details

### Dependencies to Add

**PyMuPDF (fitz):**
```bash
pip install PyMuPDF
```
- Version: 1.23.0+ recommended
- Used for: PDF manipulation and rendering
- License: AGPL (check compatibility)

**Optional: pdfrw (if PyMuPDF has issues):**
```bash
pip install pdfrw
```
- Lighter weight alternative
- Form-field focused

### PDF Field Population Example

```python
import fitz  # PyMuPDF

# Open PDF template
doc = fitz.open("vkb_gladiator_evo_right.pdf")
page = doc[0]

# Get all form fields
fields = page.widgets()

# Populate specific field
for field in fields:
    if field.field_name == "js1_button1":
        field.field_value = "Fire Weapon"
        field.update()

# Save populated PDF
doc.save("output.pdf")
doc.close()
```

### Device-to-JS Mapping Example

```python
# Parse XML profile
profile = XMLParser.parse("layout_exported.xml")

# Get device order
devices = profile.get_device_order()
# ["VKBsim Gladiator EVO R", "VKB THQ", "VPC MT-50CM3"]

# Create mapping
mapper = DeviceJoystickMapper(devices, template_registry)
js_mapping = mapper.create_mapping()
# {
#   "VKBsim Gladiator EVO R": "js1",
#   "VKB THQ": "js2",
#   "VPC MT-50CM3": "js3"
# }

# When populating field "js1_button5":
device_name = js_mapping["js1"]  # "VKBsim Gladiator EVO R"
template = template_manager.get_template(device_name)
# Load template.pdf and populate field
```

### Bidirectional Sync Signal Flow

```python
# In main_window.py setup:
self.sync_manager = LabelSyncManager(self.profile)
self.sync_manager.label_changed.connect(self.table_widget.on_label_changed)
self.sync_manager.label_changed.connect(self.pdf_widget.on_label_changed)

# When user edits in table:
def on_table_edit(self, row, col):
    device, input_code, new_label = self.get_edit_data(row, col)
    self.sync_manager.update_label(device, input_code, new_label, source="table")

# When user edits in PDF:
def on_pdf_edit(self, input_code, new_label):
    device = self.current_device
    self.sync_manager.update_label(device, input_code, new_label, source="pdf")

# In table_widget.py:
def on_label_changed(self, device, input_code, new_label, source):
    if source == "table":
        return  # Ignore our own updates
    # Update specific row in table (no full reload)
    row = self.find_row(device, input_code)
    self.table.item(row, COL_LABEL).setText(new_label)

# In pdf_widget.py:
def on_label_changed(self, device, input_code, new_label, source):
    if source == "pdf":
        return  # Ignore our own updates
    # Update specific PDF field and re-render
    self.update_field(input_code, new_label)
```

---

## Migration Strategy

### For Developers

**Clean Break Approach:**
- No backward compatibility with v0.3.0 templates
- PNG+SVG system completely removed
- Users must upgrade to v0.4.0 for new features
- v0.3.0 remains available for legacy use if needed

**Branch Strategy:**
- `main` - Production releases (v0.3.0 currently)
- `v0.4.0-pdf-templates` - PDF migration development
- Merge to main when complete and tested
- Tag v0.4.0 on main branch

### For Users

**Breaking Changes:**
- Device templates are now PDF format
- Cannot use custom PNG+SVG templates from v0.3.0
- Must download v0.4.0+ for PDF support

**Migration Path:**
- Users can keep v0.3.0 installed if needed
- Uninstall v0.3.0, install v0.4.0 (installer handles this)
- No user data lost (label overrides stored in AppData)

---

## Estimated Timeline

### Optimistic (8 weeks)
- Phase 1: 1 week
- Phase 2: 2 weeks
- Phase 3: 3 weeks
- Phase 4: 0.5 weeks
- Phase 5: 0.5 weeks
- Phase 6: 1 week

### Realistic (12 weeks)
- Phase 1: 2 weeks (research takes time)
- Phase 2: 3 weeks (template conversion is tedious)
- Phase 3: 4 weeks (core changes are complex)
- Phase 4: 1 week
- Phase 5: 1 week
- Phase 6: 1 week

### Conservative (16 weeks)
- Phase 1: 2 weeks
- Phase 2: 4 weeks
- Phase 3: 5 weeks
- Phase 4: 1 week
- Phase 5: 1 week
- Phase 6: 2 weeks
- Buffer: 1 week for unforeseen issues

**Recommended:** Plan for 12 weeks, aim for 10 weeks

---

## Success Criteria

### Functional Requirements Met
- ✅ PDF templates load and display correctly
- ✅ Form fields populate with action labels
- ✅ Device-to-joystick mapping works dynamically
- ✅ Inline editing in PDF view works
- ✅ Bidirectional sync (PDF ↔ Table) works
- ✅ All export formats work (PDF, PNG, Word, CSV)
- ✅ Label override system preserved
- ✅ Filter/search functionality maintained

### Performance Acceptable
- ✅ Profile load time < 2 seconds (for 8 devices)
- ✅ Device switching < 500ms
- ✅ PDF rendering < 1 second per page
- ✅ Memory usage < 200MB for typical profile
- ✅ No UI freezing or lag

### Quality Standards
- ✅ No critical bugs
- ✅ All documentation updated
- ✅ Code is maintainable (well-commented, structured)
- ✅ Tests cover critical functionality
- ✅ User experience is intuitive

### Release Ready
- ✅ Executable builds without errors
- ✅ Installer creates and installs successfully
- ✅ Tested on clean Windows 10/11 machines
- ✅ GitHub release published with installer
- ✅ Changelog is comprehensive

---

## Risk Assessment

### High Risk Items

**1. PyMuPDF Performance**
- **Risk:** PDF rendering may be too slow for interactive use
- **Mitigation:** Implement caching, lazy loading, adjustable DPI
- **Fallback:** Use lighter library (pdfrw) or simpler approach

**2. Form Field Compatibility**
- **Risk:** InDesign PDFs may not export form fields correctly
- **Mitigation:** Test export settings early, use validation script
- **Fallback:** Use Adobe Acrobat for form field creation

**3. Device Mapping Complexity**
- **Risk:** Dynamic mapping fails with unusual device configurations
- **Mitigation:** Extensive testing with various profiles, manual fallback
- **Fallback:** Require manual joystick_index in template registry

### Medium Risk Items

**4. Template Conversion Time**
- **Risk:** Converting 8 templates takes longer than expected (tedious work)
- **Mitigation:** Document workflow clearly, create starter template, automate where possible
- **Impact:** Timeline delay, but not a blocker

**5. Synchronization Bugs**
- **Risk:** Circular updates, race conditions in bidirectional sync
- **Mitigation:** Source tracking, careful signal/slot design, thorough testing
- **Impact:** User confusion, data loss if not caught

### Low Risk Items

**6. Export Functionality**
- **Risk:** PDF/PNG export has edge cases
- **Mitigation:** Test thoroughly, handle errors gracefully
- **Impact:** Minor, can be fixed post-release

**7. Documentation Updates**
- **Risk:** Documentation becomes outdated during development
- **Mitigation:** Update docs incrementally, final review before release
- **Impact:** User confusion, but easily fixed

---

## Open Questions

1. **InDesign Licensing:** Do we need InDesign for template creation, or can we provide alternative tools (Acrobat, LibreOffice)?
2. **Field Styling:** Should form fields have consistent styling across all templates, or allow customization per device?
3. **Multi-Page PDFs:** Do we support multi-page device PDFs (e.g., front and back views)?
4. **Template Distribution:** Should we host PDF templates separately from the app (for user-contributed templates)?
5. **Backward Compatibility:** Should we keep a "legacy mode" for PNG+SVG templates, or clean break?
   - **Decision:** Clean break, v0.3.0 remains available

---

## Notes for Future Sessions

### Starting a New Session

1. Read this document: `docs/PDF_MIGRATION_PLAN.md`
2. Check current branch: Should be on `v0.4.0-pdf-templates`
3. Review `CLAUDE.md` for project context
4. Check `CHANGELOG.md` to see what's been completed
5. Look at git commits to see recent progress

### Tracking Progress

- Update this document as phases complete
- Mark tasks with ✅ when done
- Add notes about implementation decisions
- Document deviations from plan
- Update timeline estimates if needed

### Key Files to Reference

- `CLAUDE.md` - Overall project context
- `CHANGELOG.md` - Version history
- `template_registry.json` - Current template configuration
- `src/gui/device_graphics.py` - Current graphics widget (to be replaced)
- `src/graphics/svg_generator.py` - Current SVG system (to be removed)

### Testing During Development

- Test each phase deliverable before moving on
- Keep v0.3.0 installer for comparison testing
- Test with multiple device profiles
- Document any issues or bugs found

---

## Version History

- **2025-01-08:** Initial plan created
  - v0.3.0 released as stable baseline
  - Branch `v0.4.0-pdf-templates` created from main
  - Ready to begin Phase 1
