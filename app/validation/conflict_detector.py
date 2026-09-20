import re
from collections import defaultdict

from app.extraction.schemas import (
    CaseFacts,
    Conflict,
    SourceCitation,
)
from app.ingestion.pdf_loader import PageContent


class ConflictDetector:

    DATE_PATTERNS = [
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
    ]

    INCIDENT_TERMS = (
        "incident",
        "collision",
        "accident",
        "motor vehicle",
        "mvc",
        "crash",
    )

    FOLLOWUP_TERMS = (
        "date of service",
        "visit",
        "evaluation",
        "follow-up",
        "followup",
        "referred",
        "seen by",
        "appointment",
    )

    def detect(
        self,
        facts: CaseFacts,
        pages: list[PageContent] | None = None,
    ) -> list[Conflict]:

        conflicts: list[Conflict] = []

        incident_conflict = (
            self._detect_incident_date_conflict(
                facts,
                pages or [],
            )
        )

        if incident_conflict:
            conflicts.append(incident_conflict)

        return conflicts

    def _detect_incident_date_conflict(
        self,
        facts: CaseFacts,
        pages: list[PageContent],
    ) -> Conflict | None:

        date_sources: dict[
            str,
            list[SourceCitation],
        ] = defaultdict(list)

        # First inspect the actual source pages.
        for page in pages:

            passages = self._split_into_passages(
                page.text
            )

            for passage in passages:

                if not self._looks_like_incident_passage(
                    passage
                ):
                    continue

                dates = self._extract_dates(
                    passage
                )

                for date in dates:

                    citation = SourceCitation(
                        document_name=page.document_name,
                        page_number=page.page_number,
                        passage=passage.strip(),
                    )

                    date_sources[date].append(
                        citation
                    )

        # Also inspect citations extracted by the model.
        citations = self._collect_citations(
            facts
        )

        for citation in citations:

            if not self._looks_like_incident_passage(
                citation.passage
            ):
                continue

            dates = self._extract_dates(
                citation.passage
            )

            for date in dates:
                date_sources[date].append(
                    citation
                )

        supported_dates = {
            date: sources
            for date, sources in date_sources.items()
            if sources
        }

        if len(supported_dates) <= 1:
            return None

        conflict_citations: list[
            SourceCitation
        ] = []

        for sources in supported_dates.values():
            conflict_citations.extend(
                sources
            )

        return Conflict(
            field="incident_date",
            description=(
                "Different incident dates are documented "
                "across the source medical records."
            ),
            values=sorted(
                supported_dates.keys()
            ),
            citations=self._deduplicate_citations(
                conflict_citations
            ),
        )

    def _looks_like_incident_passage(
        self,
        passage: str,
    ) -> bool:

        passage_lower = passage.lower()

        has_incident_term = any(
            term in passage_lower
            for term in self.INCIDENT_TERMS
        )

        if not has_incident_term:
            return False

        # Exclude passages where the date actually describes a
        # follow-up/visit/referral event rather than the incident
        # itself (e.g. "referred following the motor vehicle
        # collision, date of service March 20, 2026").
        has_followup_term = any(
            term in passage_lower
            for term in self.FOLLOWUP_TERMS
        )

        return not has_followup_term

    def _extract_dates(
        self,
        text: str,
    ) -> list[str]:

        dates: list[str] = []

        for pattern in self.DATE_PATTERNS:

            dates.extend(
                re.findall(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )
            )

        return dates

    @staticmethod
    def _split_into_passages(
        text: str,
    ) -> list[str]:

        passages = re.split(
            r"(?<=[.!?])\s+|\n+",
            text,
        )

        return [
            passage.strip()
            for passage in passages
            if passage.strip()
        ]

    @staticmethod
    def _collect_citations(
        facts: CaseFacts,
    ) -> list[SourceCitation]:

        citations: list[
            SourceCitation
        ] = []

        for injury in facts.injuries:
            citations.extend(
                injury.citations
            )

        for diagnosis in facts.diagnoses:
            citations.extend(
                diagnosis.citations
            )

        for provider in facts.providers:
            citations.extend(
                provider.citations
            )

        for treatment in facts.treatments:
            citations.extend(
                treatment.citations
            )

        for impact in facts.pain_and_suffering:
            citations.extend(
                impact.citations
            )

        return citations

    @staticmethod
    def _deduplicate_citations(
        citations: list[SourceCitation],
    ) -> list[SourceCitation]:

        unique: dict[
            tuple[str, int, str],
            SourceCitation,
        ] = {}

        for citation in citations:

            key = (
                citation.document_name,
                citation.page_number,
                citation.passage,
            )

            unique[key] = citation

        return list(
            unique.values()
        )