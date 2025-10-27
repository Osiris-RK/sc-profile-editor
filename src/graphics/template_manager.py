"""
Device template manager for loading and matching device graphics
"""

import json
import logging
import os
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceTemplate:
    """Represents a device template with image and metadata"""
    id: str
    name: str
    image_path: str
    device_match_patterns: List[str]
    device_type: str
    button_coordinates: Dict[str, Dict[str, int]]
    overlay_path: Optional[str] = None
    button_range: Optional[List[int]] = None  # [min_button, max_button] for device splitting


class TemplateManager:
    """Manages device templates and matching"""

    def __init__(self, templates_dir: str):
        """
        Initialize template manager

        Args:
            templates_dir: Path to visual-templates directory
        """
        self.templates_dir = templates_dir
        self.templates: List[DeviceTemplate] = []
        self.load_templates()

    def load_templates(self):
        """Load template registry from JSON"""
        registry_path = os.path.join(self.templates_dir, "template_registry.json")

        if not os.path.exists(registry_path):
            logger.warning(f"Template registry not found at {registry_path}")
            return

        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for template_data in data.get('templates', []):
                overlay_path = None
                if 'overlay' in template_data:
                    overlay_path = os.path.join(self.templates_dir, template_data['overlay'])

                template = DeviceTemplate(
                    id=template_data['id'],
                    name=template_data['name'],
                    image_path=os.path.join(self.templates_dir, template_data['image']),
                    device_match_patterns=template_data['device_match_patterns'],
                    device_type=template_data['type'],
                    button_coordinates=template_data.get('buttons', {}),
                    overlay_path=overlay_path,
                    button_range=template_data.get('button_range')
                )
                self.templates.append(template)

            logger.info(f"Loaded {len(self.templates)} device templates")

        except Exception as e:
            logger.error(f"Error loading template registry: {e}", exc_info=True)

    def find_template(self, device_name: str) -> Optional[DeviceTemplate]:
        """
        Find a template that matches the device name

        Args:
            device_name: Device name from XML (e.g., "VKBsim Gladiator EVO R")

        Returns:
            Matching DeviceTemplate or None
        """
        if not device_name:
            return None

        device_name_lower = device_name.lower()

        # Try exact pattern matching first
        for template in self.templates:
            for pattern in template.device_match_patterns:
                if pattern.lower() in device_name_lower:
                    return template

        return None

    def get_template_by_id(self, template_id: str) -> Optional[DeviceTemplate]:
        """Get template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None

    def get_all_templates(self) -> List[DeviceTemplate]:
        """Get all available templates"""
        return self.templates.copy()
