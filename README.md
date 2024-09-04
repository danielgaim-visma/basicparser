# GPT-4o HR-dokumentprosessor for Peach - filoppdeling

Dette er en Streamlit-applikasjon spesielt designet for å behandle HR-relaterte dokumenter på norsk, dele dem inn i seksjoner, og utføre en rekke HR-spesifikke analyser ved hjelp av GPT-4o. Applikasjonen er skreddersydd for bruk med Peach-plattformen.

## Funksjonalitet

- Støtter opplasting av flere HR-dokumenter samtidig (PDF, DOCX, TXT)
- Bruker GPT-4o for å utføre følgende HR-spesifikke analyser for hver seksjon:
  - Generere HR-relevante seksjontitler
  - Ekstrahere HR-nøkkelord
  - Kategorisere HR-innhold
  - Identifisere HR-enheter (ansatte, avdelinger, stillinger, kompetanser)
  - Analysere arbeidsmiljø og medarbeidertilfredshet
  - Lage HR-fokuserte sammendrag
  - Ekstrahere stemningsrelaterte nøkkelord relevante for HR
- Konverterer HR-dokumenter til strukturerte JSON-filer kompatible med Peach
- Tilbyr nedlasting av alle resultater i en ZIP-fil for enkel import til Peach
- Viser sanntidsoppdateringer om behandlingsprosessen
- Estimerer gjenværende behandlingstid

## Oppsett

1. Klon dette repositoriet
2. Installer de nødvendige pakkene:
   ```
   pip install -r requirements.txt
   ```
3. Sørg for at du har en gyldig OpenAI API-nøkkel med tilgang til GPT-4o
4. Kjør Streamlit-appen:
   ```
   streamlit run app.py
   ```

## Bruk

1. Åpne appen i nettleseren
2. Skriv inn din OpenAI API-nøkkel i sidepanelet
3. Last opp en eller flere HR-dokumenter (PDF, DOCX, eller TXT)
4. Klikk på "Start filbehandling"
5. Appen vil behandle dokumentene og vise:
   - Fremdriftsstatus for hver fil
   - Oversikt over behandlede HR-seksjoner
   - Estimert gjenværende tid
6. Når behandlingen er fullført, kan du laste ned alle resultater som en ZIP-fil for import til Peach

## Viktige merknader

- Appen er designet spesifikt for norske HR-dokumenter. Den vil advare hvis den oppdager at et dokument er på et annet språk eller ikke ser ut til å være HR-relatert.
- Sørg for at du har tilstrekkelige tokens på din OpenAI API-konto og tilgang til GPT-4o modellen.
- Appen kan automatisk gjenkjenne og ekstrahere URL-er fra dokumentene, noe som kan være nyttig for å lenke til originale HR-kilder i Peach.
- Behandlingstiden kan variere avhengig av dokumentenes størrelse og kompleksitet.
- Outputformatet er optimalisert for direkte import til Peach-plattformen.

## Feilsøking

Hvis du støter på problemer under behandlingen, sjekk følgende:
- At du har en stabil internettforbindelse
- At din OpenAI API-nøkkel er gyldig, har tilstrekkelige kreditter, og har tilgang til GPT-4o
- At filene du laster opp er i støttede formater (PDF, DOCX, TXT) og ikke er korrupte
- At dokumentene inneholder HR-relatert informasjon for optimal prosessering

## Integrasjon med Peach

Denne applikasjonen er spesielt utviklet for å generere output som er kompatibelt med Peach-plattformen. For veiledning om hvordan du importerer de behandlede dataene til Peach, vennligst referer til Peach-dokumentasjonen eller kontakt Peach-support.

## Bidrag

Bidrag for å forbedre HR-analysefunksjonaliteten eller Peach-integrasjonen er velkomne! Vennligst føl deg fri til å sende inn en Pull Request eller åpne en Issue for eventuelle forbedringer eller feilrettinger.

## Lisens

[Legg til lisensinformasjon her]