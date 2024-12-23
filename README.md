# Game Cheats Manager

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md)

![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Polonium-salts/Game-Cheats-Manager/total)
![GitHub Repo stars](https://img.shields.io/github/stars/Polonium-salts/Game-Cheats-Manager)
![GitHub Release](https://img.shields.io/github/v/release/Polonium-salts/Game-Cheats-Manager)
![GitHub License](https://img.shields.io/github/license/Polonium-salts/Game-Cheats-Manager)
[![Featured｜HelloGitHub](https://img.shields.io/badge/Featured-HelloGitHub-green)](https://hellogithub.com)

![Game Cheats Manager logo](src/assets/logo.png)

Game Cheats Manager is a one-stop solution for gamers to manage their trainers efficiently. It allows users to browse, download, and manage all their trainers from one convenient location. Each trainer, typically a standalone executable, can be launched or deleted directly through the app, simplifying your gaming experience by keeping everything organized and accessible.

## Features

1. **Browse and Search**
   - Browse installed trainers in a modern card-based interface
   - Quick search functionality for installed trainers
   - Intuitive trainer management with launch and delete options

2. **Download Management**
   - Search and download trainers from multiple sources
   - Automatic trainer updates
   - Download progress tracking
   - Customizable download path

3. **Plugin System**
   - Extensible plugin architecture
   - Built-in antivirus plugin for Windows Defender whitelist management
   - Easy plugin development interface

4. **Settings and Customization**
   - Theme selection (Dark/Light)
   - Multiple language support (English, 简体中文, 繁體中文)
   - Automatic update options
   - Customizable interface settings

## Usage

1. **Main Interface**
   - **Installed**: View and manage installed trainers
   - **Extensions**: Manage plugins and extensions
   - **Downloads**: Search and download new trainers
   - **Settings**: Customize application settings
   - **About**: View version info and updates

2. **Trainer Management**
   - Launch trainers with administrator privileges
   - Delete unwanted trainers
   - Search installed trainers
   - Import existing trainers

3. **Download Features**
   - Search trainers by game name
   - One-click download and installation
   - Automatic trainer updates
   - Download path customization

4. **Plugin System**
   - Enable/disable plugins
   - Configure plugin settings
   - Add Windows Defender exceptions

## Installation

1. **Download the Installer**
   - Navigate to the [latest release](https://github.com/Polonium-salts/Game-Cheats-Manager/releases/latest)
   - Download the installer for Windows (64-bit)

2. **Run the Installer**
   - Execute the downloaded file
   - Follow the installation wizard
   - Choose installation directory

3. **Launch the Application**
   - Start from desktop shortcut or start menu
   - First-time setup will configure basic settings

## Development

### Requirements
- Python 3.8+
- PyQt6
- Required packages listed in `requirements.txt`

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/Polonium-salts/Game-Cheats-Manager.git

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/scripts/main.py
```

### Plugin Development
1. Create a new plugin class inheriting from `BasePlugin`
2. Implement required methods and properties
3. Register plugin in `src/scripts/plugins/__init__.py`

## Disclaimer

Game Cheats Manager is an independent tool that is not affiliated with any external trainer providers. The trainers downloaded are subject to their respective terms and conditions. This software simply provides a convenient way to manage these trainers and does not host any of the content itself.

You can find their official websites below:
- **FLiNG**: https://flingtrainer.com
- **WeMod**: https://www.wemod.com

## Support

For issues, feature requests, or contributions:
- Create an [issue](https://github.com/Polonium-salts/Game-Cheats-Manager/issues)
- Submit a [pull request](https://github.com/Polonium-salts/Game-Cheats-Manager/pulls)

## License

This project is licensed under the [GPL-3.0 License](LICENSE.txt)

