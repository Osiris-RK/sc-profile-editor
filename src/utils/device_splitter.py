"""
Device splitter utility for handling composite devices like VKB Gladiator + SEM
"""

import re
from typing import Optional, Tuple


def is_vkb_with_sem(device_name: str) -> bool:
    """
    Check if device is a VKB device with SEM module attached

    Args:
        device_name: Device product name (e.g., "VKBsim Gladiator EVO R SEM")

    Returns:
        True if device has SEM module attached
    """
    if not device_name:
        return False

    device_name_upper = device_name.upper()
    return 'VKB' in device_name_upper and 'SEM' in device_name_upper


def get_base_stick_name(device_name: str) -> str:
    """
    Extract base stick name from a VKB device with SEM

    Args:
        device_name: Full device name (e.g., "VKBsim Gladiator EVO R SEM")

    Returns:
        Base stick name without SEM (e.g., "VKBsim Gladiator EVO R")
    """
    if not device_name:
        return device_name

    # Remove "SEM" and extra whitespace
    base_name = re.sub(r'\s*SEM\s*', '', device_name, flags=re.IGNORECASE)
    return base_name.strip()


def split_device_by_button(device_name: str, button_number: int) -> str:
    """
    Split a composite device into its component parts based on button number

    For VKB devices with SEM:
    - Buttons 1-40: Base stick (e.g., "VKBsim Gladiator EVO R")
    - Buttons 41-64: SEM module ("VKB SEM")

    Args:
        device_name: Full device name from SC profile
        button_number: Button number from input code

    Returns:
        Appropriate device name for the button
    """
    if not is_vkb_with_sem(device_name):
        return device_name

    # VKB SEM uses buttons 41-64
    if button_number >= 41:
        return "VKB SEM"
    else:
        return get_base_stick_name(device_name)


def extract_button_number(input_code: str) -> Optional[int]:
    """
    Extract button number from joystick input code

    Args:
        input_code: Input code like "js1_button42"

    Returns:
        Button number or None if not a button input
    """
    match = re.match(r'js\d+_button(\d+)', input_code)
    if match:
        return int(match.group(1))
    return None


def get_device_for_input(device_name: str, input_code: str) -> str:
    """
    Get the appropriate device name for a given input code

    Args:
        device_name: Full device name from SC profile
        input_code: Input code (e.g., "js1_button42")

    Returns:
        Appropriate device name (may be split into component)
    """
    button_num = extract_button_number(input_code)

    if button_num is not None:
        return split_device_by_button(device_name, button_num)

    # For non-button inputs (axes, hats, etc.), use base device
    if is_vkb_with_sem(device_name):
        return get_base_stick_name(device_name)

    return device_name
