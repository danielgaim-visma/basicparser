import re
from langdetect import detect

def norwegian_tokenize(text):
    text = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', '\n', text)
    return text.split('\n')

def is_complete_sentence(text):
    return re.search(r'[.!?]$', text.strip()) is not None

def detect_language(text):
    return detect(text)