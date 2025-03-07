# AutoEditorGUI

A simple graphical user interface for the [auto-editor](https://github.com/WyattBlue/auto-editor) tool, which automatically edits videos by analyzing audio and motion.

## Features

- **Simple Interface**: Clean, intuitive GUI to configure auto-editor parameters
- **Customizable Settings**: Adjust margins, speed settings, thresholds, and more
- **Multiple Export Options**: Support for Premiere Pro, DaVinci Resolve, Final Cut Pro, Shotcut, and clip sequences
- **Dark Mode**: Toggle between light and dark themes
- **Save Preferences**: Your settings are saved between sessions
- **Progress Tracking**: Visual progress bar while processing files
- **Auto-Updates**: Check for new versions directly from GitHub

## Installation

1. Make sure you have [auto-editor](https://github.com/WyattBlue/auto-editor) installed:
   ```
   pip install auto-editor
   ```

2. Download the latest release from the [Releases page](https://github.com/kaianvn/AutoEditorGUI/releases)

3. Extract the files and run `AutoEditorGUI.exe` (Windows)

(or just run the .py file, that also works!)

## Usage

1. **Select a File**: Click "Select File" and choose the media file you want to process
2. **Configure Options**: Switch to the "Options" tab to customize editing parameters:
   - **Margins**: Set margins for the beginning and end of detected segments
   - **Edit Method**: Choose how to detect segments (audio/motion)
   - **Speed Settings**: Configure playback speed for silent/non-silent portions
   - **Export Format**: Select your preferred editing software format
   - **Timeline Options**: Adjust frame rate, sample rate, resolution, etc.
   - **Thresholds**: Fine-tune audio and motion detection sensitivity
3. **Process**: Return to the "Process" tab and click "Process File"
4. **Review**: When processing completes, check the edited file in your preferred editor

## Requirements

- Python 3.6 or higher
- auto-editor (latest version recommended)
- Tkinter (included with most Python installations)
- Internet connection for update checking

## Configuration

All settings are automatically saved to settings.ini in the same directory as the application.

## Updates

The application can check for updates by clicking the "Check for Updates" button in the Options tab. If a new version is available, you'll be prompted to download it.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [auto-editor](https://github.com/WyattBlue/auto-editor) by WyattBlue

---
Made with ❤️ by [@kaianvn](https://github.com/kaianvn)
