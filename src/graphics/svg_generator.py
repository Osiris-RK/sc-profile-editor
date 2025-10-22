"""
SVG overlay generator using OCR to detect template tags in images
"""

import os
import json
import re
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional, Set
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class SVGOverlayGenerator:
    """Generates SVG overlay files from template images using OCR"""

    def __init__(self):
        self.reader = None
        self.config = None
        self.profile_buttons = set()  # Buttons found in profile XML

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

    def parse_profile_buttons(self, profile_path: str, joystick_instance: int = 1,
                             device_name_filter: str = None) -> Dict[str, str]:
        """
        Parse profile XML to extract all MAPPED inputs (buttons, axes, hats) for a specific joystick

        Args:
            profile_path: Path to Star Citizen profile XML
            joystick_instance: Joystick instance number (default 1)
            device_name_filter: Optional device name to match (e.g., "VPC Stick MT-50CM3")

        Returns:
            Dict mapping input labels to action names (e.g., {"Button 1": "v_attack1", "Axis X": "v_roll", ...})
        """
        if not os.path.exists(profile_path):
            logger.warning(f"Profile not found: {profile_path}")
            return {}

        try:
            tree = ET.parse(profile_path)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Error parsing profile XML: {e}", exc_info=True)
            return {}

        input_mappings = {}
        js_prefix = f"js{joystick_instance}_"

        # Find all action maps
        for action_map in root.findall('.//actionmap'):
            # Find all actions within this action map
            for action in action_map.findall('.//action'):
                action_name = action.get('name', '')

                # Find rebind elements within this action
                for rebind in action.findall('.//rebind'):
                    input_code = rebind.get('input', '').strip()

                    # Skip empty or whitespace-only inputs (cleared bindings)
                    if not input_code or input_code == js_prefix or input_code == f"{js_prefix} ":
                        continue

                    # Check if it's an input for our joystick instance and has an action
                    if input_code.startswith(js_prefix) and action_name:
                        # Parse the input code to get a human-readable label
                        input_label = self._parse_input_code(input_code, joystick_instance)
                        if input_label:
                            # Store the mapping (last one wins if multiple bindings)
                            input_mappings[input_label] = action_name

        if input_mappings:
            logger.info(f"Found {len(input_mappings)} mapped inputs in profile for joystick instance {joystick_instance}")
            logger.debug(f"Mapped inputs: {', '.join(sorted(input_mappings.keys()))}")

        return input_mappings

    def _parse_input_code(self, input_code: str, joystick_instance: int) -> Optional[str]:
        """
        Parse an input code into a human-readable label

        Args:
            input_code: Input code like "js1_button7", "js1_x", "js1_hat1_up"
            joystick_instance: Joystick instance number

        Returns:
            Human-readable label like "Button 7", "Axis X", "Hat 1 Up", or None if not parseable
        """
        js_prefix = f"js{joystick_instance}_"
        if not input_code.startswith(js_prefix):
            return None

        # Remove the joystick prefix
        input_part = input_code[len(js_prefix):]

        # Parse button (e.g., "button7" -> "Button 7")
        button_match = re.match(r'button(\d+)', input_part)
        if button_match:
            return f"Button {button_match.group(1)}"

        # Parse axis (e.g., "x" -> "Axis X", "rotz" -> "Axis ROTZ")
        axis_match = re.match(r'(x|y|z|rotx|roty|rotz|slider1|slider2)', input_part, re.IGNORECASE)
        if axis_match:
            axis_name = axis_match.group(1).upper()
            return f"Axis {axis_name}"

        # Parse hat (e.g., "hat1_up" -> "Hat 1 Up")
        hat_match = re.match(r'hat(\d+)_(up|down|left|right)', input_part)
        if hat_match:
            hat_num = hat_match.group(1)
            direction = hat_match.group(2).capitalize()
            return f"Hat {hat_num} {direction}"

        # Unknown input type
        logger.debug(f"Unknown input type: {input_code}")
        return None

    def load_config(self, config_path: str) -> Optional[Dict]:
        """
        Load SVG styling configuration from a JSON file

        Args:
            config_path: Path to config.json file

        Returns:
            Configuration dictionary or None if not found/invalid
        """
        if not os.path.exists(config_path):
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from: {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}", exc_info=True)
            return None

    def get_style_config(self, config: Optional[Dict] = None) -> Dict:
        """
        Get styling configuration with defaults

        Args:
            config: Configuration dictionary (optional)

        Returns:
            Dict with font_family, font_size, fill, text_anchor, stroke, background, etc.
        """
        defaults = {
            'font_family': 'Arial',
            'font_size': 10,
            'fill': 'black',
            'text_anchor': 'middle',
            'stroke': None,
            'stroke_width': None,
            'text_wrap': {
                'enabled': False,
                'max_words_per_line': 2,
                'line_spacing': 1.2
            },
            'background': {
                'enabled': False,
                'fill': 'white',
                'fill_opacity': 0,
                'padding': 2,
                'border_radius': 2,
                'border_color': 'none',
                'border_width': 0,
                'stroke_opacity': 1.0
            }
        }

        if config is None:
            return defaults

        # Merge config with defaults
        style = defaults.copy()
        if 'svg_style' in config:
            config_copy = config['svg_style'].copy()

            # Handle nested dicts separately to merge properly
            nested_keys = ['background', 'text_wrap']
            for key in nested_keys:
                if key in config_copy:
                    nested_config = config_copy[key]
                    style[key] = defaults[key].copy()
                    style[key].update(nested_config)
                    del config_copy[key]

            # Update remaining flat properties
            style.update(config_copy)

        return style

    def get_table_config(self, config: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get unmapped table configuration

        Args:
            config: Configuration dictionary (optional)

        Returns:
            Dict with table settings or None if disabled
        """
        defaults = {
            'enabled': False,
            'x': 20,
            'y': 20,
            'font_size': 9,
            'font_family': 'Arial',
            'fill': 'black',
            'stroke': 'white',
            'stroke_width': 1,
            'row_height': 18,
            'column_widths': [200, 150],
            'background': {
                'enabled': True,
                'fill': 'white',
                'fill_opacity': 0.9,
                'border_color': 'black',
                'border_width': 1,
                'stroke_opacity': 1.0
            }
        }

        if config is None or 'unmapped_table' not in config:
            return defaults

        # Merge with defaults
        table_config = defaults.copy()
        if 'background' in config['unmapped_table']:
            table_config['background'] = defaults['background'].copy()
            table_config['background'].update(config['unmapped_table']['background'])

            # Remove background from config_copy to avoid double-updating
            config_copy = config['unmapped_table'].copy()
            del config_copy['background']
            table_config.update(config_copy)
        else:
            table_config.update(config['unmapped_table'])

        return table_config if table_config['enabled'] else None

    def detect_template_tags(self, image_path: str) -> List[Dict]:
        """
        Detect all template tags in an image

        Args:
            image_path: Path to template image

        Returns:
            List of detected tags with positions and text
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
            logger.error(f"OCR reading error: {e}", exc_info=True)
            return []

        tags = []
        for bbox, text, confidence in results:
            # Check if this text contains template tag markers
            if '{{' in text and '}}' in text:
                # Extract the content between {{ }}
                import re
                match = re.search(r'\{\{\s*([^}]+)\s*\}\}', text)
                if match:
                    tag_content = match.group(1).strip()

                    # Get bounding box center
                    # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]

                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)

                    # Calculate box dimensions
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[2]
                    width = x2 - x1
                    height = y2 - y1

                    tags.append({
                        'tag': tag_content,
                        'x': center_x,
                        'y': center_y,
                        'bbox': bbox,
                        'width': width,
                        'height': height,
                        'confidence': confidence,
                        'original_text': text
                    })

        logger.info(f"Found {len(tags)} template tags")
        return tags

    def generate_svg_overlay(self, image_path: str, output_path: str = None,
                            font_family: str = None, font_size: int = None,
                            config_path: str = None, profile_path: str = None,
                            joystick_instance: int = 1) -> str:
        """
        Generate SVG overlay file from template image

        Args:
            image_path: Path to template image
            output_path: Path to save SVG (optional, defaults to same name as image)
            font_family: Font family for text (optional, overrides config)
            font_size: Font size for text (optional, overrides config)
            config_path: Path to config.json (optional, auto-detected if in same dir)
            profile_path: Path to SC profile XML to find unmapped buttons (optional)
            joystick_instance: Joystick instance number if using profile_path (default 1)

        Returns:
            Path to generated SVG file
        """
        # Get image dimensions
        image = Image.open(image_path)
        img_width, img_height = image.size

        # Try to load config from same directory as image if not specified
        if config_path is None:
            image_dir = os.path.dirname(image_path)
            auto_config_path = os.path.join(image_dir, 'config.json')
            if os.path.exists(auto_config_path):
                config_path = auto_config_path

        # Load configuration
        config = None
        if config_path:
            config = self.load_config(config_path)

        # Get style configuration
        style = self.get_style_config(config)

        # Override with explicit parameters if provided
        if font_family is not None:
            style['font_family'] = font_family
        if font_size is not None:
            style['font_size'] = font_size

        # Parse profile for mapped buttons if provided
        profile_buttons = {}
        if profile_path:
            logger.info(f"Parsing profile: {profile_path}")
            profile_buttons = self.parse_profile_buttons(profile_path, joystick_instance)

        # Detect template tags
        tags = self.detect_template_tags(image_path)

        if not tags:
            logger.warning("No template tags found in image")
            if not profile_buttons:
                return None
            logger.info("Will create SVG with profile buttons only")

        # Get table configuration
        table_config = self.get_table_config(config)

        # Create SVG
        svg_content = self._create_svg_content(tags, img_width, img_height, style, profile_buttons, table_config)

        # Determine output path
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_overlay.svg"

        # Write SVG file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        logger.info(f"SVG overlay saved to: {output_path}")
        return output_path

    def _wrap_text(self, text: str, max_words_per_line: int) -> List[str]:
        """
        Wrap text into multiple lines based on word count

        Args:
            text: Text to wrap
            max_words_per_line: Maximum words per line

        Returns:
            List of text lines
        """
        words = text.split()
        if len(words) <= max_words_per_line:
            return [text]

        lines = []
        for i in range(0, len(words), max_words_per_line):
            line_words = words[i:i + max_words_per_line]
            lines.append(' '.join(line_words))

        return lines

    def _create_svg_content(self, tags: List[Dict], width: int, height: int,
                           style: Dict, profile_buttons: Dict[str, str] = None,
                           table_config: Optional[Dict] = None) -> str:
        """Create SVG content from detected tags and optionally add unmapped buttons table

        Args:
            profile_buttons: Dict mapping button labels to action names (e.g., {"Button 1": "v_attack1"})
        """

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '  <!-- Auto-generated overlay from OCR detection -->',
            '  <!-- Edit this file to adjust text positions and styling -->',
            ''
        ]

        # Group tags by type for organization
        button_tags = []
        hat_tags = []
        other_tags = []
        detected_buttons = set()

        for tag_info in tags:
            tag = tag_info['tag']
            if tag.startswith('Button'):
                button_tags.append(tag_info)
                detected_buttons.add(tag)
            elif 'Hat' in tag:
                hat_tags.append(tag_info)
            else:
                other_tags.append(tag_info)

        # Add button tags
        if button_tags:
            lines.append('  <!-- Button bindings -->')
            for tag_info in sorted(button_tags, key=lambda x: int(x['tag'].split()[-1]) if x['tag'].split()[-1].isdigit() else 0):
                lines.append(self._create_text_element(tag_info, style))
            lines.append('')

        # Add hat tags
        if hat_tags:
            lines.append('  <!-- Hat switch bindings -->')
            for tag_info in hat_tags:
                lines.append(self._create_text_element(tag_info, style))
            lines.append('')

        # Add other tags
        if other_tags:
            lines.append('  <!-- Other bindings -->')
            for tag_info in other_tags:
                lines.append(self._create_text_element(tag_info, style))
            lines.append('')

        # Add unmapped inputs - inputs that are mapped in profile but don't have template tags
        if profile_buttons:
            # Find inputs that have mappings but no template tag detected
            mapped_input_labels = set(profile_buttons.keys())
            unmapped_inputs = mapped_input_labels - detected_buttons

            if unmapped_inputs:
                # Sort inputs (try to sort by number if present, otherwise alphabetically)
                def sort_key(label):
                    # Extract number if present (e.g., "Button 7" -> 7, "Hat 1 Up" -> 1)
                    match = re.search(r'\d+', label)
                    return (0, int(match.group())) if match else (1, label)

                sorted_inputs = sorted(unmapped_inputs, key=sort_key)

                if table_config and table_config.get('enabled'):
                    # Create table for unmapped inputs
                    lines.append('  <!-- Unmapped inputs table -->')
                    lines.append('  <!-- Mapped inputs without template tags on the graphic -->')
                    table_svg = self._create_unmapped_table(sorted_inputs, table_config)
                    lines.append(table_svg)
                    lines.append('')
                    logger.info(f"Added unmapped inputs table with {len(unmapped_inputs)} mapped inputs")
                else:
                    # Legacy: Add as commented-out elements
                    lines.append('  <!-- Mapped inputs without template tags on the graphic -->')
                    lines.append('  <!-- These have empty x/y coordinates - add coordinates to enable them -->')
                    lines.append('')

                    for input_label in sorted_inputs:
                        # Create tag_info with empty coordinates
                        tag_info = {
                            'tag': input_label,
                            'x': '',
                            'y': '',
                            'width': 0,
                            'height': 0,
                            'confidence': 0.0
                        }
                        # Create commented-out text element with all styling
                        element = self._create_text_element(tag_info, style, commented=True)
                        lines.append(element)

                    lines.append('')
                    logger.info(f"Added {len(unmapped_inputs)} unmapped inputs with empty coordinates")
                    logger.debug(f"Unmapped inputs: {', '.join(sorted_inputs)}")

        lines.append('</svg>')

        return '\n'.join(lines)

    def _create_unmapped_table(self, input_labels: List[str], table_config: Dict) -> str:
        """
        Create SVG table element for unmapped inputs

        Args:
            input_labels: List of input labels (e.g., ["Button 1", "Axis X", "Hat 1 Up"])
            table_config: Table configuration dictionary

        Returns:
            SVG group element containing the table
        """
        x = table_config['x']
        y = table_config['y']
        row_height = table_config['row_height']
        col_widths = table_config['column_widths']
        font_size = table_config['font_size']
        font_family = table_config['font_family']
        fill = table_config['fill']
        stroke = table_config.get('stroke')
        stroke_width = table_config.get('stroke_width', 0)

        # Calculate table dimensions
        table_width = sum(col_widths)
        table_height = (len(input_labels) + 1) * row_height  # +1 for header

        elements = ['  <g id="unmapped-table">']

        # Add background rectangle if enabled
        if table_config['background']['enabled']:
            bg = table_config['background']
            bg_rect = (f'    <rect x="{x}" y="{y}" width="{table_width}" height="{table_height}" '
                      f'fill="{bg["fill"]}" fill-opacity="{bg.get("fill_opacity", bg.get("opacity", 0.9))}" '
                      f'stroke="{bg["border_color"]}" stroke-width="{bg["border_width"]}" '
                      f'stroke-opacity="{bg.get("stroke_opacity", 1.0)}"/>')
            elements.append(bg_rect)

        # Add header row
        header_y = y + row_height / 2 + font_size / 3
        header_attrs = [
            f'x="{x + col_widths[0] / 2}"',
            f'y="{header_y}"',
            f'font-family="{font_family}"',
            f'font-size="{font_size}"',
            f'font-weight="bold"',
            f'fill="{fill}"',
            f'text-anchor="middle"'
        ]
        if stroke:
            header_attrs.append(f'stroke="{stroke}"')
            header_attrs.append(f'stroke-width="{stroke_width}"')

        elements.append(f'    <text {" ".join(header_attrs)}>Action</text>')

        header_attrs[0] = f'x="{x + col_widths[0] + col_widths[1] / 2}"'
        elements.append(f'    <text {" ".join(header_attrs)}>Input</text>')

        # Add horizontal line after header
        if table_config['background']['enabled']:
            line_y = y + row_height
            bg = table_config['background']
            elements.append(
                f'    <line x1="{x}" y1="{line_y}" x2="{x + table_width}" y2="{line_y}" '
                f'stroke="{bg["border_color"]}" stroke-width="{bg["border_width"]}"/>'
            )

        # Add data rows
        for i, input_label in enumerate(input_labels):
            row_y = y + (i + 2) * row_height - row_height / 2 + font_size / 3

            # Action column (with template tag)
            action_attrs = [
                f'x="{x + 5}"',  # Left-aligned with padding
                f'y="{row_y}"',
                f'font-family="{font_family}"',
                f'font-size="{font_size}"',
                f'fill="{fill}"',
                f'text-anchor="start"'
            ]
            if stroke:
                action_attrs.append(f'stroke="{stroke}"')
                action_attrs.append(f'stroke-width="{stroke_width}"')

            # Use template tag for action (will be replaced during rendering)
            elements.append(f'    <text {" ".join(action_attrs)}>{{{{ {input_label} }}}}</text>')

            # Input column (show input label)
            input_attrs = [
                f'x="{x + col_widths[0] + 5}"',  # Left-aligned with padding
                f'y="{row_y}"',
                f'font-family="{font_family}"',
                f'font-size="{font_size}"',
                f'fill="{fill}"',
                f'text-anchor="start"'
            ]
            if stroke:
                input_attrs.append(f'stroke="{stroke}"')
                input_attrs.append(f'stroke-width="{stroke_width}"')

            elements.append(f'    <text {" ".join(input_attrs)}>{input_label}</text>')

        # Add vertical separator line between columns
        if table_config['background']['enabled']:
            bg = table_config['background']
            line_x = x + col_widths[0]
            elements.append(
                f'    <line x1="{line_x}" y1="{y}" x2="{line_x}" y2="{y + table_height}" '
                f'stroke="{bg["border_color"]}" stroke-width="{bg["border_width"]}"/>'
            )

        elements.append('  </g>')

        return '\n'.join(elements)

    def _create_text_element(self, tag_info: Dict, style: Dict, commented: bool = False) -> str:
        """
        Create SVG text element for a tag with optional background and stroke

        Args:
            tag_info: Dictionary with tag, x, y, width, height, confidence
            style: Style configuration dictionary
            commented: If True, wrap the entire element in XML comments
        """
        tag = tag_info['tag']
        x = tag_info['x']
        y = tag_info['y']
        width = tag_info['width']
        height = tag_info['height']
        confidence = tag_info['confidence']

        # Format the template tag
        template_tag = f"{{{{ {tag} }}}}"

        # Wrap text if enabled
        text_lines = []
        if style['text_wrap']['enabled']:
            text_lines = self._wrap_text(template_tag, style['text_wrap']['max_words_per_line'])
        else:
            text_lines = [template_tag]

        elements = []

        # Calculate line spacing
        line_height = style['font_size'] * style['text_wrap']['line_spacing']
        num_lines = len(text_lines)

        # Adjust y position for multi-line text (center it)
        if num_lines > 1:
            total_height = line_height * (num_lines - 1)
            y_start = y - (total_height / 2)
        else:
            y_start = y

        # Add background rectangle if enabled
        if style['background']['enabled']:
            bg = style['background']
            padding = bg['padding']

            # Estimate text dimensions based on font size
            # This is approximate - actual rendering may vary
            char_width = style['font_size'] * 0.6  # Rough estimate

            # Find longest line for width calculation
            max_line_length = max(len(line) for line in text_lines)
            text_width = max_line_length * char_width
            text_height = style['font_size'] * 1.2 * num_lines

            # Calculate rectangle position and size
            rect_x = x - (text_width / 2) - padding
            rect_y = y_start - (style['font_size'] * 0.8) - padding
            rect_width = text_width + (padding * 2)
            rect_height = text_height + (padding * 2)

            # Create background rectangle
            rect_attrs = [
                f'x="{rect_x:.1f}"',
                f'y="{rect_y:.1f}"',
                f'width="{rect_width:.1f}"',
                f'height="{rect_height:.1f}"',
                f'fill="{bg["fill"]}"',
                f'fill-opacity="{bg.get("fill_opacity", bg.get("opacity", 0.8))}"'
            ]

            if bg['border_radius'] > 0:
                rect_attrs.append(f'rx="{bg["border_radius"]}"')

            # Add border if configured
            if 'border_color' in bg and bg['border_color'] != 'none':
                rect_attrs.append(f'stroke="{bg["border_color"]}"')
                rect_attrs.append(f'stroke-width="{bg.get("border_width", 1)}"')
                rect_attrs.append(f'stroke-opacity="{bg.get("stroke_opacity", 1.0)}"')

            elements.append(f'  <rect {" ".join(rect_attrs)}/>')

        # Build text element attributes
        # Handle empty coordinates for unmapped buttons
        if x == '' or y == '':
            x_str = '""'
            y_str = '""'
            y_start = ''
        else:
            x_str = f'"{x:.1f}"'
            y_str = f'"{y_start:.1f}"'

        text_attrs = [
            f'x={x_str}',
            f'y={y_str}',
            f'font-family="{style["font_family"]}"',
            f'font-size="{style["font_size"]}"',
            f'fill="{style["fill"]}"',
            f'text-anchor="{style["text_anchor"]}"'
        ]

        # Add stroke if specified
        if style['stroke'] is not None:
            text_attrs.append(f'stroke="{style["stroke"]}"')
            if style['stroke_width'] is not None:
                text_attrs.append(f'stroke-width="{style["stroke_width"]}"')

        # Add data attributes
        if x == '' or y == '':
            # Empty coordinates
            text_attrs.extend([
                f'data-confidence="{confidence:.2f}"',
                'data-max-width="0"',
                'data-max-height="0"'
            ])
        else:
            text_attrs.extend([
                f'data-confidence="{confidence:.2f}"',
                f'data-max-width="{width:.1f}"',
                f'data-max-height="{height:.1f}"'
            ])

        # Create text element with tspan for multi-line
        if num_lines == 1:
            # Single line - simple text element
            elements.append(f'  <text {" ".join(text_attrs)}>{text_lines[0]}</text>')
        else:
            # Multi-line - use tspan elements
            text_element = f'  <text {" ".join(text_attrs)}>'
            for i, line in enumerate(text_lines):
                dy = line_height if i > 0 else 0
                text_element += f'\n    <tspan x="{x:.1f}" dy="{dy:.1f}">{line}</tspan>'
            text_element += '\n  </text>'
            elements.append(text_element)

        # Get the final element string
        if len(elements) > 1:
            result = '  <g>\n    ' + '\n    '.join(elements) + '\n  </g>'
        else:
            result = elements[0]

        # Wrap in XML comment if requested
        if commented:
            # Split into lines and comment each line
            result_lines = result.split('\n')
            commented_lines = ['  <!-- ' + line[2:] + ' -->' for line in result_lines]
            return '\n'.join(commented_lines)

        return result

    def update_existing_svg(self, svg_path: str, image_path: str) -> str:
        """
        Update an existing SVG overlay with newly detected tags

        Args:
            svg_path: Path to existing SVG overlay
            image_path: Path to template image

        Returns:
            Path to updated SVG file
        """
        # Detect current tags in image
        new_tags = self.detect_template_tags(image_path)

        if not new_tags:
            logger.info("No new tags detected")
            return svg_path

        # Parse existing SVG
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Error parsing SVG: {e}", exc_info=True)
            return None

        # Extract existing tags
        existing_tags = set()
        ns = {'svg': 'http://www.w3.org/2000/svg'}

        for text_elem in root.findall('.//svg:text', ns):
            text_content = text_elem.text or ''
            if '{{' in text_content and '}}' in text_content:
                import re
                match = re.search(r'\{\{\s*([^}]+)\s*\}\}', text_content)
                if match:
                    existing_tags.add(match.group(1).strip())

        # Find new tags that don't exist yet
        tags_to_add = [t for t in new_tags if t['tag'] not in existing_tags]

        if not tags_to_add:
            logger.info("No new tags to add (all already exist in SVG)")
            return svg_path

        logger.info(f"Adding {len(tags_to_add)} new tags to SVG")

        # Add new tags to SVG
        for tag_info in tags_to_add:
            text_elem = ET.Element('text')
            text_elem.set('x', f"{tag_info['x']:.1f}")
            text_elem.set('y', f"{tag_info['y']:.1f}")
            text_elem.set('font-family', 'Arial')
            text_elem.set('font-size', '10')
            text_elem.set('fill', 'black')
            text_elem.set('text-anchor', 'middle')
            text_elem.set('data-confidence', f"{tag_info['confidence']:.2f}")
            text_elem.text = f"{{{{ {tag_info['tag']} }}}}"
            root.append(text_elem)

        # Save updated SVG
        tree.write(svg_path, encoding='utf-8', xml_declaration=True)
        logger.info(f"Updated SVG saved to: {svg_path}")

        return svg_path
