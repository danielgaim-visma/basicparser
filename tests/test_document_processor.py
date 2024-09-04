import json
from unittest.mock import Mock, MagicMock, patch
from document_processor import process_file

def test_process_file():
    mock_client = Mock()
    mock_file = Mock()
    mock_file.name = "test.txt"
    mock_file.type = "text/plain"
    mock_file.read.return_value = b"This is a test sentence. This is another test sentence."

    with patch('document_processor.detect_language', return_value='no'), \
         patch('document_processor.norwegian_tokenize', return_value=["This is a test sentence.", "This is another test sentence."]), \
         patch('document_processor.is_complete_sentence', return_value=True), \
         patch('document_processor.generate_hr_section_title', return_value="Test Title") as mock_title, \
         patch('document_processor.extract_hr_keywords', return_value=["keyword1", "keyword2"]) as mock_keywords, \
         patch('document_processor.categorize_hr_document', return_value="Test Category") as mock_category, \
         patch('document_processor.extract_hr_entities', return_value={"entities": []}) as mock_entities, \
         patch('document_processor.analyze_hr_sentiment', return_value={"sentiment": "positive"}) as mock_sentiment, \
         patch('document_processor.extract_sentiment_keywords', return_value=["positive1", "positive2"]) as mock_sentiment_keywords, \
         patch('document_processor.summarize_hr_text', return_value="Test Summary") as mock_summary:

        result = process_file(mock_file, mock_client)

    assert len(result) == 1
    processed_section = json.loads(result[0])
    assert processed_section["title"] == "Test Title"
    assert processed_section["body"] == "This is a test sentence. This is another test sentence."
    assert processed_section["tags"] == ["keyword1", "keyword2"]
    assert processed_section["category"] == "Test Category"
    assert processed_section["entities"] == {"entities": []}
    assert processed_section["sentiment"] == {"sentiment": "positive"}
    assert processed_section["sentiment_keywords"] == ["positive1", "positive2"]
    assert processed_section["summary"] == "Test Summary"
    assert processed_section["ref"] == "test.txt"

    # Check if all the mocked functions were called
    mock_title.assert_called_once()
    mock_keywords.assert_called_once()
    mock_category.assert_called_once()
    mock_entities.assert_called_once()
    mock_sentiment.assert_called_once()
    mock_sentiment_keywords.assert_called_once()
    mock_summary.assert_called_once()