"""
Tests for custom exceptions.
"""
import pytest
from unified_document_analysis.exceptions import (
    UnifiedAnalysisError,
    FrameworkNotInstalledError,
    UnsupportedFileTypeError,
    AnalysisError,
    ChunkingError
)


class TestFrameworkNotInstalledError:
    """Test FrameworkNotInstalledError exception."""

    def test_error_message_xml(self):
        """Test error message for XML framework."""
        error = FrameworkNotInstalledError('xml', 'document.xml')
        message = str(error)

        assert 'xml' in message
        assert 'document.xml' in message
        assert 'pip install unified-document-analysis[xml]' in message
        assert 'pip install unified-document-analysis[all]' in message

    def test_error_message_docling(self):
        """Test error message for docling framework."""
        error = FrameworkNotInstalledError('docling', 'report.pdf')
        message = str(error)

        assert 'docling' in message
        assert 'report.pdf' in message
        assert 'pip install unified-document-analysis[docling]' in message

    def test_error_attributes(self):
        """Test that error has correct attributes."""
        error = FrameworkNotInstalledError('data', 'data.csv')

        assert error.framework_name == 'data'
        assert error.file_path == 'data.csv'


class TestUnsupportedFileTypeError:
    """Test UnsupportedFileTypeError exception."""

    def test_error_message(self):
        """Test error message content."""
        error = UnsupportedFileTypeError('file.unknown', '.unknown')
        message = str(error)

        assert 'file.unknown' in message
        assert '.unknown' in message
        assert 'Unsupported file type' in message

        # Should list supported types
        assert '.xml' in message
        assert '.pdf' in message
        assert '.csv' in message
        assert '.py' in message

    def test_error_attributes(self):
        """Test that error has correct attributes."""
        error = UnsupportedFileTypeError('test.xyz', '.xyz')

        assert error.file_path == 'test.xyz'
        assert error.extension == '.xyz'

    def test_framework_hint_suggestion(self):
        """Test that error suggests using framework hint."""
        error = UnsupportedFileTypeError('file.unknown', '.unknown')
        message = str(error)

        assert 'framework_hint' in message


class TestAnalysisError:
    """Test AnalysisError exception."""

    def test_error_message(self):
        """Test error message content."""
        original_error = ValueError("Invalid input")
        error = AnalysisError('document.pdf', 'docling', original_error)
        message = str(error)

        assert 'document.pdf' in message
        assert 'docling' in message
        assert 'ValueError' in message
        assert 'Invalid input' in message

    def test_error_attributes(self):
        """Test that error has correct attributes."""
        original_error = RuntimeError("Test error")
        error = AnalysisError('test.xml', 'xml', original_error)

        assert error.file_path == 'test.xml'
        assert error.framework_name == 'xml'
        assert error.original_error == original_error

    def test_preserves_original_error_type(self):
        """Test that original error type is preserved."""
        original_error = KeyError("missing_key")
        error = AnalysisError('data.csv', 'data', original_error)

        assert isinstance(error.original_error, KeyError)
        assert 'KeyError' in str(error)


class TestChunkingError:
    """Test ChunkingError exception."""

    def test_error_message(self):
        """Test error message content."""
        original_error = ValueError("Invalid chunk size")
        error = ChunkingError('document.pdf', 'docling', original_error)
        message = str(error)

        assert 'document.pdf' in message
        assert 'docling' in message
        assert 'ValueError' in message
        assert 'Invalid chunk size' in message

    def test_error_attributes(self):
        """Test that error has correct attributes."""
        original_error = RuntimeError("Chunking failed")
        error = ChunkingError('test.xml', 'xml', original_error)

        assert error.file_path == 'test.xml'
        assert error.framework_name == 'xml'
        assert error.original_error == original_error


class TestUnifiedAnalysisError:
    """Test base UnifiedAnalysisError exception."""

    def test_base_exception(self):
        """Test that base exception works."""
        error = UnifiedAnalysisError("Test error")
        assert str(error) == "Test error"

    def test_inheritance(self):
        """Test that all exceptions inherit from base."""
        assert issubclass(FrameworkNotInstalledError, UnifiedAnalysisError)
        assert issubclass(UnsupportedFileTypeError, UnifiedAnalysisError)
        assert issubclass(AnalysisError, UnifiedAnalysisError)
        assert issubclass(ChunkingError, UnifiedAnalysisError)

    def test_catching_base_exception(self):
        """Test that base exception can catch all specific exceptions."""
        errors = [
            FrameworkNotInstalledError('xml', 'test.xml'),
            UnsupportedFileTypeError('test.unknown', '.unknown'),
            AnalysisError('test.pdf', 'docling', ValueError()),
            ChunkingError('test.csv', 'data', RuntimeError())
        ]

        for error in errors:
            with pytest.raises(UnifiedAnalysisError):
                raise error
