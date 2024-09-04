import streamlit as st
import json
import io
import zipfile
from openai import OpenAI
import asyncio
import atexit
import time
import re
import os
import logging
from file_handlers import read_pdf, read_docx
from text_processing import norwegian_tokenize, is_complete_sentence, detect_language
from hr_openai_utils import (
    extract_hr_keywords,
    categorize_hr_document,
    extract_hr_entities,
    summarize_hr_text,
    extract_sentiment_keywords
)
from config import MAX_FILE_SIZE, OPENAI_MODEL, LOG_LEVEL, LOG_FILE
from custom_exceptions import FileProcessingError, APIError
from async_processors import process_file_async

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=getattr(logging, LOG_LEVEL),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_openai_api_key():
    api_key = st.sidebar.text_input("Skriv inn din OpenAI API-nøkkel", type="password")
    if api_key:
        return api_key
    else:
        st.sidebar.warning("Vennligst skriv inn din OpenAI API-nøkkel for å fortsette.")
        return None


def create_zip_file(all_results):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for original_filename, document_json in all_results.items():
            try:
                # Parse the JSON string to ensure it's valid
                document_data = json.loads(document_json)

                # Create a filename for this document
                document_filename = f"{original_filename}.json"

                # Convert the document data back to a JSON string
                document_content = json.dumps(document_data, ensure_ascii=False, indent=2)

                # Add the file to the ZIP archive
                zip_file.writestr(document_filename, document_content)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON for document {original_filename}")
            except Exception as e:
                logger.error(f"Error adding document {original_filename} to ZIP: {str(e)}")

    zip_buffer.seek(0)
    return zip_buffer


def cleanup():
    logger.info("Performing cleanup operations...")
    # Add any necessary cleanup operations here


