#!/usr/bin/env python3
"""
Utility to inspect form fields in PDF templates
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)


def inspect_pdf_fields(pdf_path):
    """Inspect and display all form fields in a PDF"""
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        return

    try:
        doc = fitz.open(pdf_path)
        print(f"\n{'='*80}")
        print(f"PDF: {os.path.basename(pdf_path)}")
        print(f"{'='*80}")
        print(f"Pages: {len(doc)}")

        total_fields = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())

            if widgets:
                print(f"\nPage {page_num + 1}: {len(widgets)} form fields")
                print("-" * 80)

                # Group by field name pattern
                field_names = [w.field_name for w in widgets]
                field_names.sort()

                for i, widget in enumerate(widgets):
                    field_type = widget.field_type_string
                    field_name = widget.field_name
                    field_value = widget.field_value or "(empty)"

                    print(f"  [{i+1:3d}] {field_name:40s} | {field_type:15s} | {field_value}")

                total_fields += len(widgets)

        if total_fields == 0:
            print("\n⚠️  WARNING: PDF has NO form fields!")
            print("   This PDF is static and cannot be populated with bindings.")
        else:
            print(f"\n{'='*80}")
            print(f"TOTAL FORM FIELDS: {total_fields}")
            print(f"{'='*80}")

            # Analyze field naming pattern
            all_fields = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                all_fields.extend([w.field_name for w in page.widgets()])

            if all_fields:
                print("\nField Naming Analysis:")
                print("-" * 80)

                # Check if fields follow standard pattern (js1_button1, etc.)
                standard_pattern = all(
                    ('button' in f.lower() or 'axis' in f.lower() or 'hat' in f.lower())
                    for f in all_fields
                )

                if standard_pattern:
                    print("✓ Fields appear to use STANDARD naming (js1_button1, etc.)")
                    print("  → No field_mapping.json needed!")
                else:
                    print("⚠ Fields appear to use CUSTOM naming")
                    print("  → Will need field_mapping.json file")
                    print("\n  Sample field names:")
                    for name in all_fields[:10]:
                        print(f"    - {name}")
                    if len(all_fields) > 10:
                        print(f"    ... and {len(all_fields) - 10} more")

        doc.close()

    except Exception as e:
        print(f"ERROR: Failed to inspect PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_pdf_fields.py <path_to_pdf>")
        print("\nOr specify a device directory:")
        print("  python inspect_pdf_fields.py vkb_gladiator_scg_rh")
        print("  python inspect_pdf_fields.py vkb_stecs")
        sys.exit(1)

    path = sys.argv[1]

    # If it's just a directory name, assume it's in visual-templates
    if not os.path.exists(path) and not path.endswith('.pdf'):
        # Try as directory in visual-templates
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'visual-templates')
        device_dir = os.path.join(templates_dir, path)

        if os.path.isdir(device_dir):
            # Find PDF in directory
            pdf_files = [f for f in os.listdir(device_dir) if f.endswith('.pdf')]
            if pdf_files:
                path = os.path.join(device_dir, pdf_files[0])
                print(f"Found: {path}")
            else:
                print(f"ERROR: No PDF files found in {device_dir}")
                sys.exit(1)

    inspect_pdf_fields(path)
