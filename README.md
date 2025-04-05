# Goodgame Empire Bot

This is a Python bot designed to automate certain tasks in the game Goodgame Empire using image recognition and GUI automation.

## Features

* **Multi-Target Support**: Can manage up to 4 target locations in sequence
* **Sequential Processing**: Spies on targets one after another, waiting for each spy report before proceeding
* **Intelligent Timing**: Tracks and remembers timing values for each target
* **Phased Operations**: Operates in phases - spy phase, attack phase, and skip phase
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

3. **Add Targets:**
   * Click "Add Target" button
   * Click on a target location in the game window
   * Repeat for up to 4 targets

4. **Start the Bot:**
   * Click the "START LOOP" button
   * The bot will process each target in sequence:
     * Send spies to each target one by one, waiting for each spy report
     * Attack all targets in sequence
     * Process skips for all targets in sequence

5. **Stop the bot:** Press the `ESC` key at any time to stop the bot.

## How It Works

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

## Image Files (`objects/` directory)

This directory contains the template images used by PyAutoGUI to locate elements on the screen. Ensure these images match what appears in your game window for the bot to function correctly. You may need to recapture these images based on your screen resolution and game settings.

## Troubleshooting

* **Image Recognition Issues**: If the bot fails to find buttons or interface elements, you might need to update the images in the `objects/` directory to match your game's appearance.
* **OCR Problems**: Make sure Tesseract OCR is properly installed and configured. The bot will attempt to detect it automatically.
* **Performance**: Close unnecessary applications to ensure the bot runs smoothly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This bot automates gameplay actions. Use it responsibly and be aware of the game's terms of service regarding automation tools. The developers are not responsible for any consequences resulting from the use of this bot. 