#!/usr/bin/env bash
# ==============================================================================
# Kewargen VCF QR Code Runner Script (Mac / Linux)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet
    echo "Installing required dependencies (segno)..."
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet
    echo "Environment setup complete!"
fi

# Run the generator passing all CLI arguments
"$VENV_DIR/bin/python3" "$SCRIPT_DIR/vcf_qr_generator.py" "$@"

