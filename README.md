# Lawdie Medical Record Analyzer

A medical-record analysis pipeline for personal-injury cases. The system ingests medical-record PDFs, extracts text with OCR fallback, retrieves relevant evidence, extracts structured medical facts, validates source grounding, identifies conflicting information, and generates a demand-letter-style medical narrative.

## Features

- PDF medical-record ingestion
- OCR fallback for scanned or low-text pages
- Page-level source tracking
- Document chunking
- Semantic retrieval using sentence-transformers and FAISS
- Structured medical fact extraction
- Injuries and diagnoses
- Providers and treatment history
- Pain and functional limitations
- Work, sleep, mobility, hobby, and daily-activity impacts
- Source citation validation
- Conflict detection across medical records
- Grounded demand narrative generation
- JSON and text output
- Automated tests

## Architecture

```text
Medical Record PDF
        |
        v
PDF Text Extraction
        |
        +---- Low/No Text ----> Tesseract OCR
        |
        v
Page-Level Documents
        |
        v
Document Chunking
        |
        v
Sentence Transformer Embeddings
        |
        v
FAISS Semantic Retrieval
        |
        v
Relevant Evidence Only
        |
        v
Structured Fact Extraction
        |
        +----> Grounding Validation
        |
        +----> Conflict Detection
        |
        v
Grounded Case Facts
        |
        v
Demand Narrative Generation
        |
        v
JSON + Demand Text Output
```

The complete medical record is not sent to the language model in a single context. Relevant chunks are retrieved first so model context remains scoped to useful source evidence.

## Project Structure

```text
app/
  extraction/
    schemas.py
    fact_extractor.py

  generation/
    prompts.py
    demand_generator.py

  ingestion/
    pdf_loader.py
    ocr.py
    document_processor.py

  retrieval/
    chunker.py
    retriever.py

  validation/
    conflict_detector.py
    grounding.py

  config.py
  main.py

data/
  input/
  output/

sample_case/
  expected/
    expected_facts.json

  input/
    synthetic_pi_medical_record.pdf

  output/
    synthetic_pi_medical_record_analysis.json
    synthetic_pi_medical_record_demand.txt

tests/
  test_conflicts.py
  test_extraction.py
  test_grounding.py

run.py
requirements.txt
.env.example
README.md
```

## Setup

### 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

Tesseract is required for scanned or image-based medical-record pages.

On Windows, install Tesseract and make sure the `tesseract` command is available from the terminal.

Verify:

```powershell
tesseract --version
```

### 4. Configure environment variables

Copy `.env.example` to `.env`.

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini

APP_NAME=Lawdie Medical Record Analyzer
APP_ENV=development

CHUNK_SIZE=1200
CHUNK_OVERLAP=200
TOP_K=6
```

Do not commit `.env` or API credentials.

## Running the Analyzer

Run:

```powershell
python run.py data/input/synthetic_pi_medical_record.pdf
```

The pipeline performs:

1. PDF ingestion
2. OCR fallback where necessary
3. Document chunking
4. Semantic retrieval
5. Structured fact extraction
6. Citation grounding validation
7. Conflict detection
8. Demand narrative generation

Generated files are written to:

```text
data/output/
```

Example:

```text
synthetic_pi_medical_record_analysis.json
synthetic_pi_medical_record_demand.txt
```

## Structured Facts

The extraction layer captures information including:

- Patient
- Incident date
- Injuries
- Body parts
- Diagnoses
- Diagnosis codes when documented
- Providers
- Provider specialties
- Treatment dates
- Treatments and procedures
- Treatment outcomes
- Pain
- Work limitations
- Sleep limitations
- Mobility limitations
- Hobby limitations
- Daily-activity limitations

Every extracted medical fact is designed to carry source evidence containing:

```text
document_name
page_number
passage
```

## Grounding and Hallucination Control

The language model is instructed to extract only facts supported by retrieved medical-record evidence.

After extraction, citations are validated against the processed source pages.

A citation is accepted only when:

- The referenced document exists in the processed case
- The referenced page exists
- The cited passage can be matched to source text after normalization

Unsupported citations are surfaced as invalid rather than automatically trusted.

The sample end-to-end run produced 38 valid citations out of 40 extracted citations. Invalid citations remain detectable by the validation layer instead of being silently accepted.

## Conflict Detection

The system does not silently choose between contradictory source facts.

The conflict detector independently examines source medical-record pages and extracted citations.

The synthetic sample intentionally contains conflicting incident dates:

```text
March 12, 2026
March 13, 2026
```

The system surfaces this as an `incident_date` conflict and preserves supporting source citations.

This is important because inconsistent information in medical records should be visible to the reviewer rather than automatically reconciled by the model.

## Demand Narrative Generation

Demand generation uses structured case facts rather than the raw document stack.

The generation prompt prohibits the model from inventing:

- Diagnoses
- Treatments
- Providers
- Dates
- Symptoms
- Prognoses
- Medical bills
- Causation
- Settlement amounts

The generated narrative describes documented treatment and pain-and-suffering impacts while retaining inline source references.

## Sample Case

The repository includes a fully synthetic personal-injury medical record.

The case contains:

- Emergency department treatment
- Primary-care follow-up
- Physical therapy
- Lumbar MRI
- Orthopedic consultation
- Treatment progression
- Work limitations
- Sleep disruption
- Driving limitations
- Household-activity limitations
- Recreational limitations
- An intentionally conflicting incident date

No real patient information or protected health information is used.

The expected facts are documented in:

```text
sample_case/expected/expected_facts.json
```

Actual end-to-end outputs are available under:

```text
sample_case/output/
```

## Testing

Run:

```powershell
pytest -v
```

Current automated tests cover:

- Structured case-fact schemas
- Empty extraction behavior
- Conflict detection
- Valid source citations
- Rejection of unsupported citations

## What Is Not Production Ready

This project is a take-home implementation and would require additional work before handling real legal or medical workloads.

Current limitations include:

- Character-based chunking can split semantic sections.
- OCR quality depends on scan quality and Tesseract performance.
- Handwriting recognition is limited.
- Retrieval currently uses an in-memory FAISS index.
- Citation validation primarily uses normalized exact passage matching.
- Conflict detection currently focuses on incident-date discrepancies.
- LLM extraction can vary between runs.
- There is no human-review interface.
- There is no persistent case database.
- There is no authentication or role-based access control.
- There is no PHI-specific security or compliance layer.
- There is no production monitoring, audit trail, or model-evaluation framework.
- Medical bills and damages calculations are outside the current implementation.

The generated narrative should therefore be treated as draft material for human review, not as final legal or medical advice.

## What I Would Build Next

With additional time, I would focus on:

1. Sentence and section-aware chunking for medical documents.
2. Hybrid retrieval combining semantic and keyword search.
3. Better OCR preprocessing and handwriting-capable document models.
4. More granular conflict detection across diagnoses, dates, providers, medications, and treatment history.
5. Fuzzy and span-level citation verification.
6. Per-claim confidence and grounding metadata.
7. Automated evaluation against labeled medical-record cases.
8. Persistent vector storage and case-level document management.
9. A reviewer interface showing each generated claim beside its source page and passage.
10. Authentication, encryption, audit logging, PHI controls, and production observability.

## Design Principle

The central design principle is that the language model should not act as the source of truth.

The medical records are the source of truth.

Retrieval limits model context, structured extraction constrains output, grounding checks citations against source pages, and conflict detection preserves contradictory evidence for human review.