"""
WebEngine-based PDF widget for interactive PDF form editing

This widget embeds a Chromium browser to display PDFs with true interactive
form fields that can be edited directly like in a web browser.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer, QObject, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graphics.pdf_template_manager import PDFTemplateManager, PDFDeviceTemplate
from models.profile_model import ControlProfile, Device
from parser.label_generator import LabelGenerator
from utils.device_joystick_mapper import DeviceJoystickMapper
from utils.device_splitter import get_friendly_device_name

logger = logging.getLogger(__name__)


class PDFFieldBridge(QObject):
    """Bridge object for JavaScript <-> Qt communication"""

    # Signal emitted when a PDF field value changes
    field_changed = pyqtSignal(str, str)  # field_name, new_value

    @pyqtSlot(str, str)
    def onFieldChange(self, field_name, new_value):
        """Called from JavaScript when a PDF field changes"""
        logger.info(f"PDF field changed: {field_name} = {new_value}")
        self.field_changed.emit(field_name, new_value)


class WebEnginePDFWidget(QWidget):
    """Widget for displaying interactive PDFs using QtWebEngine"""

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
        self.current_pdf_path: str = None
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

        # Web view for PDF
        self.web_view = QWebEngineView()
        self.web_view.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled, True
        )
        self.web_view.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PdfViewerEnabled, True
        )

        # Set up JavaScript communication channel
        self.channel = QWebChannel()
        self.bridge = PDFFieldBridge()
        self.bridge.field_changed.connect(self.on_pdf_field_changed)
        self.channel.registerObject("qtBridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        layout.addWidget(self.web_view)

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
            if device.device_type == 'joystick':
                raw_device_name = device.product_name if device.product_name else f"Joystick {device.instance}"
                # Apply friendly name from template registry
                device_name = get_friendly_device_name(raw_device_name)

                # Try to find a PDF template for this device
                template = self.pdf_manager.find_template(device.product_name or "")

                if template:
                    self.device_combo.addItem(f"{device_name} (Interactive PDF)", device)
                else:
                    self.device_combo.addItem(f"{device_name} (No PDF template)", device)

        if self.device_combo.count() == 0:
            self.status_label.setText("No devices found")
            self.device_combo.addItem("No devices available", None)
        else:
            self.status_label.setText(f"Found {self.device_combo.count()} device(s)")

    def select_device_by_name(self, device_name: str) -> bool:
        """Select a device in the combo box by its name"""
        if not device_name:
            return False

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
            self.web_view.setHtml("")
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
            self.web_view.setHtml("<h2>No PDF template available for this device</h2>")
            self.status_label.setText("No PDF template available")
            self.export_available_changed.emit(False)
            return

        self.current_template = template

        # Verify PDF exists
        if not os.path.exists(template.pdf_path):
            self.web_view.setHtml(f"<h2>PDF template not found:</h2><p>{template.pdf_path}</p>")
            self.status_label.setText(f"PDF template not found")
            self.export_available_changed.emit(False)
            return

        # Get field values from bindings
        field_values = self.get_field_values_for_device()

        # Populate PDF and get path
        try:
            # Create populated PDF
            import tempfile
            temp_dir = os.path.dirname(template.pdf_path)
            fd, temp_pdf_path = tempfile.mkstemp(suffix='.pdf', dir=temp_dir, prefix='interactive_')
            os.close(fd)

            populated_pdf_path = self.pdf_manager.populate_pdf(template, field_values, temp_pdf_path)

            if populated_pdf_path:
                self.current_pdf_path = populated_pdf_path

                # Load PDF in web view
                pdf_url = QUrl.fromLocalFile(os.path.abspath(populated_pdf_path))
                self.web_view.load(pdf_url)

                # Set up field change monitoring after page loads
                self.web_view.loadFinished.connect(self.on_pdf_loaded)

                self.status_label.setText(f"Loaded: {template.name} - Edit fields directly in PDF")
                self.export_available_changed.emit(True)
            else:
                self.web_view.setHtml("<h2>Failed to populate PDF</h2>")
                self.status_label.setText("Failed to populate PDF")
                self.export_available_changed.emit(False)

        except Exception as e:
            logger.error(f"Error loading PDF: {e}", exc_info=True)
            self.web_view.setHtml(f"<h2>Error loading PDF:</h2><p>{str(e)}</p>")
            self.status_label.setText(f"Error: {str(e)}")
            self.export_available_changed.emit(False)

    def on_pdf_loaded(self, success: bool):
        """Called when PDF finishes loading in web view"""
        if not success:
            logger.error("Failed to load PDF in web view")
            return

        # Inject JavaScript to monitor form field changes
        js_code = """
        (function() {
            // Set up QWebChannel
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.qtBridge = channel.objects.qtBridge;

                // Monitor all form inputs
                setTimeout(function() {
                    var inputs = document.querySelectorAll('input, textarea, select');
                    inputs.forEach(function(input) {
                        input.addEventListener('change', function() {
                            if (window.qtBridge) {
                                qtBridge.onFieldChange(input.name || input.id, input.value);
                            }
                        });

                        input.addEventListener('blur', function() {
                            if (window.qtBridge) {
                                qtBridge.onFieldChange(input.name || input.id, input.value);
                            }
                        });
                    });
                }, 1000);  // Wait for PDF.js to render form fields
            });
        })();
        """

        self.web_view.page().runJavaScript(js_code)
        logger.info("Injected form field monitoring JavaScript")

    def get_field_values_for_device(self) -> dict:
        """Get PDF form field values for the current device"""
        field_values = {}

        if not self.current_device or not self.current_profile or not self.device_mapper:
            return field_values

        # Get joystick index for this device
        js_index = self.device_mapper.get_js_index_for_device(self.current_device.product_name or "")

        if js_index is None:
            logger.warning(f"No JS index found for device: {self.current_device.product_name}")
            return field_values

        # Extract JS number
        js_num = js_index.replace("js", "")

        # Get all bindings for this device
        device_bindings = self.get_device_bindings()

        # Group bindings by input code
        from collections import defaultdict
        grouped_bindings = defaultdict(list)

        for action_map_name, binding in device_bindings:
            input_code = binding.input_code.strip()
            if input_code and input_code.startswith(f"js{js_num}_"):
                grouped_bindings[input_code].append((action_map_name, binding))

        # Create field values map
        for input_code, bindings in grouped_bindings.items():
            # Get action labels
            action_labels = []
            for action_map_name, binding in bindings:
                action_label = LabelGenerator.get_action_label(binding.action_name, binding)
                action_labels.append(action_label)

            # Remove duplicates
            unique_labels = list(dict.fromkeys(action_labels))

            # Join multiple actions
            combined_label = ' / '.join(unique_labels)

            # Store in field values
            field_values[input_code] = combined_label

        logger.debug(f"Generated {len(field_values)} field values for device")
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
                if device_type == 'joystick' and binding.input_code.startswith(f'js{device_instance}_'):
                    bindings.append((action_map.name, binding))

        return bindings

    def on_pdf_field_changed(self, field_name: str, new_value: str):
        """Handle PDF field value change from JavaScript"""
        logger.info(f"PDF field changed via web view: {field_name} = '{new_value}'")

        # Map PDF field name to input code
        input_code = self.map_pdf_field_to_input_code(field_name)

        if not input_code:
            logger.warning(f"Could not map PDF field '{field_name}' to input code")
            return

        # Find the binding for this input code
        binding = self.find_binding_by_input_code(input_code)

        if not binding:
            logger.warning(f"No binding found for {input_code}")
            return

        # Update the binding's custom label
        self.update_binding_label(binding, new_value)

        # Notify parent to update table
        self.notify_label_changed(binding)

        logger.info(f"Updated binding label: {binding.action_name} -> '{new_value}'")

    def map_pdf_field_to_input_code(self, pdf_field_name: str) -> str:
        """Map PDF field name to Star Citizen input code"""
        if not self.device_mapper or not self.current_template:
            return None

        # Get JS index
        js_index = self.device_mapper.get_js_index_for_device(self.current_device.product_name or "")
        if not js_index:
            return None

        js_num = js_index.replace("js", "")

        # Get field mapping if exists
        field_mapping = self.pdf_manager.load_field_mapping(self.current_template)

        if field_mapping:
            # Has custom mapping
            button_mapping = field_mapping.get('button_mapping', {})

            # Remove _1 or _2 suffix if present
            base_field_name = pdf_field_name
            if pdf_field_name.endswith('_1') or pdf_field_name.endswith('_2'):
                base_field_name = pdf_field_name[:-2]

            # Find button number
            button_num = button_mapping.get(base_field_name)
            if button_num:
                return f"js{js_num}_button{button_num}"
        else:
            # Direct mapping
            return pdf_field_name

        return None

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
            from utils.label_overrides import get_override_manager

            override_manager = get_override_manager()

            # Get default label
            default_label = LabelGenerator.generate_action_label(binding.action_name)

            if new_label == default_label or not new_label:
                # Remove custom override
                override_manager.remove_custom_override(binding.action_name)
                binding.custom_label = None
            else:
                # Save custom override
                override_manager.set_custom_override(binding.action_name, new_label)
                binding.custom_label = new_label

            # Reload override manager
            override_manager.reload()

        except Exception as e:
            logger.error(f"Error updating binding label: {e}", exc_info=True)

    def notify_label_changed(self, binding):
        """Notify parent window that a label has changed"""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'populate_controls_table'):
                    parent.populate_controls_table()
                    parent.apply_filters()
                    logger.info("Updated main window's controls table")
                    break
                parent = parent.parent()
        except Exception as e:
            logger.warning(f"Could not update main window table: {e}")

    def export_graphic(self):
        """Export the PDF"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "No PDF", "No PDF is currently loaded.")
            return

        from PyQt6.QtWidgets import QFileDialog
        import shutil

        # Get save location
        device_name = (self.current_device.product_name or 'device').replace(' ', '_')
        default_filename = f"{device_name}_controls.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            default_filename,
            "PDF Document (*.pdf)"
        )

        if not file_path:
            return

        try:
            # Copy current PDF to export location
            shutil.copy2(self.current_pdf_path, file_path)

            QMessageBox.information(
                self,
                "Success",
                f"PDF exported successfully!\n\nSaved to:\n{file_path}"
            )
            self.status_label.setText(f"Exported to: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
            self.status_label.setText("Export failed")
