"""
Create a simple test PDF template for development/testing

This creates a basic device template with properly named form fields
that can be used to test the PDF template system without needing InDesign.

Author: Phase 3 Testing
"""

import fitz  # PyMuPDF
from pathlib import Path


def create_test_device_pdf(output_path: str):
    """
    Create a simple test PDF with form fields for a basic joystick

    Device: Test Joystick
    - 10 buttons (button1-button10)
    - 2 axes (x, y)
    - 1 hat switch (hat1: up, down, left, right)
    """

    # Create new PDF document
    doc = fitz.open()

    # Create a page (8.5x11 inches at 72 DPI)
    page = doc.new_page(width=612, height=792)

    # Add title
    page.insert_text((50, 50), "Test Joystick Template", fontsize=20)
    page.insert_text((50, 80), "For SC Profile Viewer PDF Testing", fontsize=12, color=(0.5, 0.5, 0.5))

    # Draw a simple joystick outline
    # Base circle
    page.draw_circle((306, 400), 150, color=(0, 0, 0), width=2)

    # Stick
    page.draw_line((306, 400), (306, 300), color=(0, 0, 0), width=3)
    page.draw_circle((306, 300), 20, color=(0, 0, 0), width=2, fill=(0.8, 0.8, 0.8))

    # Now add text fields over buttons
    # We'll position them in a grid around the joystick

    button_positions = [
        # Top row (buttons 1-3)
        (200, 150, "js1_button1"),
        (280, 150, "js1_button2"),
        (360, 150, "js1_button3"),

        # Left side (buttons 4-5)
        (100, 350, "js1_button4"),
        (100, 420, "js1_button5"),

        # Right side (buttons 6-7)
        (480, 350, "js1_button6"),
        (480, 420, "js1_button7"),

        # Bottom row (buttons 8-10)
        (200, 580, "js1_button8"),
        (280, 580, "js1_button9"),
        (360, 580, "js1_button10"),
    ]

    # Hat switch positions (around top of stick)
    hat_positions = [
        (286, 250, "js1_hat1_up"),
        (286, 330, "js1_hat1_down"),
        (250, 290, "js1_hat1_left"),
        (322, 290, "js1_hat1_right"),
    ]

    # Axis positions
    axis_positions = [
        (50, 650, "js1_x"),
        (150, 650, "js1_y"),
    ]

    # Note: PyMuPDF doesn't have a simple way to add form fields to a blank PDF
    # We need to save the PDF first, then add fields using a different approach

    # Add labels for where fields should be
    for x, y, label in button_positions:
        # Draw a box
        rect = fitz.Rect(x, y, x + 70, y + 25)
        page.draw_rect(rect, color=(0, 0, 1), width=0.5)
        # Add text label
        page.insert_textbox(rect, label, fontsize=8, align=1)  # align=1 is center

    for x, y, label in hat_positions:
        rect = fitz.Rect(x, y, x + 50, y + 20)
        page.draw_rect(rect, color=(0, 0.5, 0), width=0.5)
        page.insert_textbox(rect, label, fontsize=7, align=1)

    for x, y, label in axis_positions:
        rect = fitz.Rect(x, y, x + 60, y + 25)
        page.draw_rect(rect, color=(0.5, 0, 0), width=0.5)
        page.insert_textbox(rect, label, fontsize=8, align=1)

    # Add instructions
    instructions = [
        "Test Template - Field Locations:",
        "Blue boxes: Buttons (1-10)",
        "Green boxes: Hat switch (up/down/left/right)",
        "Red boxes: Axes (x, y)",
    ]

    y_pos = 700
    for line in instructions:
        page.insert_text((50, y_pos), line, fontsize=10)
        y_pos += 15

    # Add form fields before saving
    add_form_fields_to_page(page, button_positions, hat_positions, axis_positions)

    # Save the PDF
    doc.save(output_path)
    print(f"Created PDF with visual layout and form fields: {output_path}")
    doc.close()


def add_form_fields_to_page(page, button_pos, hat_pos, axis_pos):
    """
    Add interactive form fields to a PDF page

    Note: PyMuPDF's widget creation is complex. For a proper template,
    you'd use InDesign. This is just for testing.
    """
    all_positions = button_pos + hat_pos + axis_pos

    for x, y, field_name in all_positions:
        # Create a text widget (form field)
        # Determine field dimensions
        if 'button' in field_name:
            width, height = 70, 25
        elif 'hat' in field_name:
            width, height = 50, 20
        else:  # axis
            width, height = 60, 25

        rect = fitz.Rect(x, y, x + width, y + height)

        widget = fitz.Widget()
        widget.field_name = field_name
        widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        widget.field_type_string = "Tx"  # Text field
        widget.rect = rect
        widget.text_fontsize = 8.0
        widget.text_color = [0, 0, 0]
        widget.fill_color = [1, 1, 1]  # White background
        widget.border_color = [0, 0, 0]
        widget.border_width = 0.5
        widget.border_style = "S"  # Solid

        # Add the widget to the page
        page.add_widget(widget)

    print(f"Added {len(all_positions)} form fields to PDF")


def main():
    """Create test template"""
    # Output to visual-templates directory
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "visual-templates" / "test_joystick"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "test_joystick.pdf"

    print("Creating test PDF template...")
    create_test_device_pdf(str(output_path))

    print(f"\nTest template created: {output_path}")
    print("\nValidating fields...")

    # Validate the created PDF
    import subprocess
    import sys

    validator_path = project_root / "scripts" / "validation" / "validate_pdf_fields.py"
    result = subprocess.run(
        [sys.executable, str(validator_path), str(output_path)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("Validation found issues (expected - fields may not be perfect)")

    print("\n" + "="*60)
    print("Test template ready for development/testing!")
    print("="*60)


if __name__ == "__main__":
    main()
