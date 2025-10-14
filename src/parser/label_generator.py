"""
Label generator for converting action names to human-readable strings
"""

import re
from typing import Dict


class LabelGenerator:
    """Generates human-readable labels for actions and inputs"""

    # Keyboard key mappings
    KEYBOARD_KEYS = {
        # Arrow keys
        "up": "Up Arrow", "down": "Down Arrow", "left": "Left Arrow", "right": "Right Arrow",
        # Function keys
        "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4", "f5": "F5", "f6": "F6",
        "f7": "F7", "f8": "F8", "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
        # Number keys
        "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "0": "0",
        # Special keys
        "escape": "Escape", "esc": "Escape", "tab": "Tab", "capslock": "Caps Lock",
        "lshift": "Left Shift", "rshift": "Right Shift", "lctrl": "Left Ctrl", "rctrl": "Right Ctrl",
        "lalt": "Left Alt", "ralt": "Right Alt", "space": "Space", "enter": "Enter", "return": "Enter",
        "backspace": "Backspace", "delete": "Delete", "insert": "Insert",
        "home": "Home", "end": "End", "pageup": "Page Up", "pagedown": "Page Down",
        "np_0": "Numpad 0", "np_1": "Numpad 1", "np_2": "Numpad 2", "np_3": "Numpad 3",
        "np_4": "Numpad 4", "np_5": "Numpad 5", "np_6": "Numpad 6", "np_7": "Numpad 7",
        "np_8": "Numpad 8", "np_9": "Numpad 9",
        "np_multiply": "Numpad *", "np_add": "Numpad +", "np_subtract": "Numpad -",
        "np_divide": "Numpad /", "np_period": "Numpad .",
        # Punctuation
        "minus": "-", "equals": "=", "lbracket": "[", "rbracket": "]",
        "semicolon": ";", "apostrophe": "'", "grave": "`", "backslash": "\\",
        "comma": ",", "period": ".", "slash": "/",
        # Mouse buttons
        "mouse1": "Left Click", "mouse2": "Right Click", "mouse3": "Middle Click",
        "mouse4": "Mouse Button 4", "mouse5": "Mouse Button 5",
        "mwheel_up": "Mouse Wheel Up", "mwheel_down": "Mouse Wheel Down",
    }

    @staticmethod
    def generate_action_label(action_name: str) -> str:
        """Convert action name to human-readable label"""
        # Check for common prefixes
        prefixes = {
            'v_': '',  # vehicle
            'pc_': '',  # player choice
            'foip_': 'FOIP: ',  # face over IP
            'turret_': 'Turret: ',
        }

        label = action_name
        prefix_text = ''

        for prefix, display in prefixes.items():
            if action_name.startswith(prefix):
                label = action_name[len(prefix):]
                prefix_text = display
                break

        # Split by underscore and capitalize each word
        words = label.split('_')
        words = [word.capitalize() for word in words]
        readable = ' '.join(words)

        return prefix_text + readable

    @staticmethod
    def generate_input_label(input_code: str) -> str:
        """Convert input code to human-readable label"""
        if not input_code or not input_code.strip():
            return "Unbound"

        input_code = input_code.strip()

        # Parse input code format: device_input
        # Examples: kb1_down, js1_button5, js2_hat1_up

        # Keyboard input: kb1_key
        if input_code.startswith('kb'):
            match = re.match(r'kb(\d+)_(.+)', input_code)
            if match:
                instance = match.group(1)
                key = match.group(2).lower()

                # Look up key in mapping
                key_label = LabelGenerator.KEYBOARD_KEYS.get(key)
                if key_label:
                    return f"Keyboard: {key_label}"
                else:
                    # Fallback: capitalize the key
                    return f"Keyboard: {key.upper()}"

        # Joystick button: js1_button5
        elif input_code.startswith('js') and 'button' in input_code:
            match = re.match(r'js(\d+)_button(\d+)', input_code)
            if match:
                instance = match.group(1)
                button = match.group(2)
                return f"Joystick {instance}: Button {button}"

        # Joystick POV hat: js1_hat1_up
        elif input_code.startswith('js') and 'hat' in input_code:
            match = re.match(r'js(\d+)_hat(\d+)_(\w+)', input_code)
            if match:
                instance = match.group(1)
                hat = match.group(2)
                direction = match.group(3).capitalize()
                return f"Joystick {instance}: Hat {hat} {direction}"

        # Joystick axis: js1_x, js1_y, js1_rotz
        elif input_code.startswith('js') and any(axis in input_code for axis in ['_x', '_y', '_z', '_rotx', '_roty', '_rotz']):
            match = re.match(r'js(\d+)_(.+)', input_code)
            if match:
                instance = match.group(1)
                axis = match.group(2).upper()
                return f"Joystick {instance}: Axis {axis}"

        # Joystick slider: js1_slider1
        elif input_code.startswith('js') and 'slider' in input_code:
            match = re.match(r'js(\d+)_slider(\d+)', input_code)
            if match:
                instance = match.group(1)
                slider = match.group(2)
                return f"Joystick {instance}: Slider {slider}"

        # Generic joystick input
        elif input_code.startswith('js'):
            match = re.match(r'js(\d+)_(.+)', input_code)
            if match:
                instance = match.group(1)
                control = match.group(2)
                return f"Joystick {instance}: {control.capitalize()}"

        # Mouse input
        elif input_code.startswith('mouse'):
            key = input_code.lower()
            mouse_label = LabelGenerator.KEYBOARD_KEYS.get(key)
            if mouse_label:
                return f"Mouse: {mouse_label}"
            return f"Mouse: {input_code}"

        # Fallback for unknown formats
        return input_code

    @staticmethod
    def generate_actionmap_label(actionmap_name: str) -> str:
        """Convert action map name to human-readable label"""
        # Split by underscore and capitalize
        words = actionmap_name.split('_')
        words = [word.capitalize() for word in words]
        return ' '.join(words)
