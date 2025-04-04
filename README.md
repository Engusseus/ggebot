# Goodgame Empire Bot

This is a Python bot designed to automate certain tasks in the game Goodgame Empire using image recognition and GUI automation.

## Features

*   Automates sequences of actions like spying and attacking.
*   Uses image recognition (OpenCV, PyAutoGUI) to find game elements.
*   Uses OCR (Tesseract) to read in-game information like timers.
*   Navigates skip timers using available speed-ups.
*   Simple Tkinter GUI for starting the bot and selecting the target location.
*   Hotkey (ESC) to stop the bot.

## Requirements

*   Python 3.x
*   Tesseract OCR: Installation instructions can be found [here](https://github.com/tesseract-ocr/tesseract#installing-tesseract). Make sure the `tesseract` command is in your system's PATH or configure the path within the bot if needed (though automatic detection is attempted).
*   Required Python packages (see `requirements.txt`):
    *   `pyautogui`
    *   `keyboard`
    *   `pynput`
    *   `opencv-python`
    *   `numpy`
    *   `pytesseract`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ggebot
    ```
2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install Tesseract OCR:** Follow the official installation guide for your operating system.

## Usage

1.  **Run the bot:**
    ```bash
    python main.py
    ```
2.  **Configure Tesseract (if needed):** If the bot doesn't automatically find Tesseract, you might need to manually provide the path when prompted or ensure it's in your system's PATH.
3.  **Start the bot:** Click the "START BOT" button in the application window.
4.  **Select Target:** Click on the target location within the Goodgame Empire game window when prompted by the status message.
5.  **Stop the bot:** Press the `ESC` key at any time.

## Image Files (`objects/` directory)

This directory contains the template images used by PyAutoGUI to locate elements on the screen. Ensure these images match what appears in your game window for the bot to function correctly. You may need to recapture these images based on your screen resolution and game settings.

## Disclaimer

This bot automates gameplay actions. Use it responsibly and be aware of the game's terms of service regarding automation tools. The developers are not responsible for any consequences resulting from the use of this bot. 