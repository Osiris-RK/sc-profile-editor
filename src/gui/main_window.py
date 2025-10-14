"""
Main application window
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFileDialog, QMessageBox,
                              QTextEdit, QTableWidget, QTableWidgetItem, QSplitter,
                              QLineEdit, QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser.xml_parser import ProfileParser
from parser.label_generator import LabelGenerator
from models.profile_model import ControlProfile


class MainWindow(QMainWindow):
    """Main application window for SC Profile Viewer"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star Citizen Profile Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Store current profile
        self.current_profile = None

        # Store all bindings for filtering
        self.all_bindings = []

        # Create UI
        self.setup_ui()

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

        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)

        main_layout.addWidget(filter_group)

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
        self.controls_table.setColumnCount(5)
        self.controls_table.setHorizontalHeaderLabels([
            "Action Map", "Action", "Input Code", "Input Label", "Device"
        ])
        self.controls_table.horizontalHeader().setStretchLastSection(False)
        self.controls_table.setAlternatingRowColors(True)
        self.controls_table.setSortingEnabled(True)
        self.controls_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.controls_table.itemChanged.connect(self.on_cell_edited)
        splitter.addWidget(self.controls_table)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def import_profile(self):
        """Handle profile import button click"""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Star Citizen Profile XML",
            "",
            "XML Files (*.xml);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        try:
            # Parse the profile
            self.statusBar().showMessage(f"Loading profile: {file_path}")
            parser = ProfileParser(file_path)
            self.current_profile = parser.parse()

            # Update UI with profile data
            self.display_profile()

            # Enable export buttons
            self.export_csv_btn.setEnabled(True)
            self.export_pdf_btn.setEnabled(True)
            self.export_word_btn.setEnabled(True)

            self.statusBar().showMessage(f"Successfully loaded: {self.current_profile.profile_name}")

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            self.statusBar().showMessage("Error: File not found")
        except ValueError as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse XML file:\n{str(e)}")
            self.statusBar().showMessage("Error: Failed to parse XML")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")
            self.statusBar().showMessage("Error loading profile")

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

        # Populate table
        for row, (action_map_name, binding) in enumerate(self.all_bindings):
            # Action Map
            action_map_label = LabelGenerator.generate_actionmap_label(action_map_name)
            self.controls_table.setItem(row, 0, QTableWidgetItem(action_map_label))

            # Action
            action_label = LabelGenerator.generate_action_label(binding.action_name)
            self.controls_table.setItem(row, 1, QTableWidgetItem(action_label))

            # Input Code (raw) - make read-only
            input_code_item = QTableWidgetItem(binding.input_code)
            input_code_item.setFlags(input_code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 2, input_code_item)

            # Input Label (human-readable) - make read-only
            input_label = LabelGenerator.generate_input_label(binding.input_code)
            input_label_item = QTableWidgetItem(input_label)
            input_label_item.setFlags(input_label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 3, input_label_item)

            # Device (parsed from input code) - make read-only
            device = self.parse_device_from_input(binding.input_code)
            device_item = QTableWidgetItem(device)
            device_item.setFlags(device_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.controls_table.setItem(row, 4, device_item)

        # Re-enable signals
        self.controls_table.blockSignals(False)

        # Re-enable sorting
        self.controls_table.setSortingEnabled(True)

        # Resize columns to content
        self.controls_table.resizeColumnsToContents()

        # Make Action Map and Action columns wider
        self.controls_table.setColumnWidth(0, 200)
        self.controls_table.setColumnWidth(1, 250)
        self.controls_table.setColumnWidth(3, 200)

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
                device_item = self.controls_table.item(row, 4)
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
                input_code_item = self.controls_table.item(row, 2)
                input_label_item = self.controls_table.item(row, 3)
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

    def clear_filters(self):
        """Clear all filters"""
        self.search_box.clear()
        self.device_filter.setCurrentIndex(0)
        self.actionmap_filter.setCurrentIndex(0)
        self.hide_unmapped_checkbox.setChecked(False)
        self.statusBar().showMessage(f"Filters cleared - showing all {self.controls_table.rowCount()} bindings")

    def on_cell_edited(self, item):
        """Handle cell editing (only Action Map and Action columns are editable)"""
        if item.column() in [0, 1]:  # Action Map or Action column
            self.statusBar().showMessage(f"Label updated: {item.text()}")
            # Note: This is just a UI change, actual XML update would be in export

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

                # Write header
                writer.writerow(["Action Map", "Action", "Input Code", "Input Label", "Device"])

                # Write visible rows only
                for row in range(self.controls_table.rowCount()):
                    if not self.controls_table.isRowHidden(row):
                        row_data = []
                        for col in range(self.controls_table.columnCount()):
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

            # Collect visible rows
            table_data = [["Action Map", "Action", "Input Code", "Input Label", "Device"]]

            for row in range(self.controls_table.rowCount()):
                if not self.controls_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.controls_table.columnCount()):
                        item = self.controls_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    table_data.append(row_data)

            # Create table
            table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 2*inch, 1.5*inch])
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

            # Create table
            table = doc.add_table(rows=1, cols=5)
            table.style = 'Light Grid Accent 1'

            # Header row
            header_cells = table.rows[0].cells
            headers = ["Action Map", "Action", "Input Code", "Input Label", "Device"]
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
                    for col in range(self.controls_table.columnCount()):
                        item = self.controls_table.item(row, col)
                        row_cells[col].text = item.text() if item else ""

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