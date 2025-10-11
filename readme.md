# ani-cli-python

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white) [![Version](https://img.shields.io/badge/Version-1.0-green)](https://github.com/yourusername/ani-cli-python/releases/tag/1.0) [![License](https://img.shields.io/badge/License-Free-yellow)](LICENSE) [![Status](https://img.shields.io/badge/Development-Active-brightgreen)](https://github.com/yourusername/ani-cli-python)

> **A simple python script for streaming anime**

ani-cli-python is a lightweight command-line interface (CLI) tool built in Python for streaming anime episodes. It supports searching, browsing ongoing and completed series, bookmarking, and customizable settings like quality and host URL. No GUI – pure terminal magic! 🌟

*Note: For icon reference, consider using an anime-themed emoji like 📺 or 🐱 in badges, or add a custom SVG icon (e.g., from [Flaticon](https://www.flaticon.com/search?word=anime) or [Icons8](https://icons8.com/icons/set/anime)) in the repository assets for a modern, colorful look. Style it with dark/light theme compatibility via GitHub's default rendering.*

## Features

- **CLI Interface**: Simple command-line navigation – no GUI required.
- **Search & Browse**: Easily search for anime, filter by ongoing or complete series.
- **Bookmark & Tracking**: Save favorites, mark episodes as seen/watched.
- **Custom Settings**: Adjust default quality, change host URL (default: otakudesu.best).
- **Streaming Integration**: Plays episodes via MPV player.
- **Modern & Colorful UI**: Powered by Rich for vibrant terminal output.

## Requirements

- **Python**: Version 3.8+ (Note: You mentioned 3.0.0, but Python 3.8+ is recommended for compatibility with libraries).
  - Download from [official Python website](https://www.python.org/downloads/).
  - Install pip from [official pip documentation](https://pip.pypa.io/en/stable/installation/).
- **Libraries** (install via pip):
  - [typer](https://pypi.org/project/typer/) – For building the CLI.
  - [rich](https://pypi.org/project/rich/) – For colorful terminal output.
  - [questionary](https://pypi.org/project/questionary/) – For interactive prompts.
  - [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) (via `beautifulsoup4`) – For web scraping.
  - [requests](https://pypi.org/project/requests/) – For HTTP requests.
- **Other**:
  - Termux (Android terminal emulator) for mobile use.
  - MPV player installed (required for streaming).

**Disclaimer**: This script works only on Termux with MPV installed! It may not function on other environments without modifications.

## Installation

1. **Install Python and pip**:
   - Download and install Python from the [official website](https://www.python.org/downloads/).
   - Ensure pip is installed: Follow the [pip installation guide](https://pip.pypa.io/en/stable/installation/).

2. **Install Requirements**:
   ```
    pip install typer rich questionary beautifulsoup4 requests
   ```
   

4. **Install MPV for Android** (if using Termux):
- Download from [Google Play Store](https://play.google.com/store/apps/details?id=is.xyz.mpv).

5. **Clone the repository and navigate to
 the project directory**:
   ```
    git clone https://github.com/sunanja-ms/ani-cli-python.git cd ani-cli-python
   ```


## Usage
   - Run the script with:
    ```
     python cli.py
    ```
   - or
     ```
     python3 cli.py
     ```
   - Follow the interactive prompts to search, browse, and stream anime. Use settings to customize quality or host.

   - Example commands (via CLI menu):
   - Search: Type anime name.
   - Settings: Access to change defaults.

**Demo**: No demo available yet. Check the code and run it yourself!

## Screenshots

*(Place your screenshots here for a modern look. Suggested layout: Use a grid or carousel. Upload images to the repo's `images/` folder and reference them. For colorful style, ensure high-contrast images that work on dark/light themes.)*

![Screenshot 1](images/screenshot1.png)  
*Main menu interface*

![Screenshot 2](images/screenshot2.png)  
*Search results with colorful output*

*(You can adjust and add more images as needed in a prominent section.)*

## Development Status

- **Active** 🚀
- **Version**: 1.0

## License

This project is free to use, modify, and distribute. Anyone can take the code and adapt it as they wish – no restrictions! (Public domain equivalent. Add a simple LICENSE file with: "This project is released into the public domain.")

## Reporting Issues

The best way to report issues is by creating a new issue on the [GitHub repository](https://github.com/sunanja-ms/ani-cli-python/issues). Provide details like error logs, environment (e.g., Termux version), and steps to reproduce.

---

*Built with ❤️ for anime fans. Contributions welcome!*
