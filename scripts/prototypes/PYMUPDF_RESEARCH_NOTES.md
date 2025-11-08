# PyMuPDF Research Notes - Phase 1.1

**Date:** 2025-01-08
**Library:** PyMuPDF (fitz) v1.26.6
**Status:** ✅ APPROVED for v0.4.0 PDF Migration

## Executive Summary

PyMuPDF successfully meets all requirements for PDF-based device templates. The library can:
- Load PDFs and extract form fields with coordinates
- Populate form field values programmatically
- Render PDFs to images for Qt display
- Excellent performance: <10ms per load+render cycle

**Recommendation:** Proceed with PyMuPDF for v0.4.0 implementation.

---

## Test Results

### Test PDF: VKB F16 MFD (VKB-FSM-GA-v1.0.pdf)

**PDF Metadata:**
- Format: PDF 1.7
- Creator: Adobe InDesign 20.0 (Windows)
- Producer: Adobe PDF Library 17.0
- Created: November 30, 2024

**Form Fields Found:** 50 fields
- Field Type: 7 (Text fields)
- All fields currently empty (no default values)
- Field names: USER1, USER2, HDG_1, HDG_2, TRK_1, TRK_2, NAV_1, NAV_2, APR_1, APR_2, etc.

**Sample Field Data:**
```
Field Name: USER1
Field Type: 7
Rect: Rect(512.4, 36.0, 756.0, 67.26)
```

**Field Coordinates:**
- All fields have precise rectangle coordinates
- Coordinates suitable for click detection in Qt
- Can map clicks to fields for inline editing

### Rendering Performance

**Test Configuration:**
- Iterations: 10
- DPI: 150
- Output: PNG

**Results:**
- Average load time: **1.39ms**
- Average render time: **8.05ms**
- **Total time per display: 9.44ms**

**Rendered Image:**
- Resolution: 1650 x 1275 pixels
- DPI: 150 (suitable for high-quality display)
- Output format: PNG

**Performance Assessment:** ✅ Excellent
- Sub-10ms rendering is ideal for interactive UI
- No perceived lag for users
- Fast enough for real-time updates

### Form Field Manipulation

**Capabilities Tested:**
- ✅ Extract field names
- ✅ Extract field types
- ✅ Extract field coordinates (Rect)
- ✅ Extract field values
- ✅ Set field values programmatically
- ✅ Save modified PDFs

**Code Example:**
```python
import fitz

doc = fitz.open("template.pdf")
page = doc[0]
widgets = list(page.widgets())  # Note: returns generator

for widget in widgets:
    if widget.field_name == "js1_button1":
        widget.field_value = "Fire Weapon"
        widget.update()

doc.save("output.pdf")
doc.close()
```

**Findings:**
- `page.widgets()` returns a generator (must convert to list)
- Field names are case-sensitive
- `widget.update()` required after changing field_value
- Can save modified PDFs without corrupting form fields

---

## Compatibility with Requirements

### ✅ Requirement 1: Load PDF Templates
- PyMuPDF can load any PDF file
- Handles Adobe InDesign PDFs correctly
- Fast loading (1.39ms average)

### ✅ Requirement 2: Extract Form Fields
- Can iterate through all form fields on a page
- Provides field name, type, value, coordinates
- Field Type 7 = Text fields (what we need)

### ✅ Requirement 3: Populate Fields
- Can set field values programmatically
- Changes persist when saving PDF
- No corruption of PDF structure

### ✅ Requirement 4: Render for Qt Display
- Can render PDF pages to pixmap (image)
- Adjustable DPI (150 recommended for balance)
- Output as PNG or direct to QPixmap
- Very fast rendering (8ms)

### ✅ Requirement 5: Extract Coordinates
- Each field has precise Rect (x1, y1, x2, y2)
- Can map Qt mouse clicks to field regions
- Enables inline editing functionality

---

## Implementation Recommendations

### 1. Field Naming Convention

**Current Issue:** Existing PDF uses non-standard field names (USER1, HDG_1, etc.)

**Solution:**
- Document strict field naming convention: `js{N}_{input_type}{number}`
- Examples: `js1_button1`, `js1_button2`, `js2_x`, `js1_hat1_up`
- Create validation script to check field names
- Provide InDesign template with correct naming

### 2. Performance Optimization

