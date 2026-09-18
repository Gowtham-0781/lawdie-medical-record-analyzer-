from app.extraction.schemas import SourceCitation
from app.ingestion.document_processor import DocumentProcessor
from app.validation.grounding import GroundingValidator


def test_valid_citation():

    pages = DocumentProcessor().process(
        "data/input/synthetic_pi_medical_record.pdf"
    )

    citation = SourceCitation(
        document_name="synthetic_pi_medical_record.pdf",
        page_number=1,
        passage=(
            "Reported Incident: Motor vehicle collision "
            "on March 12, 2026."
        ),
    )

    validator = GroundingValidator()

    result = validator.validate_citation(
        citation,
        pages,
    )

    assert result is True


def test_fake_citation_is_rejected():

    pages = DocumentProcessor().process(
        "data/input/synthetic_pi_medical_record.pdf"
    )

    citation = SourceCitation(
        document_name="synthetic_pi_medical_record.pdf",
        page_number=1,
        passage=(
            "Patient suffered a fractured right leg "
            "requiring emergency surgery."
        ),
    )

    validator = GroundingValidator()

    result = validator.validate_citation(
        citation,
        pages,
    )

    assert result is False