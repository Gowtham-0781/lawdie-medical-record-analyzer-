from app.extraction.schemas import CaseFacts, SourceCitation
from app.ingestion.pdf_loader import PageContent


class GroundingValidator:

    def validate_citation(
        self,
        citation: SourceCitation,
        pages: list[PageContent],
    ) -> bool:

        matching_page = next(
            (
                page
                for page in pages
                if page.document_name == citation.document_name
                and page.page_number == citation.page_number
            ),
            None,
        )

        if matching_page is None:
            return False

        source_text = self._normalize(
            matching_page.text
        )

        passage_text = self._normalize(
            citation.passage
        )

        if not passage_text:
            return False

        return passage_text in source_text

    def validate_citations(
        self,
        citations: list[SourceCitation],
        pages: list[PageContent],
    ) -> tuple[
        list[SourceCitation],
        list[SourceCitation],
    ]:

        valid: list[SourceCitation] = []
        invalid: list[SourceCitation] = []

        for citation in citations:

            if self.validate_citation(
                citation,
                pages,
            ):
                valid.append(citation)
            else:
                invalid.append(citation)

        return valid, invalid

    def validate_case_facts(
        self,
        facts: CaseFacts,
        pages: list[PageContent],
    ) -> dict:

        all_citations: list[SourceCitation] = []

        for injury in facts.injuries:
            all_citations.extend(
                injury.citations
            )

        for diagnosis in facts.diagnoses:
            all_citations.extend(
                diagnosis.citations
            )

        for provider in facts.providers:
            all_citations.extend(
                provider.citations
            )

        for treatment in facts.treatments:
            all_citations.extend(
                treatment.citations
            )

        for impact in facts.pain_and_suffering:
            all_citations.extend(
                impact.citations
            )

        valid, invalid = self.validate_citations(
            all_citations,
            pages,
        )

        total = len(all_citations)

        grounding_rate = (
            len(valid) / total
            if total > 0
            else 0.0
        )

        return {
            "total_citations": total,
            "valid_citations": len(valid),
            "invalid_citations": len(invalid),
            "grounding_rate": grounding_rate,
            "invalid": invalid,
        }

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:

        return " ".join(
            text.lower().split()
        )