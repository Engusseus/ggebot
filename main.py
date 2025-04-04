import os
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pyautogui
import keyboard
import threading
from pynput import mouse
import cv2
import numpy as np
import pytesseract
from datetime import datetime

class GoodgameEmpireBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Goodgame Empire Bot")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        # Initialize attributes
        self.target_x = None
        self.target_y = None
        self.selecting_target = False
        self.running = False
        self.confidence_level = 0.8
        self.skip_confidence = 0.6  # Lower confidence for skip-related images
        self.max_retries = 5
        self.last_successful_time = 60  # Default fallback time

        # Tesseract configuration
        self.tesseract_path_var = tk.StringVar()
        self.configure_tesseract()

        # Default time setting
        self.default_time_var = tk.IntVar(value=60)

        # Status variables (not displayed but needed for functionality)
        self.status_var = tk.StringVar(value="Ready")
        self.coord_var = tk.StringVar(value="Not selected")
        self.action_var = tk.StringVar(value="Idle")

        # Image folder path
        self.image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'objects')

        # Define all image paths
        self.image_paths = {
            'spy': os.path.join(self.image_folder, 'spy.png'),
            'confirm1': os.path.join(self.image_folder, 'confirm1.png'),
            'confirm2': os.path.join(self.image_folder, 'confirm2.png'),
            'confirm3': os.path.join(self.image_folder, 'confirm3.png'),
            'confirm4': os.path.join(self.image_folder, 'confirm4.png'),
            'horse1': os.path.join(self.image_folder, 'horse1.png'),
            'horse2': os.path.join(self.image_folder, 'horse2.png'),
            'attack1': os.path.join(self.image_folder, 'attack1.png'),
            'attack2': os.path.join(self.image_folder, 'attack2.png'),
            'preset': os.path.join(self.image_folder, 'preset.png'),
            'remove': os.path.join(self.image_folder, 'remove.png'),
            'fillwaves': os.path.join(self.image_folder, 'fillwaves.png'),
            'skip': os.path.join(self.image_folder, 'skip.png'),
            'close1': os.path.join(self.image_folder, 'close1.png'),
            '30min': os.path.join(self.image_folder, '30min.png'),
            '1hour': os.path.join(self.image_folder, '1hour.png'),
            'action': os.path.join(self.image_folder, 'action.png'),  # Add the action button image
            'time_marker': os.path.join(self.image_folder, 'time_marker.png'),
            'time_marker2': os.path.join(self.image_folder, 'time_marker2.png')  # Add the new time marker
        }

        # Create simplified UI
        self.create_ui()

        # Set up hotkey to stop the bot
        keyboard.add_hotkey('esc', self.stop_bot)

        # Check if image files exist
        self.verify_images()

    def configure_tesseract(self):
        """Try to find and configure Tesseract OCR"""
        # Common Tesseract installation paths
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files\Tesseract_OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract_OCR\tesseract.exe',
            r'/usr/bin/tesseract',
            r'/usr/local/bin/tesseract'
        ]

        # Check if any of these paths exist
        for path in possible_paths:
            if os.path.exists(path):
                self.tesseract_path_var.set(path)
                pytesseract.pytesseract.tesseract_cmd = path
                return True

        # If no path works, set a default for the UI
        self.tesseract_path_var.set(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        return False

    def browse_tesseract(self):
        """Open file dialog to select Tesseract executable"""
        path = filedialog.askopenfilename(
            title="Select Tesseract Executable",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.tesseract_path_var.set(path)
            pytesseract.pytesseract.tesseract_cmd = path
            try:
                version = pytesseract.get_tesseract_version()
                messagebox.showinfo("Success", f"Tesseract OCR version {version} successfully configured!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not use the selected Tesseract path: {e}")

    def check_tesseract(self):
        """Check if Tesseract OCR is correctly configured"""
        try:
            path = self.tesseract_path_var.get()
            if not path:
                return False

            pytesseract.pytesseract.tesseract_cmd = path
            version = pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def create_ui(self):
        """Create a simplified UI with just title and start button"""
        # Title
        title_label = ttk.Label(self.root, text="Goodgame Empire Bot", font=("Arial", 16, "bold"))
        title_label.pack(pady=(30, 20))

        # Start Button
        self.start_button = tk.Button(
            self.root,
            text="START BOT",
            command=self.start_bot,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=15
        )
        self.start_button.pack(pady=10)

        # Help text
        help_label = ttk.Label(self.root, text="Press ESC anytime to stop the bot", 
                              font=("Arial", 9), foreground="gray")
        help_label.pack(pady=(20, 0))

    def update_confidence(self, event=None):
        """Update confidence level from slider"""
        self.confidence_level = 0.8  # Fixed value in simplified UI

    def update_status(self, message):
        """Update status"""
        self.status_var.set(message)
        print(f"Status: {message}")

    def update_action(self, message):
        """Update current action"""
        self.action_var.set(message)
        print(f"Action: {message}")

    def verify_images(self):
        """Check if all required image files exist"""
        if not os.path.exists(self.image_folder):
            messagebox.showerror("Error", f"Image folder not found: {self.image_folder}")
            return False

        missing_images = []
        for name, path in self.image_paths.items():
            if not os.path.exists(path) and name != 'time_marker':  # time_marker is optional
                missing_images.append(f"{name}.png")

        if missing_images:
            missing_str = "\n".join(missing_images)
            messagebox.showerror("Error",
                                 f"Missing image files in {self.image_folder}:\n{missing_str}")
            return False

        return True

    def select_target(self):
        """Wait for the user to click the target location"""
        self.update_status("Click to set target location")
        self.selecting_target = True

        def on_click(x, y, button, pressed):
            if pressed and self.selecting_target:
                self.target_x, self.target_y = x, y
                self.selecting_target = False
                self.update_target_coords()
                return False  # Stop listener

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def update_target_coords(self):
        """Update the target coordinates and start the bot loop"""
        self.coord_var.set(f"({self.target_x}, {self.target_y})")
        self.update_status(f"Target set at ({self.target_x}, {self.target_y})")

        # Start the main bot loop in a separate thread
        threading.Thread(target=self.run_bot_loop, daemon=True).start()

    def start_bot(self):
        """Start the bot by initiating target selection"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED, text="RUNNING...")
            self.target_x, self.target_y = None, None
            threading.Thread(target=self.select_target, daemon=True).start()

    def stop_bot(self):
        """Stop the bot gracefully"""
        if self.running:
            self.running = False
            self.selecting_target = False
            self.update_status("Bot stopped")
            self.update_action("Idle")
            self.start_button.config(state=tk.NORMAL, text="START BOT")

    def find_and_click(self, image_name, click=True, region=None, confidence=None):
        """Find an image on screen and click it if requested"""
        if confidence is None:
            # Use lower confidence for skip-related images
            if image_name in ['30min', '1hour']:
                confidence = self.skip_confidence
            else:
                confidence = self.confidence_level

        try:
            self.update_action(f"Looking for {image_name}")

            # Try to locate the image
            if region:
                location = pyautogui.locateCenterOnScreen(
                    self.image_paths[image_name],
                    confidence=confidence,
                    region=region
                )
            else:
                location = pyautogui.locateCenterOnScreen(
                    self.image_paths[image_name],
                    confidence=confidence
                )

            if location:
                x, y = location
                if click:
                    pyautogui.click(x, y)
                    time.sleep(0.5)  # Small delay after clicking
                else:
                    self.update_action(f"Found {image_name}")
                return location

            return None
        except Exception:
            return None

    def find_with_retry(self, image_name, max_attempts=None, click=True, region=None, click_target_on_fail=True):
        """Try to find an image with multiple attempts, clicking target coordinates on failure if requested"""
        if max_attempts is None:
            max_attempts = self.max_retries

        for attempt in range(max_attempts):
            if not self.running:
                return None

            self.update_status(f"Looking for {image_name} (attempt {attempt + 1}/{max_attempts})")
            location = self.find_and_click(image_name, click=click, region=region)

            if location:
                return location

            if click_target_on_fail and attempt < max_attempts - 1:
                self.update_action(f"Clicking target again")
                pyautogui.click(self.target_x, self.target_y)
                time.sleep(1)  # Wait a bit after clicking

        return None

    def read_time_ocr(self):
        """Use OCR to read time displayed on screen"""
        try:
            self.update_action("Reading time with OCR")

            # Make sure Tesseract is configured
            if not self.check_tesseract():
                print("Debug: Tesseract not configured properly")
                return None

            # First, try to find time_marker2.png (the new marker)
            marker_location = self.find_and_click('time_marker2', click=False, confidence=0.7)
            if marker_location:
                print("Debug: Found time_marker2.png")
                marker_type = "time_marker2"
            else:
                # Fall back to the original time_marker.png
                marker_location = self.find_and_click('time_marker', click=False, confidence=0.7)
                if marker_location:
                    print("Debug: Found time_marker.png")
                    marker_type = "time_marker"
                else:
                    print("Debug: Could not find either time marker")
                    # Use a fixed region if no marker found
                    region = (880, 400, 120, 25)
                    print(f"Debug: Using fallback region {region}")
                    marker_type = None
            
            # Define region based on which marker was found
            if marker_location:
                x, y = marker_location
                
                # Adjust region based on marker type
                if marker_type == "time_marker2":
                    # For time_marker2 - the new format
                    # The time is likely centered in the marker
                    x_start = int(x - 60)
                    y_start = int(y - 10)
                    width = 120
                    height = 25
                else:
                    # For the original time_marker
                    x_start = int(x - 100)
                    y_start = int(y - 15)
                    width = 200
                    height = 35
                
                region = (x_start, y_start, width, height)
                print(f"Debug: Using region based on {marker_type}: {region}")

            try:
                screenshot = pyautogui.screenshot(region=region)
                screenshot = np.array(screenshot)
                print("Debug: Screenshot captured for OCR successfully")
                
                # Save screenshot for debugging (optional)
                print(f"Debug: Screenshot dimensions: {screenshot.shape}")
            except Exception as e:
                print(f"Debug: Failed to capture screenshot - {str(e)}")
                return None

            # Rest of OCR processing remains similar
            # Convert to grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            
            # Apply multiple image processing techniques
            processed_images = [
                # Original grayscale (resized)
                cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC),
                
                # Increased contrast
                cv2.resize(cv2.convertScaleAbs(gray, alpha=1.5, beta=0), None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC),
                
                # Binary thresholds
                cv2.resize(cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1], None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC),
                cv2.resize(cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1], None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            ]
            
            # Try different PSM modes
            psm_modes = ['--psm 7', '--psm 6', '--psm 13', '--psm 8', '--psm 10']
            
            for img in processed_images:
                for psm in psm_modes:
                    try:
                        custom_config = f'{psm} -c tessedit_char_whitelist=0123456789:'
                        text = pytesseract.image_to_string(img, config=custom_config).strip()
                        print(f"Debug: Raw OCR output with {psm}: '{text}'")
                        
                        if ':' in text:
                            # Clean the text
                            text = ''.join(c for c in text if c.isdigit() or c == ':')
                            parts = text.split(':')
                            
                            if len(parts) == 3:  # HH:MM:SS format
                                hours = int(''.join(c for c in parts[0] if c.isdigit()) or '0')
                                minutes = int(''.join(c for c in parts[1] if c.isdigit()) or '0')
                                seconds = int(''.join(c for c in parts[2] if c.isdigit()) or '0')
                                
                                if hours >= 0 and minutes >= 0 and minutes < 60 and seconds >= 0 and seconds < 60:
                                    total_seconds = hours * 3600 + minutes * 60 + seconds
                                    print(f"Debug: Successfully read time - {hours:02d}:{minutes:02d}:{seconds:02d} ({total_seconds} seconds)")
                                    return total_seconds
                                    
                            elif len(parts) == 2:  # MM:SS format
                                minutes = int(''.join(c for c in parts[0] if c.isdigit()) or '0')
                                seconds = int(''.join(c for c in parts[1] if c.isdigit()) or '0')
                                
                                if minutes >= 0 and seconds >= 0 and seconds < 60:
                                    total_seconds = minutes * 60 + seconds
                                    print(f"Debug: Successfully read time - {minutes:02d}:{seconds:02d} ({total_seconds} seconds)")
                                    return total_seconds
                    except Exception as e:
                        print(f"Debug: OCR attempt failed - {str(e)}")
                        continue

            print("Debug: Failed to read valid time format after all attempts")
            return None
        except Exception as e:
            print(f"Debug: Error in read_time_ocr - {str(e)}")
            return None

    def read_skip_count(self, skip_type):
        """Read the count of available skips for a specific type"""
        try:
            self.update_action(f"Reading {skip_type} skip count")

            # Find the skip button first
            skip_loc = self.find_and_click(skip_type, click=False, confidence=self.skip_confidence)
            if not skip_loc:
                return 0

            x, y = skip_loc

            # Adjust the region to better capture the skip count
            count_region = (x - 30, y - 25, 60, 25)  # Wider region to ensure we capture the number

            # Take screenshot of the count region
            screenshot = pyautogui.screenshot(region=count_region)
            screenshot = np.array(screenshot)

            # Convert to grayscale and enhance
            gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # Apply threshold
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

            # OCR configuration for numbers only
            custom_config = r'--psm 7 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=custom_config).strip()

            try:
                count = int(text)
                return count
            except ValueError:
                return 0
        except Exception:
            return 0

    def read_time(self):
        """Read time using OCR"""
        time_value = self.read_time_ocr()

        # If OCR fails, use default time
        if not time_value:
            time_value = self.default_time_var.get()
        else:
            # Store successful time for future reference
            self.last_successful_time = time_value

        return time_value

    def navigate_skips(self, total_seconds):
        """Navigate and use skips to reduce waiting time"""
        self.update_status(f"Navigating skips for {total_seconds} seconds")
        print(f"\nDebug: Starting skip navigation for {total_seconds} seconds")

        if total_seconds <= 20:
            print(f"Debug: Time is less than 20 seconds, waiting naturally")
            self.update_action(f"Waiting {total_seconds}s")
            time.sleep(total_seconds)
            return True

        # Add 5-minute tolerance (300 seconds)
        tolerance = 300  # 5 minutes in seconds
        
        # Calculate how many of each skip type we need with tolerance
        hours_needed = total_seconds // 3600
        remaining_seconds = total_seconds % 3600
        
        # If remaining time is within 5 minutes of a full hour, add another hour skip
        if 3600 - remaining_seconds <= tolerance and remaining_seconds > 0:
            hours_needed += 1
            remaining_seconds = 0
            print(f"Debug: Added 1 extra hour skip due to 5-minute tolerance")
        
        # Calculate half-hours needed from the remaining seconds
        half_hours_needed = remaining_seconds // 1800
        remaining_after_half_hours = remaining_seconds % 1800
        
        # If remaining time is within 5 minutes of a half hour, add another half-hour skip
        if 1800 - remaining_after_half_hours <= tolerance and remaining_after_half_hours > 0:
            half_hours_needed += 1
            print(f"Debug: Added 1 extra 30min skip due to 5-minute tolerance")

        print(f"Debug: Need {hours_needed} 1hour skips and {half_hours_needed} 30min skips")

        # Track if we used any skips
        used_any_skips = False
        seconds_remaining = total_seconds

        # Use 1hour skips
        for i in range(hours_needed):
            if not self.running or seconds_remaining <= 20:
                break

            self.update_action(f"Using 1hour skip ({i+1}/{hours_needed})")
            print(f"Debug: Attempting to use 1hour skip {i+1}/{hours_needed}")

            # Find the 1hour skip image
            hour_location = self.find_and_click('1hour', click=False, confidence=self.skip_confidence)
            if not hour_location:
                print("Debug: Could not find 1hour skip button")
                continue

            # Calculate position to the right of 1hour button for action button
            x, y = hour_location
            action_x = x + 100  # Adjust this offset as needed
            action_y = y

            # Click the action button
            print(f"Debug: Clicking to the right of 1hour at ({action_x}, {action_y})")
            pyautogui.click(action_x, action_y)
            time.sleep(1)  # Wait for skip to be applied

            # Mark that we used a skip
            used_any_skips = True

            # Re-read the time
            new_time = self.read_time_ocr()
            if new_time is not None:
                seconds_remaining = new_time
                print(f"Debug: After 1hour skip, remaining time: {seconds_remaining} seconds")
            else:
                # If we can't read the time, estimate
                seconds_remaining -= 3600
                print(f"Debug: Estimated remaining time: {seconds_remaining} seconds")

        # Use 30min skips
        for i in range(half_hours_needed):
            if not self.running or seconds_remaining <= 20:
                break

            self.update_action(f"Using 30min skip ({i+1}/{half_hours_needed})")
            print(f"Debug: Attempting to use 30min skip {i+1}/{half_hours_needed}")

            # Find the 30min skip image
            half_hour_location = self.find_and_click('30min', click=False, confidence=self.skip_confidence)
            if not half_hour_location:
                print("Debug: Could not find 30min skip button")
                continue

            # Calculate position to the right of 30min button for action button
            x, y = half_hour_location
            action_x = x + 100  # Adjust this offset as needed
            action_y = y

            # Click the action button
            print(f"Debug: Clicking to the right of 30min at ({action_x}, {action_y})")
            pyautogui.click(action_x, action_y)
            time.sleep(1)  # Wait for skip to be applied

            # Mark that we used a skip
            used_any_skips = True

            # Re-read the time
            new_time = self.read_time_ocr()
            if new_time is not None:
                seconds_remaining = new_time
                print(f"Debug: After 30min skip, remaining time: {seconds_remaining} seconds")
            else:
                # If we can't read the time, estimate
                seconds_remaining -= 1800
                print(f"Debug: Estimated remaining time: {seconds_remaining} seconds")

        # Wait for any remaining time
        if seconds_remaining > 0:
            self.update_action(f"Waiting remaining {seconds_remaining}s")
            time.sleep(seconds_remaining)

        return used_any_skips

    def run_bot_loop(self):
        """Main bot logic loop"""
        self.update_status("Bot started")
        print("\n=== Bot Started ===")

        if not self.check_tesseract():
            print("Warning: Tesseract OCR not configured. Using default time values.")
            self.update_status("WARNING: Tesseract OCR not configured. Using default time values.")

        while self.running:
            try:
                print("\n=== Starting New Cycle ===")
                # Define all steps in sequence for better control
                steps = [
                    ('target_click', None),  # Special case for target click
                    ('spy', 'spy'),
                    ('confirm1', 'confirm1'),
                    ('horse1', 'horse1'),
                    ('read_time', None),  # Special case for reading time
                    ('confirm2', 'confirm2'),
                    ('wait_spy', None),  # Special case for waiting
                    ('target_click2', None),  # Special case for second target click
                    ('attack1', 'attack1'),
                    ('confirm3', 'confirm3'),
                    ('preset', 'preset'),
                    ('remove', 'remove'),  # Will use topmost
                    ('fillwaves', 'fillwaves'),
                    ('attack2', 'attack2'),
                    ('horse2', 'horse2'),
                    ('read_attack_time', None),  # Special case for reading time
                    ('confirm4', 'confirm4'),
                    ('wait_attack', None),  # Special case for waiting
                    ('target_click3', None),  # Special case for third target click
                    ('attack1', 'attack1'),  # Added attack1 before skip
                    ('skip', 'skip'),
                    ('read_skip_time', None),  # Special case for reading time
                    ('use_skips', None),  # Special case for skip handling
                    ('close1', 'close1')
                ]

                current_step = 0
                while current_step < len(steps) and self.running:
                    step_name, image_name = steps[current_step]
                    self.update_status(f"Executing step: {step_name}")
                    print(f"\nDebug: Executing step {current_step + 1}/{len(steps)}: {step_name}")
                    
                    success = False
                    attempts = 0
                    max_attempts = 5

                    while not success and attempts < max_attempts and self.running:
                        try:
                            if step_name.startswith('target_click'):
                                # Handle target clicks
                                self.update_action("Clicking target location")
                                print(f"Debug: Clicking target at ({self.target_x}, {self.target_y})")
                                pyautogui.click(self.target_x, self.target_y)
                                time.sleep(1)
                                success = True
                            
                            elif step_name == 'read_time':
                                # Add delay after horse1 to ensure travel time window is visible
                                print("Debug: Waiting for travel time window to appear")
                                time.sleep(2)  # Wait longer for travel time window
                                
                                # Try to read time multiple times
                                for attempt in range(3):
                                    travel_time = self.read_time_ocr()
                                    if travel_time:
                                        travel_time += 2  # Add buffer
                                        print(f"Debug: Successfully read travel time: {travel_time} seconds")
                                        success = True
                                        break
                                    else:
                                        print(f"Debug: Time read attempt {attempt+1}/3 failed, retrying...")
                                        time.sleep(0.5)
                                
                                if not success:
                                    # Fall back to default time if all attempts fail
                                    travel_time = self.default_time_var.get()
                                    print(f"Debug: Using default travel time: {travel_time} seconds")
                                    success = True

                            elif step_name == 'read_attack_time':
                                # Handle time reading for attack
                                attack_travel_time = self.read_time()
                                if attack_travel_time:
                                    attack_travel_time += 2  # Add buffer
                                    success = True

                            elif step_name == 'read_skip_time':
                                # Handle time reading for skip
                                skip_time = self.read_time()
                                if skip_time:
                                    success = True

                            elif step_name == 'wait_spy':
                                # Handle spy waiting
                                if travel_time:
                                    self.update_status(f"Waiting for spy travel: {travel_time} seconds")
                                    time.sleep(travel_time)
                                    success = True

                            elif step_name == 'wait_attack':
                                # Handle attack waiting
                                if attack_travel_time:
                                    self.update_status(f"Waiting for attack travel: {attack_travel_time} seconds")
                                    time.sleep(attack_travel_time)
                                    success = True

                            elif step_name == 'use_skips':
                                # Handle skip usage
                                if skip_time:
                                    success = self.navigate_skips(skip_time)

                            elif step_name == 'remove':
                                # Handle topmost remove button
                                if self.find_topmost_with_retry('remove', max_attempts=3):
                                    success = True

                            else:
                                # Handle normal image finding and clicking
                                if self.find_with_retry(image_name, max_attempts=1):  # Only try once per attempt
                                    success = True

                        except Exception as e:
                            print(f"Debug: Error in step {step_name} - {str(e)}")
                            pass

                        if not success:
                            attempts += 1
                            print(f"Debug: Step failed, attempt {attempts}/{max_attempts}")
                            if attempts >= max_attempts:
                                print(f"Debug: Maximum attempts reached, backtracking to previous step")
                                if current_step > 0:
                                    current_step -= 1
                            else:
                                time.sleep(1)

                    if success:
                        print(f"Debug: Step {step_name} completed successfully")
                        current_step += 1
                    elif not self.running:
                        print("Debug: Bot stopped during step execution")
                        break

                if current_step >= len(steps):
                    print("\nDebug: Completed full cycle, starting again")
                    self.update_status("Completed full cycle, starting again")

            except Exception as e:
                print(f"\nDebug: Error in main loop - {str(e)}")
                if self.running:
                    time.sleep(5)

    def find_topmost_and_click(self, image_name, click=True, confidence=None):
        """Find the topmost instance of an image on screen and click it if requested"""
        if confidence is None:
            confidence = self.confidence_level

        try:
            self.update_action(f"Looking for topmost {image_name}")

            # Find all instances of the image
            locations = list(pyautogui.locateAllOnScreen(
                self.image_paths[image_name],
                confidence=confidence
            ))

            if locations:
                # Sort by y-coordinate (top to bottom)
                locations.sort(key=lambda x: x.top)
                
                # Get the center of the topmost location
                topmost = locations[0]
                x = topmost.left + topmost.width // 2
                y = topmost.top + topmost.height // 2

                if click:
                    pyautogui.click(x, y)
                    time.sleep(0.5)  # Small delay after clicking
                else:
                    self.update_action(f"Found topmost {image_name}")
                return (x, y)

            return None
        except Exception:
            return None

    def find_topmost_with_retry(self, image_name, max_attempts=None, click=True, click_target_on_fail=True):
        """Try to find the topmost instance of an image with multiple attempts"""
        if max_attempts is None:
            max_attempts = self.max_retries

        for attempt in range(max_attempts):
            if not self.running:
                return None

            self.update_status(f"Looking for topmost {image_name} (attempt {attempt + 1}/{max_attempts})")
            location = self.find_topmost_and_click(image_name, click=click)

            if location:
                return location

            if click_target_on_fail and attempt < max_attempts - 1:
                self.update_action(f"Clicking target again")
                pyautogui.click(self.target_x, self.target_y)
                time.sleep(1)  # Wait a bit after clicking

        return None


if __name__ == "__main__":
    # Set higher DPI awareness for better screen captures
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    app = GoodgameEmpireBot(root)
    root.mainloop()