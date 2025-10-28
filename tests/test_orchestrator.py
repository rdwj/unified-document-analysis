"""
Tests for UnifiedAnalyzer orchestrator.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from unified_document_analysis import UnifiedAnalyzer
from unified_document_analysis.exceptions import (
    FrameworkNotInstalledError,
    UnsupportedFileTypeError
)


class TestUnifiedAnalyzer:
    """Test the UnifiedAnalyzer class."""

    def test_initialization(self):
        """Test that UnifiedAnalyzer initializes correctly."""
        analyzer = UnifiedAnalyzer()
        assert analyzer._loaded_frameworks == {}
        assert analyzer._router is not None

    def test_detect_framework_for_file(self):
        """Test framework detection without analysis."""
        analyzer = UnifiedAnalyzer()

        # Test XML detection
        info = analyzer.detect_framework_for_file('document.xml')
        assert info['framework'] == 'xml'
        assert info['confidence'] == 1.0
        assert info['is_ambiguous'] is False

        # Test ambiguous file
        info = analyzer.detect_framework_for_file('data.json')
        assert info['framework'] == 'document'
        assert info['is_ambiguous'] is True
        assert 'data' in info['alternatives']

    def test_detect_framework_with_hint(self):
        """Test framework detection with hint."""
        analyzer = UnifiedAnalyzer()

        info = analyzer.detect_framework_for_file('data.json', hint='data')
        assert info['framework'] == 'data'

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        analyzer = UnifiedAnalyzer()

        # Get all extensions
        all_exts = analyzer.get_supported_extensions()
        assert 'xml' in all_exts
        assert 'docling' in all_exts
        assert 'document' in all_exts
        assert 'data' in all_exts

        # All should be lists (not sets)
        assert isinstance(all_exts['xml'], list)
        assert '.xml' in all_exts['xml']

    def test_get_supported_extensions_filtered(self):
        """Test getting extensions for specific framework."""
        analyzer = UnifiedAnalyzer()

        xml_exts = analyzer.get_supported_extensions('xml')
        assert 'xml' in xml_exts
        assert 'docling' not in xml_exts

    def test_get_framework_info(self):
        """Test getting framework information."""
        analyzer = UnifiedAnalyzer()

        info = analyzer.get_framework_info('xml')
        assert info['name'] == 'xml'
        assert info['module_path'] == 'xml_analysis_framework'
        assert isinstance(info['installed'], bool)
        assert isinstance(info['extensions'], list)
        assert '.xml' in info['extensions']

    @patch('importlib.import_module')
    def test_get_available_frameworks_none_installed(self, mock_import):
        """Test getting available frameworks when none are installed."""
        # Mock all imports to fail
        mock_import.side_effect = ImportError("Not installed")

        analyzer = UnifiedAnalyzer()
        available = analyzer.get_available_frameworks()
        assert available == []

    @patch('importlib.import_module')
    def test_get_available_frameworks_some_installed(self, mock_import):
        """Test getting available frameworks when some are installed."""
        # Mock xml and document as installed, others fail
        def import_side_effect(module_path):
            if module_path in ['xml_analysis_framework', 'document_analysis_framework']:
                return Mock()
            raise ImportError("Not installed")

        mock_import.side_effect = import_side_effect

        analyzer = UnifiedAnalyzer()
        available = analyzer.get_available_frameworks()
        assert 'xml' in available
        assert 'document' in available
        assert 'docling' not in available
        assert 'data' not in available

    @patch('importlib.import_module')
    def test_analyze_framework_not_installed(self, mock_import):
        """Test that analyzing with missing framework raises error."""
        mock_import.side_effect = ImportError("Not installed")

        analyzer = UnifiedAnalyzer()
        with pytest.raises(FrameworkNotInstalledError) as exc_info:
            analyzer.analyze('document.pdf')

        error = exc_info.value
        assert error.framework_name == 'docling'
        assert 'document.pdf' in str(error)
        assert 'pip install unified-document-analysis[docling]' in str(error)

    @patch('importlib.import_module')
    def test_analyze_success(self, mock_import):
        """Test successful analysis with mocked framework."""
        # Create a mock framework module
        mock_framework = Mock()
        mock_result = {'content': 'test content'}
        mock_framework.analyze = Mock(return_value=mock_result)
        mock_import.return_value = mock_framework

        analyzer = UnifiedAnalyzer()
        result = analyzer.analyze('document.xml')

        assert result == mock_result
        mock_framework.analyze.assert_called_once_with('document.xml')

    @patch('importlib.import_module')
    def test_analyze_with_kwargs(self, mock_import):
        """Test that kwargs are passed to framework."""
        mock_framework = Mock()
        mock_framework.analyze = Mock(return_value={})
        mock_import.return_value = mock_framework

        analyzer = UnifiedAnalyzer()
        analyzer.analyze('document.xml', custom_param='value')

        mock_framework.analyze.assert_called_once_with(
            'document.xml',
            custom_param='value'
        )

    @patch('importlib.import_module')
    def test_chunk_success(self, mock_import):
        """Test successful chunking with mocked framework."""
        mock_framework = Mock()
        mock_chunks = [{'text': 'chunk1'}, {'text': 'chunk2'}]
        mock_framework.chunk = Mock(return_value=mock_chunks)
        mock_import.return_value = mock_framework

        analyzer = UnifiedAnalyzer()
        analysis_result = {'content': 'test'}
        chunks = analyzer.chunk('document.xml', analysis_result, strategy='semantic')

        assert chunks == mock_chunks
        mock_framework.chunk.assert_called_once_with(
            'document.xml',
            analysis_result,
            strategy='semantic'
        )

    @patch('importlib.import_module')
    def test_framework_caching(self, mock_import):
        """Test that frameworks are cached after first load."""
        mock_framework = Mock()
        mock_framework.analyze = Mock(return_value={})
        mock_import.return_value = mock_framework

        analyzer = UnifiedAnalyzer()

        # First call should import
        analyzer.analyze('document1.xml')
        assert mock_import.call_count == 1

        # Second call should use cached framework
        analyzer.analyze('document2.xml')
        assert mock_import.call_count == 1  # Still 1, not 2

    def test_unsupported_file_type(self):
        """Test that unsupported file types raise error."""
        analyzer = UnifiedAnalyzer()

        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            analyzer.analyze('file.unknown')

        error = exc_info.value
        assert 'file.unknown' in str(error)
        assert '.unknown' in str(error)


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @patch('unified_document_analysis.UnifiedAnalyzer')
    def test_analyze_function(self, mock_analyzer_class):
        """Test that analyze() uses UnifiedAnalyzer correctly."""
        from unified_document_analysis import analyze

        mock_analyzer = Mock()
        mock_analyzer.analyze = Mock(return_value={'test': 'result'})
        mock_analyzer_class.return_value = mock_analyzer

        # Reset the global analyzer
        import unified_document_analysis
        unified_document_analysis._analyzer = None

        result = analyze('test.xml', framework_hint='xml', param='value')

        # Should create analyzer and call its analyze method
        # Note: The global analyzer is created on first call
        assert result == {'test': 'result'}

    @patch('unified_document_analysis.UnifiedAnalyzer')
    def test_chunk_function(self, mock_analyzer_class):
        """Test that chunk() uses UnifiedAnalyzer correctly."""
        from unified_document_analysis import chunk

        mock_analyzer = Mock()
        mock_analyzer.chunk = Mock(return_value=[{'chunk': '1'}])
        mock_analyzer_class.return_value = mock_analyzer

        # Reset the global analyzer
        import unified_document_analysis
        unified_document_analysis._analyzer = None

        analysis = {'test': 'data'}
        result = chunk('test.xml', analysis, strategy='semantic')

        assert result == [{'chunk': '1'}]

    @patch('unified_document_analysis.UnifiedAnalyzer')
    def test_get_available_frameworks_function(self, mock_analyzer_class):
        """Test that get_available_frameworks() works correctly."""
        from unified_document_analysis import get_available_frameworks

        mock_analyzer = Mock()
        mock_analyzer.get_available_frameworks = Mock(return_value=['xml', 'document'])
        mock_analyzer_class.return_value = mock_analyzer

        # Reset the global analyzer
        import unified_document_analysis
        unified_document_analysis._analyzer = None

        result = get_available_frameworks()

        assert result == ['xml', 'document']
