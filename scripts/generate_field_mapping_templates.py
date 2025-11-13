#!/usr/bin/env python3
"""
Generate template field_mapping.json files for all new VKB devices
"""

import sys
import os
import json
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)


def extract_field_names(pdf_path):
    """Extract all form field names from a PDF"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        widgets = list(page.widgets())

        field_names = []
        for widget in widgets:
            field_names.append(widget.field_name)

        doc.close()
        return sorted(set(field_names))  # Remove duplicates and sort
    except Exception as e:
        print(f"ERROR: Failed to extract fields from {pdf_path}: {e}")
        return []


def clean_field_name(field_name):
    """
    Remove _1, _2 suffixes to get base field name

    Example: A1_A_1 -> A1_A
             MT_B_2 -> MT_B
    """
    # Remove trailing _1 or _2
    return re.sub(r'_[12]$', '', field_name)


def generate_field_mapping(pdf_path, output_path=None):
    """Generate a template field_mapping.json file"""

    field_names = extract_field_names(pdf_path)

    if not field_names:
        print(f"No fields found in {pdf_path}")
        return False

    # Group fields by base name (without _1/_2 suffix)
    base_fields = {}
    special_fields = []

    for field in field_names:
        if field in ['USER1', 'USER2']:
            special_fields.append(field)
            continue

        # Extract base name
        base = clean_field_name(field)

        if base not in base_fields:
            base_fields[base] = []
        base_fields[base].append(field)

    # Separate axes from buttons
    axis_keywords = ['AX_', '_X', '_Y', 'TWIST', 'THROTTLE', 'RUDDER', 'SLIDER', 'ROTZ', 'ROTY', 'ROTX', 'Z']

    button_fields = []
    axis_fields = []

    for base_field in sorted(base_fields.keys()):
        is_axis = any(keyword in base_field.upper() for keyword in axis_keywords)
        if is_axis:
            axis_fields.append(base_field)
        else:
            button_fields.append(base_field)

    # Create mapping structure
    mapping = {
        "comment": f"Button and axis mapping for {os.path.basename(os.path.dirname(pdf_path))}",
        "device_columns": {
            "_1": "First device (left column or single device)",
            "_2": "Second device (right column or dual setup)"
        },
        "button_mapping": {},
        "axis_mapping": {}
    }

    # Add button mappings with placeholder button numbers
    button_num = 1
    for base_field in button_fields:
        mapping["button_mapping"][base_field] = f"TODO_BUTTON_{button_num}"
        button_num += 1

    # Add axis mappings with placeholder axis names
    for base_field in axis_fields:
        # Try to guess the axis name from field name
        field_upper = base_field.upper()
        if '_X' in field_upper or field_upper.endswith('X'):
            axis_name = "TODO_AXIS_X"
        elif '_Y' in field_upper or field_upper.endswith('Y'):
            axis_name = "TODO_AXIS_Y"
        elif 'TWIST' in field_upper or 'ROTZ' in field_upper:
            axis_name = "TODO_AXIS_ROTZ"
        elif 'THROTTLE' in field_upper or field_upper.endswith('Z'):
            axis_name = "TODO_AXIS_Z"
        elif 'ROTX' in field_upper:
            axis_name = "TODO_AXIS_ROTX"
        elif 'ROTY' in field_upper:
            axis_name = "TODO_AXIS_ROTY"
        elif 'RUDDER' in field_upper:
            axis_name = "TODO_AXIS_RUDDER"
        elif 'SLIDER' in field_upper:
            axis_name = "TODO_AXIS_SLIDER"
        else:
            axis_name = "TODO_AXIS_UNKNOWN"

        mapping["axis_mapping"][base_field] = axis_name

    # Write to file
    if output_path is None:
        output_path = os.path.join(os.path.dirname(pdf_path), "field_mapping.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Created: {output_path}")
    print(f"  Buttons: {len(mapping['button_mapping'])}")
    print(f"  Axes: {len(mapping['axis_mapping'])}")

    return True


def process_all_new_devices():
    """Process all new VKB devices that don't have field_mapping.json yet"""

    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'visual-templates')

    # List of new devices (without field_mapping.json)
    new_devices = [
        'vkb_gladiator_scg_lh',
        'vkb_gladiator_scg_rh',
        'vkb_gladiator_scg_ota_lh',
        'vkb_gladiator_scg_ota_rh',
        'vkb_gunfighter_scg_lh',
        'vkb_gunfighter_scg_rh',
        'vkb_gunfighter_scg_ota_lh',
        'vkb_gunfighter_scg_ota_rh',
        'vkb_sem_v',
        'vkb_stecs',
        'vkb_stecs_stem',
        'vkb_stecs_atem',
        'vkb_stecs_spacethrottlegrip_lh',
        'vkb_stecs_spacethrottlegrip_rh',
        'vkb_thq_v',
        'vkb_thq_ww2',
        'vkb_thq_v_ww2',
    ]

    print(f"Generating field mapping templates for {len(new_devices)} devices...")
    print("=" * 80)

    success_count = 0

    for device_id in new_devices:
        device_dir = os.path.join(templates_dir, device_id)

        if not os.path.isdir(device_dir):
            print(f"\n[WARNING] Directory not found: {device_dir}")
            continue

        # Find PDF in directory
        pdf_files = [f for f in os.listdir(device_dir) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"\n[WARNING] No PDF found in {device_dir}")
            continue

        pdf_path = os.path.join(device_dir, pdf_files[0])

        # Check if field_mapping.json already exists
        mapping_path = os.path.join(device_dir, "field_mapping.json")
        if os.path.exists(mapping_path):
            print(f"\n[SKIP] {device_id} already has field_mapping.json")
            continue

        print(f"\nProcessing: {device_id}")
        print("-" * 80)

        if generate_field_mapping(pdf_path):
            success_count += 1

    print("\n" + "=" * 80)
    print(f"[OK] Generated {success_count} field mapping templates")
    print("\nNext steps:")
    print("1. Open each field_mapping.json file")
    print("2. Replace TODO_BUTTON_X with actual button numbers")
    print("3. Refer to VKB documentation or test with Star Citizen")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process specific PDF
        pdf_path = sys.argv[1]

        if not pdf_path.endswith('.pdf'):
            # Assume it's a device ID
            templates_dir = os.path.join(os.path.dirname(__file__), '..', 'visual-templates')
            device_dir = os.path.join(templates_dir, pdf_path)
            pdf_files = [f for f in os.listdir(device_dir) if f.endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(device_dir, pdf_files[0])

        generate_field_mapping(pdf_path)
    else:
        # Process all new devices
        process_all_new_devices()
