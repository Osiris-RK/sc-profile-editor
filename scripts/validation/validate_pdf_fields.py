"""
PDF Form Field Name Validator

Validates PDF form field names against the SC Profile Viewer naming convention.
See docs/PDF_FIELD_NAMING.md for the complete specification.

Author: Phase 1.3 - PDF Field Naming Convention
"""

import fitz  # PyMuPDF
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class PDFFieldValidator:
    """Validates PDF form field names against naming convention"""

    # Regular expression for valid field names
    FIELD_PATTERN = re.compile(
        r'^js([1-9]\d?)_'  # js1_ through js99_
        r'(button\d+|'  # button1, button2, etc.
        r'hat\d+_(up|down|left|right)|'  # hat1_up, hat2_down, etc.
        r'[xyz]|rotx|roty|rotz|'  # axes
        r'slider\d+)$'  # slider1, slider2, etc.
    )

    # Valid input types
    VALID_INPUT_TYPES = [
        'button',
        'hat',
        'x', 'y', 'z',
        'rotx', 'roty', 'rotz',
        'slider'
    ]

    # Valid hat directions
    VALID_HAT_DIRECTIONS = ['up', 'down', 'left', 'right']

    def __init__(self, pdf_path: str):
        """
        Initialize validator with PDF file

        Args:
            pdf_path: Path to PDF file to validate
        """
        self.pdf_path = pdf_path
        self.valid_fields = []
        self.invalid_fields = []
        self.warnings = []

    def validate(self) -> Tuple[bool, Dict]:
        """
        Validate all form fields in the PDF

        Returns:
            Tuple of (success, results_dict)
            success: True if all fields valid, False otherwise
            results_dict: Dictionary with validation results
        """
        if not Path(self.pdf_path).exists():
            return False, {"error": f"PDF file not found: {self.pdf_path}"}

        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            return False, {"error": f"Failed to open PDF: {e}"}

        if len(doc) == 0:
            doc.close()
            return False, {"error": "PDF has no pages"}

        # Get all form fields from first page
        page = doc[0]
        widgets = list(page.widgets())

        if not widgets:
            doc.close()
            return False, {"error": "PDF has no form fields"}

        # Validate each field
        for widget in widgets:
            field_name = widget.field_name
            if self.is_valid_field_name(field_name):
                self.valid_fields.append(field_name)
            else:
                self.invalid_fields.append((field_name, self.get_error_message(field_name)))

        doc.close()

        # Check for common issues
        self._check_common_issues()

        success = len(self.invalid_fields) == 0

        results = {
            "valid_count": len(self.valid_fields),
            "invalid_count": len(self.invalid_fields),
            "total_count": len(widgets),
            "valid_fields": self.valid_fields,
            "invalid_fields": self.invalid_fields,
            "warnings": self.warnings,
            "success": success
        }

        return success, results

    def is_valid_field_name(self, field_name: str) -> bool:
        """
        Check if a field name matches the naming convention

        Args:
            field_name: Field name to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(self.FIELD_PATTERN.match(field_name))

    def get_error_message(self, field_name: str) -> str:
        """
        Get a descriptive error message for an invalid field name

        Args:
            field_name: Invalid field name

        Returns:
            Error message describing what's wrong
        """
        if not field_name:
            return "Empty field name"

        # Check for uppercase
        if field_name != field_name.lower():
            return "Field name must be all lowercase"

        # Check for missing js prefix
        if not field_name.startswith('js'):
            return "Field name must start with 'js'"

        # Check for invalid joystick index
        js_match = re.match(r'js(\d+)_', field_name)
        if not js_match:
            return "Invalid format (should be js{N}_{type})"

        js_num = int(js_match.group(1))
        if js_num < 1:
            return "Joystick index must be >= 1"

        # Check input type
        if '_' in field_name:
            parts = field_name.split('_')
            if len(parts) >= 2:
                input_part = parts[1]

                # Check if it's a button
                if input_part.startswith('button'):
                    if not re.match(r'button\d+', input_part):
                        return "Invalid button format (should be button{N})"

                # Check if it's a hat
                elif input_part.startswith('hat'):
                    if len(parts) < 3:
                        return "Hat switch missing direction (should be hat{N}_{direction})"
                    if not re.match(r'hat\d+', input_part):
                        return "Invalid hat format (should be hat{N}_{direction})"
                    direction = parts[2] if len(parts) > 2 else ''
                    if direction not in self.VALID_HAT_DIRECTIONS:
                        return f"Invalid hat direction (should be one of: {', '.join(self.VALID_HAT_DIRECTIONS)})"

                # Check if it's an axis
                elif input_part in ['x', 'y', 'z', 'rotx', 'roty', 'rotz']:
                    # Valid axis
                    pass

                # Check if it's a slider
                elif input_part.startswith('slider'):
                    if not re.match(r'slider\d+', input_part):
                        return "Invalid slider format (should be slider{N})"

                else:
                    return f"Unknown input type '{input_part}'"

        return "Invalid format (see docs/PDF_FIELD_NAMING.md)"

    def _check_common_issues(self):
        """Check for common issues and add warnings"""

        # Check for gaps in button numbering
        button_numbers = {}
        for field in self.valid_fields:
            match = re.match(r'js(\d+)_button(\d+)', field)
            if match:
                js_idx = match.group(1)
                btn_num = int(match.group(2))
                if js_idx not in button_numbers:
                    button_numbers[js_idx] = []
                button_numbers[js_idx].append(btn_num)

        for js_idx, buttons in button_numbers.items():
            buttons.sort()
            for i in range(1, len(buttons)):
                if buttons[i] != buttons[i-1] + 1:
                    self.warnings.append(
                        f"js{js_idx}: Button numbering gap between button{buttons[i-1]} and button{buttons[i]}"
                    )

        # Check for duplicate field names
        field_counts = {}
        all_fields = self.valid_fields + [f[0] for f in self.invalid_fields]
        for field in all_fields:
            field_counts[field] = field_counts.get(field, 0) + 1

        for field, count in field_counts.items():
            if count > 1:
                self.warnings.append(f"Duplicate field name: {field} (appears {count} times)")

    def print_results(self, results: Dict):
        """
        Print validation results in a human-readable format

        Args:
            results: Results dictionary from validate()
        """
        print("=" * 70)
        print("PDF Form Field Validation Results")
        print("=" * 70)
        print(f"PDF File: {self.pdf_path}")
        print(f"Total Fields: {results['total_count']}")
        print(f"Valid Fields: {results['valid_count']}")
        print(f"Invalid Fields: {results['invalid_count']}")
        print()

        if results['invalid_fields']:
            print("Invalid Fields:")
            print("-" * 70)
            for field_name, error in results['invalid_fields']:
                print(f"  [FAIL] {field_name}")
                print(f"         {error}")
            print()

        if results['valid_fields']:
            print("Valid Fields:")
            print("-" * 70)
            for field_name in sorted(results['valid_fields'])[:10]:  # Show first 10
                print(f"  [OK] {field_name}")
            if len(results['valid_fields']) > 10:
                print(f"  ... and {len(results['valid_fields']) - 10} more")
            print()

        if results['warnings']:
            print("Warnings:")
            print("-" * 70)
            for warning in results['warnings']:
                print(f"  [WARN] {warning}")
            print()

        print("=" * 70)
        if results['success']:
            print("Status: [OK] All field names are valid!")
        else:
            print(f"Status: [FAIL] {results['invalid_count']} invalid field name(s)")
        print("=" * 70)


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python validate_pdf_fields.py <pdf_file>")
        print()
        print("Validates PDF form field names against SC Profile Viewer convention.")
        print("See docs/PDF_FIELD_NAMING.md for details.")
        sys.exit(1)

    pdf_path = sys.argv[1]

    validator = PDFFieldValidator(pdf_path)
    success, results = validator.validate()

    validator.print_results(results)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
