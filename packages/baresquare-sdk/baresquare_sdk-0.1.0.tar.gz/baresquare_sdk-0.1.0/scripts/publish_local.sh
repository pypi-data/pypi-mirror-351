#!/bin/bash
set -e

# Get absolute path to repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment from .env file"
  set -a  # automatically export all variables
  source .env
  set +a
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building and publishing: baresquare-sdk${NC}"

# Ask for confirmation
echo -e "Ready to build and publish baresquare-sdk to PyPI"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Publish canceled."
  exit 0
fi

# Check for PyPI credentials
if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
  echo -e "${RED}Error: TWINE_USERNAME and/or TWINE_PASSWORD environment variables not set.${NC}"
  exit 1
fi

# Install build dependencies
echo -e "${YELLOW}Installing build dependencies...${NC}"
pip install build twine

# Clean any previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist build *.egg-info

# Build the package
echo -e "${YELLOW}Building package...${NC}"
python -m build

# Check the built package
echo -e "${YELLOW}Checking built package...${NC}"
python -m twine check dist/*

# Upload to PyPI
echo -e "${YELLOW}Uploading to PyPI...${NC}"
python -m twine upload dist/*

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf dist build *.egg-info

echo -e "${GREEN}Package published successfully!${NC}"
echo -e "${GREEN}Users can now install with:${NC}"
echo -e "  ${YELLOW}pip install baresquare-sdk${NC}           # Core functionality"
echo -e "  ${YELLOW}pip install baresquare-sdk[aws]${NC}      # With AWS support"
echo -e "  ${YELLOW}pip install baresquare-sdk[dev]${NC}      # Development dependencies"