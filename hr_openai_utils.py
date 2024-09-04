from openai import OpenAI
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

def safe_json_loads(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai_api(client, messages, max_tokens):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def extract_hr_keywords(text, client):
    messages = [
        {"role": "system", "content": "Du er en HR-spesialist som trekker ut relevante HR-relaterte nøkkelord fra tekst på norsk."},
        {"role": "user", "content": f"Trekk ut 5 HR-relaterte nøkkelord eller fraser fra følgende tekst på norsk. Svar kun med nøkkelordene, adskilt med komma:\n\n{text[:1000]}"}
    ]
    keywords = call_openai_api(client, messages, 100).split(',')
    return [word.strip() for word in keywords][:5]

def categorize_hr_document(text, client):
    hr_categories = ["Rekruttering", "Onboarding", "Opplæring", "Ytelsesstyring", "Kompensasjon og fordeler",
                     "Arbeidsmiljø", "Personaladministrasjon", "Organisasjonsutvikling", "HMS", "Annet"]
    categories_str = ", ".join(hr_categories)
    messages = [
        {"role": "system", "content": "Du er en HR-spesialist som kategoriserer HR-dokumenter basert på gitte kategorier."},
        {"role": "user", "content": f"Kategoriser følgende HR-relaterte tekst i en av disse kategoriene: {categories_str}. Svar kun med kategorinavnet:\n\n{text[:1000]}"}
    ]
    return call_openai_api(client, messages, 50)

def extract_hr_entities(text, client):
    messages = [
        {"role": "system", "content": "Du er en HR-spesialist som trekker ut relevante enheter fra HR-relatert tekst på norsk."},
        {"role": "user", "content": f"Trekk ut relevante HR-enheter (ansatte, avdelinger, stillinger, kompetanser) fra følgende tekst. Returner resultatet som en JSON-streng med nøklene 'ansatte', 'avdelinger', 'stillinger', og 'kompetanser':\n\n{text[:2000]}"}
    ]
    return safe_json_loads(call_openai_api(client, messages, 500))

def summarize_hr_text(text, client, max_words=50):
    messages = [
        {"role": "system", "content": "Du er en HR-spesialist som lager konsise sammendrag av HR-relatert tekst på norsk."},
        {"role": "user", "content": f"Lag et HR-fokusert sammendrag på rundt {max_words} ord av følgende tekst på norsk:\n\n{text[:2000]}"}
    ]
    return call_openai_api(client, messages, max_words * 2)

def extract_sentiment_keywords(text, client):
    messages = [
        {"role": "system", "content": "Du er en HR-spesialist som analyserer stemning og trekker ut nøkkelord relatert til stemning fra HR-relatert tekst på norsk."},
        {"role": "user", "content": f"""
        Analyser følgende HR-relaterte tekst og trekk ut nøkkelord relatert til stemning. 
        Fokuser på ord og fraser som indikerer positive eller negative følelser, holdninger, eller oppfatninger.
        Returner resultatet som en JSON-streng med nøklene 'positive' og 'negative', hver med en liste av 5 relevante nøkkelord:

        {text[:2000]}
        """}
    ]
    try:
        result = call_openai_api(client, messages, 200)
        logger.info(f"Raw result from sentiment keywords extraction: {result}")
        parsed_result = safe_json_loads(result)
        logger.info(f"Parsed result from sentiment keywords extraction: {parsed_result}")
        logger.info(f"Type of parsed_result: {type(parsed_result)}")
        logger.info(f"Keys in parsed_result: {parsed_result.keys() if isinstance(parsed_result, dict) else 'Not a dict'}")

        if isinstance(parsed_result, dict) and 'positive' in parsed_result and 'negative' in parsed_result:
            logger.info("Sentiment keywords extracted successfully")
            return parsed_result
        else:
            logger.error(f"Unexpected format in sentiment keywords extraction: {parsed_result}")
            return {'positive': [], 'negative': []}
    except Exception as e:
        logger.error(f"Error in sentiment keywords extraction: {str(e)}")
        return {'positive': [], 'negative': []}