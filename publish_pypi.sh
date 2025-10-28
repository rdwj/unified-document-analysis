#!/bin/bash

# Script to build and publish the unified-document-analysis package to PyPI
# Usage:
#   ./publish_pypi.sh          # Publish to PyPI
#   ./publish_pypi.sh test     # Publish to TestPyPI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Determine target repository
if [ "$1" == "test" ]; then
    REPOSITORY="testpypi"
    REPOSITORY_URL="https://test.pypi.org/legacy/"
    echo "Publishing to TestPyPI..."
else
    REPOSITORY="pypi"
    REPOSITORY_URL="https://upload.pypi.org/legacy/"
    echo "Publishing to PyPI..."
fi

# Copy .pypirc to home directory if it exists in project
if [ -f ".pypirc" ]; then
    echo "Copying .pypirc to home directory..."
    cp .pypirc ~/.pypirc
    chmod 600 ~/.pypirc
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info src/*.egg-info

# Build the package
echo "Building package..."
python -m pip install --upgrade build
python -m build

# Check the distribution
echo "Checking package..."
python -m pip install --upgrade twine
python -m twine check dist/*

# Upload to PyPI
echo "Uploading to $REPOSITORY..."
if [ "$REPOSITORY" == "testpypi" ]; then
    python -m twine upload --repository testpypi dist/*
else
    python -m twine upload dist/*
fi

echo ""
echo "Package published successfully!"
echo ""
echo "To install, run:"
if [ "$REPOSITORY" == "testpypi" ]; then
    echo "  pip install --index-url https://test.pypi.org/simple/ unified-document-analysis"
else
    echo "  pip install unified-document-analysis"
fi
echo ""
echo "To install with specific frameworks:"
echo "  pip install unified-document-analysis[xml]"
echo "  pip install unified-document-analysis[docling]"
echo "  pip install unified-document-analysis[document]"
echo "  pip install unified-document-analysis[data]"
echo "  pip install unified-document-analysis[lightweight]"
echo "  pip install unified-document-analysis[all]"
