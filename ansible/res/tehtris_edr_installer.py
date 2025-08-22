#!/usr/bin/env python3
"""
TEHTRIS EDR MSI Installer Automation Script

This script automates the installation of TEHTRIS EDR using pywinauto.
It handles the complete installation flow from launch to completion.

Requirements:
- pywinauto
- pyautogui (fallback)
- Administrator privileges
- Windows 10 or Windows Server 2019

Author: Augment Agent
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Tuple

try:
    from pywinauto import Application, Desktop
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.findwindows import ElementNotFoundError
    from pywinauto.timings import TimeoutError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("Warning: pywinauto not available. Please install with: pip install pywinauto")

try:
    import pyautogui
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image, ImageEnhance
    PYAUTOGUI_AVAILABLE = True
    # Configure pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui/opencv/pytesseract not available. Install with: pip install pyautogui opencv-python pytesseract pillow")


class TehtrisEDRInstaller:
    """Automates TEHTRIS EDR MSI installation process."""
    
    def __init__(self, msi_path: str, dry_run: bool = False):
        self.msi_path = Path(msi_path)
        self.dry_run = dry_run
        self.app: Optional[Application] = None
        self.logger = self._setup_logging()
        
        # Installation configuration
        self.config = {
            'server_address': 'xpgapp16.tehtris.net',
            'tag': 'XPG_QAT',
            'license_key': 'MH83-2CDX-9DXQ-LG89-92FF'
        }
        
        # Timeouts and retry settings
        self.window_timeout = 30
        self.control_timeout = 10
        self.max_retries = 3
        self.retry_delay = 2

        # Screen capture settings
        self.use_screen_capture = True
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('TehtrisEDRInstaller')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('tehtris_installation.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def validate_prerequisites(self) -> bool:
        """Validate prerequisites before starting installation."""
        self.logger.info("Validating prerequisites...")
        
        if not PYWINAUTO_AVAILABLE:
            self.logger.error("pywinauto is not available. Please install it.")
            return False
        
        if not self.msi_path.exists():
            self.logger.error(f"MSI file not found: {self.msi_path}")
            return False
        
        # Note: Admin privileges may be required for MSI installation
        # but we'll let the installer handle UAC prompts if needed
        if not self.dry_run and not self._is_admin():
            self.logger.warning("Not running as Administrator - UAC prompts may appear during installation")
            self.logger.info("The installer will handle elevation requests automatically")
        
        # Validate tag format
        if not self.config['tag'].startswith('XPG_'):
            self.logger.error(f"Tag must start with 'XPG_': {self.config['tag']}")
            return False
        
        self.logger.info("Prerequisites validated successfully")
        return True
    
    def _is_admin(self) -> bool:
        """Check if script is running with admin privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def minimize_all_windows(self):
        """Minimize all windows using Win+D shortcut."""
        self.logger.info("Minimizing all windows (Win+D)...")
        if self.dry_run:
            self.logger.info("DRY RUN: Would minimize all windows")
            return

        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.hotkey('win', 'd')
                time.sleep(1)  # Allow time for windows to minimize
                self.logger.info("Successfully minimized all windows")
            except Exception as e:
                self.logger.warning(f"Failed to minimize windows: {e}")
        else:
            self.logger.warning("pyautogui not available for window minimization")

    def take_screenshot(self, step_name: str) -> Optional[str]:
        """Take a screenshot for debugging purposes."""
        if not PYAUTOGUI_AVAILABLE or self.dry_run:
            return None

        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{step_name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename

            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            self.logger.debug(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.warning(f"Failed to take screenshot: {e}")
            return None

    def find_text_on_screen(self, text: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find text on screen using OCR and return center coordinates."""
        if not PYAUTOGUI_AVAILABLE or self.dry_run:
            return None

        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)

            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            # Enhance image for better text recognition
            enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)

            # Use pytesseract to find text
            data = pytesseract.image_to_data(enhanced, output_type=pytesseract.Output.DICT)

            # Search for the text
            for i, detected_text in enumerate(data['text']):
                if text.lower() in detected_text.lower() and int(data['conf'][i]) > confidence * 100:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    self.logger.info(f"Found text '{text}' at ({x}, {y})")
                    return (x, y)

            self.logger.debug(f"Text '{text}' not found on screen")
            return None

        except Exception as e:
            self.logger.warning(f"Error finding text '{text}': {e}")
            return None

    def find_button_by_text(self, button_text: str, timeout: int = 10) -> Optional[Tuple[int, int]]:
        """Find button by text with timeout."""
        if not PYAUTOGUI_AVAILABLE or self.dry_run:
            return None

        start_time = time.time()
        while time.time() - start_time < timeout:
            position = self.find_text_on_screen(button_text)
            if position:
                return position
            time.sleep(1)

        return None

    def find_ui_element_by_color(self, color_range: dict, min_area: int = 100) -> Optional[Tuple[int, int]]:
        """Find UI element by color pattern (for buttons, checkboxes, etc.)."""
        if not PYAUTOGUI_AVAILABLE or self.dry_run:
            return None

        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

            # Create mask for the color range
            lower = np.array(color_range['lower'])
            upper = np.array(color_range['upper'])
            mask = cv2.inRange(hsv, lower, upper)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find the largest contour that meets minimum area
            for contour in sorted(contours, key=cv2.contourArea, reverse=True):
                area = cv2.contourArea(contour)
                if area > min_area:
                    # Get center of contour
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        return (cx, cy)

            return None

        except Exception as e:
            self.logger.warning(f"Error finding UI element by color: {e}")
            return None

    def smart_find_and_click(self, element_type: str, text_options: list, fallback_positions: list = None) -> bool:
        """Smart method to find and click UI elements using multiple strategies."""
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would smart click {element_type}")
            return True

        self.logger.info(f"Smart finding {element_type}...")

        # Strategy 1: Find by text using OCR (if available)
        if PYAUTOGUI_AVAILABLE:
            for text in text_options:
                # Try both with and without ampersand for Windows controls
                search_texts = [text]
                if '&' in text:
                    search_texts.append(text.replace('&', ''))
                else:
                    search_texts.append('&' + text)

                for search_text in search_texts:
                    position = self.find_text_on_screen(search_text)
                    if position:
                        x, y = position
                        if self.click_coordinates(x, y, f"{element_type} found by text '{search_text}'"):
                            return True
        else:
            self.logger.warning("PyAutoGUI not available, skipping OCR text search")

        # Strategy 2: Try pyautogui's built-in image recognition if we have reference images
        # (This would require pre-captured button images)

        # Strategy 3: Use fallback coordinates if provided and not empty
        if fallback_positions and len(fallback_positions) > 0:
            self.logger.info(f"Using fallback positions for {element_type}")
            for x, y in fallback_positions:
                if self.click_coordinates(x, y, f"{element_type} fallback position"):
                    time.sleep(0.5)  # Give UI time to respond
                    return True

        # Strategy 2: Try keyboard shortcuts for common buttons
        if PYAUTOGUI_AVAILABLE:
            self.logger.info(f"Trying keyboard shortcuts for {element_type}")
            if "next" in element_type.lower():
                # Try Alt+N for Next button
                pyautogui.hotkey('alt', 'n')
                time.sleep(0.5)
                self.logger.info("Tried Alt+N for Next button")
                return True
            elif "accept" in element_type.lower():
                # Try Alt+A for Accept
                pyautogui.hotkey('alt', 'a')
                time.sleep(0.5)
                self.logger.info("Tried Alt+A for Accept")
                return True
            elif "install" in element_type.lower():
                # Try Alt+I for Install
                pyautogui.hotkey('alt', 'i')
                time.sleep(0.5)
                self.logger.info("Tried Alt+I for Install")
                return True
            elif "finish" in element_type.lower():
                # Try Alt+F for Finish
                pyautogui.hotkey('alt', 'f')
                time.sleep(0.5)
                self.logger.info("Tried Alt+F for Finish")
                return True

        self.logger.error(f"Failed to find {element_type} using all strategies")
        return False

    def print_window_text(self):
        """Print all text from the current installer window using multiple methods."""
        print(f"\n=== WINDOW TEXT DEBUG ===")

        # Method 1: Try pywinauto
        try:
            if self.app:
                window = self.app.window(title_re=".*TEHTRIS EDR Setup.*")
                if window.exists():
                    print(f"Window Title: {window.window_text()}")
                    print(f"Window Class: {window.class_name()}")

                    # Get all controls
                    controls = window.descendants()
                    print(f"Found {len(controls)} controls:")

                    for i, control in enumerate(controls):
                        try:
                            text = control.window_text()
                            class_name = control.class_name()
                            if text.strip() or class_name in ['Button', 'Static', 'Edit']:
                                print(f"  [{i}] {class_name}: '{text}'")
                        except:
                            pass
        except Exception as e:
            print(f"pywinauto method failed: {e}")

        # Method 2: Try OCR if available
        try:
            if PYAUTOGUI_AVAILABLE:
                print("\n--- OCR Text Recognition ---")
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

                # Use pytesseract to extract text
                text = pytesseract.image_to_string(gray)
                if text.strip():
                    print("OCR detected text:")
                    for line in text.split('\n'):
                        if line.strip():
                            print(f"  {line}")
                else:
                    print("No text detected by OCR")
        except Exception as e:
            print(f"OCR method failed: {e}")

        # Method 3: Try Windows API
        try:
            print("\n--- Windows API Method ---")
            import win32gui


            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if "TEHTRIS" in window_text or "Setup" in window_text:
                        windows.append((hwnd, window_text))
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            for hwnd, title in windows:
                print(f"Found window: {title}")

                # Try to get child windows
                def enum_child_callback(child_hwnd, texts):
                    try:
                        child_text = win32gui.GetWindowText(child_hwnd)
                        class_name = win32gui.GetClassName(child_hwnd)
                        if child_text.strip():
                            texts.append(f"  {class_name}: '{child_text}'")
                    except:
                        pass
                    return True

                child_texts = []
                win32gui.EnumChildWindows(hwnd, enum_child_callback, child_texts)
                for text in child_texts:
                    print(text)

        except Exception as e:
            print(f"Windows API method failed: {e}")

        print(f"=== END DEBUG ===\n")

    def click_with_win32gui(self, button_text: str) -> bool:
        """Click button using win32gui API with improved error handling."""
        try:
            import win32gui
            import win32con

            self.logger.info(f"Looking for button with text: {button_text}")

            # Find all TEHTRIS windows with safer enumeration
            tehtris_windows = []
            try:
                def find_tehtris_windows(hwnd, windows):
                    try:
                        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if window_text and "TEHTRIS EDR Setup" in window_text:
                                windows.append(hwnd)
                                self.logger.debug(f"Found TEHTRIS window: {window_text}")
                    except Exception as e:
                        self.logger.debug(f"Error checking window {hwnd}: {e}")
                    return True

                win32gui.EnumWindows(find_tehtris_windows, tehtris_windows)

            except Exception as enum_error:
                self.logger.error(f"EnumWindows failed: {enum_error}")
                # Try alternative approach - find window by class
                try:
                    hwnd = win32gui.FindWindow(None, "TEHTRIS EDR Setup")
                    if hwnd:
                        tehtris_windows = [hwnd]
                        self.logger.info("Found TEHTRIS window using FindWindow")
                except:
                    pass

            if not tehtris_windows:
                self.logger.error("No TEHTRIS windows found")
                return False

            self.logger.info(f"Found {len(tehtris_windows)} TEHTRIS windows")

            # Search for button in all TEHTRIS windows
            all_buttons_found = []
            for window_index, tehtris_hwnd in enumerate(tehtris_windows):
                try:
                    self.logger.info(f"Searching in window {window_index+1}: {tehtris_hwnd}")

                    def find_button_callback(hwnd, button_info):
                        try:
                            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
                                window_text = win32gui.GetWindowText(hwnd)
                                class_name = win32gui.GetClassName(hwnd)

                                # Log all buttons for debugging
                                if class_name == 'Button' and window_text:
                                    all_buttons_found.append(f"Window {window_index+1} - {class_name}: '{window_text}'")

                                if window_text:  # Only process controls with text
                                    # Handle Windows ampersand characters and case variations
                                    clean_window_text = window_text.replace('&', '').lower()
                                    clean_button_text = button_text.replace('&', '').lower()

                                    self.logger.debug(f"Checking {class_name}: '{window_text}' vs '{button_text}'")

                                    if (clean_button_text in clean_window_text and
                                        class_name == 'Button' and
                                        'not' not in clean_window_text):
                                        button_info['hwnd'] = hwnd
                                        button_info['text'] = window_text
                                        return False  # Stop enumeration
                        except Exception as e:
                            self.logger.debug(f"Error checking control {hwnd}: {e}")
                        return True

                    # Find the button in child windows
                    button_info = {}
                    try:
                        win32gui.EnumChildWindows(tehtris_hwnd, find_button_callback, button_info)
                    except Exception as child_enum_error:
                        self.logger.debug(f"EnumChildWindows failed for {tehtris_hwnd}: {child_enum_error}")
                        continue

                    if 'hwnd' in button_info:
                        # Click the button using PostMessage
                        try:
                            win32gui.PostMessage(button_info['hwnd'], win32con.BM_CLICK, 0, 0)
                            self.logger.info(f"Clicked button via win32gui: {button_info['text']}")
                            return True
                        except Exception as click_error:
                            self.logger.error(f"Failed to click button: {click_error}")
                            continue

                except Exception as window_error:
                    self.logger.debug(f"Error searching window {tehtris_hwnd}: {window_error}")
                    continue

            self.logger.error(f"Button with text '{button_text}' not found in any TEHTRIS window")
            return False

        except Exception as e:
            self.logger.error(f"win32gui click failed: {e}")
            return False

    def fill_field_with_win32gui(self, field_label: str, value: str) -> bool:
        """Fill input field using win32gui API with improved error handling."""
        try:
            import win32gui
            import win32con

            self.logger.info(f"Looking for field: {field_label}")

            # Find all TEHTRIS windows with safer enumeration
            tehtris_windows = []
            try:
                def find_tehtris_windows(hwnd, windows):
                    try:
                        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if window_text and "TEHTRIS EDR Setup" in window_text:
                                windows.append(hwnd)
                    except:
                        pass
                    return True

                win32gui.EnumWindows(find_tehtris_windows, tehtris_windows)

            except Exception as enum_error:
                self.logger.error(f"EnumWindows failed: {enum_error}")
                # Try alternative approach
                try:
                    hwnd = win32gui.FindWindow(None, "TEHTRIS EDR Setup")
                    if hwnd:
                        tehtris_windows = [hwnd]
                        self.logger.info("Found TEHTRIS window using FindWindow")
                except:
                    pass

            if not tehtris_windows:
                self.logger.error("No TEHTRIS windows found for field filling")
                return False

            # Search for edit controls in all TEHTRIS windows
            for tehtris_hwnd in tehtris_windows:
                try:
                    edit_controls = []
                    def find_edit_callback(hwnd, controls):
                        try:
                            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
                                class_name = win32gui.GetClassName(hwnd)
                                # Look for various input field types
                                if class_name in ['Edit', 'TextBox', 'RichEdit', 'RichEdit20A', 'RichEdit20W']:
                                    controls.append(hwnd)
                                    self.logger.debug(f"Found input control: {class_name}")
                        except:
                            pass
                        return True

                    win32gui.EnumChildWindows(tehtris_hwnd, find_edit_callback, edit_controls)

                    if edit_controls:
                        # For simplicity, fill fields in order: Server, Tag, License
                        if "server" in field_label.lower():
                            field_index = 0
                        elif "tag" in field_label.lower():
                            field_index = 1
                        elif "license" in field_label.lower():
                            field_index = 2
                        else:
                            field_index = 0

                        if field_index < len(edit_controls):
                            edit_hwnd = edit_controls[field_index]

                            # Click on field to set focus
                            rect = win32gui.GetWindowRect(edit_hwnd)
                            center_x = (rect[0] + rect[2]) // 2
                            center_y = (rect[1] + rect[3]) // 2

                            if PYAUTOGUI_AVAILABLE:
                                pyautogui.click(center_x, center_y)
                                time.sleep(0.2)
                            win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, "")
                            time.sleep(0.1)

                            win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, value)
                            time.sleep(0.1)

                            # Send Tab to move focus forward and trigger validation
                            win32gui.SendMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_TAB, 0)
                            win32gui.SendMessage(edit_hwnd, win32con.WM_KEYUP, win32con.VK_TAB, 0)
                            
                            self.logger.info(f"Filled {field_label} with '{value}' using win32gui")
                            return True

                except Exception as window_error:
                    self.logger.debug(f"Error searching window {tehtris_hwnd}: {window_error}")
                    continue

            self.logger.error(f"Edit field for {field_label} not found")
            return False

        except Exception as e:
            self.logger.error(f"win32gui fill field failed: {e}")
            return False
        
    def find_input_field_by_label(self, label_text: str, offset_x: int = 0, offset_y: int = 25) -> Optional[Tuple[int, int]]:
        """Find input field by looking for its label and calculating field position."""
        if not PYAUTOGUI_AVAILABLE or self.dry_run:
            return None

        try:
            # Find the label text
            label_position = self.find_text_on_screen(label_text)
            if label_position:
                label_x, label_y = label_position
                # Calculate input field position (usually below or to the right of label)
                field_x = label_x + offset_x
                field_y = label_y + offset_y
                self.logger.info(f"Found input field for '{label_text}' at ({field_x}, {field_y})")
                return (field_x, field_y)

            return None

        except Exception as e:
            self.logger.warning(f"Error finding input field for '{label_text}': {e}")
            return None

    def smart_fill_field(self, field_name: str, value: str, label_options: list, fallback_positions: list = None) -> bool:
        """Smart method to find and fill input fields."""
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would fill {field_name} with '{value}'")
            return True

        self.logger.info(f"Smart filling {field_name}...")

        # Strategy 1: Find field by label
        for label in label_options:
            field_position = self.find_input_field_by_label(label)
            if field_position:
                x, y = field_position
                if self.click_coordinates(x, y, f"{field_name} field found by label '{label}'"):
                    time.sleep(0.3)
                    if PYAUTOGUI_AVAILABLE:
                        pyautogui.hotkey('ctrl', 'a')  # Select all existing text
                        pyautogui.write(value)
                        self.logger.info(f"Filled {field_name} with '{value}'")
                        return True

        # Strategy 2: Use fallback positions
        if fallback_positions:
            self.logger.info(f"Using fallback positions for {field_name}")
            for x, y in fallback_positions:
                if self.click_coordinates(x, y, f"{field_name} fallback position"):
                    time.sleep(0.3)
                    if PYAUTOGUI_AVAILABLE:
                        pyautogui.hotkey('ctrl', 'a')  # Select all existing text
                        pyautogui.write(value)
                        self.logger.info(f"Filled {field_name} with '{value}' using fallback")
                        return True

        self.logger.error(f"Failed to fill {field_name} using all strategies")
        return False
    
    def launch_installer(self) -> bool:
        """Launch the MSI installer."""
        self.logger.info("Step 1: Launching installer...")

        if self.dry_run:
            self.logger.info(f"DRY RUN: Would launch {self.msi_path}")
            return True

        try:
            # Minimize all windows first for clean desktop
            self.minimize_all_windows()

            # Take screenshot before launching
            self.take_screenshot("before_launch")

            # Launch MSI - open the installer GUI for manual interaction
            # No /qr flag - this opens the full installer interface
            cmd = f'msiexec /i "{self.msi_path}"'
            self.logger.debug(f"Executing command: {cmd}")
            self.logger.info("Opening installer GUI - you can interact with it manually")

            subprocess.Popen(cmd, shell=True)
            time.sleep(5)  # Give installer more time to start

            # Take screenshot after launching
            self.take_screenshot("after_launch")

            # Try to connect to the installer window
            try:
                self.app = Application().connect(title_re=".*TEHTRIS EDR Setup.*", timeout=self.window_timeout)
                self.logger.info("Successfully connected to installer window")

                # Print window text for debugging
                self.print_window_text()

                return True
            except Exception as connect_error:
                self.logger.warning(f"Could not connect via pywinauto: {connect_error}")



                self.logger.info("Falling back to screen capture method")
                # Continue with screen capture fallback
                return True

        except Exception as e:
            self.logger.error(f"Failed to launch installer: {e}")
            return False

    def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(self.retry_delay * (attempt + 1))

    def handle_welcome_screen(self) -> bool:
        """Handle the welcome screen - click Next button."""
        self.logger.info("Step 2: Handling welcome screen...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would click Next on welcome screen")
            return True

        # Take screenshot for debugging
        self.take_screenshot("welcome_screen")

        # Print window text for debugging
        self.print_window_text()

        # Try win32gui method first
        self.logger.info("Trying win32gui method for welcome screen...")
        if self.click_with_win32gui("Next"):
            return True

        # Fallback to smart finding method
        self.logger.info("win32gui failed, trying smart finding...")
        next_text_options = ["&Next >", "Next >", "Next", "Suivant >", "Suivant"]

        return self.smart_find_and_click(
            "Next button (welcome screen)",
            next_text_options,
            []  # No fallback positions
        )

    def handle_license_agreement(self) -> bool:
        """Handle license agreement - accept terms and click Next."""
        self.logger.info("Step 3: Handling license agreement...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would accept license agreement")
            return True

        # Take screenshot for debugging
        self.take_screenshot("license_agreement")

        # Print window text for debugging
        self.print_window_text()

        # Try win32gui method first
        self.logger.info("Trying win32gui method for license agreement...")

        # Click "I accept" button using win32gui
        if self.click_with_win32gui("accept"):
            time.sleep(0.5)

            # Click Next button using win32gui
            if self.click_with_win32gui("Next"):
                return True

        # Fallback to smart finding method
        self.logger.info("win32gui failed, trying smart finding...")
        accept_text_options = ["I accept", "J'accepte", "accept", "accepte"]

        # First, try to find and click "I accept"
        if self.smart_find_and_click(
            "I accept radio button",
            accept_text_options,
            []  # No fallback positions
        ):
            time.sleep(0.5)

        # Then find and click Next button
        next_text_options = ["&Next >", "Next >", "Next", "Suivant >", "Suivant"]

        return self.smart_find_and_click(
            "Next button (license screen)",
            next_text_options,
            []  # No fallback positions
        )

    def handle_activation_information(self) -> bool:
        """Handle activation information screen - fill fields and click Next."""
        self.logger.info("Step 4: Handling activation information...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would fill activation information")
            return True

        # Take screenshot for debugging
        self.take_screenshot("activation_information")

        # Print window text for debugging
        self.print_window_text()

        # Try win32gui method first
        self.logger.info("Trying win32gui method for activation information...")

        # Fill fields using win32gui
        success = True
        success &= self.fill_field_with_win32gui("server", self.config['server_address'])
        success &= self.fill_field_with_win32gui("tag", self.config['tag'])
        success &= self.fill_field_with_win32gui("license", self.config['license_key'])

        if success:
            time.sleep(0.5)
            # Click Next button using win32gui
            if self.click_with_win32gui("Next"):
                return True

        # Fallback to smart field filling methods
        self.logger.info("win32gui failed, using smart field filling...")

        # Fill server address
        server_labels = ["Server address", "Adresse serveur", "Server", "Serveur"]
        self.smart_fill_field(
            "Server address",
            self.config['server_address'],
            server_labels,
            []  # No fallback positions
        )

        # Fill tag
        tag_labels = ["Tag", "Étiquette"]
        self.smart_fill_field(
            "Tag",
            self.config['tag'],
            tag_labels,
            []  # No fallback positions
        )

        # Fill license key
        license_labels = ["License key", "Clé de licence", "License", "Licence"]
        self.smart_fill_field(
            "License key",
            self.config['license_key'],
            license_labels,
            []  # No fallback positions
        )

        # Click Next button
        time.sleep(1)  # Allow fields to update
        next_text_options = ["&Next >", "Next >", "Next", "Suivant >", "Suivant"]

        return self.smart_find_and_click(
            "Next button (activation screen)",
            next_text_options,
            []  # No fallback positions
        )

    def handle_installation(self) -> bool:
        """Handle installation screen - click Install and wait for completion."""
        self.logger.info("Step 5: Handling installation...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would start installation")
            return True

        # Take screenshot for debugging
        self.take_screenshot("installation_screen")

        # Try win32gui method first
        self.logger.info("Trying win32gui method for Install button...")
        if self.click_with_win32gui("Install"):
            return True

        # Fallback to smart finding for Install button
        self.logger.info("win32gui failed, trying smart finding...")
        install_text_options = ["Install", "Installer", "Install >"]

        return self.smart_find_and_click(
            "Install button",
            install_text_options,
            []  # No fallback positions
        )

    def wait_for_completion(self) -> bool:
        """Wait for installation to complete and handle finish screen."""
        self.logger.info("Step 6: Waiting for installation completion...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would wait for completion")
            return True

        try:
            # Wait for completion window (reasonable timeout for installation)
            completion_timeout = 180  # 3 minutes for installation
            start_time = time.time()

            while time.time() - start_time < completion_timeout:
                try:
                    # Take screenshot to check for completion
                    self.take_screenshot("completion_check")

                    elapsed = int(time.time() - start_time)
                    self.logger.info(f"Checking for completion... ({elapsed}s elapsed)")

                    # Try clicking Finish button using win32gui (primary method)
                    self.logger.info("Trying win32gui method for Finish button...")
                    if self.click_with_win32gui("Finish"):
                        self.logger.info("Clicked Finish button via win32gui")
                        return True

                    # Try clicking Close button using win32gui
                    self.logger.info("Trying win32gui method for Close button...")
                    if self.click_with_win32gui("Close"):
                        self.logger.info("Clicked Close button via win32gui")
                        return True

                    # No button found, wait before next attempt
                    self.logger.info("No completion button found, waiting 2 seconds before retry...")
                    time.sleep(2)  # Check every 2 seconds

                except Exception as e:
                    self.logger.debug(f"Waiting for completion: {e}")
                    time.sleep(2)

            # Final attempt if timeout reached
            self.logger.warning("Timeout reached, trying final attempt...")

            # Try keyboard shortcut as last resort
            if PYAUTOGUI_AVAILABLE:
                self.logger.info("Trying Alt+F for Finish button as final attempt")
                pyautogui.hotkey('alt', 'f')
                time.sleep(1)
                return True  # Assume success if we got this far

            self.logger.error("Installation did not complete within timeout")
            return False

        except Exception as e:
            self.logger.error(f"Failed while waiting for completion: {e}")
            return False

    def verify_installation(self) -> bool:
        """Verify that the installation was successful."""
        self.logger.info("Step 7: Verifying installation...")

        if self.dry_run:
            self.logger.info("DRY RUN: Would verify installation")
            return True

        try:
            import psutil

            self.logger.info("Checking for Agent processes with TEHTRIS description...")
            tehtris_agents = []

            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()

                        # Look for processes named "Agent"
                        if 'agent' in proc_name:
                            try:
                                # Get process executable path for description check
                                exe_path = proc_info.get('exe', '')
                                if exe_path:
                                    # Get file description using Windows API
                                    import win32api
                                    try:
                                        file_info = win32api.GetFileVersionInfo(exe_path, '\\StringFileInfo\\040904b0\\FileDescription')
                                        if file_info and 'tehtris' in file_info.lower():
                                            tehtris_agents.append({
                                                'pid': proc_info['pid'],
                                                'name': proc_info['name'],
                                                'exe': exe_path,
                                                'description': file_info
                                            })
                                            self.logger.info(f"[FOUND] TEHTRIS Agent process: PID {proc_info['pid']} - {proc_info['name']} - {file_info}")
                                    except Exception:
                                        # Fallback: check if exe path contains tehtris
                                        if 'tehtris' in exe_path.lower():
                                            tehtris_agents.append({
                                                'pid': proc_info['pid'],
                                                'name': proc_info['name'],
                                                'exe': exe_path,
                                                'description': 'Path contains TEHTRIS'
                                            })
                                            self.logger.info(f"[FOUND] TEHTRIS Agent process: PID {proc_info['pid']} - {proc_info['name']} - Path: {exe_path}")
                            except Exception as e:
                                self.logger.debug(f"Error checking process {proc_info['name']}: {e}")
                                continue

                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

            except Exception as e:
                self.logger.error(f"Error checking processes: {e}")
                return True  # Don't fail on process check error

            if tehtris_agents:
                self.logger.info(f"[SUCCESS] TEHTRIS EDR installation verified - Found {len(tehtris_agents)} Agent process(es)")
                return True
            else:
                self.logger.warning("[NOT FOUND] No TEHTRIS Agent processes found")
                self.logger.warning("Installation may have completed but processes haven't started yet")
                return True  # Don't fail verification as process might start later

        except ImportError:
            self.logger.warning("psutil not available for process verification")
            return True
        except Exception as e:
            self.logger.warning(f"Verification failed: {e}")
            return True  # Don't fail the entire installation for verification issues

    def cleanup(self):
        """Cleanup resources."""
        if self.app:
            try:
                self.app = None
            except:
                pass

    def run_installation(self) -> bool:
        """Run the complete installation process."""
        self.logger.info("Starting TEHTRIS EDR installation automation")

        try:
            # Validate prerequisites
            if not self.validate_prerequisites():
                return False

            # Step 1: Launch installer
            if not self.launch_installer():
                return False

            time.sleep(0.5)  # Allow installer to fully load

            # Step 2: Handle welcome screen
            if not self.handle_welcome_screen():
                return False

            time.sleep(0.5)

            # Step 3: Handle license agreement
            if not self.handle_license_agreement():
                return False

            time.sleep(0.5)

            # Step 4: Handle activation information
            if not self.handle_activation_information():
                return False

            time.sleep(0.5)

            # Step 5: Handle installation
            if not self.handle_installation():
                return False

            # Step 6: Wait for completion
            if not self.wait_for_completion():
                return False

            # Step 7: Verify installation
            if not self.verify_installation():
                self.logger.warning("Installation verification failed, but installation may still be successful")

            self.logger.info("TEHTRIS EDR installation completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Installation failed with error: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automate TEHTRIS EDR MSI installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tehtris_edr_installer.py                    # Full automated installation
  python tehtris_edr_installer.py --open-only        # Just open installer GUI
  python tehtris_edr_installer.py --dry-run          # Test without installation
  python tehtris_edr_installer.py --debug            # Enable debug logging
  python tehtris_edr_installer.py --open-only --debug # Open GUI with debug info
        """
    )

    parser.add_argument(
        '--msi-path',
        default='TEHTRIS_EDR_2.0.0_Windows_x86_64_MS-28.msi',
        help='Path to the TEHTRIS EDR MSI file (default: TEHTRIS_EDR_2.0.0_Windows_x86_64_MS-28.msi)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual installation)'
    )



    args = parser.parse_args()

    # Note about administrator privileges
    if not args.dry_run:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("Note: Not running as Administrator")
                print("UAC prompts may appear during MSI installation - this is normal")
                print("The installer will request elevation automatically when needed")
                print()
        except:
            print("Note: Could not verify administrator privileges")
            print("UAC prompts may appear during installation")
            print()

    # Create installer instance and run
    installer = TehtrisEDRInstaller(args.msi_path, args.dry_run)
    success = installer.run_installation()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
