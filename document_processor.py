import json
import re
import os
from file_handlers import read_pdf, read_docx
from text_processing import norwegian_tokenize, is_complete_sentence, detect_language
from hr_openai_utils import (
    extract_hr_keywords,
    categorize_hr_document,
    extract_hr_entities,
    summarize_hr_text,
    extract_sentiment_keywords
)


def extract_url(text):
    url_match = re.match(r'^(https?://\S+)\s*([\s\S]*)', text.strip())
    if url_match:
        return url_match.group(1), url_match.group(2).strip()
    return None, text


def clean_filename(filename):
    # Remove file extension
    name = os.path.splitext(filename)[0]
    # Remove 'docx' if it's still present (for cases like 'file.name.docx')
    name = name.replace('docx', '').strip()
    # Replace underscores and hyphens with spaces
    name = re.sub(r'[_-]', ' ', name)
    # Capitalize the first letter of each word
    return ' '.join(word.capitalize() for word in name.split())


def process_file(file, client):
    if file.type == "text/plain":
        text = file.read().decode("utf-8")
    elif file.type == "application/pdf":
        text = read_pdf(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(file)
    else:
        raise ValueError("Filtypen støttes ikke.")

    return structure_document(text, client, file.name)


def structure_document(text, client, filename):
    lang = detect_language(text)
    if lang != 'no':
        print(f"Advarsel: Dokumentet ser ut til å være på {lang}, ikke norsk. Resultater kan være unøyaktige.")

    url, text = extract_url(text)

    try:
        title = clean_filename(filename)
        keywords = extract_hr_keywords(text, client)
        category = categorize_hr_document(text, client)
        entities = extract_hr_entities(text, client)
        tags2 = extract_sentiment_keywords(text, client)
        summary = summarize_hr_text(text, client)

        document_data = {
            "title": title,
            "body": text.strip(),
            "category": category,
            "entities": entities,
            "summary": summary,
        }

        if url:
            document_data["body"] += f"\n\nURL: \"{url}\""

        document_data["body"] += f"\n\nTags: {', '.join(keywords)}"

        if isinstance(tags2, dict) and 'positive' in tags2 and 'negative' in tags2:
            all_tags2 = tags2['positive'] + tags2['negative']
            document_data["body"] += f"\nTags2: {', '.join(all_tags2)}"
        else:
            document_data["body"] += "\nTags2: [Kunne ikke generere Tags2]"

        return json.dumps(document_data, ensure_ascii=False)
    except Exception as e:
        print(f"Error processing document {filename}: {str(e)}")
        return None