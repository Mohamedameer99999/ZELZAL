#!/bin/bash
#
# ZELZAL v5.0 - Kali Linux Installation Script
# Installs all dependencies, sets up symlinks, and creates desktop entry
#
# Usage:
#   chmod +x install.sh
#   sudo ./install.sh
#

set -e

VERSION="5.0"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
cat << "EOF"
███████╗███████╗██╗     ███████╗ █████╗ ██╗
╚══███╔╝╚══███╔╝██║     ██╔════╝██╔══██╗██║
  ███╔╝   ███╔╝ ██║     █████╗  ███████║██║
 ███╔╝   ███╔╝  ██║     ██╔══╝  ██╔══██║██║
███████╗███████╗███████╗███████╗██║  ██║███████╗
╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝
EOF
echo -e "${NC}"
echo -e "${CYAN}ZELZAL v${VERSION} Installer - Kali Linux Cybersecurity Toolkit${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Some features require root privileges.${NC}"
    echo -e "${YELLOW}    Consider re-running with: sudo ./install.sh${NC}"
    echo ""
fi

INSTALL_DIR="/opt/zelzal"
SYMLINK_PATH="/usr/local/bin/zelzal"

echo -e "${CYAN}[*] Installing ZELZAL to ${INSTALL_DIR}...${NC}"

if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi

cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/zelzal.py"
chmod +x "$INSTALL_DIR/core.py"

echo -e "${CYAN}[*] Installing Python dependencies...${NC}"
pip3 install -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || \
    apt-get install -y python3-pip python3-rich 2>/dev/null || \
    echo -e "${YELLOW}[!] Could not install Python packages. Run: pip3 install rich${NC}"

echo -e "${CYAN}[*] Installing system dependencies...${NC}"
REQUIRED_TOOLS=(
    nmap iptables iptables-persistent net-tools conntrack dnsutils
    wireguard-tools bridge-utils ethtool tcpdump whois
    clamav clamav-daemon lynis rkhunter auditd
    rfkill wireless-tools aircrack-ng speedtest-cli
    whois macchanger
)

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &>/dev/null && ! dpkg -l "$tool" &>/dev/null 2>&1; then
        echo -e "${YELLOW}[!] $tool not found, installing...${NC}"
        apt-get install -y "$tool" 2>/dev/null || true
    fi
done

echo -e "${CYAN}[*] Creating symlink...${NC}"
if [ -L "$SYMLINK_PATH" ] || [ -f "$SYMLINK_PATH" ]; then
    rm -f "$SYMLINK_PATH"
fi
ln -sf "$INSTALL_DIR/zelzal.py" "$SYMLINK_PATH"
chmod +x "$SYMLINK_PATH"

echo -e "${CYAN}[*] Creating desktop entry...${NC}"
cat > /usr/share/applications/zelzal.desktop << 'DESKTOP'
[Desktop Entry]
Name=ZELZAL Security Toolkit
Comment=Kali Linux Cybersecurity Toolkit
Exec=python3 /opt/zelzal/zelzal.py
Terminal=true
Type=Application
Categories=Security;System;
Icon=/opt/zelzal/icon.png
DESKTOP

echo -e "${CYAN}[*] Creating reports directory...${NC}"
mkdir -p "$INSTALL_DIR/reports"

echo -e "${CYAN}[*] Setting up log rotation...${NC}"
cat > /etc/logrotate.d/zelzal << 'LOGROTATE'
/opt/zelzal/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
LOGROTATE

echo ""
echo -e "${GREEN}[✓] ZELZAL v${VERSION} installed successfully!${NC}"
echo ""
echo -e "  Run:  ${CYAN}zelzal${NC}              (interactive menu)"
echo -e "  Run:  ${CYAN}zelzal --scan${NC}        (quick system scan)"
echo -e "  Run:  ${CYAN}zelzal --report${NC}      (full security report)"
echo ""
echo -e "${YELLOW}NOTE: Some features require root. Run with sudo for full functionality.${NC}"
