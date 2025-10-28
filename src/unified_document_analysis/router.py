"""
Smart file type detection and routing to appropriate analysis framework.
"""
import os
from pathlib import Path
from typing import Optional, Tuple
from .exceptions import UnsupportedFileTypeError


# Framework-specific extensions
XML_EXTENSIONS = {'.xml'}

DOCLING_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx',
    '.png', '.jpg', '.jpeg', '.tiff', '.bmp'
}

DATA_EXTENSIONS = {
    '.csv', '.parquet', '.db', '.sqlite', '.sqlite3',
    '.feather', '.hdf5', '.h5'
}

# Document framework handles code, text, and structured data files
DOCUMENT_EXTENSIONS = {
    # Programming languages
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.m', '.mm', '.sh', '.bash', '.zsh', '.fish', '.ps1',

    # Web technologies
    '.html', '.htm', '.css', '.scss', '.sass', '.less',
    '.vue', '.svelte', '.jsx', '.tsx',

    # Configuration and data formats
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',

    # Documentation
    '.md', '.markdown', '.rst', '.txt', '.tex', '.adoc',

    # Other
    '.sql', '.graphql', '.proto', '.thrift',
    '.dockerfile', '.containerfile',
    '.makefile', '.cmake',
    '.gitignore', '.dockerignore',
}

# Ambiguous extensions that could belong to multiple frameworks
AMBIGUOUS_EXTENSIONS = {
    '.json': ['document', 'data'],  # Could be config or data
    '.yaml': ['document', 'xml'],   # Could be config or data structure
    '.yml': ['document', 'xml'],    # Could be config or data structure
}


class FileRouter:
    """Routes files to appropriate analysis framework based on type detection."""

    @staticmethod
    def detect_framework(file_path: str, hint: Optional[str] = None) -> str:
        """
        Detect which framework should handle this file.

        Args:
            file_path: Path to the file
            hint: Optional framework hint ('xml', 'docling', 'document', 'data')

        Returns:
            Framework name: 'xml', 'docling', 'document', or 'data'

        Raises:
            UnsupportedFileTypeError: If file type is not supported
        """
        # If hint provided, validate and use it
        if hint:
            valid_hints = {'xml', 'docling', 'document', 'data'}
            if hint not in valid_hints:
                raise ValueError(
                    f"Invalid framework hint '{hint}'. "
                    f"Valid options: {', '.join(sorted(valid_hints))}"
                )
            return hint

        # Get file extension
        path = Path(file_path)
        extension = path.suffix.lower()

        if not extension:
            # No extension - default to document framework
            return 'document'

        # Check each framework's extensions
        if extension in XML_EXTENSIONS:
            return 'xml'

        if extension in DOCLING_EXTENSIONS:
            return 'docling'

        if extension in DATA_EXTENSIONS:
            return 'data'

        if extension in DOCUMENT_EXTENSIONS:
            return 'document'

        # Check ambiguous extensions
        if extension in AMBIGUOUS_EXTENSIONS:
            # Default to first option (usually document framework)
            return AMBIGUOUS_EXTENSIONS[extension][0]

        # Unknown extension - raise error
        raise UnsupportedFileTypeError(file_path, extension)

    @staticmethod
    def get_confidence(file_path: str, framework: str) -> float:
        """
        Get confidence score (0.0-1.0) for routing decision.

        Args:
            file_path: Path to the file
            framework: Detected framework name

        Returns:
            Confidence score between 0.0 and 1.0
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        # High confidence for unambiguous extensions
        if framework == 'xml' and extension in XML_EXTENSIONS:
            return 1.0

        if framework == 'docling' and extension in DOCLING_EXTENSIONS:
            return 1.0

        if framework == 'data' and extension in DATA_EXTENSIONS:
            return 1.0

        if framework == 'document' and extension in DOCUMENT_EXTENSIONS:
            # Check if it's an ambiguous extension
            if extension in AMBIGUOUS_EXTENSIONS:
                return 0.7  # Medium confidence for ambiguous
            return 1.0

        # No extension - low confidence default
        if not extension:
            return 0.5

        # Unknown case
        return 0.3

    @staticmethod
    def get_framework_module_path(framework: str) -> str:
        """
        Get the module import path for a framework.

        Args:
            framework: Framework name ('xml', 'docling', 'document', 'data')

        Returns:
            Module path string
        """
        module_mapping = {
            'xml': 'xml_analysis_framework',
            'docling': 'docling_analysis_framework',
            'document': 'document_analysis_framework',
            'data': 'data_analysis_framework'
        }
        return module_mapping.get(framework, framework)

    @staticmethod
    def get_supported_extensions(framework: Optional[str] = None) -> dict:
        """
        Get supported extensions, optionally filtered by framework.

        Args:
            framework: Optional framework name to filter by

        Returns:
            Dictionary mapping framework names to extension sets
        """
        all_extensions = {
            'xml': XML_EXTENSIONS,
            'docling': DOCLING_EXTENSIONS,
            'document': DOCUMENT_EXTENSIONS,
            'data': DATA_EXTENSIONS,
        }

        if framework:
            return {framework: all_extensions.get(framework, set())}

        return all_extensions

    @staticmethod
    def is_ambiguous(file_path: str) -> Tuple[bool, list]:
        """
        Check if a file extension is ambiguous (could belong to multiple frameworks).

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_ambiguous: bool, possible_frameworks: list)
        """
        extension = Path(file_path).suffix.lower()

        if extension in AMBIGUOUS_EXTENSIONS:
            return True, AMBIGUOUS_EXTENSIONS[extension]

        return False, []
