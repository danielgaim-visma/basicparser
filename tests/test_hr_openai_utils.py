from unittest.mock import Mock, MagicMock
from hr_openai_utils import generate_hr_section_title, extract_hr_keywords

def test_generate_hr_section_title():
    mock_client = Mock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test Title"
    mock_client.chat.completions.create.return_value = mock_response

    result = generate_hr_section_title("Test text", mock_client)
    assert result == "Test Title"
    mock_client.chat.completions.create.assert_called_once()

def test_extract_hr_keywords():
    mock_client = Mock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "keyword1, keyword2, keyword3"
    mock_client.chat.completions.create.return_value = mock_response

    result = extract_hr_keywords("Test text", mock_client)
    assert result == ["keyword1", "keyword2", "keyword3"]
    mock_client.chat.completions.create.assert_called_once()