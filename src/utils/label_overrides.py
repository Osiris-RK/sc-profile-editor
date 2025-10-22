"""
Label Override Manager

Manages custom label overrides for action names. Provides a two-tier system:
- Global default overrides (label_overrides.json) - shipped with app
- Custom user overrides (label_overrides_custom.json) - user modifications

Load priority: custom → global → auto-generated (via LabelGenerator)
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
import shutil


class LabelOverrideManager:
    """Manages action label overrides with custom and global fallback."""

    # File names
    GLOBAL_OVERRIDE_FILE = "label_overrides.json"
    CUSTOM_OVERRIDE_FILE = "label_overrides_custom.json"

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the label override manager.

        Args:
            base_path: Base directory for override files. If None, uses project root.
        """
        if base_path is None:
            # Default to project root directory
            base_path = Path(__file__).parent.parent.parent

        self.base_path = Path(base_path)
        self.global_file_path = self.base_path / self.GLOBAL_OVERRIDE_FILE
        self.custom_file_path = self.base_path / self.CUSTOM_OVERRIDE_FILE

        # Cache for loaded overrides
        self._custom_overrides: Optional[Dict[str, str]] = None
        self._global_overrides: Optional[Dict[str, str]] = None

    def load_global_overrides(self) -> Dict[str, str]:
        """
        Load global default overrides from label_overrides.json.

        Returns:
            Dictionary mapping action names to override labels.
        """
        if self._global_overrides is not None:
            return self._global_overrides

        if not self.global_file_path.exists():
            print(f"Global override file not found: {self.global_file_path}")
            self._global_overrides = {}
            return self._global_overrides

        try:
            with open(self.global_file_path, 'r', encoding='utf-8') as f:
                self._global_overrides = json.load(f)
            print(f"Loaded {len(self._global_overrides)} global label overrides")
        except Exception as e:
            print(f"Error loading global overrides: {e}")
            self._global_overrides = {}

        return self._global_overrides

    def load_custom_overrides(self) -> Dict[str, str]:
        """
        Load custom user overrides from label_overrides_custom.json.

        Returns:
            Dictionary mapping action names to override labels.
        """
        if self._custom_overrides is not None:
            return self._custom_overrides

        if not self.custom_file_path.exists():
            print(f"Custom override file not found: {self.custom_file_path}")
            self._custom_overrides = {}
            return self._custom_overrides

        try:
            with open(self.custom_file_path, 'r', encoding='utf-8') as f:
                self._custom_overrides = json.load(f)
            print(f"Loaded {len(self._custom_overrides)} custom label overrides")
        except Exception as e:
            print(f"Error loading custom overrides: {e}")
            self._custom_overrides = {}

        return self._custom_overrides

    def get_override_label(self, action_name: str) -> Optional[str]:
        """
        Get the override label for an action name.

        Priority: custom → global → None

        Args:
            action_name: The action name to look up (e.g., "v_attack1")

        Returns:
            Override label if found, None otherwise.
        """
        # Check custom overrides first
        custom = self.load_custom_overrides()
        if action_name in custom:
            return custom[action_name]

        # Fall back to global overrides
        global_overrides = self.load_global_overrides()
        if action_name in global_overrides:
            return global_overrides[action_name]

        # No override found
        return None

    def set_custom_override(self, action_name: str, custom_label: str):
        """
        Set a custom override label for an action.

        If this is the first custom override, copies the global file to custom file.

        Args:
            action_name: The action name (e.g., "v_attack1")
            custom_label: The custom label to use
        """
        # Ensure custom overrides are loaded
        custom = self.load_custom_overrides()

        # If custom file doesn't exist and global does, copy global → custom first
        if not self.custom_file_path.exists() and self.global_file_path.exists():
            try:
                shutil.copy2(self.global_file_path, self.custom_file_path)
                print(f"Created custom override file from global: {self.custom_file_path}")
                # Reload custom overrides from the newly created file
                self._custom_overrides = None
                custom = self.load_custom_overrides()
            except Exception as e:
                print(f"Error copying global to custom override file: {e}")

        # Update the custom override
        custom[action_name] = custom_label

        # Save to file
        self._save_custom_overrides(custom)

    def remove_custom_override(self, action_name: str):
        """
        Remove a custom override for an action.

        Args:
            action_name: The action name to remove override for
        """
        custom = self.load_custom_overrides()

        if action_name in custom:
            del custom[action_name]
            self._save_custom_overrides(custom)
            print(f"Removed custom override for: {action_name}")

    def _save_custom_overrides(self, overrides: Dict[str, str]):
        """
        Save custom overrides to file.

        Args:
            overrides: Dictionary of action names to custom labels
        """
        try:
            with open(self.custom_file_path, 'w', encoding='utf-8') as f:
                json.dump(overrides, f, indent=2, ensure_ascii=False)
            self._custom_overrides = overrides
            print(f"Saved {len(overrides)} custom overrides to {self.custom_file_path}")
        except Exception as e:
            print(f"Error saving custom overrides: {e}")

    def get_all_overrides(self) -> Dict[str, str]:
        """
        Get all overrides (merged custom + global, with custom taking priority).

        Returns:
            Dictionary of all overrides.
        """
        global_overrides = self.load_global_overrides()
        custom = self.load_custom_overrides()

        # Merge: global first, then custom (custom overrides global)
        merged = dict(global_overrides)
        merged.update(custom)

        return merged

    def reload(self):
        """Force reload of override files from disk."""
        self._custom_overrides = None
        self._global_overrides = None
        self.load_global_overrides()
        self.load_custom_overrides()


# Global instance for easy access
_override_manager: Optional[LabelOverrideManager] = None


def get_override_manager() -> LabelOverrideManager:
    """Get the global LabelOverrideManager instance."""
    global _override_manager
    if _override_manager is None:
        _override_manager = LabelOverrideManager()
    return _override_manager
