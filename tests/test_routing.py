"""
Tests for file routing and framework detection.
"""
import pytest
from unified_document_analysis.router import FileRouter
from unified_document_analysis.exceptions import UnsupportedFileTypeError


class TestFileRouter:
    """Test the FileRouter class."""

    def test_xml_file_detection(self):
        """Test that .xml files route to xml framework."""
        router = FileRouter()
        framework = router.detect_framework('document.xml')
        assert framework == 'xml'

    def test_pdf_file_detection(self):
        """Test that .pdf files route to docling framework."""
        router = FileRouter()
        framework = router.detect_framework('document.pdf')
        assert framework == 'docling'

    def test_office_file_detection(self):
        """Test that Office files route to docling framework."""
        router = FileRouter()
        assert router.detect_framework('document.docx') == 'docling'
        assert router.detect_framework('presentation.pptx') == 'docling'
        assert router.detect_framework('spreadsheet.xlsx') == 'docling'

    def test_image_file_detection(self):
        """Test that image files route to docling framework."""
        router = FileRouter()
        assert router.detect_framework('image.png') == 'docling'
        assert router.detect_framework('photo.jpg') == 'docling'
        assert router.detect_framework('scan.jpeg') == 'docling'
        assert router.detect_framework('diagram.tiff') == 'docling'

    def test_data_file_detection(self):
        """Test that data files route to data framework."""
        router = FileRouter()
        assert router.detect_framework('data.csv') == 'data'
        assert router.detect_framework('data.parquet') == 'data'
        assert router.detect_framework('database.db') == 'data'
        assert router.detect_framework('database.sqlite') == 'data'

    def test_code_file_detection(self):
        """Test that code files route to document framework."""
        router = FileRouter()
        assert router.detect_framework('script.py') == 'document'
        assert router.detect_framework('app.js') == 'document'
        assert router.detect_framework('component.ts') == 'document'
        assert router.detect_framework('Main.java') == 'document'

    def test_config_file_detection(self):
        """Test that config files route to document framework."""
        router = FileRouter()
        assert router.detect_framework('config.json') == 'document'
        assert router.detect_framework('config.yaml') == 'document'
        assert router.detect_framework('settings.toml') == 'document'
        assert router.detect_framework('app.ini') == 'document'

    def test_markdown_file_detection(self):
        """Test that markdown files route to document framework."""
        router = FileRouter()
        assert router.detect_framework('README.md') == 'document'
        assert router.detect_framework('notes.txt') == 'document'

    def test_framework_hint_override(self):
        """Test that framework hints override detection."""
        router = FileRouter()
        # JSON normally goes to document, but can be overridden
        framework = router.detect_framework('data.json', hint='data')
        assert framework == 'data'

    def test_invalid_framework_hint(self):
        """Test that invalid hints raise ValueError."""
        router = FileRouter()
        with pytest.raises(ValueError, match="Invalid framework hint"):
            router.detect_framework('file.txt', hint='invalid')

    def test_unsupported_extension(self):
        """Test that unsupported extensions raise error."""
        router = FileRouter()
        with pytest.raises(UnsupportedFileTypeError):
            router.detect_framework('file.unknown')

    def test_no_extension_defaults_to_document(self):
        """Test that files without extensions default to document framework."""
        router = FileRouter()
        framework = router.detect_framework('Makefile')
        assert framework == 'document'

    def test_confidence_scoring(self):
        """Test confidence scores for different file types."""
        router = FileRouter()

        # High confidence for unambiguous extensions
        assert router.get_confidence('file.xml', 'xml') == 1.0
        assert router.get_confidence('file.pdf', 'docling') == 1.0
        assert router.get_confidence('file.csv', 'data') == 1.0

        # Medium confidence for ambiguous extensions
        assert router.get_confidence('file.json', 'document') == 0.7

        # Low confidence for no extension
        assert router.get_confidence('Makefile', 'document') == 0.5

    def test_ambiguous_file_detection(self):
        """Test detection of ambiguous file types."""
        router = FileRouter()

        # JSON is ambiguous
        is_amb, alts = router.is_ambiguous('data.json')
        assert is_amb is True
        assert 'document' in alts
        assert 'data' in alts

        # YAML is ambiguous
        is_amb, alts = router.is_ambiguous('config.yaml')
        assert is_amb is True

        # XML is not ambiguous
        is_amb, alts = router.is_ambiguous('file.xml')
        assert is_amb is False
        assert alts == []

    def test_get_framework_module_path(self):
        """Test that module paths are correct."""
        router = FileRouter()
        assert router.get_framework_module_path('xml') == 'xml_analysis_framework'
        assert router.get_framework_module_path('docling') == 'docling_analysis_framework'
        assert router.get_framework_module_path('document') == 'document_analysis_framework'
        assert router.get_framework_module_path('data') == 'data_analysis_framework'

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        router = FileRouter()

        # Get all extensions
        all_exts = router.get_supported_extensions()
        assert 'xml' in all_exts
        assert 'docling' in all_exts
        assert 'document' in all_exts
        assert 'data' in all_exts

        # Check specific framework extensions
        assert '.xml' in all_exts['xml']
        assert '.pdf' in all_exts['docling']
        assert '.csv' in all_exts['data']
        assert '.py' in all_exts['document']

    def test_get_supported_extensions_filtered(self):
        """Test getting extensions for specific framework."""
        router = FileRouter()

        # Get XML extensions only
        xml_exts = router.get_supported_extensions('xml')
        assert 'xml' in xml_exts
        assert '.xml' in xml_exts['xml']
        assert 'docling' not in xml_exts

    def test_case_insensitive_extension(self):
        """Test that extension matching is case-insensitive."""
        router = FileRouter()
        assert router.detect_framework('FILE.PDF') == 'docling'
        assert router.detect_framework('SCRIPT.PY') == 'document'
        assert router.detect_framework('DATA.CSV') == 'data'

    def test_containerfile_detection(self):
        """Test that Containerfile/Dockerfile route correctly."""
        router = FileRouter()
        # Files without extensions default to document
        assert router.detect_framework('Containerfile') == 'document'
        assert router.detect_framework('Dockerfile') == 'document'

    def test_common_programming_languages(self):
        """Test detection of various programming language files."""
        router = FileRouter()
        languages = [
            'script.py', 'app.js', 'component.ts', 'Main.java',
            'program.c', 'program.cpp', 'header.h', 'code.cs',
            'app.go', 'lib.rs', 'script.rb', 'page.php'
        ]
        for lang_file in languages:
            assert router.detect_framework(lang_file) == 'document'

    def test_multiple_dots_in_filename(self):
        """Test files with multiple dots in name."""
        router = FileRouter()
        assert router.detect_framework('my.config.json') == 'document'
        assert router.detect_framework('data.backup.csv') == 'data'
        assert router.detect_framework('report.final.pdf') == 'docling'
