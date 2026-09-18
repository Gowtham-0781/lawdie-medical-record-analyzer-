from app.extraction.schemas import (
    CaseFacts,
    Diagnosis,
    Injury,
    PainAndSuffering,
    Provider,
    SourceCitation,
    TreatmentEvent,
)


def test_case_facts_structure():

    citation = SourceCitation(
        document_name="synthetic_pi_medical_record.pdf",
        page_number=1,
        passage=(
            "Assessment: Acute cervical strain; "
            "acute lumbar strain; post-traumatic headache."
        ),
    )

    facts = CaseFacts(
        patient_name="Jordan Miller",
        incident_date="March 12, 2026",
        injuries=[
            Injury(
                name="Cervical strain",
                body_part="Neck",
                severity="Acute",
                citations=[citation],
            )
        ],
        diagnoses=[
            Diagnosis(
                name="Acute cervical strain",
                date="March 12, 2026",
                provider=(
                    "Peachtree Regional Medical Center"
                ),
                citations=[citation],
            )
        ],
        providers=[
            Provider(
                name=(
                    "Peachtree Regional Medical Center"
                ),
                specialty="Emergency Department",
                citations=[citation],
            )
        ],
        treatments=[
            TreatmentEvent(
                date="March 12, 2026",
                provider=(
                    "Peachtree Regional Medical Center"
                ),
                treatment="Acetaminophen",
                body_part="Neck",
                citations=[citation],
            )
        ],
        pain_and_suffering=[
            PainAndSuffering(
                description=(
                    "Neck pain made it difficult "
                    "to turn the head while driving."
                ),
                category="daily_activity",
                citations=[citation],
            )
        ],
    )

    assert facts.patient_name == "Jordan Miller"
    assert facts.incident_date == "March 12, 2026"

    assert len(facts.injuries) == 1
    assert len(facts.diagnoses) == 1
    assert len(facts.providers) == 1
    assert len(facts.treatments) == 1
    assert len(facts.pain_and_suffering) == 1

    assert (
        facts.injuries[0].name
        == "Cervical strain"
    )

    assert (
        facts.treatments[0].treatment
        == "Acetaminophen"
    )

    assert (
        facts.injuries[0]
        .citations[0]
        .page_number
        == 1
    )


def test_empty_case_facts():

    facts = CaseFacts()

    assert facts.patient_name is None
    assert facts.incident_date is None

    assert facts.injuries == []
    assert facts.diagnoses == []
    assert facts.providers == []
    assert facts.treatments == []
    assert facts.pain_and_suffering == []
    assert facts.conflicts == []