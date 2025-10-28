# Unified Document Analysis

A thin wrapper providing a single entry point for all document analysis frameworks with automatic routing based on file type.

## Overview

This package provides a unified interface for analyzing any document type by automatically routing files to the appropriate specialized framework:

- **xml-analysis-framework** - For XML files (S1000D, DITA, etc.)
- **docling-analysis-framework** - For PDFs, Office documents, and images
- **document-analysis-framework** - For code, text, and configuration files
- **data-analysis-framework** - For CSV, Parquet, databases, and data files

## Why Use This?

Instead of learning and managing 4 different frameworks, you get:

- **Single API** - One `analyze()` and `chunk()` function for everything
- **Automatic routing** - File type detection happens automatically
- **Lazy loading** - Only loads frameworks when needed
- **Minimal dependencies** - Install only what you need via optional dependencies
- **Helpful errors** - Clear messages when frameworks are missing

## Installation

Install the base package:

```bash
pip install unified-document-analysis
```

Then install the frameworks you need:

```bash
# Individual frameworks
pip install unified-document-analysis[xml]
pip install unified-document-analysis[docling]
pip install unified-document-analysis[document]
pip install unified-document-analysis[data]

# Lightweight set (xml + document, no heavy dependencies)
pip install unified-document-analysis[lightweight]

# Everything
pip install unified-document-analysis[all]
```

## Quick Start

### Basic Usage

```python
from unified_document_analysis import analyze, chunk

# Analyze any file - automatically detects type and routes to correct framework
result = analyze('technical_manual.xml')
result = analyze('report.pdf')
result = analyze('data.csv')
result = analyze('config.py')

# Chunk the file
chunks = chunk('report.pdf', result, strategy="semantic")
```

### Using the UnifiedAnalyzer Class

```python
from unified_document_analysis import UnifiedAnalyzer

analyzer = UnifiedAnalyzer()

# Check what's installed
print(analyzer.get_available_frameworks())
# Output: ['xml', 'document', 'data']

# Detect framework for a file (without analyzing)
info = analyzer.detect_framework_for_file('document.json')
print(f"Framework: {info['framework']}, Confidence: {info['confidence']}")

# Analyze with optional framework hint (for ambiguous files)
result = analyzer.analyze('ambiguous.json', framework_hint='data')

# Get framework information
info = analyzer.get_framework_info('xml')
print(f"Installed: {info['installed']}")
print(f"Extensions: {info['extensions']}")
```

### Advanced Features

```python
from unified_document_analysis import (
    UnifiedAnalyzer,
    get_available_frameworks,
    get_supported_extensions,
    detect_framework_for_file
)

# Check what frameworks are installed
frameworks = get_available_frameworks()
print(f"Available: {frameworks}")

# Get all supported extensions
all_exts = get_supported_extensions()
print(f"XML extensions: {all_exts['xml']}")
print(f"Docling extensions: {all_exts['docling']}")

# Detect framework for a file
info = detect_framework_for_file('document.yaml')
if info['is_ambiguous']:
    print(f"Ambiguous file. Alternatives: {info['alternatives']}")
```

## Framework Routing Table

| File Type | Extensions | Framework Used |
|-----------|-----------|----------------|
| **XML** | `.xml` | xml-analysis-framework |
| **PDFs** | `.pdf` | docling-analysis-framework |
| **Office** | `.docx`, `.pptx`, `.xlsx` | docling-analysis-framework |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp` | docling-analysis-framework |
| **Data** | `.csv`, `.parquet`, `.db`, `.sqlite` | data-analysis-framework |
| **Code** | `.py`, `.js`, `.ts`, `.java`, `.c`, etc. | document-analysis-framework |
| **Text** | `.md`, `.txt`, `.rst`, `.tex` | document-analysis-framework |
| **Config** | `.json`, `.yaml`, `.toml`, `.ini` | document-analysis-framework |

### Ambiguous File Types

Some extensions could belong to multiple frameworks. By default:
- `.json` → document-analysis-framework (confidence: 0.7)
- `.yaml`/`.yml` → document-analysis-framework (confidence: 0.7)

Use `framework_hint` to override:

```python
# Treat JSON as data instead of document
result = analyze('data.json', framework_hint='data')
```

## API Reference

### Main Functions

#### `analyze(file_path, framework_hint=None, **kwargs)`

Analyze any supported file type.

**Args:**
- `file_path` (str): Path to file to analyze
- `framework_hint` (str, optional): Force specific framework ('xml', 'docling', 'document', 'data')
- `**kwargs`: Additional arguments passed to framework's analyze method

**Returns:** Analysis result from appropriate framework

**Raises:**
- `FrameworkNotInstalledError`: If required framework is not installed
- `UnsupportedFileTypeError`: If file type is not supported
- `AnalysisError`: If analysis fails

#### `chunk(file_path, analysis_result, strategy="auto", framework_hint=None, **kwargs)`

Chunk a file based on its analysis result.

**Args:**
- `file_path` (str): Path to file to chunk
- `analysis_result`: Analysis result from `analyze()`
- `strategy` (str): Chunking strategy (framework-specific)
- `framework_hint` (str, optional): Force specific framework
- `**kwargs`: Additional arguments passed to framework's chunk method

**Returns:** List of chunks from appropriate framework

#### `get_available_frameworks()`

Get list of installed frameworks.

**Returns:** List of framework names (e.g., `['xml', 'document']`)

#### `detect_framework_for_file(file_path, hint=None)`

Detect which framework would be used for a file.

**Returns:** Dictionary with:
- `framework`: Detected framework name
- `confidence`: Confidence score (0.0-1.0)
- `is_ambiguous`: Whether file type is ambiguous
- `alternatives`: List of alternative frameworks for ambiguous types
- `installed`: Whether framework is installed

### UnifiedAnalyzer Class

#### Methods

- `analyze(file_path, framework_hint=None, **kwargs)` - Analyze a file
- `chunk(file_path, analysis_result, strategy="auto", **kwargs)` - Chunk a file
- `get_available_frameworks()` - Get installed frameworks
- `get_framework_info(framework_name)` - Get framework details
- `detect_framework_for_file(file_path, hint=None)` - Detect framework
- `get_supported_extensions(framework=None)` - Get supported extensions

## Error Handling

The package provides helpful error messages:

### Framework Not Installed

```python
# If you try to analyze a PDF but docling framework is not installed
try:
    result = analyze('document.pdf')
