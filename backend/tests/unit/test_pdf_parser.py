from unittest.mock import MagicMock, patch

import pytest

from app.ai.ingestion.pdf_parser import PDFParser
from app.core.errors import AppError


def test_pdf_parser_success():
    mock_pdf_content = b"%PDF-1.4 mock content"
    
    with patch("app.ai.ingestion.pdf_parser.PdfReader") as MockPdfReader:
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content here."
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content here."
        
        mock_reader.pages = [mock_page1, mock_page2]
        MockPdfReader.return_value = mock_reader
        
        parser = PDFParser()
        result = parser.parse(mock_pdf_content)
        
        assert len(result) == 2
        assert result[0]["page_number"] == 1
        assert result[0]["text"] == "Page 1 content here."
        assert result[1]["page_number"] == 2
        assert result[1]["text"] == "Page 2 content here."

def test_pdf_parser_encrypted():
    mock_pdf_content = b"%PDF-1.4 mock content"
    
    with patch("app.ai.ingestion.pdf_parser.PdfReader") as MockPdfReader:
        mock_reader = MagicMock()
        mock_reader.is_encrypted = True
        MockPdfReader.return_value = mock_reader
        
        parser = PDFParser()
        with pytest.raises(AppError) as exc_info:
            parser.parse(mock_pdf_content)
            
        assert exc_info.value.status_code == 422
        assert "Encrypted PDFs are not supported" in exc_info.value.detail

def test_pdf_parser_scanned_no_text():
    mock_pdf_content = b"%PDF-1.4 mock content"
    
    with patch("app.ai.ingestion.pdf_parser.PdfReader") as MockPdfReader:
        mock_reader = MagicMock()
        mock_reader.is_encrypted = False
        
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "" # No text extracted
        
        mock_reader.pages = [mock_page1]
        MockPdfReader.return_value = mock_reader
        
        parser = PDFParser()
        with pytest.raises(AppError) as exc_info:
            parser.parse(mock_pdf_content)
            
        assert exc_info.value.status_code == 422
        assert "No extractable text found" in exc_info.value.detail
