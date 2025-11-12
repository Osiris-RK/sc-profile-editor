"""
XML parser for Star Citizen control profiles
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.profile_model import ControlProfile, Device, ActionMap, ActionBinding


class ProfileParser:
    """Parser for Star Citizen XML profile files"""

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = None
        self.root = None

    def parse(self) -> ControlProfile:
        """Parse the XML file and return ControlProfile object"""
        try:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML file: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file not found: {self.xml_path}")

        profile_name = self.get_profile_name()
        devices = self.get_devices()
        categories = self.get_categories()
        action_maps = self.get_action_maps()

        return ControlProfile(
            profile_name=profile_name,
            devices=devices,
            action_maps=action_maps,
            categories=categories,
            is_modified=False,
            source_xml_path=self.xml_path
        )

    def get_profile_name(self) -> str:
        """Extract profile name from XML"""
        if self.root is None:
            return "Unknown"

        # Try to get from root attribute
        profile_name = self.root.get('profileName')
        if profile_name:
            return profile_name

        # Fallback to CustomisationUIHeader label
        header = self.root.find('CustomisationUIHeader')
        if header is not None:
            label = header.get('label')
            if label:
                return label

        return "Unknown"

    def get_categories(self) -> List[str]:
        """Extract category labels from XML"""
        if self.root is None:
            return []

        categories = []
        header = self.root.find('CustomisationUIHeader')
        if header is not None:
            categories_elem = header.find('categories')
            if categories_elem is not None:
                for category in categories_elem.findall('category'):
                    label = category.get('label', '')
                    if label:
                        categories.append(label)

        return categories

    def get_devices(self) -> List[Device]:
        """Extract device information from XML"""
        if self.root is None:
            return []

        devices = []

        # Get device declarations from CustomisationUIHeader
        header = self.root.find('CustomisationUIHeader')
        if header is not None:
            devices_elem = header.find('devices')
            if devices_elem is not None:
                for device_elem in devices_elem:
                    device_type = device_elem.tag  # keyboard, mouse, joystick
                    instance = int(device_elem.get('instance', 1))

                    # Try to find product info from options elements
                    product_id = None
                    product_name = None

                    for options in self.root.findall('options'):
                        if (options.get('type') == device_type and
                            int(options.get('instance', 1)) == instance):
                            product = options.get('Product', '')
                            if product:
                                product_id = product
                                # Extract readable name from product string
                                # Format: " VKBsim Gladiator EVO R    {GUID}"
                                if '{' in product:
                                    product_name = product.split('{')[0].strip()
                                else:
                                    product_name = product.strip()
                            break

                    devices.append(Device(
                        device_type=device_type,
                        instance=instance,
                        product_id=product_id,
                        product_name=product_name
                    ))

        return devices

    def get_action_maps(self) -> List[ActionMap]:
        """Extract all action maps and their bindings"""
        if self.root is None:
            return []

        action_maps = []

        for actionmap_elem in self.root.findall('actionmap'):
            map_name = actionmap_elem.get('name', 'unknown')
            actions = []

            for action_elem in actionmap_elem.findall('action'):
                action_name = action_elem.get('name', 'unknown')

                # Find all rebind elements (actions can have multiple bindings)
                for rebind_elem in action_elem.findall('rebind'):
                    input_code = rebind_elem.get('input', '')
                    activation_mode = rebind_elem.get('activationMode')

                    # Only add if there's an actual input binding (not empty)
                    if input_code and input_code.strip():
                        actions.append(ActionBinding(
                            action_name=action_name,
                            input_code=input_code,
                            activation_mode=activation_mode
                        ))

            # Only add action map if it has bindings
            if actions:
                action_maps.append(ActionMap(
                    name=map_name,
                    actions=actions
                ))

        return action_maps