except FrameworkNotInstalledError as e:
    print(e)
    # Output:
    # The 'docling' framework is required to process 'document.pdf'
    # but is not installed.
    #
    # Install it with:
    #   pip install unified-document-analysis[docling]
    #
    # Or install all frameworks:
    #   pip install unified-document-analysis[all]
```

### Unsupported File Type

```python
try:
    result = analyze('document.unknown')
except UnsupportedFileTypeError as e:
    print(e)
    # Provides list of all supported file types
```

## When to Use What

### Use `unified-document-analysis` when:
- You're building an application that needs to handle multiple file types
- You want a simple API that "just works"
- You want to minimize dependencies by installing only needed frameworks
- You're prototyping and want quick file analysis

### Use individual frameworks when:
- You only need one framework (e.g., only XML files)
- You need advanced framework-specific features
- You want maximum control over configuration

## How It Works

### Lazy Loading

Frameworks are only imported when needed:

```python
# Only imports base package (lightweight)
from unified_document_analysis import analyze

# Framework only loaded when analyze() is called
result = analyze('document.pdf')  # Now docling is imported
```

### Smart Routing

The router examines file extensions and routes to the appropriate framework:

1. Get file extension
2. Look up extension in routing table
3. Dynamically import framework module
4. Call framework's analyze/chunk methods
5. Return results

### Optional Dependencies

```toml
[project.optional-dependencies]
xml = ["xml-analysis-framework>=2.0.0"]
docling = ["docling-analysis-framework>=2.0.0"]
document = ["document-analysis-framework>=2.0.0"]
data = ["data-analysis-framework>=2.0.0"]
```

## Examples

### Multi-Format Document Pipeline

```python
from unified_document_analysis import analyze, chunk

def process_documents(file_paths):
    """Process multiple document types in a single pipeline."""
    results = []

    for path in file_paths:
        # Analyze (auto-routes to correct framework)
        analysis = analyze(path)

        # Chunk (uses same framework)
        chunks = chunk(path, analysis, strategy="semantic")

        results.append({
            'path': path,
            'analysis': analysis,
            'chunks': chunks
        })

    return results

# Works with any mix of file types
files = [
    'manual.xml',
    'report.pdf',
    'data.csv',
    'config.py'
]

results = process_documents(files)
```

### Check Before Processing

```python
from unified_document_analysis import detect_framework_for_file, get_available_frameworks

def can_process_file(file_path):
    """Check if a file can be processed with installed frameworks."""
    info = detect_framework_for_file(file_path)
    available = get_available_frameworks()

    if not info['installed']:
        print(f"Cannot process {file_path}: {info['framework']} framework not installed")
        return False

    if info['is_ambiguous']:
        print(f"Ambiguous file type. Will use {info['framework']} framework.")
        print(f"Alternatives: {info['alternatives']}")

    return True

# Check before processing
if can_process_file('document.json'):
    result = analyze('document.json')
```

### Custom Framework Selection

```python
from unified_document_analysis import UnifiedAnalyzer

analyzer = UnifiedAnalyzer()

# Override automatic detection for JSON data files
json_files = ['data1.json', 'data2.json']

for file_path in json_files:
    # Force data framework instead of document framework
    result = analyzer.analyze(file_path, framework_hint='data')
    print(f"Processed {file_path} as data")
```

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

Repository: https://github.com/rdwj/unified-document-analysis

## License

Apache License 2.0

## Related Projects

- [analysis-framework-base](https://github.com/rdwj/analysis-framework-base) - Base interfaces and types
- [xml-analysis-framework](https://github.com/rdwj/xml-analysis-framework) - XML document analysis
- [docling-analysis-framework](https://github.com/rdwj/docling-analysis-framework) - PDF/Office analysis
- [document-analysis-framework](https://github.com/rdwj/document-analysis-framework) - Code/text analysis
- [data-analysis-framework](https://github.com/rdwj/data-analysis-framework) - Data file analysis

## Support

For issues, questions, or contributions, please visit:
https://github.com/rdwj/unified-document-analysis/issues
