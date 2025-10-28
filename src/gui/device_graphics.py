"""
Device graphics widget for displaying and annotating device images
"""

import sys
import os
import logging
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QGraphicsView, QGraphicsScene,
                              QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem,
                              QFileDialog, QMessageBox)
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QBrush, QImage
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graphics.template_manager import TemplateManager, DeviceTemplate
from models.profile_model import ControlProfile, Device, ActionBinding
from parser.label_generator import LabelGenerator
from utils.device_splitter import is_vkb_with_sem, get_base_stick_name

logger = logging.getLogger(__name__)


class ResizableGraphicsView(QGraphicsView):
    """Custom QGraphicsView that re-fits content on resize"""

    def __init__(self, scene):
        super().__init__(scene)
        self._fit_on_resize = True

    def resizeEvent(self, event):
        """Re-fit the view when resized"""
        super().resizeEvent(event)
        if self._fit_on_resize and self.scene() and not self.scene().sceneRect().isEmpty():
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class DeviceGraphicsWidget(QWidget):
    """Widget for displaying device with control annotations"""

    # Signal emitted when export availability changes
    export_available_changed = pyqtSignal(bool)

    def __init__(self, templates_dir: str):
        super().__init__()
        self.templates_dir = templates_dir
        self.template_manager = TemplateManager(templates_dir)
        self.current_profile: ControlProfile = None
        self.current_device: Device = None
        self.current_template: DeviceTemplate = None
        self.current_device_name: str = None  # Actual device name to display (may differ from current_device.product_name for split devices)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Device selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Device:"))

        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        selection_layout.addWidget(self.device_combo, 1)

        layout.addLayout(selection_layout)

        # Graphics view
        self.scene = QGraphicsScene()
        self.view = ResizableGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        layout.addWidget(self.view)

        # Status label
        self.status_label = QLabel("No device selected")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.status_label)

    def load_profile(self, profile: ControlProfile):
        """Load a profile and populate device list"""
        self.current_profile = profile
        self.device_combo.clear()

        if not profile:
            return

        # Add devices that have templates
        for device in profile.devices:
            if device.device_type == 'joystick':  # Focus on joysticks for now
                device_name = device.product_name if device.product_name else f"Joystick {device.instance}"

                # Check if this is a VKB device with SEM module
                if is_vkb_with_sem(device_name):
                    # Add two entries: base stick and SEM module
                    base_stick_name = get_base_stick_name(device_name)

                    # Check if templates exist for both
                    base_template = self.template_manager.find_template(base_stick_name)
                    sem_template = self.template_manager.find_template("VKB SEM")

                    if base_template:
                        # Store device and base stick name in item data as tuple
                        self.device_combo.addItem(f"{base_stick_name} (Template available)", (device, base_stick_name))
                    else:
                        self.device_combo.addItem(f"{base_stick_name} (No template)", (device, base_stick_name))

                    if sem_template:
                        # Store device and "VKB SEM" name in item data as tuple
                        self.device_combo.addItem(f"VKB SEM (Template available)", (device, "VKB SEM"))
                    else:
                        self.device_combo.addItem(f"VKB SEM (No template)", (device, "VKB SEM"))
                else:
                    # Regular device (not split)
                    template = self.template_manager.find_template(device.product_name or "")

                    if template:
                        # Store device and device name as tuple for consistency
                        self.device_combo.addItem(f"{device_name} (Template available)", (device, device_name))
                    else:
                        self.device_combo.addItem(f"{device_name} (No template)", (device, device_name))

        if self.device_combo.count() == 0:
            self.status_label.setText("No devices with templates found")
            self.device_combo.addItem("No devices available", None)
        else:
            self.status_label.setText(f"Found {self.device_combo.count()} device(s)")

    def select_device_by_name(self, device_name: str) -> bool:
        """
        Select a device in the combo box by its display name.
        Returns True if device was found and selected, False otherwise.
        """
        if not device_name:
            return False

        # Search through combo box items
        for i in range(self.device_combo.count()):
            item_text = self.device_combo.itemText(i)
            item_data = self.device_combo.itemData(i)

            # Check if this matches the device name
            # Compare against the actual device name stored in item_data
            if item_data:
                stored_device, stored_name = item_data
                # Match against the product name or the stored device name
                if (stored_device.product_name == device_name or
                    stored_name == device_name or
                    item_text.startswith(device_name)):
                    self.device_combo.setCurrentIndex(i)
                    return True

        return False

    def on_device_changed(self, index: int):
        """Handle device selection change"""
        if index < 0:
            return

        item_data = self.device_combo.itemData(index)
        if not item_data:
            self.scene.clear()
            self.status_label.setText("No device selected")
            self.export_available_changed.emit(False)
            return

        # Item data is a tuple: (device, device_name)
        self.current_device, self.current_device_name = item_data
        self.load_device_graphic()

    def load_device_graphic(self):
        """Load and display device graphic with annotations"""
        if not self.current_device or not self.current_device_name:
            return

        # Find template for this device (use current_device_name for split devices)
        template = self.template_manager.find_template(self.current_device_name)

        if not template:
            self.scene.clear()
            self.status_label.setText("No template available for this device")
            self.export_available_changed.emit(False)
            return

        self.current_template = template

        # Load image
        if not os.path.exists(template.image_path):
            self.scene.clear()
            self.status_label.setText(f"Template image not found: {template.image_path}")
            self.export_available_changed.emit(False)
            return

        # Clear scene
        self.scene.clear()

        # Load and display device image
        pixmap = QPixmap(template.image_path)

        if pixmap.isNull():
            self.status_label.setText(f"Failed to load image: {template.image_path}")
            self.export_available_changed.emit(False)
            return

        # Add image to scene
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Add annotations
        self.add_annotations()

        # Fit view to scene
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        self.status_label.setText(f"Loaded: {template.name}")
        self.export_available_changed.emit(True)

    def add_annotations(self):
        """Add control annotations to the device graphic"""
        if not self.current_device or not self.current_profile:
            return

        # Check if template has SVG overlay
        if self.current_template and self.current_template.overlay_path:
            if os.path.exists(self.current_template.overlay_path):
                self.add_svg_overlay_annotations()
                return

        # Fall back to JSON mapping or legend
        mapping = self.load_detailed_mapping()
        if mapping:
            self.add_callout_annotations(mapping)
        else:
            device_bindings = self.get_device_bindings()
            if device_bindings:
                self.add_binding_legend(device_bindings)

    def add_svg_overlay_annotations(self):
        """Add annotations using SVG overlay with template tags"""
        if not self.current_template or not self.current_template.overlay_path:
            return

        # Read SVG file
        try:
            with open(self.current_template.overlay_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        except Exception as e:
            logger.error(f"Error reading SVG overlay: {e}", exc_info=True)
            return

        # Get all bindings for this device
        device_bindings = self.get_device_bindings()

        # First, group bindings by input_code to handle multiple actions per button
        from collections import defaultdict
        grouped_bindings = defaultdict(list)

        for action_map_name, binding in device_bindings:
            # Skip empty or whitespace-only input codes (cleared bindings)
            input_code = binding.input_code.strip()
            if not input_code or input_code.endswith('_ ') or input_code.endswith('_'):
                continue

            # Get the human-readable input label (e.g., "Button 3", "Hat 1 Up")
            input_label = LabelGenerator.generate_input_label(binding.input_code)
            # Remove device prefix if present (e.g., "Joystick 1: Button 3" -> "Button 3")
            if ': ' in input_label:
                input_label = input_label.split(': ', 1)[1]

            # Skip if the label is empty or just whitespace after processing
            if not input_label or not input_label.strip():
                continue

            grouped_bindings[input_label].append((action_map_name, binding))

        # Create mapping from input labels to action labels
        bindings_map = {}
        for input_label, bindings in grouped_bindings.items():
            # Get action labels for all bindings on this input
            action_labels = []
            for action_map_name, binding in bindings:
                action_label = LabelGenerator.get_action_label(binding.action_name, binding)
                action_labels.append(action_label)

            # Remove duplicates while preserving order (e.g., when multiple actions have same custom label)
            unique_labels = list(dict.fromkeys(action_labels))

            # Join multiple actions with slash separator (single line)
            combined_label = ' / '.join(unique_labels)

            # Store mapping - use the original label as the primary key
            bindings_map[input_label] = combined_label

            # For hat buttons, also store under template-friendly formats
            # Templates may use different formats:
            # - "Hat up", "Hat down" (no number, lowercase) - used by right stick
            # - "Hat1 up", "Hat1 down" (no space, lowercase) - used by left stick
            # So we store the action under ALL possible formats the templates might use
            hat_match = re.match(r'Hat\s+(\d+)\s+(\w+)', input_label)
            if hat_match:
                hat_num = hat_match.group(1)
                direction = hat_match.group(2).lower()
                # Format 1: "Hat up" (no number, lowercase direction)
                bindings_map[f"Hat {direction}"] = combined_label
                # Format 2: "Hat1 up" (no space between Hat and number, lowercase direction)
                bindings_map[f"Hat{hat_num} {direction}"] = combined_label

        # Replace template tags in SVG with actual bindings
        def replace_tag(match):
            tag_content = match.group(1).strip()
            # Look up the binding for this input
            return bindings_map.get(tag_content, tag_content)  # Keep original if not found

        # Replace all {{...}} tags
        processed_svg = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_tag, svg_content)

        # Render the processed SVG, passing the bindings map to filter unmapped buttons
        self.render_svg_overlay(processed_svg, bindings_map)

    def render_svg_overlay(self, svg_content: str, bindings_map: dict = None):
        """Render processed SVG content as overlay on the scene"""
        # Parse SVG XML to extract elements and render them
        try:
            import xml.etree.ElementTree as ET
            import re
            root = ET.fromstring(svg_content)

            # Find and render rectangle elements (for table backgrounds)
            for rect_elem in root.findall('.//{http://www.w3.org/2000/svg}rect'):
                x = float(rect_elem.get('x', 0))
                y = float(rect_elem.get('y', 0))
                width = float(rect_elem.get('width', 0))
                height = float(rect_elem.get('height', 0))
                fill = rect_elem.get('fill', 'white')

                # Support both old 'opacity' and new 'fill-opacity' attributes
                fill_opacity = float(rect_elem.get('fill-opacity', rect_elem.get('opacity', 1.0)))
                stroke_opacity = float(rect_elem.get('stroke-opacity', 1.0))

                stroke = rect_elem.get('stroke', 'none')
                stroke_width = float(rect_elem.get('stroke-width', 0))

                rect_item = QGraphicsRectItem(x, y, width, height)

                # Set fill with opacity
                fill_color = QColor(fill)
                fill_color.setAlphaF(fill_opacity)
                rect_item.setBrush(QBrush(fill_color))

                if stroke != 'none':
                    stroke_color = QColor(stroke)
                    stroke_color.setAlphaF(stroke_opacity)
                    pen = QPen(stroke_color)
                    pen.setWidthF(stroke_width)
                    rect_item.setPen(pen)
                else:
                    rect_item.setPen(QPen(Qt.PenStyle.NoPen))

                self.scene.addItem(rect_item)

            # Find and render line elements (for table borders)
            for line_elem in root.findall('.//{http://www.w3.org/2000/svg}line'):
                x1 = float(line_elem.get('x1', 0))
                y1 = float(line_elem.get('y1', 0))
                x2 = float(line_elem.get('x2', 0))
                y2 = float(line_elem.get('y2', 0))
                stroke = line_elem.get('stroke', 'black')
                stroke_width = float(line_elem.get('stroke-width', 1))

                pen = QPen(QColor(stroke))
                pen.setWidthF(stroke_width)

                line_item = self.scene.addLine(x1, y1, x2, y2, pen)

            # Find all text elements
            for text_elem in root.findall('.//{http://www.w3.org/2000/svg}text'):
                # Extract attributes
                x = float(text_elem.get('x', 0))
                y = float(text_elem.get('y', 0))
                font_family = text_elem.get('font-family', 'Arial')
                font_size = int(text_elem.get('font-size', 10))
                fill = text_elem.get('fill', 'black')
                text_anchor = text_elem.get('text-anchor', 'start')
                font_weight = text_elem.get('font-weight', 'normal')
                stroke_attr = text_elem.get('stroke')
                stroke_width_attr = text_elem.get('stroke-width', '0')

                # Get max dimensions from data attributes
                max_width = float(text_elem.get('data-max-width', 0))
                max_height = float(text_elem.get('data-max-height', 0))

                # Check for tspan elements (multi-line text from config)
                tspan_elems = text_elem.findall('.//{http://www.w3.org/2000/svg}tspan')

                if tspan_elems:
                    # Multi-line text using tspan elements
                    wrapped_lines = []
                    for tspan in tspan_elems:
                        tspan_text = tspan.text or ''
                        if tspan_text.strip():
                            wrapped_lines.append(tspan_text)

                    # Skip if all lines are empty
                    if not any(line.strip() for line in wrapped_lines):
                        continue

                    # Check first line for unmapped button pattern
                    first_line = wrapped_lines[0].strip() if wrapped_lines else ''
                    if bindings_map is not None and re.match(r'^Button\s+\d+$', first_line):
                        continue

                    wrapped_text = '<br/>'.join(wrapped_lines)
                else:
                    # Single-line text
                    text_content = text_elem.text or ''

                    # Skip empty text
                    if not text_content.strip():
                        continue

                    # Skip unmapped buttons (those that still have "Button X" pattern)
                    # UNLESS we're in a table (bindings_map will still process table rows)
                    parent = text_elem.find('..')
                    in_table = False
                    if parent is not None:
                        # Check if parent or ancestor is the unmapped-table group
                        current = text_elem
                        for _ in range(3):  # Check up to 3 levels up
                            parent_elem = root.find(f".//*[@id='unmapped-table']")
                            if parent_elem is not None and current in list(parent_elem.iter()):
                                in_table = True
                                break
                            # Move up (this is approximate - XML doesn't have parent refs)
                            break

                    # For table text, don't skip unmapped buttons
                    if not in_table and bindings_map is not None:
                        if re.match(r'^Button\s+\d+$', text_content.strip()):
                            continue

                    wrapped_text = text_content

                # Create Qt text item
                text_item = QGraphicsTextItem()
                text_item.setPlainText(wrapped_text)

                # Set font
                font = QFont(font_family, font_size)
                if font_weight == 'bold':
                    font.setBold(True)
                text_item.setFont(font)

                # Auto-scale font if text is too wide/tall and max dimensions are specified
                if max_width > 0 and max_height > 0:
                    current_width = text_item.boundingRect().width()
                    current_height = text_item.boundingRect().height()

                    # Scale down font if text exceeds max dimensions
                    if current_width > max_width or current_height > max_height:
                        scale_factor = min(max_width / current_width, max_height / current_height)
                        new_font_size = max(6, int(font_size * scale_factor * 0.9))  # 0.9 for padding
                        font = QFont(font_family, new_font_size)
                        if font_weight == 'bold':
                            font.setBold(True)
                        text_item.setFont(font)

                # Set color
                color = QColor(fill)
                text_item.setDefaultTextColor(color)

                # Set transparent background (Qt default, but explicitly set)
                text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, False)

                # Adjust position based on text-anchor
                if text_anchor == 'middle':
                    text_width = text_item.boundingRect().width()
                    x -= text_width / 2
                elif text_anchor == 'end':
                    text_width = text_item.boundingRect().width()
                    x -= text_width

                # SVG y is baseline, Qt y is top, so adjust
                y -= text_item.boundingRect().height() * 0.75

                text_item.setPos(x, y)
                self.scene.addItem(text_item)

        except Exception as e:
            logger.error(f"Error rendering SVG overlay: {e}", exc_info=True)

    def load_detailed_mapping(self) -> dict:
        """Load detailed callout mapping for current template"""
        if not self.current_template:
            return None

        # Try to find a detailed mapping JSON file
        template_id = self.current_template.id
        mapping_path = os.path.join(self.templates_dir, f"{template_id}.json")

        if not os.path.exists(mapping_path):
            return None

        try:
            import json
            with open(mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading mapping file: {e}", exc_info=True)
            return None

    def add_callout_annotations(self, mapping: dict):
        """Add annotations using detailed callout box mapping"""
        if not self.current_device or not self.current_profile:
            return

        # Get all bindings for this device
        device_bindings = self.get_device_bindings()

        # Create a dictionary of bindings by input code
        bindings_dict = {}
        for action_map_name, binding in device_bindings:
            # Extract the button/axis part (e.g., "js1_button3" -> "button3")
            input_code = binding.input_code
            device_prefix = f"js{self.current_device.instance}_"

            if input_code.startswith(device_prefix):
                input_part = input_code[len(device_prefix):]
                bindings_dict[input_part] = (action_map_name, binding)

        # Process callouts
        for callout in mapping.get('callouts', []):
            input_id = callout.get('input')
            if input_id in bindings_dict:
                action_map_name, binding = bindings_dict[input_id]
                action_label = LabelGenerator.get_action_label(binding.action_name, binding)

                # Add text to callout box
                pos = callout.get('position', {})
                self.add_text_to_callout(
                    action_label,
                    pos.get('x', 0),
                    pos.get('y', 0),
                    callout.get('width', 180),
                    callout.get('height', 35)
                )

        # Process hat switch directions if present
        for axis in mapping.get('axes', []):
            if 'directions' in axis:
                input_id = axis.get('input')
                # Handle hat switch directions
                for direction, info in axis['directions'].items():
                    hat_input = f"{input_id}_{direction}"
                    if hat_input in bindings_dict:
                        action_map_name, binding = bindings_dict[hat_input]
                        action_label = LabelGenerator.get_action_label(binding.action_name, binding)

                        pos = info.get('position', {})
                        self.add_text_to_callout(
                            action_label,
                            pos.get('x', 0),
                            pos.get('y', 0),
                            info.get('width', 180),
                            info.get('height', 35)
                        )

    def add_text_to_callout(self, text: str, x: float, y: float, width: float, height: float):
        """Add text to a specific callout box position"""
        # Create text item
        text_item = QGraphicsTextItem(text)
        text_item.setDefaultTextColor(QColor(0, 0, 0))

        # Set font to fit in callout box
        font = QFont("Arial", 8)
        text_item.setFont(font)

        # Truncate if too long
        if text_item.boundingRect().width() > width - 10:
            # Try smaller font
            font = QFont("Arial", 7)
            text_item.setFont(font)

            # Still too long? Truncate
            if text_item.boundingRect().width() > width - 10:
                while text_item.boundingRect().width() > width - 10 and len(text) > 5:
                    text = text[:-4] + "..."
                    text_item.setPlainText(text)

        # Center text in callout box
        text_width = text_item.boundingRect().width()
        text_height = text_item.boundingRect().height()

        centered_x = x + (width - text_width) / 2
        centered_y = y + (height - text_height) / 2

        text_item.setPos(centered_x, centered_y)
        self.scene.addItem(text_item)

    def get_device_bindings(self) -> list:
        """Get all bindings for the current device"""
        if not self.current_device or not self.current_profile or not self.current_device_name:
            return []

        bindings = []
        device_instance = self.current_device.instance
        device_type = self.current_device.device_type

        # Get button range for this template (if it has one)
        template = self.template_manager.find_template(self.current_device_name)
        button_range = template.button_range if template and template.button_range else None

        for action_map in self.current_profile.action_maps:
            for binding in action_map.actions:
                # Check if this binding is for this device instance
                if device_type == 'joystick' and binding.input_code.startswith(f'js{device_instance}_'):
                    # If we have a button range, filter by it
                    if button_range:
                        from utils.device_splitter import extract_button_number
                        button_num = extract_button_number(binding.input_code)

                        # Only include if button is in range
                        if button_num is not None:
                            if button_range[0] <= button_num <= button_range[1]:
                                bindings.append((action_map.name, binding))
                        # For non-button inputs (axes, hats), only include for base device (lower button range)
                        elif button_range[0] == 1:
                            bindings.append((action_map.name, binding))
                    else:
                        # No button range filtering - include all bindings for this device
                        bindings.append((action_map.name, binding))

        return bindings

    def add_binding_legend(self, bindings: list):
        """Add a legend showing bindings"""
        # Add a semi-transparent background for legend
        legend_width = 300
        legend_x = self.scene.sceneRect().right() - legend_width - 20
        legend_y = 20

        bg_rect = QGraphicsRectItem(legend_x, legend_y, legend_width, min(len(bindings) * 20 + 40, 400))
        bg_rect.setBrush(QBrush(QColor(255, 255, 255, 200)))
        bg_rect.setPen(QPen(QColor(0, 0, 0)))
        self.scene.addItem(bg_rect)

        # Add title
        title = QGraphicsTextItem("Control Bindings")
        title.setDefaultTextColor(QColor(0, 0, 0))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        title.setFont(font)
        title.setPos(legend_x + 10, legend_y + 5)
        self.scene.addItem(title)

        # Add bindings (limit to first 15 to avoid overflow)
        y_offset = 35
        for i, (action_map_name, binding) in enumerate(bindings[:15]):
            if i >= 15:
                break

            action_label = LabelGenerator.get_action_label(binding.action_name, binding)
            input_label = LabelGenerator.generate_input_label(binding.input_code)

            text = f"{input_label}: {action_label}"
            text_item = QGraphicsTextItem(text)
            text_item.setDefaultTextColor(QColor(0, 0, 0))
            font = QFont("Arial", 9)
            text_item.setFont(font)
            text_item.setPos(legend_x + 10, legend_y + y_offset)

            # Truncate if too long
            if text_item.boundingRect().width() > legend_width - 20:
                text = text[:40] + "..."
                text_item.setPlainText(text)

            self.scene.addItem(text_item)
            y_offset += 20

        if len(bindings) > 15:
            more_text = QGraphicsTextItem(f"... and {len(bindings) - 15} more")
            more_text.setDefaultTextColor(QColor(100, 100, 100))
            font = QFont("Arial", 9, QFont.Weight.Bold)
            more_text.setFont(font)
            more_text.setPos(legend_x + 10, legend_y + y_offset)
            self.scene.addItem(more_text)

    def export_graphic(self):
        """Export the annotated graphic"""
        if not self.current_template:
            return

        # Create default filename with underscores instead of spaces
        device_name = (self.current_device.product_name or 'device').replace(' ', '_')
        default_filename = f"{device_name}_controls.png"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Device Graphic",
            default_filename,
            "PNG Image (*.png);;PDF Document (*.pdf)"
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.pdf'):
                self.export_to_pdf(file_path)
            else:
                self.export_to_png(file_path)

            # Create message box with custom buttons
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText(f"Graphic exported successfully!")
            msg_box.setInformativeText(f"Saved to:\n{file_path}")

            # Add Open and OK buttons
            open_button = msg_box.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
            ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)

            msg_box.exec()

            # Check which button was clicked
            if msg_box.clickedButton() == open_button:
                # Open the file with the default system application
                import subprocess
                import platform

                try:
                    if platform.system() == 'Windows':
                        os.startfile(file_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', file_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', file_path])
                except Exception as open_error:
                    QMessageBox.warning(self, "Cannot Open File",
                                      f"File exported successfully but couldn't open it automatically:\n{str(open_error)}")

            self.status_label.setText(f"Exported to: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export graphic:\n{str(e)}")
            self.status_label.setText("Export failed")

    def export_to_png(self, file_path: str):
        """Export scene to PNG"""
        # Get scene bounding rect
        rect = self.scene.sceneRect()

        # Create image
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)

        # Render scene to image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene.render(painter)
        painter.end()

        # Save image
        image.save(file_path, "PNG")

    def export_to_pdf(self, file_path: str):
        """Export scene to PDF"""
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        # First export to PNG, then embed in PDF
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
            self.export_to_png(tmp_path)

        # Create PDF
        c = canvas.Canvas(file_path, pagesize=landscape(letter))
        page_width, page_height = landscape(letter)

        # Add title
        c.setFont("Helvetica-Bold", 16)
        device_name = self.current_device.product_name or "Device"
        c.drawString(50, page_height - 50, f"{device_name} - Control Layout")

        # Add image
        img = ImageReader(tmp_path)
        img_width, img_height = img.getSize()

        # Calculate scaling to fit page
        max_width = page_width - 100
        max_height = page_height - 150
        scale = min(max_width / img_width, max_height / img_height)

        scaled_width = img_width * scale
        scaled_height = img_height * scale

        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height - 100)

        c.drawImage(tmp_path, x, y, width=scaled_width, height=scaled_height)

        c.save()

        # Clean up temp file
        os.unlink(tmp_path)
