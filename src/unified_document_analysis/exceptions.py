"""
Custom exceptions for unified-document-analysis.
"""


class UnifiedAnalysisError(Exception):
    """Base exception for unified analysis errors."""
    pass


class FrameworkNotInstalledError(UnifiedAnalysisError):
    """Raised when a required framework is not installed."""

    def __init__(self, framework_name: str, file_path: str):
        self.framework_name = framework_name
        self.file_path = file_path

        # Map framework names to pip install extras
        extra_mapping = {
            'xml': 'xml',
            'docling': 'docling',
            'document': 'document',
            'data': 'data'
        }

        extra = extra_mapping.get(framework_name, framework_name)

        message = (
            f"The '{framework_name}' framework is required to process '{file_path}' "
            f"but is not installed.\n\n"
            f"Install it with:\n"
            f"  pip install unified-document-analysis[{extra}]\n\n"
            f"Or install all frameworks:\n"
            f"  pip install unified-document-analysis[all]"
        )
        super().__init__(message)


class UnsupportedFileTypeError(UnifiedAnalysisError):
    """Raised when a file type is not supported by any framework."""

    def __init__(self, file_path: str, extension: str):
        self.file_path = file_path
        self.extension = extension

        message = (
            f"Unsupported file type '{extension}' for file '{file_path}'.\n\n"
            f"Supported file types:\n"
            f"  - XML: .xml\n"
            f"  - PDF/Office: .pdf, .docx, .pptx, .xlsx\n"
            f"  - Images: .png, .jpg, .jpeg, .tiff\n"
            f"  - Data: .csv, .parquet, .db, .sqlite\n"
            f"  - Code/Documents: .py, .js, .ts, .md, .txt, .yaml, .json, etc.\n\n"
            f"If you believe this file should be supported, you can specify a framework hint:\n"
            f"  analyze('{file_path}', framework_hint='document')"
        )
        super().__init__(message)


class AnalysisError(UnifiedAnalysisError):
    """Raised when analysis fails."""

    def __init__(self, file_path: str, framework_name: str, original_error: Exception):
        self.file_path = file_path
        self.framework_name = framework_name
        self.original_error = original_error

        message = (
            f"Failed to analyze '{file_path}' using '{framework_name}' framework.\n"
            f"Error: {type(original_error).__name__}: {str(original_error)}"
        )
        super().__init__(message)


class ChunkingError(UnifiedAnalysisError):
    """Raised when chunking fails."""

    def __init__(self, file_path: str, framework_name: str, original_error: Exception):
        self.file_path = file_path
        self.framework_name = framework_name
        self.original_error = original_error

        message = (
            f"Failed to chunk '{file_path}' using '{framework_name}' framework.\n"
            f"Error: {type(original_error).__name__}: {str(original_error)}"
        )
        super().__init__(message)
