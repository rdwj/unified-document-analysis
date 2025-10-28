"""
Unified Document Analysis Framework

A thin wrapper providing a single entry point for all document analysis frameworks
with automatic routing based on file type.

This package provides convenient access to:
- xml-analysis-framework for XML files
- docling-analysis-framework for PDFs, Office docs, and images
- document-analysis-framework for code and text files
- data-analysis-framework for CSV, Parquet, and databases

Example:
    Basic usage with automatic framework detection:

    >>> from unified_document_analysis import analyze, chunk
    >>>
    >>> # Analyze any file - automatically routes to correct framework
    >>> result = analyze('document.pdf')
    >>> result = analyze('data.csv')
    >>> result = analyze('config.xml')
    >>>
    >>> # Chunk with automatic routing
    >>> chunks = chunk('document.pdf', result, strategy="semantic")

    Using the UnifiedAnalyzer class:

    >>> from unified_document_analysis import UnifiedAnalyzer
    >>>
    >>> analyzer = UnifiedAnalyzer()
    >>>
    >>> # Check what's installed
    >>> print(analyzer.get_available_frameworks())
    ['xml', 'document', 'data']
    >>>
    >>> # Detect framework for a file
    >>> info = analyzer.detect_framework_for_file('document.json')
    >>> print(f"Will use: {info['framework']}")
    >>>
    >>> # Analyze with optional framework hint
    >>> result = analyzer.analyze('ambiguous.json', framework_hint='data')

Installation:
    # Install base package
    pip install unified-document-analysis

    # Install with specific frameworks
    pip install unified-document-analysis[xml]
    pip install unified-document-analysis[docling]
    pip install unified-document-analysis[document]
    pip install unified-document-analysis[data]

    # Install lightweight set (xml + document)
    pip install unified-document-analysis[lightweight]

    # Install all frameworks
    pip install unified-document-analysis[all]
"""

from .orchestrator import UnifiedAnalyzer
from .router import FileRouter
from .exceptions import (
    UnifiedAnalysisError,
    FrameworkNotInstalledError,
    UnsupportedFileTypeError,
    AnalysisError,
    ChunkingError,
)

__version__ = "1.0.0"
__all__ = [
    # Main API
    "analyze",
    "chunk",
    "get_available_frameworks",

    # Classes
    "UnifiedAnalyzer",
    "FileRouter",

    # Exceptions
    "UnifiedAnalysisError",
    "FrameworkNotInstalledError",
    "UnsupportedFileTypeError",
    "AnalysisError",
    "ChunkingError",
]


# Module-level convenience functions
_analyzer = None


def _get_analyzer() -> UnifiedAnalyzer:
    """Get or create the global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = UnifiedAnalyzer()
    return _analyzer


def analyze(file_path: str, framework_hint: str = None, **kwargs):
    """
    Analyze any supported file type.

    Convenience function that uses a global UnifiedAnalyzer instance.
    Automatically detects the file type and routes to the appropriate framework.

    Args:
        file_path: Path to the file to analyze
        framework_hint: Optional framework override ('xml', 'docling', 'document', 'data')
        **kwargs: Additional arguments passed to the framework's analyze method

    Returns:
        Analysis result from the appropriate framework

    Raises:
        FrameworkNotInstalledError: If the required framework is not installed
        UnsupportedFileTypeError: If the file type is not supported
        AnalysisError: If analysis fails

    Example:
        >>> from unified_document_analysis import analyze
        >>> result = analyze('document.pdf')
        >>> result = analyze('data.csv')
        >>> result = analyze('ambiguous.json', framework_hint='data')
    """
    analyzer = _get_analyzer()
    return analyzer.analyze(file_path, framework_hint=framework_hint, **kwargs)


def chunk(
    file_path: str,
    analysis_result,
    strategy: str = "auto",
    framework_hint: str = None,
    **kwargs
):
    """
    Chunk a file based on its analysis result.

    Convenience function that uses a global UnifiedAnalyzer instance.
    Uses the same framework that would be used for analysis.

    Args:
        file_path: Path to the file to chunk
        analysis_result: Analysis result from analyze()
        strategy: Chunking strategy (framework-specific, default: "auto")
        framework_hint: Optional framework override
        **kwargs: Additional arguments passed to the framework's chunk method

    Returns:
        List of chunks from the appropriate framework

    Raises:
        FrameworkNotInstalledError: If the required framework is not installed
        UnsupportedFileTypeError: If the file type is not supported
        ChunkingError: If chunking fails

    Example:
        >>> from unified_document_analysis import analyze, chunk
        >>> result = analyze('document.pdf')
        >>> chunks = chunk('document.pdf', result, strategy="semantic")
    """
    analyzer = _get_analyzer()
    return analyzer.chunk(
        file_path,
        analysis_result,
        strategy=strategy,
        framework_hint=framework_hint,
        **kwargs
    )


def get_available_frameworks():
    """
    Check which frameworks are currently installed.

    Returns:
        List of installed framework names

    Example:
        >>> from unified_document_analysis import get_available_frameworks
        >>> print(get_available_frameworks())
        ['xml', 'document', 'data']
    """
    analyzer = _get_analyzer()
    return analyzer.get_available_frameworks()


def get_framework_info(framework_name: str):
    """
    Get information about a specific framework.

    Args:
        framework_name: Name of the framework ('xml', 'docling', 'document', 'data')

    Returns:
        Dictionary with framework information

    Example:
        >>> from unified_document_analysis import get_framework_info
        >>> info = get_framework_info('xml')
        >>> print(info['installed'])
        True
    """
    analyzer = _get_analyzer()
    return analyzer.get_framework_info(framework_name)


def detect_framework_for_file(file_path: str, hint: str = None):
    """
    Detect which framework would be used for a file.

    Args:
        file_path: Path to the file
        hint: Optional framework hint

    Returns:
        Dictionary with detection information

    Example:
        >>> from unified_document_analysis import detect_framework_for_file
        >>> info = detect_framework_for_file('document.json')
        >>> print(f"Framework: {info['framework']}")
        Framework: document
    """
    analyzer = _get_analyzer()
    return analyzer.detect_framework_for_file(file_path, hint=hint)


def get_supported_extensions(framework: str = None):
    """
    Get all supported file extensions.

    Args:
        framework: Optional framework name to filter by

    Returns:
        Dictionary mapping framework names to lists of extensions

    Example:
        >>> from unified_document_analysis import get_supported_extensions
        >>> all_exts = get_supported_extensions()
        >>> xml_exts = get_supported_extensions('xml')
    """
    analyzer = _get_analyzer()
    return analyzer.get_supported_extensions(framework=framework)
