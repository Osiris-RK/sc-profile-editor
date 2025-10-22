"""
Main application window
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFileDialog, QMessageBox,
                              QTextEdit, QTableWidget, QTableWidgetItem, QSplitter,
                              QLineEdit, QComboBox, QGroupBox, QCheckBox, QTabWidget,
                              QStyledItemDelegate)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser.xml_parser import ProfileParser
from parser.label_generator import LabelGenerator
from models.profile_model import ControlProfile
from gui.device_graphics import DeviceGraphicsWidget
from utils.settings import AppSettings


class SelectAllDelegate(QStyledItemDelegate):
    """Custom delegate that selects all text when editing starts"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window

    def setEditorData(self, editor, index):
        """Set the editor's data with the original text and select all"""
        if isinstance(editor, QLineEdit):
            # Use the original text stored before editing started
            if self.main_window._editing_original_text is not None:
                editor.setText(self.main_window._editing_original_text)
            else:
                # Fallback to model data
                super().setEditorData(editor, index)

            # Select all text with a small delay to ensure the editor is ready
            def select_text():
                if editor and not editor.isHidden():
                    editor.selectAll()
                    editor.setFocus()

            QTimer.singleShot(0, select_text)
        else:
            super().setEditorData(editor, index)


class MainWindow(QMainWindow):
    """Main application window for SC Profile Viewer"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star Citizen Profile Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize settings manager
        self.settings = AppSettings()

        # Store current profile
        self.current_profile = None
        self.current_profile_path = None

        # Store all bindings for filtering
        self.all_bindings = []

        # Create UI
        self.setup_ui()

        # Restore window geometry if saved
        self.restore_window_state()

        # Auto-load last profile after UI is shown (use QTimer to defer until after show())
        QTimer.singleShot(100, self.auto_load_last_profile)

    def setup_ui(self):
        """Set up the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Star Citizen Profile Viewer")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Export buttons
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.setStyleSheet("padding: 10px 20px; font-size: 14px;")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        header_layout.addWidget(self.export_csv_btn)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.setStyleSheet("padding: 10px 20px; font-size: 14px;")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setEnabled(False)
        header_layout.addWidget(self.export_pdf_btn)

        self.export_word_btn = QPushButton("Export Word")
        self.export_word_btn.setStyleSheet("padding: 10px 20px; font-size: 14px;")
        self.export_word_btn.clicked.connect(self.export_word)
        self.export_word_btn.setEnabled(False)
        header_layout.addWidget(self.export_word_btn)

        import_btn = QPushButton("Import Profile XML")
        import_btn.setStyleSheet("padding: 10px 20px; font-size: 14px; background-color: #4CAF50; color: white;")
        import_btn.clicked.connect(self.import_profile)
        header_layout.addWidget(import_btn)

        main_layout.addLayout(header_layout)

        # Profile info label
        self.profile_info_label = QLabel("No profile loaded")
        self.profile_info_label.setStyleSheet("font-size: 12px; margin: 5px; color: #666;")
        main_layout.addWidget(self.profile_info_label)

        # Filter toolbar
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        filter_group.setLayout(filter_layout)

        # Search box
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter actions, inputs, or devices...")
        self.search_box.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_box, 2)

        # Device filter
        filter_layout.addWidget(QLabel("Device:"))
        self.device_filter = QComboBox()
        self.device_filter.addItem("All Devices")
        self.device_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.device_filter, 1)

        # Action Map filter
        filter_layout.addWidget(QLabel("Action Map:"))
        self.actionmap_filter = QComboBox()
        self.actionmap_filter.addItem("All Action Maps")
        self.actionmap_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.actionmap_filter, 1)

        # Hide unmapped keys checkbox
        self.hide_unmapped_checkbox = QCheckBox("Hide Unmapped Keys")
        self.hide_unmapped_checkbox.stateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.hide_unmapped_checkbox)

        # Show detailed checkbox
        self.show_detailed_checkbox = QCheckBox("Show Detailed")
        self.show_detailed_checkbox.stateChanged.connect(self.toggle_detailed_view)
        filter_layout.addWidget(self.show_detailed_checkbox)

        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)

        main_layout.addWidget(filter_group)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Tab 1: Controls Table View
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        table_tab.setLayout(table_layout)

        # Splitter for info and table
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Profile summary text
        self.profile_summary = QTextEdit()
        self.profile_summary.setReadOnly(True)
        self.profile_summary.setMaximumHeight(150)
        self.profile_summary.setPlaceholderText("Profile summary will appear here...")
        splitter.addWidget(self.profile_summary)

        # Controls table
        self.controls_table = QTableWidget()
        self.controls_table.setColumnCount(6)  # Max columns for detailed view
        self.controls_table.setHorizontalHeaderLabels([
            "Action Map", "Action", "Action (Override)", "Input Code", "Input Label", "Device"
        ])
        self.controls_table.horizontalHeader().setStretchLastSection(False)
        self.controls_table.setAlternatingRowColors(True)
        self.controls_table.setSortingEnabled(True)
        self.controls_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.controls_table.itemChanged.connect(self.on_cell_edited)
        self.controls_table.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Set custom delegate for column 2 to handle text selection
        delegate = SelectAllDelegate(self.controls_table, self)
        self.controls_table.setItemDelegateForColumn(2, delegate)

        splitter.addWidget(self.controls_table)

        # Track editing state
        self._editing_item = None
        self._editing_original_text = None

        # Track editable columns (column 2 is Action Override, editable only in detailed view)
        self.editable_columns = {2}  # Column 2: Action (Override)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        table_layout.addWidget(splitter)
        self.tab_widget.addTab(table_tab, "Controls Table")

        # Tab 2: Device Graphics View
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "visual-templates")
        self.graphics_widget = DeviceGraphicsWidget(templates_dir)
        self.tab_widget.addTab(self.graphics_widget, "Device Graphics")

        # Status bar
        self.statusBar().showMessage("Ready")

    def restore_window_state(self):
        """Restore saved window geometry and state"""
        geometry = self.settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
            logger.debug("Restored window geometry")

        state = self.settings.get_window_state()
        if state:
            self.restoreState(state)
            logger.debug("Restored window state")

    def closeEvent(self, event):
        """Save window state before closing"""
        self.settings.set_window_geometry(self.saveGeometry())
        self.settings.set_window_state(self.saveState())
        logger.debug("Saved window state")
        event.accept()

    def auto_load_last_profile(self):
        """Automatically load the last opened profile if it exists"""
        last_profile_path = self.settings.get_last_profile_path()

        if not last_profile_path:
            logger.info("No last profile found")
            return

        if not os.path.exists(last_profile_path):
            logger.warning(f"Last profile no longer exists: {last_profile_path}")
            self.settings.clear_last_profile_path()
            return

        logger.info(f"Auto-loading last profile: {last_profile_path}")
        self.load_profile_from_path(last_profile_path)

    def import_profile(self):
        """Handle profile import button click"""
        # Get last directory if available
        last_path = self.settings.get_last_profile_path()
        start_dir = os.path.dirname(last_path) if last_path and os.path.exists(last_path) else ""

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Star Citizen Profile XML",
            start_dir,
            "XML Files (*.xml);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        self.load_profile_from_path(file_path)

    def load_profile_from_path(self, file_path: str):
        """
        Load a profile from the given file path

        Args:
            file_path: Path to the profile XML file
        """
        try:
            # Parse the profile
            self.statusBar().showMessage(f"Loading profile: {file_path}")
            logger.info(f"Loading profile: {file_path}")
            parser = ProfileParser(file_path)
            self.current_profile = parser.parse()
            self.current_profile_path = file_path

            # Save as last opened profile
            self.settings.set_last_profile_path(file_path)

            # Update UI with profile data
            self.display_profile()

            # Enable export buttons
            self.export_csv_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(True)
            self.export_word_btn.setEnabled(True)

            self.statusBar().showMessage(f"Successfully loaded: {self.current_profile.profile_name}")
            logger.info(f"Successfully loaded profile: {self.current_profile.profile_name}")

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            self.statusBar().showMessage("Error: File not found")
            logger.error(f"File not found: {file_path}")
        except ValueError as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse XML file:\n{str(e)}")
            self.statusBar().showMessage("Error: Failed to parse XML")
            logger.error(f"Parse error: {e}", exc_info=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")
            self.statusBar().showMessage("Error loading profile")
            logger.error(f"Error loading profile: {e}", exc_info=True)

    def display_profile(self):
        """Display the loaded profile data"""
        if not self.current_profile:
            return

        profile = self.current_profile

        # Update profile info label
        self.profile_info_label.setText(f"Profile: {profile.profile_name}")

        # Build summary text
        summary_parts = []
        summary_parts.append(f"Profile Name: {profile.profile_name}")
        summary_parts.append(f"Devices: {len(profile.devices)}")

        # List devices
        for device in profile.devices:
            device_name = device.product_name if device.product_name else device.device_type.capitalize()
            summary_parts.append(f"  - {device.device_type.capitalize()} {device.instance}: {device_name}")

        summary_parts.append(f"\nAction Maps: {len(profile.action_maps)}")
        summary_parts.append(f"Total Bindings: {len(profile.get_all_bindings())}")

        if profile.categories:
            summary_parts.append(f"\nCategories: {', '.join(profile.categories[:5])}")
            if len(profile.categories) > 5:
                summary_parts.append(f"  ... and {len(profile.categories) - 5} more")

        self.profile_summary.setText('\n'.join(summary_parts))

        # Populate controls table
        self.populate_controls_table()

        # Apply filters to show the rows (important when loading a new profile)
        self.apply_filters()

        # Load profile into graphics widget
        self.graphics_widget.load_profile(profile)

    def populate_controls_table(self):
        """Populate the controls table with bindings"""
        if not self.current_profile:
            return

        # Disable sorting while populating
        self.controls_table.setSortingEnabled(False)

        # Block signals to prevent itemChanged from triggering during population
        self.controls_table.blockSignals(True)

        # Get all bindings and store for filtering
        self.all_bindings = []
        for action_map in self.current_profile.action_maps:
            for binding in action_map.actions:
                self.all_bindings.append((action_map.name, binding))

        # Populate filter dropdowns
        self.populate_filter_dropdowns()

        # Set row count
        self.controls_table.setRowCount(len(self.all_bindings))

        # Determine if we're in detailed view
        is_detailed = self.show_detailed_checkbox.isChecked()

        # Configure column visibility based on view mode
        if is_detailed:
            # Detailed view: Show all 6 columns
            # 0: Action Map, 1: Action (original), 2: Action (Override), 3: Input Code, 4: Input Label, 5: Device
            self.controls_table.setColumnHidden(1, False)
            self.controls_table.setColumnHidden(2, False)
            self.controls_table.setColumnHidden(3, False)
            self.controls_table.setColumnHidden(4, False)
        else:
            # Default view: Show only 3 columns (0: Action Map, 2: Action, 5: Device)
            # Hide columns 1, 3, 4
            self.controls_table.setColumnHidden(1, True)
            self.controls_table.setColumnHidden(3, True)
            self.controls_table.setColumnHidden(4, True)
            self.controls_table.setColumnHidden(2, False)  # Show override column (as "Action")

        # Populate table
        for row, (action_map_name, binding) in enumerate(self.all_bindings):
            # Column 0: Action Map
            action_map_label = LabelGenerator.generate_actionmap_label(action_map_name)
            action_map_item = QTableWidgetItem(action_map_label)
            action_map_item.setFlags(action_map_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 0, action_map_item)

            # Column 1: Action (original auto-generated) - only visible in detailed view
            action_label_original = LabelGenerator.generate_action_label(binding.action_name)
            action_original_item = QTableWidgetItem(action_label_original)
            action_original_item.setFlags(action_original_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 1, action_original_item)

            # Column 2: Action (with override) - editable, visible in both views
            action_label_override = LabelGenerator.get_action_label(binding.action_name, binding)
            action_override_item = QTableWidgetItem(action_label_override)
            # Store binding reference in the item for later retrieval during editing
            action_override_item.setData(Qt.ItemDataRole.UserRole, (action_map_name, binding))
            self.controls_table.setItem(row, 2, action_override_item)

            # Column 3: Input Code (raw) - only visible in detailed view
            input_code_item = QTableWidgetItem(binding.input_code)
            input_code_item.setFlags(input_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 3, input_code_item)

            # Column 4: Input Label (human-readable) - only visible in detailed view
            input_label = LabelGenerator.generate_input_label(binding.input_code)
            input_label_item = QTableWidgetItem(input_label)
            input_label_item.setFlags(input_label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 4, input_label_item)

            # Column 5: Device (parsed from input code)
            device = self.parse_device_from_input(binding.input_code)
            device_item = QTableWidgetItem(device)
            device_item.setFlags(device_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 5, device_item)

        # Re-enable signals
        self.controls_table.blockSignals(False)

        # Re-enable sorting
        self.controls_table.setSortingEnabled(True)

        # Resize columns to content
        self.controls_table.resizeColumnsToContents()

        # Set column widths based on view mode
        if is_detailed:
            self.controls_table.setColumnWidth(0, 200)  # Action Map
            self.controls_table.setColumnWidth(1, 200)  # Action (Original)
            self.controls_table.setColumnWidth(2, 200)  # Action (Override)
            self.controls_table.setColumnWidth(3, 150)  # Input Code
            self.controls_table.setColumnWidth(4, 200)  # Input Label
            self.controls_table.setColumnWidth(5, 150)  # Device
        else:
            self.controls_table.setColumnWidth(0, 250)  # Action Map
            self.controls_table.setColumnWidth(2, 350)  # Action (Override)
            self.controls_table.setColumnWidth(5, 200)  # Device

    def parse_device_from_input(self, input_code: str) -> str:
        """Parse device type from input code"""
        if input_code.startswith('kb'):
            return "Keyboard"
        elif input_code.startswith('js'):
            # Extract joystick instance
            import re
            match = re.match(r'js(\d+)_', input_code)
            if match:
                instance = match.group(1)
                # Try to find device name
                for device in self.current_profile.devices:
                    if device.device_type == 'joystick' and device.instance == int(instance):
                        return device.product_name if device.product_name else f"Joystick {instance}"
                return f"Joystick {instance}"
        elif 'mouse' in input_code.lower():
            return "Mouse"
        return "Unknown"

    def populate_filter_dropdowns(self):
        """Populate the device and action map filter dropdowns"""
        # Get unique devices
        devices = set()
        action_maps = set()

        for action_map_name, binding in self.all_bindings:
            device = self.parse_device_from_input(binding.input_code)
            devices.add(device)
            action_map_label = LabelGenerator.generate_actionmap_label(action_map_name)
            action_maps.add(action_map_label)

        # Update device filter
        self.device_filter.blockSignals(True)
        self.device_filter.clear()
        self.device_filter.addItem("All Devices")
        for device in sorted(devices):
            self.device_filter.addItem(device)
        self.device_filter.blockSignals(False)

        # Update action map filter
        self.actionmap_filter.blockSignals(True)
        self.actionmap_filter.clear()
        self.actionmap_filter.addItem("All Action Maps")
        for action_map in sorted(action_maps):
            self.actionmap_filter.addItem(action_map)
        self.actionmap_filter.blockSignals(False)

    def apply_filters(self):
        """Apply current filter settings to the table"""
        if not self.all_bindings:
            return

        search_text = self.search_box.text().lower()
        device_filter = self.device_filter.currentText()
        actionmap_filter = self.actionmap_filter.currentText()
        hide_unmapped = self.hide_unmapped_checkbox.isChecked()

        # Show/hide rows based on filters
        for row in range(self.controls_table.rowCount()):
            show_row = True

            # Search filter - check all columns
            if search_text:
                row_text = ""
                for col in range(self.controls_table.columnCount()):
                    item = self.controls_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "

                if search_text not in row_text:
                    show_row = False

            # Device filter
            if show_row and device_filter != "All Devices":
                device_item = self.controls_table.item(row, 5)  # Device is now column 5
                if device_item and device_item.text() != device_filter:
                    show_row = False

            # Action map filter
            if show_row and actionmap_filter != "All Action Maps":
                actionmap_item = self.controls_table.item(row, 0)
                if actionmap_item and actionmap_item.text() != actionmap_filter:
                    show_row = False

            # Unmapped keys filter - check if input_code == input_label (after stripping)
            # or if the label indicates an empty/unmapped binding
            if show_row and hide_unmapped:
                input_code_item = self.controls_table.item(row, 3)  # Input Code is now column 3
                input_label_item = self.controls_table.item(row, 4)  # Input Label is now column 4
                if input_code_item and input_label_item:
                    input_code = input_code_item.text().strip()
                    input_label = input_label_item.text().strip()

                    # Check if they're the same after stripping
                    if input_code == input_label:
                        show_row = False
                    # Also check for patterns that indicate unmapped keys
                    # e.g., "Keyboard: ", "Joystick 1: ", "Mouse: " with nothing after
                    elif input_label.endswith(': ') or input_label.endswith(':'):
                        show_row = False

            self.controls_table.setRowHidden(row, not show_row)

        # Update status bar
        visible_rows = sum(1 for row in range(self.controls_table.rowCount())
                          if not self.controls_table.isRowHidden(row))
        total_rows = self.controls_table.rowCount()
        self.statusBar().showMessage(f"Showing {visible_rows} of {total_rows} bindings")

    def toggle_detailed_view(self):
        """Toggle between default and detailed view"""
        if not self.current_profile:
            return

        # Repopulate the table with the new view mode
        self.populate_controls_table()

        # Reapply filters
        self.apply_filters()

        # Update status message
        view_mode = "detailed" if self.show_detailed_checkbox.isChecked() else "default"
        self.statusBar().showMessage(f"Switched to {view_mode} view")

    def clear_filters(self):
        """Clear all filters"""
        self.search_box.clear()
        self.device_filter.setCurrentIndex(0)
        self.actionmap_filter.setCurrentIndex(0)
        self.hide_unmapped_checkbox.setChecked(False)
        self.statusBar().showMessage(f"Filters cleared - showing all {self.controls_table.rowCount()} bindings")

    def on_item_double_clicked(self, item):
        """Handle double-click - hide the item text while editing"""
        if item.column() == 2:  # Action (Override) column
            # Store the original text and item
            self._editing_item = item
            self._editing_original_text = item.text()

            # Temporarily clear the item's display text to prevent overlap
            # Block signals to avoid triggering on_cell_edited
            self.controls_table.blockSignals(True)
            item.setText("")
            self.controls_table.blockSignals(False)

    def on_cell_edited(self, item):
        """Handle cell editing (only column 2: Action Override is editable)"""
        if item.column() != 2:  # Only Action (Override) column is editable
            return

        # Clear editing state
        self._editing_item = None
        self._editing_original_text = None

        # Get the binding data stored in the item
        binding_data = item.data(Qt.ItemDataRole.UserRole)
        if not binding_data:
            self.statusBar().showMessage("Error: Could not save label override")
            return

        action_map_name, binding = binding_data
        new_label = item.text().strip()

        # If label is empty, remove the custom override (will fall back to auto-generated or global)
        if not new_label:
            try:
                # Import with error handling for different execution contexts
                try:
                    from utils.label_overrides import get_override_manager
                except ImportError:
                    from ..utils.label_overrides import get_override_manager

                override_manager = get_override_manager()
                override_manager.remove_custom_override(binding.action_name)

                # Clear the custom_label field to fall back to auto-generated/global
                binding.custom_label = None

                # Update the table to show the fallback label
                fallback_label = LabelGenerator.get_action_label(binding.action_name, binding)
                self.controls_table.blockSignals(True)
                item.setText(fallback_label)
                self.controls_table.blockSignals(False)

                # Update graphics widget
                self.graphics_widget.load_profile(self.current_profile)

                self.statusBar().showMessage(f"Custom label removed for '{binding.action_name}' - using auto-generated label")
            except Exception as e:
                self.statusBar().showMessage(f"Error removing label override: {str(e)}")
                print(f"Error removing label override: {e}")
            return

        # Save to override manager
        try:
            # Import with error handling for different execution contexts
            try:
                from utils.label_overrides import get_override_manager
            except ImportError:
                from ..utils.label_overrides import get_override_manager

            override_manager = get_override_manager()
            override_manager.set_custom_override(binding.action_name, new_label)

            # Update binding's custom_label field
            binding.custom_label = new_label

            # Update graphics widget
            self.graphics_widget.load_profile(self.current_profile)

            self.statusBar().showMessage(f"Label override saved: '{binding.action_name}' → '{new_label}'")
        except Exception as e:
            self.statusBar().showMessage(f"Error saving label override: {str(e)}")
            print(f"Error saving label override: {e}")

    def export_csv(self):
        """Export profile to CSV"""
        if not self.current_profile:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"{self.current_profile.profile_name}.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Determine columns based on detailed view setting
                is_detailed = self.show_detailed_checkbox.isChecked()

                if is_detailed:
                    # Write header for detailed view (all columns)
                    writer.writerow(["Action Map", "Action (Original)", "Action (Override)", "Input Code", "Input Label", "Device"])
                    visible_cols = [0, 1, 2, 3, 4, 5]
                else:
                    # Write header for default view (3 columns)
                    writer.writerow(["Action Map", "Action", "Device"])
                    visible_cols = [0, 2, 5]  # Action Map, Action (Override), Device

                # Write visible rows only
                for row in range(self.controls_table.rowCount()):
                    if not self.controls_table.isRowHidden(row):
                        row_data = []
                        for col in visible_cols:
                            item = self.controls_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

            QMessageBox.information(self, "Success", f"Profile exported to:\n{file_path}")
            self.statusBar().showMessage(f"Exported to CSV: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")
            self.statusBar().showMessage("CSV export failed")

    def export_pdf(self):
        """Export profile to PDF"""
        if not self.current_profile:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            f"{self.current_profile.profile_name}.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch

            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title = Paragraph(f"<b>{self.current_profile.profile_name}</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            # Profile info
            info_text = f"Devices: {len(self.current_profile.devices)} | "
            info_text += f"Bindings: {len(self.current_profile.get_all_bindings())}"
            info = Paragraph(info_text, styles['Normal'])
            elements.append(info)
            elements.append(Spacer(1, 0.3 * inch))

            # Determine columns based on detailed view setting
            is_detailed = self.show_detailed_checkbox.isChecked()

            if is_detailed:
                # Detailed view header and columns
                table_data = [["Action Map", "Action (Original)", "Action (Override)", "Input Code", "Input Label", "Device"]]
                visible_cols = [0, 1, 2, 3, 4, 5]
                col_widths = [1.3*inch, 1.5*inch, 1.5*inch, 1*inch, 1.5*inch, 1.2*inch]
            else:
                # Default view header and columns
                table_data = [["Action Map", "Action", "Device"]]
                visible_cols = [0, 2, 5]
                col_widths = [2.5*inch, 4*inch, 2.5*inch]

            for row in range(self.controls_table.rowCount()):
                if not self.controls_table.isRowHidden(row):
                    row_data = []
                    for col in visible_cols:
                        item = self.controls_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    table_data.append(row_data)

            # Create table
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(table)

            # Build PDF
            doc.build(elements)

            QMessageBox.information(self, "Success", f"Profile exported to:\n{file_path}")
            self.statusBar().showMessage(f"Exported to PDF: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
            self.statusBar().showMessage("PDF export failed")

    def export_word(self):
        """Export profile to Word document"""
        if not self.current_profile:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Word",
            f"{self.current_profile.profile_name}.docx",
            "Word Documents (*.docx)"
        )

        if not file_path:
            return

        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = Document()

            # Title
            title = doc.add_heading(self.current_profile.profile_name, 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Profile info
            info = doc.add_paragraph()
            info.add_run(f"Devices: {len(self.current_profile.devices)} | ")
            info.add_run(f"Total Bindings: {len(self.current_profile.get_all_bindings())}")
            info.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph()  # Spacer

            # Device list
            doc.add_heading("Devices", 2)
            for device in self.current_profile.devices:
                device_name = device.product_name if device.product_name else device.device_type.capitalize()
                doc.add_paragraph(
                    f"{device.device_type.capitalize()} {device.instance}: {device_name}",
                    style='List Bullet'
                )

            doc.add_paragraph()  # Spacer

            # Control bindings table
            doc.add_heading("Control Bindings", 2)

            # Determine columns based on detailed view setting
            is_detailed = self.show_detailed_checkbox.isChecked()

            if is_detailed:
                headers = ["Action Map", "Action (Original)", "Action (Override)", "Input Code", "Input Label", "Device"]
                visible_cols = [0, 1, 2, 3, 4, 5]
            else:
                headers = ["Action Map", "Action", "Device"]
                visible_cols = [0, 2, 5]

            # Create table
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Light Grid Accent 1'

            # Header row
            header_cells = table.rows[0].cells
            for i, header in enumerate(headers):
                header_cells[i].text = header
                # Make header bold
                for paragraph in header_cells[i].paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True

            # Add data rows
            for row in range(self.controls_table.rowCount()):
                if not self.controls_table.isRowHidden(row):
                    row_cells = table.add_row().cells
                    for i, col in enumerate(visible_cols):
                        item = self.controls_table.item(row, col)
                        row_cells[i].text = item.text() if item else ""

            # Save document
            doc.save(file_path)

            QMessageBox.information(self, "Success", f"Profile exported to:\n{file_path}")
            self.statusBar().showMessage(f"Exported to Word: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export Word document:\n{str(e)}")
            self.statusBar().showMessage("Word export failed")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())