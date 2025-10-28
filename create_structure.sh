#!/bin/bash

# Create unified-document-analysis package structure

BASE_DIR="/Users/wjackson/Developer/AI-Building-Blocks/unified-document-analysis"

# Create main directories
mkdir -p "$BASE_DIR/src/unified_document_analysis"
mkdir -p "$BASE_DIR/tests"

# Create __init__.py files
touch "$BASE_DIR/src/unified_document_analysis/__init__.py"
touch "$BASE_DIR/tests/__init__.py"

echo "Directory structure created successfully"
