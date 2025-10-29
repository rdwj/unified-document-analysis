#!/bin/bash

# Create document-analysis-service directory structure

# Navigate to parent directory
cd /Users/wjackson/Developer/AI-Building-Blocks

# Create main project directory
mkdir -p document-analysis-service

cd document-analysis-service

# Create main directory structure
mkdir -p src/api
mkdir -p src/mcp
mkdir -p src/core
mkdir -p src/utils
mkdir -p tests
mkdir -p manifests/base
mkdir -p manifests/overlays/dev
mkdir -p manifests/overlays/prod

# Create empty __init__.py files
touch src/__init__.py
touch src/api/__init__.py
touch src/mcp/__init__.py
touch src/core/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# Create placeholder files
touch src/api/rest.py
touch src/api/models.py
touch src/mcp/MCP_TOOLS_SPEC.md
touch src/core/analyzer.py
touch src/core/chunker.py
touch src/core/file_handler.py
touch src/utils/s3.py
touch src/main.py

# Create test files
touch tests/test_api.py
touch tests/test_core.py

# Create manifest files
touch manifests/base/deployment.yaml
touch manifests/base/service.yaml
touch manifests/base/route.yaml
touch manifests/base/configmap.yaml
touch manifests/base/kustomization.yaml
touch manifests/overlays/dev/kustomization.yaml
touch manifests/overlays/prod/kustomization.yaml

# Create other files
touch Containerfile
touch podman-compose.yml
touch pyproject.toml
touch README.md
touch .gitignore

echo "Directory structure created successfully in document-analysis-service/"
