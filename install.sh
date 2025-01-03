#!/bin/bash

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Define paths
INSTALL_DIR="/usr/local/share/vodka"
BIN_DIR="/usr/local/bin"
VODKA_HOME="$HOME/.vodka"

echo -e "${GREEN}Installing Vodka Wine Version Manager...${NC}"

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo${NC}"
    exit 1
fi

# Check if required files exist
if [ ! -f "vodka.py" ] || [ ! -f "versions.json" ]; then
    echo -e "${RED}Required files (vodka.py and versions.json) not found in current directory${NC}"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$VODKA_HOME"

# Copy files to install directory
cp vodka.py "$INSTALL_DIR/"
cp versions.json "$INSTALL_DIR/"

# Create the vodka command wrapper
echo '#!/bin/bash' > "$BIN_DIR/vodka"
echo 'python3 /usr/local/share/vodka/vodka.py "$@"' >> "$BIN_DIR/vodka"

# Set correct permissions
chmod 755 "$INSTALL_DIR/vodka.py"
chmod 644 "$INSTALL_DIR/versions.json"
chmod 755 "$BIN_DIR/vodka"
chown -R root:root "$INSTALL_DIR"
chown "$SUDO_USER:$SUDO_USER" "$VODKA_HOME"

# Add PATH to bashrc if not already present
BASHRC="$HOME/.bashrc"
PATH_LINE='export PATH="$HOME/.vodka/default/files/bin:$PATH"'

if ! grep -q "$PATH_LINE" "$BASHRC"; then
    echo "Adding Vodka to PATH in .bashrc..."
    echo "" >> "$BASHRC"
    echo "# Vodka Wine Version Manager" >> "$BASHRC"
    echo "$PATH_LINE" >> "$BASHRC"
fi

echo -e "${GREEN}Installation completed!${NC}"
echo "Please restart your terminal or run 'source ~/.bashrc' to use vodka"
echo "Usage:"
echo "  vodka list               - List all available versions"
echo "  vodka install <version>  - Install a specific version"
echo "  vodka default <version>  - Set default version"
