import pytest
from unittest.mock import Mock, patch, mock_open
from file_handlers import read_pdf, read_docx

def test_read_pdf():
    with patch('PyPDF2.PdfReader') as mock_pdf_reader:
        mock_pdf_reader.return_value.pages = [Mock(extract_text=lambda: "Test content")]
        result = read_pdf(mock_open(read_data=b"pdf content")())
    assert result == "Test content\n"

def test_read_docx():
    with patch('docx2txt.process', return_value="Test content"):
        result = read_docx(mock_open(read_data=b"docx content")())
    assert result == "Test content"

