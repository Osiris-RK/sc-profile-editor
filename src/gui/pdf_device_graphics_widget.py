"""
PDF-based device graphics widget for displaying and annotating device PDFs
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QGraphicsView, QGraphicsScene,
                              QGraphicsPixmapItem, QMessageBox)
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt, pyqtSignal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graphics.pdf_template_manager import PDFTemplateManager, PDFDeviceTemplate
from models.profile_model import ControlProfile, Device
from parser.label_generator import LabelGenerator
from utils.device_joystick_mapper import DeviceJoystickMapper

logger = logging.getLogger(__name__)


class InteractivePDFGraphicsView(QGraphicsView):
    """Custom QGraphicsView with clickable form fields"""

    # Signal emitted when a field is clicked: (field_name, current_value)
    field_clicked = pyqtSignal(str, str)

    def __init__(self, scene):
        super().__init__(scene)
        self._fit_on_resize = True
        self.field_regions = {}  # field_name -> QRectF (in scene coordinates)
        self.field_values = {}  # field_name -> current_value
        self.dpi_scale = 1.0  # Scale factor from PDF to rendered image

    def set_field_regions(self, field_regions: dict, field_values: dict, dpi_scale: float):
        """Set clickable field regions"""
        self.field_regions = field_regions
        self.field_values = field_values
        self.dpi_scale = dpi_scale

    def resizeEvent(self, event):
        """Re-fit the view when resized"""
        super().resizeEvent(event)
        if self._fit_on_resize and self.scene() and not self.scene().sceneRect().isEmpty():
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Handle mouse clicks to detect field clicks"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Map view coordinates to scene coordinates
            scene_pos = self.mapToScene(event.pos())

            # Check if click is within any field region
            for field_name, rect in self.field_regions.items():
                if rect.contains(scene_pos):
                    # Field clicked - emit signal with field name
                    current_value = self.field_values.get(field_name, "")
                    self.field_clicked.emit(field_name, current_value)
                    return

        # Default handling for non-field clicks
        super().mousePressEvent(event)


class PDFDeviceGraphicsWidget(QWidget):
    """Widget for displaying PDF-based device templates with interactive form fields"""

    # Signal emitted when export availability changes
    export_available_changed = pyqtSignal(bool)

    def __init__(self, templates_dir: str):
        super().__init__()
        self.templates_dir = templates_dir
        self.pdf_manager = PDFTemplateManager(templates_dir)
        self.current_profile: ControlProfile = None
        self.current_device: Device = None
        self.current_template: PDFDeviceTemplate = None
        self.device_mapper: DeviceJoystickMapper = None
        self.current_field_values: dict = {}  # Store current field values
        self.field_to_input_code: dict = {}  # Map PDF field names to input codes

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

        # Graphics view (interactive)
        self.scene = QGraphicsScene()
        self.view = InteractivePDFGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)  # Allow clicks
        self.view.field_clicked.connect(self.on_field_clicked)
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

        # Create device-to-joystick mapper
        try:
            self.device_mapper = DeviceJoystickMapper(profile,
                os.path.join(self.templates_dir, "template_registry.json"))
        except Exception as e:
            logger.error(f"Error creating device mapper: {e}", exc_info=True)
            self.device_mapper = None

        # Add devices that have PDF templates
        for device in profile.devices:
            if device.device_type == 'joystick':  # Focus on joysticks for now
                device_name = device.product_name if device.product_name else f"Joystick {device.instance}"

                # Try to find a PDF template for this device
                template = self.pdf_manager.find_template(device.product_name or "")

                if template:
                    # Store device in item data
                    self.device_combo.addItem(f"{device_name} (PDF Template)", device)
                else:
                    # Also show devices without templates
                    self.device_combo.addItem(f"{device_name} (No PDF template)", device)

        if self.device_combo.count() == 0:
            self.status_label.setText("No devices found")
            self.device_combo.addItem("No devices available", None)
        else:
            self.status_label.setText(f"Found {self.device_combo.count()} device(s)")

    def select_device_by_name(self, device_name: str) -> bool:
        """
        Select a device in the combo box by its name.
        Returns True if device was found and selected, False otherwise.
        """
        if not device_name:
            return False

        # Search through combo box items
        for i in range(self.device_combo.count()):
            item_data = self.device_combo.itemData(i)

            if item_data and hasattr(item_data, 'product_name'):
                if item_data.product_name == device_name:
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

        self.current_device = item_data
        self.load_device_pdf()

    def load_device_pdf(self):
        """Load and display device PDF with populated form fields"""
        if not self.current_device:
            return

        # Find PDF template for this device
        template = self.pdf_manager.find_template(self.current_device.product_name or "")

        if not template:
            self.scene.clear()
            self.status_label.setText("No PDF template available for this device")
            self.export_available_changed.emit(False)
            return

        self.current_template = template

        # Verify PDF exists
        if not os.path.exists(template.pdf_path):
            self.scene.clear()
            self.status_label.setText(f"PDF template not found: {template.pdf_path}")
            self.export_available_changed.emit(False)
            return

        # Get field values from bindings
        field_values = self.get_field_values_for_device()
        self.current_field_values = field_values

        # Get field regions for clickable areas
        field_regions, field_value_map = self.get_field_regions(template, dpi=150)

        # Render PDF with populated fields
        try:
            pixmap = self.pdf_manager.render_template(template, field_values, dpi=150)

            if pixmap is None or pixmap.isNull():
                self.scene.clear()
                self.status_label.setText(f"Failed to render PDF: {template.pdf_path}")
                self.export_available_changed.emit(False)
                return

            # Clear scene and add pixmap
            self.scene.clear()
            pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)

            # Set clickable field regions in the view
            self.view.set_field_regions(field_regions, field_value_map, dpi_scale=150/72.0)

            # Fit view to scene
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

            self.status_label.setText(f"Loaded: {template.name} ({len(field_values)} fields populated) - Click fields to edit")
            self.export_available_changed.emit(True)

        except Exception as e:
            logger.error(f"Error rendering PDF template: {e}", exc_info=True)
            self.scene.clear()
            self.status_label.setText(f"Error rendering PDF: {str(e)}")
            self.export_available_changed.emit(False)

    def get_field_values_for_device(self) -> dict:
        """
        Get PDF form field values for the current device

        Returns:
            Dictionary mapping field names (e.g., "js1_button1") to action labels
        """
        field_values = {}

        if not self.current_device or not self.current_profile or not self.device_mapper:
            return field_values

        # Get joystick index for this device
        js_index = self.device_mapper.get_js_index_for_device(self.current_device.product_name or "")

        if js_index is None:
            logger.warning(f"No JS index found for device: {self.current_device.product_name}")
            return field_values

        # Extract JS number (e.g., "js1" -> "1")
        js_num = js_index.replace("js", "")

        # Get all bindings for this device
        device_bindings = self.get_device_bindings()

        # Group bindings by input code to handle multiple actions per button
        from collections import defaultdict
        grouped_bindings = defaultdict(list)

        for action_map_name, binding in device_bindings:
            input_code = binding.input_code.strip()
            if input_code and input_code.startswith(f"js{js_num}_"):
                grouped_bindings[input_code].append((action_map_name, binding))

        # Create field values map
        for input_code, bindings in grouped_bindings.items():
            # Get action labels for all bindings on this input
            action_labels = []
            for action_map_name, binding in bindings:
                action_label = LabelGenerator.get_action_label(binding.action_name, binding)
                action_labels.append(action_label)

            # Remove duplicates while preserving order
            unique_labels = list(dict.fromkeys(action_labels))

            # Join multiple actions with slash separator
            combined_label = ' / '.join(unique_labels)

            # Store in field values using the input code as field name
            field_values[input_code] = combined_label

        logger.debug(f"Generated {len(field_values)} field values for device {self.current_device.product_name}")
        return field_values

    def get_device_bindings(self) -> list:
        """Get all bindings for the current device"""
        if not self.current_device or not self.current_profile:
            return []

        bindings = []
        device_instance = self.current_device.instance
        device_type = self.current_device.device_type

        for action_map in self.current_profile.action_maps:
            for binding in action_map.actions:
                # Check if this binding is for this device instance
                if device_type == 'joystick' and binding.input_code.startswith(f'js{device_instance}_'):
                    bindings.append((action_map.name, binding))

        return bindings

    def export_graphic(self):
        """Export the rendered PDF graphic"""
        if not self.current_template:
            QMessageBox.warning(self, "No Template", "No device template is currently loaded.")
            return

        from PyQt6.QtWidgets import QFileDialog

        # Create default filename
        device_name = (self.current_device.product_name or 'device').replace(' ', '_')
        default_filename = f"{device_name}_controls.png"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Device Graphic",
            default_filename,
            "PNG Image (*.png)"
        )

        if not file_path:
            return

        try:
            self.export_to_png(file_path)

            # Show success message
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
        from PyQt6.QtGui import QImage

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

    def get_field_regions(self, template: PDFDeviceTemplate, dpi: int = 150):
        """
        Get field regions from PDF for click detection

        Returns:
            Tuple of (field_regions, field_values):
            - field_regions: Dictionary mapping input_code -> QRectF (scene coordinates)
            - field_values: Dictionary mapping input_code -> current_value
        """
        from PyQt6.QtCore import QRectF
        import fitz

        field_regions = {}
        field_values = {}

        try:
            doc = fitz.open(template.pdf_path)
            page = doc[0]

            # Get field mapping if exists
            field_mapping = self.pdf_manager.load_field_mapping(template)

            # DPI scale factor
            zoom = dpi / 72.0

            for widget in page.widgets():
                field_name = widget.field_name
                rect = widget.rect

                # Scale rect to match rendered image
                scaled_rect = QRectF(
                    rect.x0 * zoom,
                    rect.y0 * zoom,
                    (rect.x1 - rect.x0) * zoom,
                    (rect.y1 - rect.y0) * zoom
                )

                # Map PDF field name to input code
                input_code = self.map_pdf_field_to_input_code(field_name, field_mapping)

                if input_code:
                    field_regions[input_code] = scaled_rect
                    # Store current value for this field
                    current_value = self.current_field_values.get(input_code, "")
                    field_values[input_code] = current_value
                    # Store reverse mapping
                    self.field_to_input_code[field_name] = input_code

            doc.close()

        except Exception as e:
            logger.error(f"Error getting field regions: {e}", exc_info=True)

        return field_regions, field_values

    def map_pdf_field_to_input_code(self, pdf_field_name: str, field_mapping: dict) -> str:
        """Map PDF field name to Star Citizen input code"""
        if not self.device_mapper:
            return None

        # Get JS index for this device
        js_index = self.device_mapper.get_js_index_for_device(self.current_device.product_name or "")
        if not js_index:
            return None

        js_num = js_index.replace("js", "")

        if field_mapping:
            # Has custom mapping - reverse lookup
            button_mapping = field_mapping.get('button_mapping', {})

            # Remove _1 or _2 suffix if present
            base_field_name = pdf_field_name
            if pdf_field_name.endswith('_1') or pdf_field_name.endswith('_2'):
                base_field_name = pdf_field_name[:-2]

            # Find button number for this PDF field
            button_num = button_mapping.get(base_field_name)
            if button_num:
                return f"js{js_num}_button{button_num}"
        else:
            # Direct mapping - PDF field should be input code
            return pdf_field_name

        return None

    def on_field_clicked(self, input_code: str, current_value: str):
        """Handle click on a PDF form field"""
        from PyQt6.QtWidgets import QInputDialog

        # Find the binding for this input code
        binding = self.find_binding_by_input_code(input_code)

        if not binding:
            logger.warning(f"No binding found for {input_code}")
            QMessageBox.information(
                self,
                "No Binding",
                f"No binding found for {input_code}.\nThis button is not assigned to any action."
            )
            return

        # Show dialog to edit label
        new_label, ok = QInputDialog.getText(
            self,
            "Edit Control Label",
            f"Edit label for {input_code}:\n({binding.action_name})",
            text=current_value
        )

        if ok and new_label != current_value:
            if not new_label:
                # Empty string - revert to default
                new_label = LabelGenerator.get_default_action_label(binding.action_name)

            # Update binding's custom label
            self.update_binding_label(binding, new_label)

            # Reload override manager cache
            try:
                from utils.label_overrides import get_override_manager
            except ImportError:
                from ..utils.label_overrides import get_override_manager

            override_manager = get_override_manager()
            override_manager.reload()

            # Reload the PDF with updated values
            self.load_device_pdf()

            # Notify parent to update table if possible
            self.notify_label_changed(binding)

            logger.info(f"Updated label for {input_code}: {new_label}")

    def find_binding_by_input_code(self, input_code: str):
        """Find binding object by input code"""
        if not self.current_profile:
            return None

        for action_map in self.current_profile.action_maps:
            for binding in action_map.actions:
                if binding.input_code == input_code:
                    return binding

        return None

    def update_binding_label(self, binding, new_label: str):
        """Update a binding's custom label"""
        try:
            # Import label override manager
            try:
                from utils.label_overrides import get_override_manager
            except ImportError:
                from ..utils.label_overrides import get_override_manager

            override_manager = get_override_manager()

            # Get default label to check if new label is different
            default_label = LabelGenerator.get_default_action_label(binding.action_name)

            if new_label == default_label:
                # New label matches default - remove custom override
                override_manager.remove_custom_override(binding.action_name)
                binding.custom_label = None
            else:
                # Save as custom override
                override_manager.set_custom_override(binding.action_name, new_label)
                binding.custom_label = new_label

        except Exception as e:
            logger.error(f"Error updating binding label: {e}", exc_info=True)

    def notify_label_changed(self, binding):
        """Notify parent window that a label has changed"""
        try:
            # Try to find and update the main window's table
            parent = self.parent()
            while parent:
                if hasattr(parent, 'populate_controls_table'):
                    # Found main window - refresh the table
                    parent.populate_controls_table()
                    parent.apply_filters()
                    logger.info("Updated main window's controls table")
                    break
                parent = parent.parent()
        except Exception as e:
            logger.warning(f"Could not update main window table: {e}")
