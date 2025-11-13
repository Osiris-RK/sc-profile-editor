"""
Input detection module for capturing joystick, keyboard, and mouse inputs

This module uses pygame to detect and identify controller inputs for button remapping.
"""

import logging
import pygame
from typing import Optional, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

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
        self.pygame_initialized = False

    def run(self):
        """Run the input detection loop"""
        try:
            # Initialize pygame if not already done
            if not self.pygame_initialized:
                pygame.init()
                pygame.joystick.init()
                self.pygame_initialized = True

            # Initialize all connected joysticks
            joysticks = []
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks.append(joystick)
                logger.info(f"Initialized joystick {i}: {joystick.get_name()}")

            if len(joysticks) == 0:
                logger.warning("No joysticks detected")

            self.running = True
            clock = pygame.time.Clock()
            elapsed_time = 0

            # Detection loop
            while self.running and elapsed_time < self.timeout_ms:
                # Process pygame events
                for event in pygame.event.get():
                    input_code, description = self._process_event(event)
                    if input_code:
                        logger.info(f"Detected input: {input_code} - {description}")
                        self.input_detected.emit(input_code, description)
                        self.running = False
                        return

                # Check for significant axis movements (not event-based)
                for js_idx, joystick in enumerate(joysticks):
                    input_code, description = self._check_axes(joystick, js_idx + 1)
                    if input_code:
                        logger.info(f"Detected axis: {input_code} - {description}")
                        self.input_detected.emit(input_code, description)
                        self.running = False
                        return

                # Wait and update elapsed time
                clock.tick(30)  # 30 FPS
                elapsed_time += 1000 / 30

            # Timeout or cancelled
            if self.running:
                logger.info("Input detection timed out")
                self.detection_cancelled.emit()

        except Exception as e:
            logger.error(f"Error in input detection: {e}", exc_info=True)
            self.detection_cancelled.emit()

        finally:
            self.running = False

    def _process_event(self, event) -> Tuple[Optional[str], Optional[str]]:
        """Process a pygame event and return input code if detected"""

        # Joystick button press
        if event.type == pygame.JOYBUTTONDOWN:
            js_num = event.joy + 1
            button_num = event.button + 1
            input_code = f"js{js_num}_button{button_num}"
            description = f"Joystick {js_num} Button {button_num}"
            return input_code, description

        # Joystick hat movement
        elif event.type == pygame.JOYHATMOTION:
            js_num = event.joy + 1
            hat_num = event.hat + 1
            hat_value = event.value

            # Determine direction
            direction = None
            if hat_value[1] == 1:
                direction = "up"
            elif hat_value[1] == -1:
                direction = "down"
            elif hat_value[0] == -1:
                direction = "left"
            elif hat_value[0] == 1:
                direction = "right"

            if direction:
                input_code = f"js{js_num}_hat{hat_num}_{direction}"
                description = f"Joystick {js_num} Hat {hat_num} {direction.upper()}"
                return input_code, description

        # Keyboard key press
        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            # Map pygame key names to Star Citizen format
            input_code = f"kb1_{key_name}"
            description = f"Keyboard {key_name.upper()}"
            return input_code, description

        # Mouse button press
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            if button <= 3:  # Left, middle, right
                input_code = f"mouse{button}"
                button_names = {1: "Left", 2: "Middle", 3: "Right"}
                description = f"Mouse {button_names.get(button, button)}"
                return input_code, description
            elif button == 4:
                input_code = "mwheel_up"
                description = "Mouse Wheel Up"
                return input_code, description
            elif button == 5:
                input_code = "mwheel_down"
                description = "Mouse Wheel Down"
                return input_code, description

        return None, None

    def _check_axes(self, joystick, js_num: int, threshold: float = 0.5) -> Tuple[Optional[str], Optional[str]]:
        """Check for significant axis movements"""
        num_axes = joystick.get_numaxes()

        # Common axis mappings (Star Citizen format)
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

        for axis_idx in range(num_axes):
            value = joystick.get_axis(axis_idx)

            # Check if axis moved significantly
            if abs(value) > threshold:
                axis_name = axis_names.get(axis_idx, f"axis{axis_idx}")
                input_code = f"js{js_num}_{axis_name}"
                direction = "+" if value > 0 else "-"
                description = f"Joystick {js_num} {axis_name.upper()} ({direction})"
                return input_code, description

        return None, None

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
            pygame.init()
            pygame.joystick.init()

            # Add keyboard and mouse (always available)
            devices.append({"type": "keyboard", "instance": 1, "name": "Keyboard"})
            devices.append({"type": "mouse", "instance": 1, "name": "Mouse"})

            # Add joysticks
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                devices.append({
                    "type": "joystick",
                    "instance": i + 1,
                    "name": joystick.get_name()
                })

        except Exception as e:
            logger.error(f"Error getting devices: {e}", exc_info=True)

        return devices
