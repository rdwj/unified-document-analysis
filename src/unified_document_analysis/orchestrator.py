"""
Main UnifiedAnalyzer class that orchestrates routing and lazy loading of frameworks.
"""
import importlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from .router import FileRouter
from .exceptions import (
    FrameworkNotInstalledError,
    AnalysisError,
    ChunkingError
)


class UnifiedAnalyzer:
    """
    Unified document analyzer that automatically routes files to appropriate frameworks.

    This class provides a single entry point for analyzing any supported file type.
    It uses lazy loading to avoid importing heavy dependencies until they're needed,
    and provides helpful error messages when required frameworks are not installed.
    """

    def __init__(self):
        """Initialize the unified analyzer."""
        self._loaded_frameworks = {}
        self._router = FileRouter()

    def analyze(
        self,
        file_path: str,
        framework_hint: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Analyze any supported file type.

        This method automatically detects the file type and routes it to the
        appropriate analysis framework. Frameworks are loaded lazily only when needed.

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
            >>> analyzer = UnifiedAnalyzer()
            >>> result = analyzer.analyze('document.pdf')
            >>> result = analyzer.analyze('data.csv', framework_hint='data')
        """
        # Detect which framework to use
        framework_name = self._router.detect_framework(file_path, framework_hint)

        # Get confidence score for logging/debugging
        confidence = self._router.get_confidence(file_path, framework_name)

        # Load the framework
        framework = self._load_framework(framework_name, file_path)

        # Perform analysis
        try:
            result = framework.analyze(file_path, **kwargs)
            return result
        except Exception as e:
            raise AnalysisError(file_path, framework_name, e)

    def chunk(
        self,
        file_path: str,
        analysis_result: Any,
        strategy: str = "auto",
        framework_hint: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Chunk a file based on its analysis result.

        This method uses the same framework that was used for analysis (or the
        detected framework if analysis_result is from a different source).

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
            >>> analyzer = UnifiedAnalyzer()
            >>> result = analyzer.analyze('document.pdf')
            >>> chunks = analyzer.chunk('document.pdf', result, strategy="semantic")
        """
        # Detect which framework to use
        framework_name = self._router.detect_framework(file_path, framework_hint)

        # Load the framework
        framework = self._load_framework(framework_name, file_path)

        # Perform chunking
        try:
            chunks = framework.chunk(
                file_path,
                analysis_result,
                strategy=strategy,
                **kwargs
            )
            return chunks
        except Exception as e:
            raise ChunkingError(file_path, framework_name, e)

    def get_available_frameworks(self) -> List[str]:
        """
        Check which frameworks are currently installed.

        Returns:
            List of installed framework names

        Example:
            >>> analyzer = UnifiedAnalyzer()
            >>> print(analyzer.get_available_frameworks())
            ['xml', 'document', 'data']
        """
        frameworks = ['xml', 'docling', 'document', 'data']
        available = []

        for framework_name in frameworks:
            module_path = self._router.get_framework_module_path(framework_name)
            try:
                importlib.import_module(module_path)
                available.append(framework_name)
            except ImportError:
                continue

        return available

    def get_framework_info(self, framework_name: str) -> Dict[str, Any]:
        """
        Get information about a specific framework.

        Args:
            framework_name: Name of the framework ('xml', 'docling', 'document', 'data')

        Returns:
            Dictionary with framework information including:
                - installed: Whether the framework is installed
                - extensions: Supported file extensions
                - module_path: Python module path

        Example:
            >>> analyzer = UnifiedAnalyzer()
            >>> info = analyzer.get_framework_info('xml')
            >>> print(info['installed'])
            True
        """
        module_path = self._router.get_framework_module_path(framework_name)
        extensions = self._router.get_supported_extensions(framework_name)

        # Check if installed
        installed = False
        try:
            importlib.import_module(module_path)
            installed = True
        except ImportError:
            pass

        return {
            'name': framework_name,
            'installed': installed,
            'module_path': module_path,
            'extensions': list(extensions.get(framework_name, set())),
        }

    def detect_framework_for_file(
        self,
        file_path: str,
        hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect which framework would be used for a file without analyzing it.

        Args:
            file_path: Path to the file
            hint: Optional framework hint

        Returns:
            Dictionary with detection information:
                - framework: Detected framework name
                - confidence: Confidence score (0.0-1.0)
                - is_ambiguous: Whether the file type is ambiguous
                - alternatives: List of alternative frameworks for ambiguous types
                - installed: Whether the framework is installed

        Example:
            >>> analyzer = UnifiedAnalyzer()
            >>> info = analyzer.detect_framework_for_file('document.json')
            >>> print(f"Framework: {info['framework']}, Confidence: {info['confidence']}")
            Framework: document, Confidence: 0.7
        """
        framework_name = self._router.detect_framework(file_path, hint)
        confidence = self._router.get_confidence(file_path, framework_name)
        is_ambiguous, alternatives = self._router.is_ambiguous(file_path)

        # Check if framework is installed
        module_path = self._router.get_framework_module_path(framework_name)
        installed = False
        try:
            importlib.import_module(module_path)
            installed = True
        except ImportError:
            pass

        return {
            'framework': framework_name,
            'confidence': confidence,
            'is_ambiguous': is_ambiguous,
            'alternatives': alternatives,
            'installed': installed,
        }

    def _load_framework(self, framework_name: str, file_path: str) -> Any:
        """
        Lazy load a framework module.

        Args:
            framework_name: Name of the framework to load
            file_path: Path to file being processed (for error messages)

        Returns:
            Loaded framework module

        Raises:
            FrameworkNotInstalledError: If the framework is not installed
        """
        # Check if already loaded
        if framework_name in self._loaded_frameworks:
            return self._loaded_frameworks[framework_name]

        # Get module path
        module_path = self._router.get_framework_module_path(framework_name)

        # Try to import
        try:
            module = importlib.import_module(module_path)
            self._loaded_frameworks[framework_name] = module
            return module
        except ImportError:
            raise FrameworkNotInstalledError(framework_name, file_path)

    def get_supported_extensions(
        self,
        framework: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get all supported file extensions, optionally filtered by framework.

        Args:
            framework: Optional framework name to filter by

        Returns:
            Dictionary mapping framework names to lists of extensions

        Example:
            >>> analyzer = UnifiedAnalyzer()
            >>> all_exts = analyzer.get_supported_extensions()
            >>> xml_exts = analyzer.get_supported_extensions('xml')
        """
        extensions = self._router.get_supported_extensions(framework)
        # Convert sets to lists for JSON serialization
        return {
            fw: sorted(list(exts))
            for fw, exts in extensions.items()
        }
