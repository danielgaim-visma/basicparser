import json
import re
import os
import logging
from file_handlers import read_pdf, read_docx
from text_processing import detect_language
from hr_openai_utils import (
    extract_hr_keywords,
    categorize_hr_document,
    extract_hr_entities,
    summarize_hr_text,
    extract_sentiment_keywords
)

logger = logging.getLogger(__name__)


def extract_url(text):
    logger.info(f"Extracting URL from text: {text[:100].encode('unicode_escape').decode('utf-8')}")
    text = text.lstrip('\ufeff')
    url_pattern = r'(https?://[^\s]+)'
    match = re.search(url_pattern, text)
    if match:
        url = match.group(1)
        remaining_text = text[:match.start()] + text[match.end():]
        logger.info(f"Extracted URL: {url}")
        logger.info(f"Remaining text: {remaining_text[:100].encode('unicode_escape').decode('utf-8')}")
        return url, remaining_text.strip()
    logger.info("No URL found in text")
    return None, text.strip()


def clean_filename(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace('docx', '').strip()
    name = re.sub(r'[_-]', ' ', name)
    return ' '.join(word.capitalize() for word in name.split())


def process_file(file, client):
    try:
        if file.type == "text/plain":
            text = file.read().decode("utf-8")
        elif file.type == "application/pdf":
            text = read_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(file)
        else:
            raise ValueError("Filtypen støttes ikke.")

        logger.info(f"File content for {file.name} (first 100 characters): {text[:100].encode('unicode_escape').decode('utf-8')}")
        if not text.strip():
            logger.warning(f"File {file.name} is empty or contains only whitespace.")
            return None

        return structure_document(text, client, file.name)
    except Exception as e:
        logger.error(f"Error processing file {file.name}: {str(e)}", exc_info=True)
        return None


def structure_document(text, client, filename):
    lang = detect_language(text)
    logger.info(f"Detected language for {filename}: {lang}")
    if lang != 'no':
        logger.warning(f"Document {filename} appears to be in {lang}, not Norwegian. Results may be inaccurate.")

    logger.info(f"Original text (first 100 characters): {text[:100].encode('unicode_escape').decode('utf-8')}")
    url, text = extract_url(text)
    logger.info(f"Extracted URL for {filename}: {url}")
    logger.info(f"Processed text (first 100 characters): {text[:100].encode('unicode_escape').decode('utf-8')}")

    try:
        title = clean_filename(filename)
        keywords = extract_hr_keywords(text, client)
        category = categorize_hr_document(text, client)
        entities = extract_hr_entities(text, client)
        sentiment_keywords = extract_sentiment_keywords(text, client)
        logger.info(f"Sentiment keywords for {filename}: {sentiment_keywords}")
        summary = summarize_hr_text(text, client, max_words=200)

        document_data = {
            "title": title,
            "body": text.strip(),
            "summary": summary,
            "tags": keywords,
            "url": url,
            "category": category,
            "entities": entities if isinstance(entities, dict) else {"raw": entities},
            "positive": sentiment_keywords.get('positive', []) if isinstance(sentiment_keywords, dict) else [],
            "negative": sentiment_keywords.get('negative', []) if isinstance(sentiment_keywords, dict) else []
        }

        logger.info(f"Final document data for {filename}: {json.dumps(document_data, ensure_ascii=False, indent=2)}")
        return json.dumps(document_data, ensure_ascii=False)

