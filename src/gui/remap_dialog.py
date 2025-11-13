"""
Simplified remapping dialog for editing button assignments
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QComboBox, QGroupBox, QMessageBox,
                              QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.profile_model import ActionBinding, ControlProfile
from parser.label_generator import LabelGenerator
from utils.input_validator import InputValidator

logger = logging.getLogger(__name__)


class RemapDialog(QDialog):
    """Simplified dialog for editing button assignments and labels"""

    # Signal emitted when binding is changed: (action_name, new_label)
    binding_changed = pyqtSignal(str, str)

    def __init__(self, input_code: str, profile: ControlProfile, parent=None):
        super().__init__(parent)
        self.input_code = input_code
        self.profile = profile
        self.current_binding = self.find_binding_by_input_code(input_code)

        # Store all actions grouped by action map
        self.actions_by_map = {}
        self.action_map_friendly_names = {}
        self._build_action_maps()

        self.setWindowTitle("Edit Button Assignment")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.setup_ui()
        self.populate_from_binding()

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
        # Remove underscores and capitalize words
        words = map_name.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)

    def setup_ui(self):
        """Set up the simplified user interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header - show button info
        header_label = QLabel(f"<b>Editing Button:</b> {self.input_code}")
        header_font = QFont()
        header_font.setPointSize(11)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Show input description
        input_desc = InputValidator.get_input_description(self.input_code)
        desc_label = QLabel(f"Input: {input_desc}")
        desc_label.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        layout.addSpacing(10)

        # === LABEL EDITING SECTION ===
        label_group = QGroupBox("Display Label")
        label_layout = QFormLayout()
        label_group.setLayout(label_layout)

        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Enter custom label")
        label_layout.addRow("Custom Label:", self.label_edit)

        layout.addWidget(label_group)

        # === ACTION MAPPING SECTION ===
        action_group = QGroupBox("Action Assignment")
        action_layout = QVBoxLayout()
        action_group.setLayout(action_layout)

        # Current action display
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("<b>Current Action:</b>"))
        self.current_action_label = QLabel()
        self.current_action_label.setStyleSheet("font-size: 11px; color: #0066cc;")
        current_layout.addWidget(self.current_action_label)
        current_layout.addStretch()
        action_layout.addLayout(current_layout)

        action_layout.addSpacing(10)

        # Action map category selection
        category_layout = QFormLayout()

        self.action_map_combo = QComboBox()
        self.action_map_combo.addItem("-- Select Action Category --", None)

        # Add "ALL" option to show all actions
        self.action_map_combo.addItem("ALL", "ALL")

        # Add all action map categories
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

        action_layout.addLayout(category_layout)

        # Show action description when selected
        self.action_desc_label = QLabel("")
        self.action_desc_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-left: 20px;")
        self.action_desc_label.setWordWrap(True)
        action_layout.addWidget(self.action_desc_label)
        self.action_combo.currentIndexChanged.connect(self.on_action_selected)

        layout.addWidget(action_group)

        # Info message
        info_label = QLabel("Select an action category and action to assign to this button, or edit the label.")
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def find_binding_by_input_code(self, input_code: str):
        """Find binding object by input code"""
        for action_map in self.profile.action_maps:
            for binding in action_map.actions:
                if binding.input_code == input_code:
                    return binding
        return None

    def populate_from_binding(self):
        """Populate dialog fields from the current binding (if exists)"""
        if self.current_binding:
            # Show current action
            action_label = LabelGenerator.get_action_label(
                self.current_binding.action_name,
                self.current_binding
            )
            self.current_action_label.setText(
                f"{self.current_binding.action_name} ({action_label})"
            )

            # Set custom label
            custom_label = getattr(self.current_binding, 'custom_label', None) or ""
            self.label_edit.setText(custom_label)

            # Pre-select the action map and action in dropdowns
            for action_map in self.profile.action_maps:
                if self.current_binding in action_map.actions:
                    # Find and select the action map
                    for i in range(self.action_map_combo.count()):
                        if self.action_map_combo.itemData(i) == action_map.name:
                            self.action_map_combo.setCurrentIndex(i)
                            # This will trigger on_action_map_changed
                            break

                    # Find and select the action
                    for i in range(self.action_combo.count()):
                        if self.action_combo.itemData(i) == self.current_binding:
                            self.action_combo.setCurrentIndex(i)
                            break
                    break
        else:
            # No current binding for this button
            self.current_action_label.setText("(None)")
            self.label_edit.setText("")

    def on_action_map_changed(self, index: int):
        """Handle action map category selection"""
        # Clear action combo
        self.action_combo.clear()
        self.action_combo.addItem("-- Select Action --", None)
        self.action_desc_label.setText("")

        # Get selected action map
        map_name = self.action_map_combo.itemData(index)

        if map_name == "ALL":
            # Show all actions from all categories
            all_actions = []
            for actions in self.actions_by_map.values():
                all_actions.extend(actions)

            # Sort all actions by friendly label for better readability
            for action_binding in sorted(all_actions, key=lambda b: LabelGenerator.get_action_label(b.action_name, b)):
                # Get friendly label
                action_label = LabelGenerator.get_action_label(
                    action_binding.action_name,
                    action_binding
                )
                display_text = f"{action_label} ({action_binding.action_name})"
                self.action_combo.addItem(display_text, action_binding)

            self.action_combo.setEnabled(True)

        elif map_name:
            # Populate actions for this specific map
            actions = self.actions_by_map.get(map_name, [])
            for action_binding in sorted(actions, key=lambda b: LabelGenerator.get_action_label(b.action_name, b)):
                # Get friendly label
                action_label = LabelGenerator.get_action_label(
                    action_binding.action_name,
                    action_binding
                )
                display_text = f"{action_label} ({action_binding.action_name})"
                self.action_combo.addItem(display_text, action_binding)

            self.action_combo.setEnabled(True)
        else:
            self.action_combo.setEnabled(False)

    def on_action_selected(self, index: int):
        """Handle action selection"""
        selected_binding = self.action_combo.itemData(index)

        if selected_binding:
            # Show description
            default_label = LabelGenerator.generate_action_label(selected_binding.action_name)
            self.action_desc_label.setText(f"Default label: {default_label}")

            # Update label field if empty
            if not self.label_edit.text():
                self.label_edit.setText(default_label)
        else:
            self.action_desc_label.setText("")

    def accept_changes(self):
        """Accept and apply changes"""
        # Get selected action (if any)
        selected_binding = self.action_combo.currentData()
        new_label = self.label_edit.text().strip()

        # Check if anything changed
        label_changed = False
        action_changed = False

        if self.current_binding:
            # Existing binding - check for changes
            old_label = getattr(self.current_binding, 'custom_label', None) or ""
            label_changed = new_label != old_label

            if selected_binding and selected_binding != self.current_binding:
                # User wants to assign a different action to this button
                action_changed = True

        else:
            # No existing binding - this is a new assignment
            if selected_binding:
                action_changed = True
            label_changed = bool(new_label)

        # If no changes, just close
        if not label_changed and not action_changed:
            self.accept()
            return

        # Handle action change
        if action_changed and selected_binding:
            # Check if the new action already has a binding
            old_input_code = selected_binding.input_code

            if old_input_code and old_input_code != self.input_code:
                # Warn about rebinding
                reply = QMessageBox.question(
                    self,
                    "Rebind Action",
                    f"The action '{selected_binding.action_name}' is currently bound to:\n"
                    f"  {old_input_code} ({InputValidator.get_input_description(old_input_code)})\n\n"
                    f"Do you want to move it to:\n"
                    f"  {self.input_code} ({InputValidator.get_input_description(self.input_code)})?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    return

            # If this button had a previous binding, clear it
            if self.current_binding and self.current_binding != selected_binding:
                # Unbind the old action from this button
                self.current_binding.input_code = ""

            # Bind the new action to this button
            selected_binding.input_code = self.input_code

            # Emit signal with the new action and label
            self.binding_changed.emit(selected_binding.action_name, new_label)

        elif label_changed and self.current_binding:
            # Only label changed
            self.binding_changed.emit(self.current_binding.action_name, new_label)

        # Accept dialog
        self.accept()
