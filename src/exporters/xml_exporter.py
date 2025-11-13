"""
XML exporter for saving modified Star Citizen control profiles
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import os
import logging
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.profile_model import ControlProfile, ActionBinding

logger = logging.getLogger(__name__)


class XMLExporter:
    """Export modified control profiles to Star Citizen XML format"""

    def __init__(self, original_xml_path: str):
        """
        Initialize exporter with original XML path

        Args:
            original_xml_path: Path to the original XML file (to preserve structure)
        """
        self.original_xml_path = original_xml_path
        self.tree = None
        self.root = None

    def export(self, profile: ControlProfile, output_path: str) -> bool:
        """
        Export modified profile to XML file

        Args:
            profile: Modified ControlProfile object
            output_path: Path where to save the modified XML

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load original XML to preserve structure
            self.tree = ET.parse(self.original_xml_path)
            self.root = self.tree.getroot()

            # Update profile name if changed
            if profile.profile_name:
                self.root.set('profileName', profile.profile_name)

                # Also update in CustomisationUIHeader
                header = self.root.find('CustomisationUIHeader')
                if header is not None:
                    header.set('label', profile.profile_name)

            # Update all rebind elements with modified bindings
            self.update_bindings(profile)

            # Write to output file with proper formatting
            self.write_formatted_xml(output_path)

            logger.info(f"Successfully exported profile to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export profile: {e}", exc_info=True)
            return False

    def update_bindings(self, profile: ControlProfile):
        """Update all rebind elements in the XML tree"""

        # Create a lookup map for quick access to modified bindings
        # Key: (action_map_name, action_name) -> ActionBinding
        binding_map = {}

        for action_map in profile.action_maps:
            for binding in action_map.actions:
                key = (action_map.name, binding.action_name)
                # Store all bindings with this key (support for multiple bindings per action)
                if key not in binding_map:
                    binding_map[key] = []
                binding_map[key].append(binding)

        # Iterate through XML and update matching bindings
        for actionmap_elem in self.root.findall('actionmap'):
            map_name = actionmap_elem.get('name', '')

            for action_elem in actionmap_elem.findall('action'):
                action_name = action_elem.get('name', '')

                # Check if we have modified bindings for this action
                key = (map_name, action_name)
                if key not in binding_map:
                    continue

                modified_bindings = binding_map[key]

                # Clear existing rebind elements
                for rebind_elem in list(action_elem.findall('rebind')):
                    action_elem.remove(rebind_elem)

                # Add updated rebind elements
                for binding in modified_bindings:
                    rebind_elem = ET.SubElement(action_elem, 'rebind')
                    rebind_elem.set('input', binding.input_code)

                    # Add activation mode if specified
                    if binding.activation_mode:
                        rebind_elem.set('activationMode', binding.activation_mode)

                logger.debug(f"Updated binding: {map_name}.{action_name} -> {[b.input_code for b in modified_bindings]}")

    def write_formatted_xml(self, output_path: str):
        """Write XML with proper formatting and indentation"""

        # Convert ElementTree to string
        xml_string = ET.tostring(self.root, encoding='unicode')

        # Pretty print with minidom
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent=' ', encoding='utf-8')

        # Remove extra blank lines that minidom adds
        lines = pretty_xml.decode('utf-8').split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(non_empty_lines))

    @staticmethod
    def create_new_profile(profile: ControlProfile, output_path: str,
                          version: str = "1", options_version: str = "2",
                          rebind_version: str = "2") -> bool:
        """
        Create a new XML profile from scratch (not from an existing file)

        Args:
            profile: ControlProfile object
            output_path: Path where to save the XML
            version: ActionMaps version
            options_version: Options version
            rebind_version: Rebind version

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create root element
            root = ET.Element('ActionMaps')
            root.set('version', version)
            root.set('optionsVersion', options_version)
            root.set('rebindVersion', rebind_version)
            root.set('profileName', profile.profile_name)

            # Create CustomisationUIHeader
            header = ET.SubElement(root, 'CustomisationUIHeader')
            header.set('label', profile.profile_name)
            header.set('description', '')
            header.set('image', '')

            # Add devices
            devices_elem = ET.SubElement(header, 'devices')
            for device in profile.devices:
                device_elem = ET.SubElement(devices_elem, device.device_type)
                device_elem.set('instance', str(device.instance))

            # Add categories
            if profile.categories:
                categories_elem = ET.SubElement(header, 'categories')
                for category in profile.categories:
                    category_elem = ET.SubElement(categories_elem, 'category')
                    category_elem.set('label', category)

            # Add device options
            for device in profile.devices:
                if device.product_id:
                    options_elem = ET.SubElement(root, 'options')
                    options_elem.set('type', device.device_type)
                    options_elem.set('instance', str(device.instance))
                    options_elem.set('Product', device.product_id)

            # Add modifiers (empty for now)
            ET.SubElement(root, 'modifiers')

            # Add action maps and bindings
            for action_map in profile.action_maps:
                actionmap_elem = ET.SubElement(root, 'actionmap')
                actionmap_elem.set('name', action_map.name)

                # Group bindings by action name
                from collections import defaultdict
                actions_dict = defaultdict(list)

                for binding in action_map.actions:
                    actions_dict[binding.action_name].append(binding)

                # Create action elements
                for action_name, bindings in actions_dict.items():
                    action_elem = ET.SubElement(actionmap_elem, 'action')
                    action_elem.set('name', action_name)

                    # Add rebind elements
                    for binding in bindings:
                        rebind_elem = ET.SubElement(action_elem, 'rebind')
                        rebind_elem.set('input', binding.input_code)

                        if binding.activation_mode:
                            rebind_elem.set('activationMode', binding.activation_mode)

            # Write formatted XML
            xml_string = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_string)
            pretty_xml = dom.toprettyxml(indent=' ', encoding='utf-8')

            # Remove extra blank lines
            lines = pretty_xml.decode('utf-8').split('\n')
            non_empty_lines = [line for line in lines if line.strip()]

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(non_empty_lines))

            logger.info(f"Successfully created new profile: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create new profile: {e}", exc_info=True)
            return False


def export_profile(profile: ControlProfile, original_xml_path: str,
                  output_path: str) -> bool:
    """
    Convenience function to export a modified profile

    Args:
        profile: Modified ControlProfile object
        original_xml_path: Path to original XML (for structure preservation)
        output_path: Path where to save the modified XML

    Returns:
        True if successful, False otherwise
    """
    exporter = XMLExporter(original_xml_path)
    return exporter.export(profile, output_path)
