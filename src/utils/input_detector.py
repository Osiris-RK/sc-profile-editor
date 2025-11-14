"""
Input detection module for capturing joystick, keyboard, and mouse inputs

This module uses python-dinput for joystick/gamepad detection and pynput
for keyboard and mouse input detection.
"""

import logging
from typing import Optional, Tuple, Dict
from PyQt6.QtCore import QThread, pyqtSignal
import threading
import time

logger = logging.getLogger(__name__)


class InputDetectorThread(QThread):
    """Thread-safe input detector that listens for controller inputs"""

    # Signal emitted when input is detected: (input_code, input_description)
    input_detected = pyqtSignal(str, str)

    # Signal emitted when detection times out or is cancelled
    detection_cancelled = pyqtSignal()

    def __init__(self, timeout_ms: int = 10000):
        super().__init__()
        self.timeout_ms = timeout_ms
        self.running = False
        self.joystick_state: Dict[int, Dict] = {}  # Track joystick axis state for threshold detection

    def run(self):
        """Run the input detection loop"""
        try:
            self.running = True
            start_time = time.time()
            elapsed_ms = 0
            last_detected_joystick = None
            last_detected_keyboard_listener = None
            last_detected_mouse_listener = None

            # Start joystick detection thread
            joystick_detected = threading.Event()
            joystick_result = {"code": None, "description": None}

            joystick_thread = threading.Thread(
                target=self._detect_joystick,
                args=(joystick_detected, joystick_result),
                daemon=True
            )
            joystick_thread.start()

            # Start keyboard detection listener
            keyboard_detected = threading.Event()
            keyboard_result = {"code": None, "description": None}

            try:
                from pynput import keyboard
                keyboard_listener = keyboard.Listener(
                    on_press=lambda key: self._on_keyboard_press(key, keyboard_detected, keyboard_result)
                )
                keyboard_listener.start()
            except Exception as e:
                logger.warning(f"Could not start keyboard listener: {e}")
                keyboard_listener = None

            # Start mouse detection listener
            mouse_detected = threading.Event()
            mouse_result = {"code": None, "description": None}

            try:
                from pynput import mouse
                mouse_listener = mouse.Listener(
                    on_click=lambda x, y, button, pressed: self._on_mouse_click(button, pressed, mouse_detected, mouse_result)
                )
                mouse_listener.start()
            except Exception as e:
                logger.warning(f"Could not start mouse listener: {e}")
                mouse_listener = None

            # Detection loop
            while self.running and elapsed_ms < self.timeout_ms:
                # Check for joystick input
                if joystick_detected.is_set():
                    if joystick_result["code"]:
                        logger.info(f"Detected joystick input: {joystick_result['code']} - {joystick_result['description']}")
                        self.input_detected.emit(joystick_result["code"], joystick_result["description"])
                        self.running = False
                        break

                # Check for keyboard input
                if keyboard_detected.is_set():
                    if keyboard_result["code"]:
                        logger.info(f"Detected keyboard input: {keyboard_result['code']} - {keyboard_result['description']}")
                        self.input_detected.emit(keyboard_result["code"], keyboard_result["description"])
                        self.running = False
                        break

                # Check for mouse input
                if mouse_detected.is_set():
                    if mouse_result["code"]:
                        logger.info(f"Detected mouse input: {mouse_result['code']} - {mouse_result['description']}")
                        self.input_detected.emit(mouse_result["code"], mouse_result["description"])
                        self.running = False
                        break

                # Update elapsed time and sleep
                time.sleep(0.05)  # 50ms polling interval
                elapsed_ms = (time.time() - start_time) * 1000

            # Clean up listeners
            if keyboard_listener:
                try:
                    keyboard_listener.stop()
                except:
                    pass

            if mouse_listener:
                try:
                    mouse_listener.stop()
                except:
                    pass

            # Timeout
            if self.running:
                logger.info("Input detection timed out")
                self.detection_cancelled.emit()

        except Exception as e:
            logger.error(f"Error in input detection: {e}", exc_info=True)
            self.detection_cancelled.emit()

        finally:
            self.running = False

    def _detect_joystick(self, detected_event, result_dict):
        """Detect joystick input in a separate thread"""
        try:
            import dinput

            # Get list of devices
            devices = dinput.get_joysticks()

            if not devices:
                logger.warning("No joysticks detected")
                return

            logger.info(f"Found {len(devices)} joystick(s)")

            # Create joystick objects
            joysticks = []
            for i, device_guid in enumerate(devices):
                try:
                    joystick = dinput.Joystick(device_guid)
                    joystick.open()
                    joysticks.append((i + 1, joystick))  # 1-indexed for SC
                    logger.info(f"Initialized joystick {i + 1}")
                except Exception as e:
                    logger.warning(f"Could not initialize joystick {i}: {e}")

            if not joysticks:
                return

            # Joystick detection loop
            start_time = time.time()
            axis_state = {}  # Track previous axis values to detect significant changes

            while self.running and (time.time() - start_time) * 1000 < self.timeout_ms:
                try:
                    for js_num, joystick in joysticks:
                        try:
                            # Update state
                            joystick.update()
                            state = joystick.state

                            # Check buttons
                            if hasattr(state, 'buttons') and state.buttons:
                                for button_idx, button_pressed in enumerate(state.buttons):
                                    if button_pressed:
                                        input_code = f"js{js_num}_button{button_idx + 1}"
                                        result_dict["code"] = input_code
                                        result_dict["description"] = f"Joystick {js_num} Button {button_idx + 1}"
                                        detected_event.set()
                                        return

                            # Check POV/hat switches
                            if hasattr(state, 'pov') and state.pov is not None and state.pov >= 0:
                                # POV is in degrees: 0=up, 9000=right, 18000=down, 27000=left
                                # -1 or 65535 means not pressed
                                if state.pov < 36000:  # Valid POV value
                                    if state.pov == 0:
                                        direction = "up"
                                    elif state.pov == 9000:
                                        direction = "right"
                                    elif state.pov == 18000:
                                        direction = "down"
                                    elif state.pov == 27000:
                                        direction = "left"
                                    else:
                                        # Diagonal - use closest direction
                                        if state.pov < 4500:
                                            direction = "up"
                                        elif state.pov < 13500:
                                            direction = "right"
                                        elif state.pov < 22500:
                                            direction = "down"
                                        else:
                                            direction = "left"

                                    input_code = f"js{js_num}_hat1_{direction}"
                                    result_dict["code"] = input_code
                                    result_dict["description"] = f"Joystick {js_num} Hat 1 {direction.upper()}"
                                    detected_event.set()
                                    return

                            # Check axes (with threshold for analog sticks)
                            axis_names = {
                                0: "x",       # X axis (left stick horizontal)
                                1: "y",       # Y axis (left stick vertical)
                                2: "z",       # Z axis (right stick horizontal, or throttle)
                                3: "rotz",    # Rotation Z (right stick vertical)
                                4: "rotx",    # Rotation X (twist)
                                5: "roty",    # Rotation Y
                                6: "slider1", # Slider 1
                                7: "slider2", # Slider 2
                            }

                            if hasattr(state, 'lX'):
                                axes = [
                                    state.lX if hasattr(state, 'lX') else 0,
                                    state.lY if hasattr(state, 'lY') else 0,
                                    state.lZ if hasattr(state, 'lZ') else 0,
                                    state.lRz if hasattr(state, 'lRz') else 0,
                                    state.lRx if hasattr(state, 'lRx') else 0,
                                    state.lRy if hasattr(state, 'lRy') else 0,
                                ]

                                # Normalize axes from -32768 to 32767 to -1.0 to 1.0
                                threshold = 0.5
                                for axis_idx, raw_value in enumerate(axes):
                                    # Normalize
                                    if raw_value > 0:
                                        normalized_value = raw_value / 32767.0
                                    else:
                                        normalized_value = raw_value / 32768.0

                                    # Check if significant movement
                                    if abs(normalized_value) > threshold:
                                        axis_name = axis_names.get(axis_idx, f"axis{axis_idx}")
                                        direction = "+" if normalized_value > 0 else "-"
                                        input_code = f"js{js_num}_{axis_name}"
                                        result_dict["code"] = input_code
                                        result_dict["description"] = f"Joystick {js_num} {axis_name.upper()} ({direction})"
                                        detected_event.set()
                                        return

                        except Exception as e:
                            logger.debug(f"Error checking joystick {js_num}: {e}")
                            continue

                    time.sleep(0.05)  # 50ms polling interval

                except Exception as e:
                    logger.debug(f"Error in joystick detection loop: {e}")
                    time.sleep(0.05)

        except ImportError:
            logger.error("python-dinput not installed. Joystick detection unavailable.")
        except Exception as e:
            logger.error(f"Error in joystick detection: {e}", exc_info=True)

    def _on_keyboard_press(self, key, detected_event, result_dict):
        """Handle keyboard key press (callback from pynput)"""
        try:
            from pynput.keyboard import Key

            if not self.running:
                return False  # Stop listener

            # Get key name
            try:
                if isinstance(key, Key):
                    # Special keys
                    key_name = key.name
                else:
                    # Regular character keys
                    key_name = key.char if hasattr(key, 'char') else str(key)
            except AttributeError:
                key_name = str(key)

            # Map to Star Citizen format
            input_code = f"kb1_{key_name}"
            result_dict["code"] = input_code
            result_dict["description"] = f"Keyboard {key_name.upper()}"
            detected_event.set()
            return False  # Stop listener

        except Exception as e:
            logger.debug(f"Error handling keyboard press: {e}")
            return True  # Continue listening

    def _on_mouse_click(self, button, pressed, detected_event, result_dict):
        """Handle mouse button click (callback from pynput)"""
        try:
            from pynput.mouse import Button

            if not self.running or not pressed:
                return True  # Continue listening

            # Get button name
            button_names = {
                Button.left: ("mouse1", "Mouse Left"),
                Button.middle: ("mouse2", "Mouse Middle"),
                Button.right: ("mouse3", "Mouse Right"),
            }

            if button in button_names:
                input_code, description = button_names[button]
                result_dict["code"] = input_code
                result_dict["description"] = description
                detected_event.set()
                return False  # Stop listener

            return True  # Continue listening

        except Exception as e:
            logger.debug(f"Error handling mouse click: {e}")
            return True  # Continue listening

    def stop(self):
        """Stop the detection loop"""
        self.running = False


