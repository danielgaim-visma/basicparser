import pytest
from text_processing import norwegian_tokenize, is_complete_sentence, detect_language

def test_norwegian_tokenize():
    text = "Dette er en setning. Dette er en annen setning."
    result = norwegian_tokenize(text)
    assert result == ["Dette er en setning.", "Dette er en annen setning."]

def test_is_complete_sentence():
    assert is_complete_sentence("Dette er en komplett setning.")
    assert not is_complete_sentence("Dette er ikke en komplett")

def test_detect_language():
    assert detect_language("Dette er på norsk.") == "no"
    assert detect_language("This is in English.") == "en"

# Add more tests for text_processing.py functions