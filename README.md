# Goodgame Empire Bot

This is a Python bot designed to automate certain tasks in the game Goodgame Empire using image recognition and GUI automation.

## Features

### Game Modes
* **Event Mode**: The standard mode with spy-attack-skip cycle for up to 4 targets
* **Baron Mode**: Attack-only mode supporting unlimited targets with intelligent attack scheduling

### Core Functionality
* **Multi-Target Support**: Manage target locations based on selected mode (up to 4 in Event Mode, unlimited in Baron Mode)
* **Target Selection Overlay**: Transparent overlay for selecting targets without moving the game view
* **Sequential Processing**: Processes targets in an optimal sequence based on the selected mode
* **Intelligent Timing**: Tracks and remembers timing values for each target
* **Progress Tracking**: Visual progress bar shows completion status of operations
* **Phased Operations**: Operates in different phases depending on the selected mode
* **Image Recognition**: Uses OpenCV and PyAutoGUI to find game elements on screen
* **OCR Integration**: Uses Tesseract OCR to read in-game timers and information
* **Skip Management**: Navigates skip timers using available speed-ups
* **User-Friendly Interface**: Simple Tkinter GUI for managing targets and controlling the bot
* **Emergency Stop**: Press ESC hotkey to stop the bot at any time

## Requirements

* Python 3.x
* Tesseract OCR: Installation instructions can be found [here](https://github.com/tesseract-ocr/tesseract#installing-tesseract). Make sure the `tesseract` command is in your system's PATH or configure the path within the bot if needed.
* Required Python packages (see `requirements.txt`):
  * `pyautogui`
  * `keyboard`
  * `pynput`
  * `opencv-python`
  * `numpy`
  * `pytesseract`

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ggebot
   ```
2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Tesseract OCR:** Follow the official installation guide for your operating system.

## Usage

1. **Run the bot:**
   ```bash
   python main.py
   ```
2. **Configure Tesseract (if needed):** If the bot doesn't automatically find Tesseract, you may need to ensure it's in your system's PATH.

3. **Select Mode:**
   * Choose between "Event Mode" or "Baron Mode" from the dropdown menu
   * The start button will update to reflect your selection

4. **Add Targets:**
   * Click "Add Target" button
   * A transparent overlay will appear
   * Click on target locations in the game window (green dots will mark your selections)
   * Click "Done" when finished
   * Event Mode: Maximum 4 targets
   * Baron Mode: Unlimited targets

5. **Start the Bot:**
   * Click the "START EVENT MODE" or "START BARON MODE" button
   * The bot will process targets based on the selected mode
   * Progress bar will show completion status

6. **Stop the bot:** Press the `ESC` key at any time to stop the bot.

## How It Works

### Event Mode

The bot operates in three distinct phases:

1. **Spy Phase:**
   * Clicks on target 1 and sends a spy
   * Waits for spy report (+ buffer time)
   * Moves to target 2, and so on

2. **Attack Phase:**
   * Attacks target 1
   * Attacks target 2, and so on
   * Waits for the shortest attack time

3. **Skip Phase:**
   * Processes skip operations for all targets

### Baron Mode

Baron Mode operates differently:

1. **Attack-Only Phase:**
   * Attacks each target without sending spies
   * Uses a simplified attack sequence (preset → fill waves)
   * Maintains a maximum of 18 simultaneous attacks
   * When reaching 18 active attacks, waits for the next slot based on attack timing
   * Continues until all targets have been attacked

2. **Sleep Phase:**
   * After attacking all targets, waits for 3 hours before starting the next cycle

## Image Files (`objects/` directory)

This directory contains the template images used by PyAutoGUI to locate elements on the screen. Ensure these images match what appears in your game window for the bot to function correctly. You may need to recapture these images based on your screen resolution and game settings.

## Future Work

* **Baron Mode Attack Timing**: Further optimization and refinement of the attack scheduling system in Baron Mode is needed to ensure optimal performance in all scenarios.
* **Dynamic Overlay Sizing**: Automatic adjustment of the target selection overlay based on game window size.

## Troubleshooting

* **Image Recognition Issues**: If the bot fails to find buttons or interface elements, you might need to update the images in the `objects/` directory to match your game's appearance.
* **OCR Problems**: Make sure Tesseract OCR is properly installed and configured. The bot will attempt to detect it automatically.
* **Performance**: Close unnecessary applications to ensure the bot runs smoothly.
* **Target Selection**: If the overlay doesn't align perfectly with your game window, adjust the width and height values in the Target Selection Overlay section.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot automates gameplay actions. Use it responsibly and be aware of the game's terms of service regarding automation tools. The developers are not responsible for any consequences resulting from the use of this bot. 