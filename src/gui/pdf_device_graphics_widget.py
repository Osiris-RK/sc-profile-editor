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

            # Fit view to scene
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

            self.status_label.setText(f"Loaded: {template.name} ({len(field_values)} fields populated)")
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