class InputDetector:
    """Main input detector class - wrapper around the thread"""

    def __init__(self):
        self.thread = None

    def start_detection(self, timeout_ms: int = 10000) -> InputDetectorThread:
        """
        Start listening for input

        Args:
            timeout_ms: How long to wait for input before timing out

        Returns:
            InputDetectorThread object with signals to connect to
        """
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()

        self.thread = InputDetectorThread(timeout_ms)
        self.thread.start()
        return self.thread

    def stop_detection(self):
        """Stop listening for input"""
        if self.thread:
            self.thread.stop()
            self.thread.wait()

    @staticmethod
    def get_available_devices() -> list:
        """Get list of available input devices"""
        devices = []

        try:
            # Keyboard and mouse are always available
            devices.append({"type": "keyboard", "instance": 1, "name": "Keyboard"})
            devices.append({"type": "mouse", "instance": 1, "name": "Mouse"})

            # Add joysticks
            try:
                import dinput
                joystick_guids = dinput.get_joysticks()

                for i, guid in enumerate(joystick_guids):
                    try:
                        joystick = dinput.Joystick(guid)
                        joystick.open()
                        devices.append({
                            "type": "joystick",
                            "instance": i + 1,
                            "name": f"Joystick {i + 1}"
                        })
                        joystick.close()
                    except Exception as e:
                        logger.debug(f"Could not open joystick {i}: {e}")
                        devices.append({
                            "type": "joystick",
                            "instance": i + 1,
                            "name": f"Joystick {i + 1} (unavailable)"
                        })

            except ImportError:
                logger.warning("python-dinput not available, joystick detection skipped")
            except Exception as e:
                logger.error(f"Error detecting joysticks: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error getting devices: {e}", exc_info=True)

        return devices
