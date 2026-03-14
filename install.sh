#!/bin/bash
# ============================================================
#  m7bla — Business Logic Abuse Framework
#  Installer for Kali Linux / Debian
#  Author: Sharlix | Milkyway Intelligence
# ============================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
DIM='\033[2m'
RESET='\033[0m'
BOLD='\033[1m'

INSTALL_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

banner() {
echo -e "${GREEN}"
cat << 'EOF'
  #     #  #####  ____  _        _
  ##   ## #     # |  _ \| |      / \
  # # # # #     # | |_) | |     / _ \
  #  #  #  #####  |  _ <| |___ / ___ \
  #     # #     # | |_) | ____/ /   \ \
  #     #  #####  |____/|_____/_/     \_\
         M  7  B  L  A
EOF
echo -e "${RESET}"
echo -e "  ${CYAN}Business Logic Abuse Framework${RESET} — ${DIM}Milkyway Intelligence${RESET}"
echo -e "  ${DIM}Author: Sharlix  |  For authorized testing only${RESET}"
echo ""
}

info()    { echo -e "  ${CYAN}[*]${RESET} $1"; }
success() { echo -e "  ${GREEN}[v]${RESET} $1"; }
warn()    { echo -e "  ${YELLOW}[!]${RESET} $1"; }
error()   { echo -e "  ${RED}[x]${RESET} $1"; exit 1; }

banner

info "Checking Python version..."
python3 -c "import sys; assert sys.version_info >= (3,8), 'Python 3.8+ required'" \
  || error "Python 3.8+ required."
PY_VER=$(python3 --version)
success "$PY_VER detected"

info "Checking pip..."
if ! command -v pip3 &>/dev/null; then
  sudo apt-get install -y python3-pip -qq
fi
success "pip3 ready"

info "Installing Python dependencies..."
pip3 install --break-system-packages -q httpx rich 2>/dev/null \
  || pip3 install -q httpx rich 2>/dev/null \
  || warn "pip install failed — install httpx and rich manually"
success "Dependencies installed"

info "Setting up directories..."
mkdir -p "$INSTALL_DIR/reports"
success "reports/ directory ready"

info "Creating launcher script..."
cat > "$INSTALL_DIR/m7bla" << LAUNCHER
#!/bin/bash
SCRIPT_DIR="\$(cd "\$(dirname "\$(readlink -f "\$0")")" && pwd)"
export PYTHONPATH="\$SCRIPT_DIR:\$PYTHONPATH"
cd "\$SCRIPT_DIR"
python3 "\$SCRIPT_DIR/cli/main.py" "\$@"
LAUNCHER

chmod +x "$INSTALL_DIR/m7bla"
chmod +x "$INSTALL_DIR/cli/main.py"
success "Launcher created: ./m7bla"

if ! grep -q "m7bla" ~/.bashrc 2>/dev/null; then
  echo "" >> ~/.bashrc
  echo "# m7bla — Milkyway Intelligence" >> ~/.bashrc
  echo "export PATH=\"\$PATH:${INSTALL_DIR}\"" >> ~/.bashrc
  success "Added to PATH in ~/.bashrc"
else
  success "PATH already configured"
fi

echo ""
echo -e "  ${GREEN}${BOLD}══════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}${BOLD}  m7bla installed successfully!${RESET}"
echo -e "  ${GREEN}${BOLD}══════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${DIM}Usage:${RESET}"
echo -e "    ${CYAN}./m7bla -t https://target.com${RESET}"
echo -e "    ${CYAN}./m7bla -t https://target.com --proxy http://127.0.0.1:8080${RESET}"
echo -e "    ${CYAN}./m7bla -t https://target.com --mode quick${RESET}"
echo -e "    ${CYAN}./m7bla --scenarios${RESET}"
echo ""
echo -e "  ${DIM}Modes:${RESET} full | quick | idor | payment | race | recharge | coupon | ratelimit"
echo ""
echo -e "  ${YELLOW}For authorized / lab testing only.${RESET}"
echo ""
