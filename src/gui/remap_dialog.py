"""
Remapping dialog for editing button assignments with multi-action support
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QComboBox, QGroupBox, QMessageBox,
                              QFormLayout, QDialogButtonBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.profile_model import ActionBinding, ControlProfile
from parser.label_generator import LabelGenerator
from utils.input_validator import InputValidator
from utils.input_detector import InputDetector

logger = logging.getLogger(__name__)


class ActionAssignmentWidget(QWidget):
    """Widget for displaying and editing a single action assignment"""

    # Signals
    delete_requested = pyqtSignal(object)  # Emits the binding

    def __init__(self, binding: ActionBinding, label_generator, parent=None):
        super().__init__(parent)
        self.binding = binding
        self.label_generator = label_generator
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for this action assignment"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(layout)

        # Action name and label display
        action_label = self.label_generator.get_action_label(
            self.binding.action_name,
            self.binding
        )

        # Header with action info
        header_layout = QHBoxLayout()

        action_info_label = QLabel(f"<b>{action_label}</b>")
        action_info_label.setStyleSheet("font-size: 10px;")
        header_layout.addWidget(action_info_label)

        action_name_label = QLabel(f"<span style='color: #666; font-size: 9px;'>({self.binding.action_name})</span>")
        header_layout.addWidget(action_name_label)

        header_layout.addStretch()

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setMaximumWidth(80)
        delete_btn.setStyleSheet("font-size: 9px; padding: 3px 6px;")
        delete_btn.clicked.connect(self.on_delete_clicked)
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Custom label editor
        label_layout = QFormLayout()

        self.label_edit = QLineEdit()
        custom_label = getattr(self.binding, 'custom_label', None) or ""
        self.label_edit.setText(custom_label)
        self.label_edit.setPlaceholderText(f"Default: {action_label}")
        label_layout.addRow("Custom Label:", self.label_edit)

        layout.addLayout(label_layout)

        # Border styling
        self.setStyleSheet("""
            ActionAssignmentWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                margin: 4px 0px;
            }
        """)

    def on_delete_clicked(self):
        """Handle delete button click"""
        reply = QMessageBox.question(
            self,
            "Delete Assignment",
            f"Are you sure you want to delete the assignment for:\n{self.binding.action_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(self.binding)

    def get_custom_label(self) -> str:
        """Get the custom label from the text field"""
        return self.label_edit.text().strip()


class RemapDialog(QDialog):
    """Dialog for editing button assignments with support for multiple actions"""

    # Signal emitted when bindings are changed
    bindings_changed = pyqtSignal(list)  # List of modified bindings

    def __init__(self, input_code: str, profile: ControlProfile, parent=None):
        super().__init__(parent)
        self.input_code = input_code
        self.profile = profile
        self.bindings_for_input = self.find_bindings_by_input_code(input_code)
        self.deleted_bindings = []  # Track bindings to be deleted

        # Store all actions grouped by action map
        self.actions_by_map = {}
        self.action_map_friendly_names = {}
        self._build_action_maps()

        # Input detection setup
        self.input_detector = InputDetector()
        self.detecting_input = False

        # Store action assignment widgets for easy access
        self.action_widgets = []

        self.setWindowTitle("Edit Button Assignment")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.populate_from_bindings()

    def _build_action_maps(self):
        """Build action map structure for dropdowns"""
        for action_map in self.profile.action_maps:
            # Convert internal name to friendly name
            friendly_name = self._get_friendly_map_name(action_map.name)
            self.action_map_friendly_names[action_map.name] = friendly_name

            # Store actions by map
            self.actions_by_map[action_map.name] = action_map.actions

    def _get_friendly_map_name(self, map_name: str) -> str:
        """Convert internal action map name to friendly display name"""
        words = map_name.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)

    def find_bindings_by_input_code(self, input_code: str) -> list:
        """Find all bindings for an input code"""
        bindings = []
        for action_map in self.profile.action_maps:
            for binding in action_map.actions:
                if binding.input_code == input_code:
                    bindings.append(binding)
        return bindings

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header - show button info
        header_label = QLabel(f"<b>Editing Button:</b> {self.input_code}")
        header_font = QFont()
        header_font.setPointSize(11)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Show input description with detect button
        input_desc_layout = QHBoxLayout()
        input_desc = InputValidator.get_input_description(self.input_code)
        desc_label = QLabel(f"Input: {input_desc}")
        desc_label.setStyleSheet("color: #666; font-size: 10px;")
        self.desc_label = desc_label
        input_desc_layout.addWidget(desc_label)
        input_desc_layout.addStretch()

        self.detect_input_btn = QPushButton("Detect Input")
        self.detect_input_btn.setMaximumWidth(150)
        self.detect_input_btn.clicked.connect(self.on_detect_input_clicked)
        input_desc_layout.addWidget(self.detect_input_btn)

        layout.addLayout(input_desc_layout)
        layout.addSpacing(10)

        # === CURRENT ACTIONS SECTION ===
        current_group = QGroupBox("Current Actions for This Button")
        current_layout = QVBoxLayout()
        current_group.setLayout(current_layout)

        # Scrollable area for action widgets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.actions_container = QWidget()
        self.actions_container_layout = QVBoxLayout()
        self.actions_container_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_container.setLayout(self.actions_container_layout)

        scroll_area.setWidget(self.actions_container)
        current_layout.addWidget(scroll_area)

        # "No actions" placeholder
        self.no_actions_label = QLabel("No actions assigned to this button yet.")
        self.no_actions_label.setStyleSheet("color: #999; font-style: italic; padding: 10px;")
        self.actions_container_layout.addWidget(self.no_actions_label)

        layout.addWidget(current_group, 1)  # Stretch this section

        # === ADD NEW ACTION SECTION ===
        add_group = QGroupBox("Add New Action")
        add_layout = QVBoxLayout()
        add_group.setLayout(add_layout)

        # Action map category selection
        category_layout = QFormLayout()

        self.action_map_combo = QComboBox()
        self.action_map_combo.addItem("-- Select Action Category --", None)
        self.action_map_combo.addItem("ALL", "ALL")

        for map_name in sorted(self.actions_by_map.keys()):
            friendly_name = self.action_map_friendly_names[map_name]
            self.action_map_combo.addItem(friendly_name, map_name)

        self.action_map_combo.currentIndexChanged.connect(self.on_action_map_changed)
        category_layout.addRow("Action Category:", self.action_map_combo)

        # Action selection (filtered by category)
        self.action_combo = QComboBox()
        self.action_combo.addItem("-- Select Action --", None)
        self.action_combo.setEnabled(False)
        category_layout.addRow("Action:", self.action_combo)

        add_layout.addLayout(category_layout)

        # Show action description when selected
        self.action_desc_label = QLabel("")
        self.action_desc_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        self.action_desc_label.setWordWrap(True)
        add_layout.addWidget(self.action_desc_label)
        self.action_combo.currentIndexChanged.connect(self.on_action_selected)

        # Add button
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        self.add_action_btn = QPushButton("Add Action")
        self.add_action_btn.setMaximumWidth(120)
        self.add_action_btn.clicked.connect(self.on_add_action_clicked)
        self.add_action_btn.setEnabled(False)
        add_btn_layout.addWidget(self.add_action_btn)
        add_layout.addLayout(add_btn_layout)

        layout.addWidget(add_group)

        # Info message
        info_label = QLabel("You can add multiple actions to the same button, or delete existing ones.")
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_from_bindings(self):
        """Populate dialog from all bindings for this input code"""
        if self.bindings_for_input:
            # Hide "no actions" label
            self.no_actions_label.hide()

            # Create widget for each action
            for binding in self.bindings_for_input:
                self.add_action_widget(binding)
        else:
            # Show "no actions" label
            self.no_actions_label.show()

    def add_action_widget(self, binding: ActionBinding):
        """Add an action assignment widget to the display"""
        widget = ActionAssignmentWidget(binding, LabelGenerator, self)
        widget.delete_requested.connect(self.on_action_delete_requested)
        self.action_widgets.append(widget)

        # Insert before the stretch
        self.actions_container_layout.insertWidget(
            self.actions_container_layout.count() - 1,
            widget
        )

    def on_action_delete_requested(self, binding: ActionBinding):
        """Handle request to delete an action"""
        self.deleted_bindings.append(binding)

        # Remove widget from display
        for i, widget in enumerate(self.action_widgets):
            if widget.binding == binding:
                self.actions_container_layout.removeWidget(widget)
                widget.deleteLater()
                self.action_widgets.pop(i)
                break

        # Remove from current bindings list
        if binding in self.bindings_for_input:
            self.bindings_for_input.remove(binding)

        # Show "no actions" label if empty
        if not self.action_widgets:
            self.no_actions_label.show()

    def on_action_map_changed(self, index: int):
        """Handle action map category selection"""
        self.action_combo.clear()
        self.action_combo.addItem("-- Select Action --", None)
        self.action_desc_label.setText("")
        self.add_action_btn.setEnabled(False)

        map_name = self.action_map_combo.itemData(index)

        if map_name == "ALL":
            all_actions = []
            for actions in self.actions_by_map.values():
                all_actions.extend(actions)

            for action_binding in sorted(all_actions, key=lambda b: LabelGenerator.get_action_label(b.action_name, b)):
                action_label = LabelGenerator.get_action_label(action_binding.action_name, action_binding)
                display_text = f"{action_label} ({action_binding.action_name})"
                self.action_combo.addItem(display_text, action_binding)

            self.action_combo.setEnabled(True)

        elif map_name:
            actions = self.actions_by_map.get(map_name, [])
            for action_binding in sorted(actions, key=lambda b: LabelGenerator.get_action_label(b.action_name, b)):
                action_label = LabelGenerator.get_action_label(action_binding.action_name, action_binding)
                display_text = f"{action_label} ({action_binding.action_name})"
                self.action_combo.addItem(display_text, action_binding)

            self.action_combo.setEnabled(True)
        else:
            self.action_combo.setEnabled(False)

    def on_action_selected(self, index: int):
        """Handle action selection"""
        selected_binding = self.action_combo.itemData(index)

        if selected_binding:
            # Check if this action is already assigned to this button
            already_assigned = any(b.action_name == selected_binding.action_name
                                  for b in self.bindings_for_input)

            if already_assigned:
                self.action_desc_label.setText("(Already assigned to this button)")
                self.add_action_btn.setEnabled(False)
            else:
                default_label = LabelGenerator.generate_action_label(selected_binding.action_name)
                self.action_desc_label.setText(f"Default label: {default_label}")
                self.add_action_btn.setEnabled(True)
        else:
            self.action_desc_label.setText("")
            self.add_action_btn.setEnabled(False)

    def on_add_action_clicked(self):
        """Handle adding a new action to this button"""
        selected_binding = self.action_combo.currentData()

        if not selected_binding:
            return

        # Check if action is already bound elsewhere
        # Only show rebind warning if the action is bound to a different input (input doesn't end with underscore)
        is_bound = selected_binding.input_code and not selected_binding.input_code.endswith('_')
        if is_bound and selected_binding.input_code != self.input_code:
            reply = QMessageBox.question(
                self,
                "Rebind Action",
                f"The action '{selected_binding.action_name}' is currently bound to:\n"
                f"  {selected_binding.input_code} ({InputValidator.get_input_description(selected_binding.input_code)})\n\n"
                f"Do you want to move it to:\n"
                f"  {self.input_code} ({InputValidator.get_input_description(self.input_code)})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        # Bind the action to this button
        selected_binding.input_code = self.input_code

        # Add to our current bindings list
        if selected_binding not in self.bindings_for_input:
            self.bindings_for_input.append(selected_binding)

        # Add widget to display
        self.add_action_widget(selected_binding)

        # Hide "no actions" label
        if self.action_widgets:
            self.no_actions_label.hide()

        # Reset the selector
        self.action_map_combo.setCurrentIndex(0)
        self.action_combo.setCurrentIndex(0)

    def accept_changes(self):
        """Accept and apply all changes"""
        # Collect all modified bindings (with custom labels)
        modified_bindings = []

        # Update custom labels for all current bindings
        for i, widget in enumerate(self.action_widgets):
            custom_label = widget.get_custom_label()
            binding = widget.binding

            # Set custom label
            default_label = LabelGenerator.generate_action_label(binding.action_name)
            if custom_label:
                binding.custom_label = custom_label
            else:
                binding.custom_label = None

            modified_bindings.append(binding)

        # Clear input code for deleted bindings
        for binding in self.deleted_bindings:
            binding.input_code = ""
            modified_bindings.append(binding)

        # Emit signal with all modified bindings
        self.bindings_changed.emit(modified_bindings)

        # Accept dialog
        self.accept()

    def on_detect_input_clicked(self):
        """Handle Detect Input button click"""
        if self.detecting_input:
            # Stop detection
            self.input_detector.stop_detection()
            self.detecting_input = False
            self.detect_input_btn.setText("Detect Input")
            self.detect_input_btn.setEnabled(True)
            self._disable_controls(False)
            logger.info("Input detection cancelled")
        else:
            # Start detection
            self.detecting_input = True
            self.detect_input_btn.setText("Listening... (Cancel)")
            self._disable_controls(True)
            logger.info("Starting input detection")

            # Start input detection
            detector_thread = self.input_detector.start_detection(timeout_ms=10000)
            detector_thread.input_detected.connect(self.on_input_detected)
            detector_thread.detection_cancelled.connect(self.on_input_detection_timeout)

    def on_input_detected(self, input_code: str, description: str):
        """Handle detected input"""
        logger.info(f"Input detected: {input_code} - {description}")

        # Update the stored input code
        self.input_code = input_code

        # Update the UI
        self.desc_label.setText(f"Input: {description}")

        # Stop detection and re-enable controls
        self.detecting_input = False
        self.detect_input_btn.setText("Detect Input")
        self._disable_controls(False)

    def on_input_detection_timeout(self):
        """Handle input detection timeout"""
        logger.info("Input detection timed out")

        QMessageBox.warning(
            self,
            "No Input Detected",
            "No input was detected within 10 seconds.\n\nPlease try again."
        )

        self.detecting_input = False
        self.detect_input_btn.setText("Detect Input")
        self._disable_controls(False)

    def _disable_controls(self, disable: bool):
        """Enable/disable controls during input detection"""
        self.action_map_combo.setEnabled(not disable)
        self.action_combo.setEnabled(not disable)
        self.add_action_btn.setEnabled(not disable)
        for child in self.findChildren(QPushButton):
            if child != self.detect_input_btn:
                child.setEnabled(not disable)
