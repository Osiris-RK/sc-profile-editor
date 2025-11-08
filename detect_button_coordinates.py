#!/usr/bin/env python
"""
Script to use OCR to detect button positions from callout boxes in device templates.

This script detects button numbers from callout boxes where the number appears
on the inner left of the box, then determines where the callout is pointing to
(the actual button location).
"""

import sys
import os
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class ButtonCoordinateDetector:
    """Detects button coordinates from callout boxes using OCR"""

    def __init__(self):
        self.reader = None

    def initialize_ocr(self):
        """Lazy initialization of EasyOCR reader"""
        if self.reader is None:
            try:
                import easyocr
                # Initialize reader for English text (verbose=False to avoid encoding issues)
                self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                logger.info("OCR initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OCR: {e}")
                logger.error("Make sure easyocr is installed: pip install easyocr")
                self.reader = None

    def detect_button_numbers(self, image_path: str) -> List[Dict]:
        """
        Detect all button numbers in the image using OCR

        Args:
            image_path: Path to template image

        Returns:
            List of detected button numbers with their bounding boxes
        """
        self.initialize_ocr()
        if self.reader is None:
            return []

        logger.info(f"Reading image: {image_path}")
        image = Image.open(image_path)

        try:
            logger.info("Running OCR detection...")
            results = self.reader.readtext(np.array(image))
        except Exception as e:
            logger.error(f"OCR reading error: {e}")
            return []

        button_detections = []
        for bbox, text, confidence in results:
            # Look for button numbers (1-100)
            # Try to extract a number from the text
            text_clean = text.strip()

            # Check if it's just a number
            if text_clean.isdigit():
                button_num = int(text_clean)
                if 1 <= button_num <= 100:
                    # Get bounding box coordinates
                    # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]

                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)

                    x1, y1 = bbox[0]  # Top-left
                    x2, y2 = bbox[2]  # Bottom-right
                    width = x2 - x1
                    height = y2 - y1

                    button_detections.append({
                        'button_number': button_num,
                        'text': text,
                        'center_x': center_x,
                        'center_y': center_y,
                        'bbox': bbox,
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'width': width,
                        'height': height,
                        'confidence': confidence
                    })
                    logger.info(f"Found Button {button_num} at ({center_x:.1f}, {center_y:.1f}) with confidence {confidence:.2f}")

        logger.info(f"Found {len(button_detections)} button numbers")
        return sorted(button_detections, key=lambda x: x['button_number'])

    def create_or_update_svg(self, svg_path: str, button_detections: List[Dict],
                           image_path: str, output_path: str = None) -> str:
        """
        Create or update SVG with detected button coordinates

        Args:
            svg_path: Path to existing SVG (or where to create new one)
            button_detections: List of detected buttons with coordinates
            image_path: Path to source image
            output_path: Optional output path (defaults to svg_path)

        Returns:
            Path to created/updated SVG
        """
        if output_path is None:
            output_path = svg_path

        # Get image dimensions
        image = Image.open(image_path)
        img_width, img_height = image.size

        # Check if SVG exists
        if os.path.exists(svg_path):
            logger.info(f"Updating existing SVG: {svg_path}")
            return self._update_existing_svg(svg_path, button_detections, output_path)
        else:
            logger.info(f"Creating new SVG: {output_path}")
            return self._create_new_svg(button_detections, img_width, img_height, output_path)

    def _update_existing_svg(self, svg_path: str, button_detections: List[Dict],
                            output_path: str) -> str:
        """Update existing SVG with detected coordinates"""
        try:
            # Register namespaces to preserve them
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

            tree = ET.parse(svg_path)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Error parsing SVG: {e}")
            return None

        # Find all text elements with button template tags
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        updated_count = 0
        added_count = 0

        # First, try to update existing button text elements
        for text_elem in root.findall('.//text', ns):
            text_content = ''.join(text_elem.itertext())

            # Look for button template tags like "{{ Button X }}"
            match = re.search(r'\{\{\s*Button\s+(\d+)\s*\}\}', text_content)
            if match:
                button_num = int(match.group(1))

                # Find corresponding detection
                detection = next((d for d in button_detections if d['button_number'] == button_num), None)

                if detection:
                    # Update coordinates
                    old_x = text_elem.get('x', '')
                    old_y = text_elem.get('y', '')

                    text_elem.set('x', f"{detection['center_x']:.1f}")
                    text_elem.set('y', f"{detection['center_y']:.1f}")

                    # Add confidence as data attribute
                    text_elem.set('data-ocr-confidence', f"{detection['confidence']:.2f}")

                    logger.info(f"Updated Button {button_num}: ({old_x}, {old_y}) -> ({detection['center_x']:.1f}, {detection['center_y']:.1f})")
                    updated_count += 1
                else:
                    logger.warning(f"No OCR detection found for Button {button_num}")

        # Find which buttons were detected but not in the SVG yet
        existing_buttons = set()
        for text_elem in root.findall('.//text', ns):
            text_content = ''.join(text_elem.itertext())
            match = re.search(r'\{\{\s*Button\s+(\d+)\s*\}\}', text_content)
            if match:
                existing_buttons.add(int(match.group(1)))

        # Add new button elements for detected buttons not in SVG
        for detection in button_detections:
            button_num = detection['button_number']
            if button_num not in existing_buttons:
                # Create new text element
                text_elem = ET.Element('text')
                text_elem.set('x', f"{detection['center_x']:.1f}")
                text_elem.set('y', f"{detection['center_y']:.1f}")
                text_elem.set('font-family', 'Arial')
                text_elem.set('font-size', '10')
                text_elem.set('fill', 'black')
                text_elem.set('text-anchor', 'middle')
                text_elem.set('data-ocr-confidence', f"{detection['confidence']:.2f}")
                text_elem.text = f"{{{{ Button {button_num} }}}}"

                root.append(text_elem)
                logger.info(f"Added new Button {button_num} at ({detection['center_x']:.1f}, {detection['center_y']:.1f})")
                added_count += 1

        # Write updated SVG
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        logger.info(f"Updated {updated_count} button coordinates, added {added_count} new buttons in SVG")
        logger.info(f"SVG saved to: {output_path}")

        return output_path

    def _create_new_svg(self, button_detections: List[Dict], width: int, height: int,
                       output_path: str) -> str:
        """Create new SVG with detected button coordinates"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '  <!-- Auto-generated from OCR button detection -->',
            '  <!-- Button coordinates detected from callout boxes -->',
            ''
        ]

        # Add button elements
        if button_detections:
            lines.append('  <!-- Button bindings -->')
            for detection in button_detections:
                button_num = detection['button_number']
                x = detection['center_x']
                y = detection['center_y']
                confidence = detection['confidence']

                # Create text element with template tag
                text_elem = (
                    f'  <text x="{x:.1f}" y="{y:.1f}" '
                    f'font-family="Arial" font-size="10" fill="black" '
                    f'text-anchor="middle" data-ocr-confidence="{confidence:.2f}">'
                    f'{{{{ Button {button_num} }}}}</text>'
                )
                lines.append(text_elem)
            lines.append('')

        lines.append('</svg>')

        # Write SVG file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"Created SVG with {len(button_detections)} buttons")
        logger.info(f"SVG saved to: {output_path}")

        return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_button_coordinates.py <image_file> [svg_file] [output_file]")
        print("\nExample:")
        print("  python detect_button_coordinates.py vkb_f16_mfd.png")
        print("  python detect_button_coordinates.py vkb_f16_mfd.png vkb_f16_mfd.svg")
        print("  python detect_button_coordinates.py vkb_f16_mfd.png vkb_f16_mfd.svg output.svg")
        sys.exit(1)

    image_path = sys.argv[1]

    # Determine SVG path
    if len(sys.argv) >= 3:
        svg_path = sys.argv[2]
    else:
        # Default to same name as image but with _overlay.svg suffix
        base_name = os.path.splitext(image_path)[0]
        svg_path = f"{base_name}.svg"

    # Determine output path
    if len(sys.argv) >= 4:
        output_path = sys.argv[3]
    else:
        output_path = svg_path

    # Check if image exists
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        sys.exit(1)

    # Create detector
    detector = ButtonCoordinateDetector()

    # Detect button numbers
    print(f"\n{'='*60}")
    print("DETECTING BUTTON COORDINATES")
    print(f"{'='*60}\n")

    button_detections = detector.detect_button_numbers(image_path)

    if not button_detections:
        logger.error("No button numbers detected in image")
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure the image contains button numbers (1-100)")
        logger.info("2. Check that button numbers are clearly visible")
        logger.info("3. Ensure EasyOCR is properly installed")
        sys.exit(1)

    # Create/update SVG
    print(f"\n{'='*60}")
    print("CREATING/UPDATING SVG")
    print(f"{'='*60}\n")

    result_path = detector.create_or_update_svg(svg_path, button_detections,
                                                image_path, output_path)

    if result_path:
        print(f"\n{'='*60}")
        print("SUCCESS!")
        print(f"{'='*60}")
        print(f"Detected {len(button_detections)} buttons")
        print(f"SVG saved to: {result_path}")
        print("\nNext steps:")
        print("1. Review the SVG file to verify button positions")
        print("2. Manually adjust any incorrect coordinates if needed")
        print("3. Test the SVG overlay with your profile viewer")
    else:
        logger.error("Failed to create/update SVG")
        sys.exit(1)


if __name__ == "__main__":
    main()