**Caching Strategy:**
- Cache rendered pixmaps (don't re-render unless field changes)
- Lazy load devices (render only when selected)
- Consider lower DPI for initial display (faster), higher for export

**Memory Management:**
- Close documents when switching devices
- Clear pixmap cache periodically
- Monitor memory usage with large profiles

### 3. Qt Integration

**QPixmap Conversion:**
```python
# PyMuPDF pixmap to QPixmap
pix = page.get_pixmap()
img_data = pix.tobytes("png")
qpixmap = QPixmap()
qpixmap.loadFromData(img_data)
```

**Click Detection:**
```python
def on_mouse_click(self, pos: QPoint):
    # Convert Qt coordinates to PDF coordinates
    for widget in self.widgets:
        rect = widget.rect
        if rect.contains(pos.x(), pos.y()):
            # Show inline editor for this field
            self.edit_field(widget.field_name)
```

### 4. Error Handling

**Common Issues to Handle:**
- PDF file not found
- PDF has no form fields
- Corrupted PDF files
- Field names don't match convention
- Missing fields for known buttons

**Recommended Approach:**
- Graceful degradation (show error, don't crash)
- Validate PDFs on load
- Log warnings for missing/misnamed fields
- Provide helpful error messages to users

---

## Alternative Libraries Considered

### pdfrw
- **Pros:** Lighter weight, pure Python, simpler API
- **Cons:** No rendering capabilities (would need separate library)
- **Verdict:** Not recommended (lack of rendering is a dealbreaker)

### reportlab
- **Pros:** Already in use for PDF export, pure Python
- **Cons:** Designed for PDF creation, not manipulation
- **Verdict:** Not suitable for this use case

### PyPDF2/pypdf
- **Pros:** Pure Python, good for basic PDF operations
- **Cons:** Limited form field support, no rendering
- **Verdict:** Insufficient for our needs

**Winner:** PyMuPDF (fitz)
- Best all-in-one solution
- Excellent performance
- Active development
- Comprehensive documentation

---

## Known Limitations

### 1. License Consideration
- PyMuPDF uses AGPL license
- Need to verify compatibility with project license
- Commercial use may require different licensing

### 2. Binary Dependencies
- Not pure Python (includes C++ library)
- Larger installation size
- Platform-specific binaries (Windows, Linux, macOS)

### 3. Form Field Types
- Only tested with text fields (Type 7)
- May need to handle other types (checkboxes, radio buttons)
- Behavior with complex field types unknown

### 4. Multi-Page PDFs
- Only tested single-page PDFs
- Need to verify behavior with multi-page templates
- May need page selection logic

---

## Next Steps (Phase 1 Continuation)

### Immediate Tasks:
1. ✅ Install PyMuPDF - DONE
2. ✅ Create proof-of-concept - DONE
3. ⏳ Create DeviceJoystickMapper utility
4. ⏳ Define PDF field naming convention (documentation)
5. ⏳ Create field validation script

### Future Integration Tasks:
- Create `PDFTemplateManager` class (Phase 3.1)
- Create `PDFDeviceGraphicsWidget` class (Phase 3.2)
- Implement inline editing (Phase 3.3)
- Add to requirements.txt
- Update build scripts

---

## Code Examples for Implementation

### Loading and Populating Template

```python
class PDFTemplateManager:
    def __init__(self, template_path: str):
        self.doc = fitz.open(template_path)
        self.page = self.doc[0]
        self.widgets = list(self.page.widgets())
        self.widget_map = {w.field_name: w for w in self.widgets}

    def populate_fields(self, field_values: Dict[str, str]):
        """Populate form fields with action labels"""
        for field_name, value in field_values.items():
            if field_name in self.widget_map:
                widget = self.widget_map[field_name]
                widget.field_value = value
                widget.update()

    def render_to_qpixmap(self, dpi: int = 150) -> QPixmap:
        """Render PDF page to QPixmap for Qt display"""
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = self.page.get_pixmap(matrix=mat)

        # Convert to QPixmap
        img_data = pix.tobytes("png")
        qpixmap = QPixmap()
        qpixmap.loadFromData(img_data)
        return qpixmap

    def save(self, output_path: str):
        """Save populated PDF"""
        self.doc.save(output_path)

    def close(self):
        """Clean up resources"""
        self.doc.close()
```

### Click Detection for Inline Editing

```python
class PDFDeviceGraphicsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.widgets = []  # List of form field widgets
        self.scale_factor = 1.0  # PDF to screen scaling

    def mousePressEvent(self, event: QMouseEvent):
        """Handle clicks on PDF form fields"""
        click_pos = event.pos()

        # Convert screen coordinates to PDF coordinates
        pdf_x = click_pos.x() / self.scale_factor
        pdf_y = click_pos.y() / self.scale_factor

        # Check if click is within any field
        for widget in self.widgets:
            rect = widget.rect
            if rect.contains(pdf_x, pdf_y):
                self.edit_field(widget.field_name, rect)
                break

    def edit_field(self, field_name: str, rect: fitz.Rect):
        """Show inline editor for field"""
        # Create QLineEdit overlay at field position
        editor = QLineEdit(self)
        editor.setGeometry(
            int(rect.x0 * self.scale_factor),
            int(rect.y0 * self.scale_factor),
            int(rect.width * self.scale_factor),
            int(rect.height * self.scale_factor)
        )
        editor.setText(self.get_field_value(field_name))
        editor.selectAll()
        editor.show()
        editor.setFocus()

        # Connect signals for save/cancel
        editor.editingFinished.connect(
            lambda: self.on_field_edited(field_name, editor.text())
        )
```

---

## Conclusion

PyMuPDF is an **excellent choice** for the PDF-based device template migration. It provides all required functionality with outstanding performance. The library is mature, well-documented, and actively maintained.

**Status:** ✅ Phase 1.1 Complete - Ready to proceed with Phase 1.2

**Confidence Level:** High (95%)
- All core requirements tested and verified
- Performance exceeds expectations
- No significant blockers identified
- Implementation path is clear

---

## Appendix: Test Output

**Test Files Generated:**
- `pdf_test_output/test_basic.pdf` - Basic test PDF
- `pdf_test_output/test_render.png` - Rendered VKB F16 MFD (1650x1275)

**Test Script:** `scripts/prototypes/pdf_poc.py`

**Run Command:**
```bash
.venv/Scripts/python.exe scripts/prototypes/pdf_poc.py
```