def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}t {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def extract_url(text):
    lines = text.split('\n')
    for i, line in enumerate(lines[:5]):
        url_match = re.search(r'(https?://\S+)', line)
        if url_match:
            url = url_match.group(1)
            lines[i] = line.replace(url, '').strip()
            new_text = '\n'.join(line for line in lines if line.strip())
            return url, new_text
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
    try:
        if file.type == "text/plain":
            text = file.read().decode("utf-8")
        elif file.type == "application/pdf":
            text = read_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(file)
        else:
            raise ValueError("Filtypen støttes ikke.")

        logger.info(f"Filinnhold for {file.name}: {text[:100]}...")  # Log the first 100 characters
        if not text.strip():
            logger.warning(f"Filen {file.name} er tom eller inneholder bare whitespace.")
            return None

        return structure_document(text, client, file.name)
    except Exception as e:
        logger.error(f"Error processing file {file.name}: {str(e)}", exc_info=True)
        return None  # Return None instead of raising an exception


def structure_document(text, client, filename):
    lang = detect_language(text)
    logger.info(f"Detected language for {filename}: {lang}")
    if lang != 'no':
        logger.warning(f"Document {filename} appears to be in {lang}, not Norwegian. Results may be inaccurate.")

    url, text = extract_url(text)
    logger.info(f"Processing entire document: {filename}")

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
            "category": category,
            "entities": entities,
            "summary": summary,
            "tags": keywords,
            "url": url if url else None
        }

        if isinstance(sentiment_keywords, dict) and 'positive' in sentiment_keywords and 'negative' in sentiment_keywords:
            document_data["tags"].extend(sentiment_keywords['positive'] + sentiment_keywords['negative'])
            logger.info(f"Added sentiment keywords to tags for {filename}")
        else:
            logger.warning(f"Unexpected format for sentiment keywords in {filename}: {sentiment_keywords}")

        logger.info(f"Document processed successfully: {filename}")
        return json.dumps(document_data, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error processing document {filename}: {str(e)}", exc_info=True)
        return None

async def process_files(uploaded_files, api_key, progress_bar, status_text, file_overview, document_overview,
                        time_estimate):
    client = OpenAI(api_key=api_key)
    all_results = {}
    document_titles = []
    start_time = time.time()
    total_files = len(uploaded_files)

    for i, uploaded_file in enumerate(uploaded_files):
        try:
            file_start_time = time.time()
            status_text.text(f"Behandler fil {i + 1} av {total_files}: {uploaded_file.name}")
            logger.info(f"Processing file {i + 1} of {total_files}: {uploaded_file.name}")

            if uploaded_file.size > MAX_FILE_SIZE:
                raise FileProcessingError(f"File {uploaded_file.name} exceeds maximum size limit.")

            logger.info(f"File size of {uploaded_file.name}: {uploaded_file.size} bytes")

            document_json = process_file(uploaded_file, client)

            if document_json:
                all_results[uploaded_file.name] = document_json
                logger.info(f"Added results for {uploaded_file.name}")

                try:
                    document = json.loads(document_json)
                    title = document.get('title', f"Document: {uploaded_file.name}")
                    document_titles.append(f"{clean_filename(uploaded_file.name)}")
                    logger.info(f"Processed document: {uploaded_file.name}: {title}")
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON for document: {clean_filename(uploaded_file.name)}")
                    st.warning(f"Kunne ikke parse JSON for dokument: {clean_filename(uploaded_file.name)}")
                    document_titles.append(f"{clean_filename(uploaded_file.name)} - [Parsing Error]")
                except Exception as e:
                    logger.error(f"Error processing document: {clean_filename(uploaded_file.name)}: {str(e)}",
                                 exc_info=True)
                    st.warning(f"Feil ved behandling av dokument: {clean_filename(uploaded_file.name)}: {str(e)}")
                    document_titles.append(f"{clean_filename(uploaded_file.name)} - [Processing Error]")
            else:
                logger.warning(f"No content was generated for {uploaded_file.name}")
                document_titles.append(f"{clean_filename(uploaded_file.name)} - [Processing Failed]")

            # Update file overview
            file_status = {name: "Processed" if doc else "Failed" for name, doc in all_results.items()}
            file_overview.json(file_status)

            document_overview.text("Behandlede dokumenter:\n" + "\n".join(document_titles))

            await asyncio.sleep(0.1)

            progress_bar.progress((i + 1) / total_files)

            # Calculate and update time estimate
            elapsed_time = time.time() - start_time
            files_processed = i + 1
            if files_processed > 1:  # Avoid division by zero
                avg_time_per_file = elapsed_time / files_processed
                remaining_files = total_files - files_processed
                estimated_remaining_time = avg_time_per_file * remaining_files
                time_estimate.text(f"Estimert gjenværende tid: {format_time(estimated_remaining_time)} "
                                   f"({files_processed}/{total_files} filer behandlet)")
            else:
                time_estimate.text(f"Beregner estimert gjenværende tid... "
                                   f"({files_processed}/{total_files} filer behandlet)")

        except Exception as e:
            logger.error(f"Error processing file {uploaded_file.name}: {str(e)}", exc_info=True)
            st.error(f"Feil ved behandling av {uploaded_file.name}: {str(e)}")

    status_text.text(f"Alle {total_files} filer er behandlet.")
    progress_bar.empty()
    time_estimate.empty()

    logger.info(f"All files processed. Total results: {len(all_results)}")
    return all_results


async def main_async():
    st.title("GPT-4 Dokumentprosessor for Norsk - filoppdeling")

    api_key = get_openai_api_key()

    if api_key:
        uploaded_files = st.file_uploader("Velg filer", type=["txt", "pdf", "docx"], accept_multiple_files=True)

        start_processing = st.button("Start filbehandling")

        if start_processing:
            if not uploaded_files:
                st.error("Vennligst last opp filer før du starter behandlingen.")
            else:
                progress_placeholder = st.empty()
                status_placeholder = st.empty()
                file_overview_placeholder = st.empty()
                document_overview_placeholder = st.empty()
                time_estimate_placeholder = st.empty()

                with st.spinner("Forbereder behandling..."):
                    try:
                        logger.info(f"Starting processing of {len(uploaded_files)} files")
                        all_results = await process_files(
                            uploaded_files,
                            api_key,
                            progress_placeholder,
                            status_placeholder,
                            file_overview_placeholder,
                            document_overview_placeholder,
                            time_estimate_placeholder
                        )

                        logger.info(f"Processing complete. Results: {all_results}")

                        if all_results:
                            st.success(f"Behandlet {len(all_results)} dokument(er) vellykket.")

                            # Check if there are any documents in the results
                            total_documents = len(all_results)
                            logger.info(f"Total documents generated: {total_documents}")

                            if total_documents > 0:
                                zip_buffer = create_zip_file(all_results)
                                st.download_button(
                                    label=f"Last ned alle resultater ({total_documents} dokumenter) (ZIP)",
                                    data=zip_buffer,
                                    file_name="alle_dokumentresultater.zip",
                                    mime="application/zip"
                                )
                                logger.info("ZIP file created and download button displayed")
                            else:
                                st.warning("Ingen dokumenter ble generert fra de opplastede filene.")
                                logger.warning("No documents were generated from the uploaded files")
                        else:
                            st.warning("Ingen resultater ble generert fra de opplastede filene.")
                            logger.warning("No results were generated from the uploaded files")
                    except Exception as e:
                        logger.error(f"Error during file processing: {str(e)}", exc_info=True)
                        st.error(f"En feil oppstod under filbehandlingen: {str(e)}")
    else:
        st.warning("Vennligst skriv inn din OpenAI API-nøkkel i sidepanelet for å bruke dokumentprosessoren.")


def main():
    atexit.register(cleanup)
    asyncio.run(main_async())


if __name__ == "__main__":
    main()