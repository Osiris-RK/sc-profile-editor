"""
Proof-of-Concept: PDF Form Field Manipulation with PyMuPDF

This script tests PyMuPDF's capabilities for:
1. Creating PDFs with form fields
2. Reading form field properties
3. Populating form fields with text
4. Rendering PDF pages to images (for Qt display)
5. Extracting form field coordinates

Author: Phase 1.1 - PDF Library Selection & Prototyping
"""

import fitz  # PyMuPDF
import sys
from pathlib import Path


def create_test_pdf_with_fields(output_path: str):
    """Create a simple PDF with form fields for testing"""
    print("\n=== Creating Test PDF with Form Fields ===")

    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    # Add some text
    page.insert_text((50, 50), "Star Citizen Profile Viewer - PDF Test", fontsize=16)
    page.insert_text((50, 80), "Test Form Fields (Joystick Buttons)", fontsize=12)

    # Note: PyMuPDF doesn't directly create form fields in the simple way
    # We'll test with existing PDFs that have fields
    # For now, just create a basic PDF

    doc.save(output_path)
    doc.close()
    print(f"[OK] Created test PDF: {output_path}")


def test_existing_pdf_with_fields(pdf_path: str):
    """Test reading form fields from an existing PDF"""
    print(f"\n=== Testing Existing PDF: {pdf_path} ===")

    if not Path(pdf_path).exists():
        print(f"[FAIL] PDF not found: {pdf_path}")
        return None

    doc = fitz.open(pdf_path)
    print(f"[OK] Opened PDF: {doc.name}")
    print(f"  Pages: {len(doc)}")
    print(f"  Metadata: {doc.metadata}")

    # Check first page for form fields
    if len(doc) > 0:
        page = doc[0]
        widgets = list(page.widgets())  # Convert generator to list

        if widgets:
            print(f"\n[OK] Found {len(widgets)} form fields on page 1:")
            for i, widget in enumerate(widgets[:10]):  # Show first 10
                print(f"  [{i+1}] Field Name: {widget.field_name}")
                print(f"      Field Type: {widget.field_type}")
                print(f"      Field Value: {widget.field_value}")
                print(f"      Rect: {widget.rect}")
                print()
        else:
            print("  No form fields found on page 1")

    doc.close()
    return widgets if widgets else None


def test_populate_fields(input_pdf: str, output_pdf: str):
    """Test populating form fields with sample data"""
    print(f"\n=== Testing Field Population ===")

    if not Path(input_pdf).exists():
        print(f"[FAIL] Input PDF not found: {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    page = doc[0]
    widgets = list(page.widgets())  # Convert generator to list

    if not widgets:
        print("[FAIL] No form fields to populate")
        doc.close()
        return

    # Populate fields with test data
    test_values = {
        "js1_button1": "Fire Weapon",
        "js1_button2": "Target Lock",
        "js1_button3": "Missile Launch",
        "js1_x": "Pitch",
        "js1_y": "Yaw",
    }

    populated_count = 0
    for widget in widgets:
        field_name = widget.field_name
        if field_name in test_values:
            widget.field_value = test_values[field_name]
            widget.update()
            populated_count += 1
            print(f"[OK] Populated: {field_name} = '{test_values[field_name]}'")

    if populated_count > 0:
        doc.save(output_pdf)
        print(f"\n[OK] Saved populated PDF: {output_pdf}")
    else:
        print("\n[FAIL] No matching fields found to populate")

    doc.close()


def test_render_to_image(pdf_path: str, output_image: str, dpi: int = 150):
    """Test rendering PDF page to image (for Qt display simulation)"""
    print(f"\n=== Testing PDF Rendering to Image ===")

    if not Path(pdf_path).exists():
        print(f"[FAIL] PDF not found: {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    page = doc[0]

    # Render page to pixmap (image)
    # zoom factor: dpi/72 (72 is default PDF DPI)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # Save as PNG
    pix.save(output_image)

    print(f"[OK] Rendered PDF page to image:")
    print(f"  Resolution: {pix.width} x {pix.height}")
    print(f"  DPI: {dpi}")
    print(f"  Output: {output_image}")

    doc.close()


def test_performance(pdf_path: str, iterations: int = 10):
    """Test rendering performance"""
    print(f"\n=== Testing Rendering Performance ===")

    if not Path(pdf_path).exists():
        print(f"[FAIL] PDF not found: {pdf_path}")
        return

    import time

    # Test load time
    start = time.time()
    for _ in range(iterations):
        doc = fitz.open(pdf_path)
        doc.close()
    load_time = (time.time() - start) / iterations

    # Test render time
    doc = fitz.open(pdf_path)
    page = doc[0]
    start = time.time()
    for _ in range(iterations):
        pix = page.get_pixmap()
    render_time = (time.time() - start) / iterations
    doc.close()

    print(f"Average load time: {load_time*1000:.2f}ms")
    print(f"Average render time: {render_time*1000:.2f}ms")
    print(f"Total time per display: {(load_time + render_time)*1000:.2f}ms")


def main():
    """Run all proof-of-concept tests"""
    print("=" * 60)
    print("PDF Form Field Manipulation - Proof of Concept")
    print("PyMuPDF (fitz) Library Testing")
    print("=" * 60)

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "scripts" / "prototypes" / "pdf_test_output"
    output_dir.mkdir(exist_ok=True)

    test_pdf = output_dir / "test_basic.pdf"
    test_image = output_dir / "test_render.png"
    populated_pdf = output_dir / "test_populated.pdf"

    # Test 1: Create basic PDF
    create_test_pdf_with_fields(str(test_pdf))

    # Test 2: Check existing PDF with fields (if available)
    existing_pdf = project_root / "visual-templates" / "vkb_f16_mfd" / "VKB-FSM-GA-v1.0.pdf"
    if existing_pdf.exists():
        widgets = test_existing_pdf_with_fields(str(existing_pdf))

        # Test 3: Render original PDF (regardless of field matching)
        test_render_to_image(str(existing_pdf), str(test_image))

        # Test 4: Populate fields if found (optional)
        if widgets:
            test_populate_fields(str(existing_pdf), str(populated_pdf))
            # Render populated PDF if it was created
            if Path(populated_pdf).exists():
                test_image_populated = output_dir / "test_render_populated.png"
                test_render_to_image(str(populated_pdf), str(test_image_populated))

        # Test 5: Performance
        test_performance(str(existing_pdf))
    else:
        print(f"\n[INFO] No existing PDF found at: {existing_pdf}")
        print("  Rendering basic test PDF instead")
        test_render_to_image(str(test_pdf), str(test_image))

    print("\n" + "=" * 60)
    print("[OK] Proof-of-Concept Complete!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
