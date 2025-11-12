"""
OCR-based annotation system for detecting and replacing template tags in images
"""

import re
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


class OCRAnnotator:
    """Uses OCR to detect template tags in images and replace them with bindings"""

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
                logger.error(f"Error initializing OCR: {e}", exc_info=True)
                self.reader = None

    def process_template_image(self, image_path: str, bindings_map: dict) -> Image:
        """
        Process a template image, detecting and replacing template tags

        Args:
            image_path: Path to template image
            bindings_map: Dictionary mapping input labels to action labels

        Returns:
            PIL Image with replaced text
        """
        # Initialize OCR if needed
        self.initialize_ocr()
        if self.reader is None:
            return Image.open(image_path)

        # Open image
        image = Image.open(image_path)

        # Detect text in image
        try:
            results = self.reader.readtext(np.array(image))
        except Exception as e:
            logger.error(f"OCR reading error: {e}", exc_info=True)
            return image

        # Process results and replace template tags
        annotated_image = self.replace_template_tags(image, results, bindings_map)

        return annotated_image

    def replace_template_tags(self, image: Image, ocr_results: list, bindings_map: dict) -> Image:
        """
        Replace detected template tags with actual bindings

        Args:
            image: PIL Image
            ocr_results: List of OCR results [(bbox, text, confidence), ...]
            bindings_map: Dictionary mapping input labels to action labels

        Returns:
            PIL Image with replaced text
        """
        # Create a copy of the image
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)

        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()

        # Process each detected text
        for bbox, text, confidence in ocr_results:
            # Check if this text is a template tag
            template_match = re.search(r'\{\{\s*([^}]+)\s*\}\}', text)

            if template_match:
                # Extract the input label from template tag
                input_label = template_match.group(1).strip()

                # Look up the binding
                action_label = bindings_map.get(input_label, input_label)

                # Get bounding box coordinates
                # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]  # Bottom right

                # Calculate box dimensions
                box_width = x2 - x1
                box_height = y2 - y1

                # Clear the old text (draw white rectangle)
                draw.rectangle([x1, y1, x2, y2], fill='white')

                # Draw the new text centered in the box
                # Try to fit text in box
                font_size = 10
                while font_size > 6:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()

                    bbox_test = draw.textbbox((0, 0), action_label, font=font)
                    text_width = bbox_test[2] - bbox_test[0]
                    text_height = bbox_test[3] - bbox_test[1]

                    if text_width <= box_width - 4 and text_height <= box_height - 4:
                        break
                    font_size -= 1

                # Center the text
                text_x = x1 + (box_width - text_width) / 2
                text_y = y1 + (box_height - text_height) / 2

                # Draw the new text
                draw.text((text_x, text_y), action_label, fill='black', font=font)

                logger.debug(f"Replaced '{input_label}' with '{action_label}' at ({x1}, {y1})")

        return annotated

    def detect_template_tags(self, image_path: str) -> list:
        """
        Detect all template tags in an image (for debugging)

        Args:
            image_path: Path to template image

        Returns:
            List of detected template tags
        """
        self.initialize_ocr()
        if self.reader is None:
            return []

        image = Image.open(image_path)

        try:
            results = self.reader.readtext(np.array(image))
        except Exception as e:
            logger.error(f"OCR reading error: {e}", exc_info=True)
            return []

        tags = []
        for bbox, text, confidence in results:
            template_match = re.search(r'\{\{\s*([^}]+)\s*\}\}', text)
            if template_match:
                tags.append({
                    'tag': template_match.group(1).strip(),
                    'bbox': bbox,
                    'confidence': confidence
                })

        return tags
