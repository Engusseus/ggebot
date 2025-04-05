# Contributing to GGEBot

Thank you for considering contributing to the Goodgame Empire Bot! This document provides guidelines for contributing to the project.

## Code Structure

The bot is organized as follows:

- `main.py` - The main bot script containing all functionality
- `objects/` - Directory containing template images for recognition
- `.venv/` - Virtual environment (not tracked in git)
- `requirements.txt` - Python dependencies

## Key Components

1. **GUI Interface** - Built with Tkinter, manages target selection and bot control
2. **Image Recognition** - Uses PyAutoGUI and OpenCV to find elements on screen
3. **OCR Integration** - Uses Tesseract to read time values
4. **Multi-Target Logic** - Manages sequential processing of multiple targets
5. **Timing Management** - Tracks and stores timing values for each target

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

### Adding New Game Elements

To add support for new game elements:

1. Capture screen images of the elements and save to `objects/`
2. Add new image paths to the `image_paths` dictionary
3. Integrate the new elements into the appropriate phase of the bot logic

### Modifying Phase Logic

If modifying the phase logic:

1. Understand the current flow: spy phase → attack phase → skip phase
2. Each phase processes all targets sequentially
3. Ensure proper waiting between operations
4. Update time tracking and storage

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 