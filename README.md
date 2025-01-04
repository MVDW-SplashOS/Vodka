# Vodka - Wine Version Manager

Vodka is a command-line tool for managing multiple WINE versions. It allows you to easily install, manage, and switch between different versions and forks of WINE.

## Features

- Install multiple Wine versions and forks
- Set default version
- List available versions
- Refresh version list
- Easy command-line interface

## Installation

You can install Vodka using pip:

```bash
pip install vodka-cli
```

## Usage

### Basic Commands

```bash
# List all available versions
vodka list

# Install a specific version
vodka install GE-Proton9-20

# Set default version
vodka default GE-Proton9-20

# Refresh available versions list
vodka refresh
```

### Command Details

- `list`: Shows all available versions with their installation and default status
- `install <version>`: Downloads and installs the specified version
- `default <version>`: Sets the specified installed version as default
- `refresh`: Updates the list of available versions

## Directory Structure

Vodka stores all installed versions and configuration in `~/.vodka/` directory:

```
~/.vodka/
├── versions.json       # Available versions list
├── default            # Symlink to default version
└── GE-Proton*        # Installed versions
```

## Requirements

- Python 3.6 or higher
- Linux operating system
- Internet connection for downloading versions

## Development

To contribute to Vodka development:

1. Clone the repository:
```bash
git clone https://github.com/MVDW-Java/vodka.git
```

2. Install development dependencies:
```bash
cd vodka
pip install -e lib/
pip install -e cli/
```
