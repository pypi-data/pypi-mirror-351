# OMST AVR-Tool

A Python tool for programming AVR microcontrollers, developed for internal use at OceanScan-MST.

## Features

- Flash AVR microcontrollers using avrdude
- Generate setup certificates as PDF documents
- Upload certificates to network shares
- Support for multiple board versions and firmware releases

## Installation

### From PyPI

```bash
pip install omst-avrtool
```


## Dependencies

- Python 3.8 or higher
- avrdude must be installed and available in your PATH
- WeasyPrint dependencies (Cairo, Pango, GLib)
```bash
# On Ubuntu/Debian
# Install complete set of dependencies for WeasyPrint
pip install dbus-python secretstorage
```

## Usage

```bash
# Check out firmware from repository
omst-avrtool checkout

# List available boards
omst-avrtool flash -l

# Flash a board
omst-avrtool flash -b BOARD_NAME -n INVENTORY_NUMBER -a AUTHOR_NAME

# Flash without generating report
omst-avrtool flash -b BOARD_NAME --no-report
```

## Development

```bash
# Create virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -e ".[dev]"

# Build package
python -m build

# Install the built package
pip install --force-reinstall dist/omst_avrtool-*.whl
```

## Publishing
```bash
python -m pip install --upgrade pip
pip install build twine
python -m build
twine upload dist/*
```

## Credentials Management

When connecting to network shares, credentials are managed securely:

1. Credentials can be provided via environment variables:
   - `OMST_AVR_USERNAME`: Username for network share
   - `OMST_AVR_PASSWORD`: Password for network share

2. Alternatively, you can store credentials in your system's keyring:
   - First-time use will prompt for credentials
   - You'll be asked if you want to save them for future use

3. If neither environment variables nor keyring entries are found, 
   you'll be prompted to enter credentials interactively

## License

This project is licensed under the MIT License - see the LICENSE file for details.