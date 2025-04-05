# Contributing to GGEBot

Thank you for considering contributing to the Goodgame Empire Bot! This document provides guidelines for contributing to the project.

## Code Structure

The bot is organized as follows:

- `main.py` - The main bot script containing all functionality
- `objects/` - Directory containing template images for recognition
- `.venv/` - Virtual environment (not tracked in git)
- `requirements.txt` - Python dependencies

## Key Components

1. **Mode Selection** - Allows switching between Event Mode and Baron Mode
2. **GUI Interface** - Built with Tkinter, manages target selection and bot control
3. **Target Selection Overlay** - Transparent overlay for clicking targets without affecting the game
4. **Image Recognition** - Uses PyAutoGUI and OpenCV to find elements on screen
5. **OCR Integration** - Uses Tesseract to read time values
6. **Multi-Target Logic** - Manages processing of multiple targets based on selected mode
7. **Attack Scheduling** - Smart scheduling of attacks in Baron Mode (maximum 18 simultaneous attacks)
8. **Timing Management** - Tracks and stores timing values for each target
9. **Progress Tracking** - Visual progress bar for monitoring completion status

## Development Setup

1. Clone the repository
2. Set up a virtual environment and install dependencies
3. Install Tesseract OCR
4. Make sure all required template images are in the `objects/` directory

## How to Contribute

1. **Report Bugs** - If you find a bug, please create an issue describing:
   - What happened vs. what you expected
   - Steps to reproduce
   - Your environment (OS, Python version, etc.)

2. **Suggest Enhancements** - Feel free to suggest improvements or new features

3. **Submit Pull Requests** - For code contributions:
   - Fork the repository
   - Create a branch for your changes
   - Make your changes
   - Test thoroughly
   - Submit a pull request with a clear description of the changes

## Coding Guidelines

1. **Code Style** - Follow PEP 8 conventions
2. **Documentation** - Document functions, classes, and complex logic
3. **Testing** - Test changes thoroughly before submitting

## Extending the Bot

### Priority Improvements

1. **Baron Mode Attack Timing** - The attack scheduling system in Baron Mode needs further optimization to ensure optimal performance in all scenarios
2. **Overlay Positioning** - Improve positioning and sizing of the target selection overlay
3. **Dynamic Configuration** - Add more user-configurable settings

### Adding New Game Elements

To add support for new game elements:

1. Capture screen images of the elements and save to `objects/`
2. Add new image paths to the `image_paths` dictionary
3. Integrate the new elements into the appropriate phase of the bot logic

### Modifying Phase Logic

#### Event Mode
- The current flow: spy phase → attack phase → skip phase
- Each phase processes all targets sequentially

#### Baron Mode
- Attack-only phase (no spy or skip phases)
- Smart scheduling with maximum 18 simultaneous attacks
- 3-hour sleep period between attack cycles

When modifying either mode:
1. Ensure proper waiting between operations
2. Update time tracking and storage
3. Maintain progress bar updates

## Adding New Modes

If adding a new operation mode:
1. Add the mode to the mode selection dropdown
2. Create a new mode-specific loop function
3. Implement mode-specific UI and progress tracking
4. Document the new mode in README.md

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 