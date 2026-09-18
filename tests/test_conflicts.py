from app.extraction.schemas import (
    CaseFacts,
    Injury,
    SourceCitation,
)
from app.validation.conflict_detector import ConflictDetector


def test_incident_date_conflict():

    facts = CaseFacts(
        patient_name="Jordan Miller",
        incident_date="March 12, 2026",
        injuries=[
            Injury(
                name="Cervical strain",
                citations=[
                    SourceCitation(
                        document_name="synthetic_pi_medical_record.pdf",
                        page_number=1,
                        passage=(
                            "Reported Incident: Motor vehicle "
                            "collision on March 12, 2026."
                        ),
                    )
                ],
            ),
            Injury(
                name="Low back pain",
                citations=[
                    SourceCitation(
                        document_name="synthetic_pi_medical_record.pdf",
                        page_number=8,
                        passage=(
                            "Incident Date Entered: "
                            "March 13, 2026."
                        ),
                    )
                ],
            ),
        ],
    )

    detector = ConflictDetector()

    conflicts = detector.detect(facts)

    assert len(conflicts) == 1

    conflict = conflicts[0]

    assert conflict.field == "incident_date"

    assert "March 12, 2026" in conflict.values
    assert "March 13, 2026" in conflict.values

    assert len(conflict.citations) == 2