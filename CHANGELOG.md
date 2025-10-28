# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-27

### Added
- Initial release of unified-document-analysis
- Single entry point for all document analysis frameworks
- Automatic file type detection and routing
- Lazy loading of framework dependencies
- Support for 4 specialized frameworks:
  - xml-analysis-framework for XML files
  - docling-analysis-framework for PDFs, Office docs, images
  - document-analysis-framework for code and text files
  - data-analysis-framework for CSV, Parquet, databases
- UnifiedAnalyzer class with comprehensive API
- Module-level convenience functions (analyze, chunk, get_available_frameworks)
- Smart routing with confidence scoring
- Ambiguous file type handling (e.g., .json can be document or data)
- Optional dependency groups:
  - Individual: [xml], [docling], [document], [data]
  - Lightweight: [lightweight] (xml + document)
  - All: [all]
- Helpful error messages with installation instructions
- Framework detection and information methods
- Support for 60+ file extensions
- Comprehensive test suite
- Full documentation and examples

### Features
- **Lazy Loading**: Frameworks only imported when needed
- **Automatic Routing**: File extension-based framework detection
- **Flexible Installation**: Install only needed frameworks
- **Error Handling**: Clear messages when frameworks missing
- **Framework Hints**: Override detection for ambiguous files
- **Discovery API**: Check installed frameworks and supported extensions

### Documentation
- Comprehensive README with examples
- API reference documentation
- Framework routing table
- Installation instructions
- Error handling guide
- Contributing guidelines

[1.0.0]: https://github.com/rdwj/unified-document-analysis/releases/tag/v1.0.0
