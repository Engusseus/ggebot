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
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        # Initialize attributes
        self.target_x = None
        self.target_y = None
        self.targets = []  # List to store multiple targets
        self.current_target_index = 0  # Track which target is being processed
        self.selecting_target = False
        self.running = False
        self.confidence_level = 0.8
        self.skip_confidence = 0.6  # Lower confidence for skip-related images
        self.max_retries = 5
        self.last_successful_time = 60  # Default fallback time
        self.target_times = {}  # Dictionary to store travel times for each target

        # Tesseract configuration
        self.tesseract_path_var = tk.StringVar()
        self.configure_tesseract()

        # Default time setting
        self.default_time_var = tk.IntVar(value=60)

        # Status variables (not displayed but needed for functionality)
        self.status_var = tk.StringVar(value="Ready")
        self.coord_var = tk.StringVar(value="No targets selected")
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
        """Create UI with target management and start button"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Goodgame Empire Bot", font=("Arial", 16, "bold"))
        title_label.pack(pady=(10, 15))

        # Target Management Frame
        target_frame = ttk.LabelFrame(main_frame, text="Targets (Max 4)")
        target_frame.pack(pady=10, padx=5, fill=tk.X)

        # Target Listbox
        self.target_listbox = tk.Listbox(target_frame, height=4)
        self.target_listbox.pack(pady=5, padx=5, fill=tk.X)

        # Target Buttons Frame
        button_frame = ttk.Frame(target_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))

        self.add_target_button = ttk.Button(
            button_frame,
            text="Add Target",
            command=self.add_target
        )
        self.add_target_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.remove_target_button = ttk.Button(
            button_frame,
            text="Remove Selected",
            command=self.remove_target
        )
        self.remove_target_button.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

        # Status Label
        status_label = ttk.Label(main_frame, text="Status:")
        status_label.pack(anchor=tk.W, padx=5)
        
        status_value = ttk.Label(main_frame, textvariable=self.status_var, wraplength=380)
        status_value.pack(fill=tk.X, padx=5)

        # Action Label
        action_label = ttk.Label(main_frame, text="Action:")
        action_label.pack(anchor=tk.W, padx=5)
        
        action_value = ttk.Label(main_frame, textvariable=self.action_var, wraplength=380)
        action_value.pack(fill=tk.X, padx=5)

        # Start Button
        self.start_button = tk.Button(
            main_frame,
            text="START LOOP",
            command=self.start_bot,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            width=15
        )
        self.start_button.pack(pady=10)

        # Help text
        help_label = ttk.Label(main_frame, text="Press ESC anytime to stop the bot", 
                              font=("Arial", 9), foreground="gray")
        help_label.pack(pady=(5, 0))

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

    def add_target(self):
        """Start the process of adding a target coordinate"""
        if len(self.targets) >= 4:
            messagebox.showwarning("Maximum Targets", "You can only add up to 4 targets.")
            return
            
        if not self.running:
            self.selecting_target = True
            self.update_status("Click to set target location")
            threading.Thread(target=self.select_target, daemon=True).start()
        else:
            messagebox.showwarning("Bot Running", "Cannot add targets while the bot is running.")

    def select_target(self):
        """Wait for the user to click the target location"""
        def on_click(x, y, button, pressed):
            if pressed and self.selecting_target:
                # Store the new target
                self.targets.append((x, y))
                self.update_status(f"Added target at ({x}, {y})")
                self.update_target_listbox()
                self.selecting_target = False
                return False  # Stop listener

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def remove_target(self):
        """Remove the selected target from the list"""
        if self.running:
            messagebox.showwarning("Bot Running", "Cannot remove targets while the bot is running.")
            return
            
        selected = self.target_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a target to remove.")
            return
            
        index = selected[0]
        removed = self.targets.pop(index)
        self.update_status(f"Removed target at ({removed[0]}, {removed[1]})")
        self.update_target_listbox()

    def update_target_listbox(self):
        """Update the listbox with current targets"""
        self.target_listbox.delete(0, tk.END)
        for i, (x, y) in enumerate(self.targets):
            self.target_listbox.insert(tk.END, f"Target {i+1}: ({x}, {y})")
            
        # Update the coordinate display
        if self.targets:
            self.coord_var.set(f"{len(self.targets)} target(s) selected")
        else:
            self.coord_var.set("No targets selected")

    def start_bot(self):
        """Start the bot loop if targets are available"""
        if not self.targets:
            messagebox.showwarning("No Targets", "Please add at least one target first.")
            return
            
        if not self.running:
            self.running = True
            self.current_target_index = 0  # Start with the first target
            self.start_button.config(state=tk.DISABLED, text="RUNNING...")
            self.add_target_button.config(state=tk.DISABLED)
            self.remove_target_button.config(state=tk.DISABLED)
            self.update_status("Bot running")
            threading.Thread(target=self.run_bot_loop, daemon=True).start()

    def stop_bot(self):
        """Stop the bot gracefully"""
        if self.running:
            self.running = False
            self.selecting_target = False
            self.update_status("Bot stopped")
            self.update_action("Idle")
            self.start_button.config(state=tk.NORMAL, text="START LOOP")
            self.add_target_button.config(state=tk.NORMAL)
            self.remove_target_button.config(state=tk.NORMAL)

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
                self.update_action(f"Clicking target {self.current_target_index + 1} again")
                target_x, target_y = self.targets[self.current_target_index]
                pyautogui.click(target_x, target_y)
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
        """Main bot logic loop - batches similar operations across all targets"""
        self.update_status("Bot started")
        print("\n=== Bot Started ===")

        if not self.check_tesseract():
            print("Warning: Tesseract OCR not configured. Using default time values.")
            self.update_status("WARNING: Tesseract OCR not configured. Using default time values.")

        # Main loop - continue until bot is stopped
        while self.running:
            if not self.targets:
                self.update_status("No targets set. Please add targets.")
                break

            # Dictionary to track operation state for each target
            target_states = {}
            for i, coords in enumerate(self.targets):
                target_key = f"target_{i}"
                target_states[target_key] = {
                    "coords": coords,
                    "spy_time": None,
                    "attack_time": None,
                    "skip_time": None,
                    "index": i,
                    "spy_start_time": None  # Track when the spy was sent
                }

            # ====================== PHASE 1: SPY TARGETS ONE BY ONE, WAITING FOR EACH ======================
            self.update_status("Phase 1: Sending spies and waiting for reports")
            print("\n=== PHASE 1: SENDING SPIES AND WAITING FOR REPORTS ===")
            
            for target_key, state in target_states.items():
                if not self.running:
                    break
                    
                i = state["index"]
                target_x, target_y = state["coords"]
                self.current_target_index = i
                
                self.update_status(f"Spying on Target {i+1}/{len(self.targets)}")
                print(f"\n--- Spying on Target {i+1}: ({target_x}, {target_y}) ---")
                
                try:
                    # Click target to start spy sequence
                    self.update_action(f"Clicking target {i+1} for spy")
                    pyautogui.click(target_x, target_y)
                    time.sleep(1)
                    
                    # Execute spy sequence
                    spy_steps = [
                        ('spy', 'spy'),
                        ('confirm1', 'confirm1'),
                        ('horse1', 'horse1'),
                        ('read_time', None),  # Read spy travel time
                        ('confirm2', 'confirm2')
                    ]
                    
                    success = self.execute_steps(spy_steps, i, target_x, target_y)
                    if success and self.running:
                        # Get the travel time that was set during the steps
                        if f"{target_key}_spy" in self.target_times:
                            spy_time = self.target_times[f"{target_key}_spy"]
                            # Add 20 seconds buffer to the spy time as requested
                            spy_time += 20
                            state["spy_time"] = spy_time
                            state["spy_start_time"] = time.time()  # Record when the spy was sent
                            print(f"Debug: Target {i+1} spy time set to {spy_time}s (including +20s buffer)")
                            
                            # Wait for this spy to return before proceeding to the next target
                            self.update_status(f"Waiting {spy_time}s for spy on Target {i+1} to return")
                            print(f"\n--- Waiting {spy_time}s for spy report from Target {i+1} ---")
                            
                            # Wait with checks to allow stopping
                            wait_start = time.time()
                            while self.running and (time.time() - wait_start) < spy_time:
                                time.sleep(1)
                                remaining = spy_time - (time.time() - wait_start)
                                if remaining > 0 and remaining % 10 < 1:  # Update roughly every 10 seconds
                                    self.update_status(f"Waiting for spy from Target {i+1}: {int(remaining)}s remaining")
                            
                            if self.running:
                                print(f"--- Spy report from Target {i+1} has arrived, ready for next target ---")
                        else:
                            # If we couldn't read the time, use default plus buffer
                            default_time = self.default_time_var.get() + 20
                            state["spy_time"] = default_time
                            print(f"Debug: Target {i+1} using default spy time: {default_time}s (including +20s buffer)")
                            
                            # Wait using default time
                            self.update_status(f"Waiting {default_time}s for spy on Target {i+1} to return (default)")
                            print(f"\n--- Waiting {default_time}s for spy report from Target {i+1} (default) ---")
                            
                            # Wait with checks to allow stopping
                            wait_start = time.time()
                            while self.running and (time.time() - wait_start) < default_time:
                                time.sleep(1)
                                remaining = default_time - (time.time() - wait_start)
                                if remaining > 0 and remaining % 10 < 1:  # Update roughly every 10 seconds
                                    self.update_status(f"Waiting for spy from Target {i+1}: {int(remaining)}s remaining")
                            
                            if self.running:
                                print(f"--- Spy report from Target {i+1} has arrived, ready for next target ---")
                    
                except Exception as e:
                    print(f"Debug: Error in spy phase for Target {i+1} - {str(e)}")
                    # Continue to next target rather than stopping completely
            
            # ====================== PHASE 2: ATTACK ALL TARGETS ======================
            if self.running:
                self.update_status("Phase 2: Attacking all targets")
                print("\n=== PHASE 2: ATTACKING ALL TARGETS ===")
                
                for target_key, state in target_states.items():
                    if not self.running:
                        break
                        
                    i = state["index"]
                    target_x, target_y = state["coords"]
                    self.current_target_index = i
                    
                    self.update_status(f"Attacking Target {i+1}/{len(self.targets)}")
                    print(f"\n--- Attacking Target {i+1}: ({target_x}, {target_y}) ---")
                    
                    try:
                        # Click target to start attack sequence
                        self.update_action(f"Clicking target {i+1} for attack")
                        pyautogui.click(target_x, target_y)
                        time.sleep(1)
                        
                        # Execute attack sequence
                        attack_steps = [
                            ('attack1', 'attack1'),
                            ('confirm3', 'confirm3'),
                            ('preset', 'preset'),
                            ('remove', 'remove'),  # Will use topmost
                            ('fillwaves', 'fillwaves'),
                            ('attack2', 'attack2'),
                            ('horse2', 'horse2'),
                            ('read_attack_time', None),  # Read attack travel time
                            ('confirm4', 'confirm4')
                        ]
                        
                        success = self.execute_steps(attack_steps, i, target_x, target_y)
                        if success and self.running:
                            # Get the travel time that was set during the steps
                            if f"{target_key}_attack" in self.target_times:
                                state["attack_time"] = self.target_times[f"{target_key}_attack"]
                                print(f"Debug: Target {i+1} attack time set to {state['attack_time']}s")
                        
                        time.sleep(1)  # Short delay between targets
                        
                    except Exception as e:
                        print(f"Debug: Error in attack phase for Target {i+1} - {str(e)}")
                        # Continue to next target rather than stopping completely
            
            # ====================== WAIT FOR ATTACKS AND START SKIPS ======================
            # Calculate the shortest attack time to know when to start skips
            min_attack_time = float('inf')
            for state in target_states.values():
                if state["attack_time"] and state["attack_time"] < min_attack_time:
                    min_attack_time = state["attack_time"]
            
            # If no valid attack times, use a default wait
            if min_attack_time == float('inf'):
                min_attack_time = self.default_time_var.get()
            
            # Wait for the shortest attack time
            if self.running:
                self.update_status(f"Waiting {min_attack_time}s for attacks to arrive")
                print(f"\n=== Waiting {min_attack_time}s for attacks to arrive ===")
                
                # Wait, with checks to allow stopping
                wait_start = time.time()
                while self.running and (time.time() - wait_start) < min_attack_time:
                    time.sleep(1)
                    remaining = min_attack_time - (time.time() - wait_start)
                    if remaining > 0 and remaining % 10 < 1:  # Update roughly every 10 seconds
                        self.update_status(f"Waiting for attacks: {int(remaining)}s remaining")
            
            # ====================== PHASE 3: SKIP ALL TARGETS ======================
            if self.running:
                self.update_status("Phase 3: Processing skips for all targets")
                print("\n=== PHASE 3: PROCESSING SKIPS FOR ALL TARGETS ===")
                
                for target_key, state in target_states.items():
                    if not self.running:
                        break
                        
                    i = state["index"]
                    target_x, target_y = state["coords"]
                    self.current_target_index = i
                    
                    self.update_status(f"Processing skips for Target {i+1}/{len(self.targets)}")
                    print(f"\n--- Skip phase for Target {i+1}: ({target_x}, {target_y}) ---")
                    
                    try:
                        # Click target to start skip sequence
                        self.update_action(f"Clicking target {i+1} for skip")
                        pyautogui.click(target_x, target_y)
                        time.sleep(1)
                        
                        # Execute skip sequence
                        skip_steps = [
                            ('attack1', 'attack1'),  # First need to start attack again
                            ('skip', 'skip'),
                            ('read_skip_time', None),  # Read remaining skip time
                            ('use_skips', None),  # Use skip items
                            ('close1', 'close1')
                        ]
                        
                        success = self.execute_steps(skip_steps, i, target_x, target_y)
                        if success and self.running:
                            # Get the skip time that was set during the steps (for future reference)
                            if f"{target_key}_skip" in self.target_times:
                                state["skip_time"] = self.target_times[f"{target_key}_skip"]
                                print(f"Debug: Target {i+1} skip time was {state['skip_time']}s")
                        
                        time.sleep(1)  # Short delay between targets
                        
                    except Exception as e:
                        print(f"Debug: Error in skip phase for Target {i+1} - {str(e)}")
                        # Continue to next target rather than stopping completely
            
            # Cycle complete
            if self.running:
                self.update_status("Completed full cycle through all targets")
                print("\n=== COMPLETED FULL CYCLE THROUGH ALL TARGETS ===")
                time.sleep(5)  # Wait a bit before starting the next cycle
            else:
                print("\n=== Bot cycle stopped ===")
        
        # Reset the UI when the bot stops
        self.stop_bot()

    def execute_steps(self, steps, target_index, target_x, target_y):
        """Execute a sequence of steps for a target and return success/failure"""
        target_key = f"target_{target_index}"
        
        for step_idx, (step_name, image_name) in enumerate(steps):
            if not self.running:
                return False
                
            self.update_status(f"Target {target_index+1}: Step {step_name}")
            print(f"Debug: Target {target_index+1} - Step {step_idx+1}/{len(steps)}: {step_name}")
            
            success = False
            attempts = 0
            max_attempts = 4  # Lower than default to avoid long waits
            
            while not success and attempts < max_attempts and self.running:
                try:
                    if step_name == 'read_time':
                        # Read spy travel time
                        time.sleep(2)  # Wait for travel time window
                        travel_time = self.read_time()  # This calls read_time_ocr internally
                        
                        if travel_time:
                            print(f"Debug: Target {target_index+1} - Read spy time: {travel_time}s")
                            # Store this time for future reference
                            self.target_times[f"{target_key}_spy"] = travel_time
                            success = True
                        else:
                            # Try to use a previously recorded time for this target
                            if f"{target_key}_spy" in self.target_times:
                                travel_time = self.target_times[f"{target_key}_spy"]
                                print(f"Debug: Target {target_index+1} - Using stored spy time: {travel_time}s")
                            else:
                                travel_time = self.default_time_var.get()
                                print(f"Debug: Target {target_index+1} - Using default spy time: {travel_time}s")
                            success = True

                    elif step_name == 'read_attack_time':
                        # Read attack travel time
                        attack_travel_time = self.read_time()  # This calls read_time_ocr internally
                        
                        if attack_travel_time:
                            print(f"Debug: Target {target_index+1} - Read attack time: {attack_travel_time}s")
                            # Store this time for future reference
                            self.target_times[f"{target_key}_attack"] = attack_travel_time
                            success = True
                        else:
                            # Try to use a previously recorded time for this target
                            if f"{target_key}_attack" in self.target_times:
                                attack_travel_time = self.target_times[f"{target_key}_attack"]
                                print(f"Debug: Target {target_index+1} - Using stored attack time: {attack_travel_time}s")
                            else:
                                attack_travel_time = self.default_time_var.get()
                                print(f"Debug: Target {target_index+1} - Using default attack time: {attack_travel_time}s")
                            success = True

                    elif step_name == 'read_skip_time':
                        # Read skip time
                        skip_time = self.read_time()  # This calls read_time_ocr internally
                        
                        if skip_time:
                            print(f"Debug: Target {target_index+1} - Read skip time: {skip_time}s")
                            # Store this time for future reference
                            self.target_times[f"{target_key}_skip"] = skip_time
                            success = True
                        else:
                            # Try to use a previously recorded time for this target
                            if f"{target_key}_skip" in self.target_times:
                                skip_time = self.target_times[f"{target_key}_skip"]
                                print(f"Debug: Target {target_index+1} - Using stored skip time: {skip_time}s")
                            else:
                                skip_time = self.default_time_var.get()
                                print(f"Debug: Target {target_index+1} - Using default skip time: {skip_time}s")
                            success = True

                    elif step_name == 'use_skips':
                        # Handle skip usage
                        if f"{target_key}_skip" in self.target_times:
                            skip_time = self.target_times[f"{target_key}_skip"]
                            self.update_status(f"Target {target_index+1}: Using skips for {skip_time}s")
                            success = self.navigate_skips(skip_time)
                        else:
                            # No skip time available, try to read it now
                            skip_time = self.read_time()
                            if skip_time:
                                self.update_status(f"Target {target_index+1}: Using skips for {skip_time}s")
                                success = self.navigate_skips(skip_time)
                            else:
                                # Can't determine skip time, use default
                                skip_time = self.default_time_var.get()
                                self.update_status(f"Target {target_index+1}: Using skips with default time {skip_time}s")
                                success = self.navigate_skips(skip_time)

                    elif step_name == 'remove':
                        # Handle topmost remove button
                        if self.find_topmost_with_retry('remove', max_attempts=3):
                            success = True
                        else:
                            # If can't find remove button, assume we need to continue anyway
                            print(f"Debug: Target {target_index+1} - Could not find remove button, continuing")
                            success = True
                            
                    else:
                        # Handle normal image finding and clicking
                        if self.find_with_retry(image_name, max_attempts=2):  # Reduced attempts per step
                            success = True
                        
                except Exception as e:
                    print(f"Debug: Target {target_index+1} - Error in step {step_name} - {str(e)}")
                    # Continue with attempts
                
                if not success:
                    attempts += 1
                    print(f"Debug: Target {target_index+1} - Step {step_name} failed, attempt {attempts}/{max_attempts}")
                    
                    if attempts >= max_attempts:
                        # If we've tried enough times, move to the next step
                        print(f"Debug: Target {target_index+1} - Max attempts reached for {step_name}, skipping to next step")
                        success = True  # Force success to move on
                    else:
                        # Try clicking the target again before next attempt
                        pyautogui.click(target_x, target_y)
                        time.sleep(1)
            
            # If a step failed and we didn't force success, or the bot was stopped
            if not success or not self.running:
                return False
                
        # All steps completed
        return True

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
                self.update_action(f"Clicking target {self.current_target_index + 1} again")
                target_x, target_y = self.targets[self.current_target_index]
                pyautogui.click(target_x, target_y)
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