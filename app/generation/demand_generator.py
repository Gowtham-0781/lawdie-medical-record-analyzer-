import json

from openai import OpenAI

from app.config import settings
from app.extraction.schemas import (
    CaseFacts,
    DemandNarrative,
)
from app.generation.prompts import (
    DEMAND_GENERATION_SYSTEM_PROMPT,
    build_demand_prompt,
)


class DemandGenerator:

    def __init__(self):

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. "
                "Add it to the local .env file."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def generate(
        self,
        facts: CaseFacts,
    ) -> DemandNarrative:

        facts_json = json.dumps(
            facts.model_dump(),
            indent=2,
        )

        response = self.client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        DEMAND_GENERATION_SYSTEM_PROMPT
                    ),
                },
                {
                    "role": "user",
                    "content": build_demand_prompt(
                        facts_json
                    ),
                },
            ],
        )

        narrative = response.output_text.strip()

        if not narrative:
            raise RuntimeError(
                "Model did not return a demand narrative."
            )

        citations = []

        for injury in facts.injuries:
            citations.extend(injury.citations)

        for diagnosis in facts.diagnoses:
            citations.extend(diagnosis.citations)

        for provider in facts.providers:
            citations.extend(provider.citations)

        for treatment in facts.treatments:
            citations.extend(treatment.citations)

        for impact in facts.pain_and_suffering:
            citations.extend(impact.citations)

        citations = self._deduplicate_citations(
            citations
        )

        return DemandNarrative(
            narrative=narrative,
            citations=citations,
        )

    @staticmethod
    def _deduplicate_citations(
        citations,
    ):

        unique = {}

        for citation in citations:

            key = (
                citation.document_name,
                citation.page_number,
                citation.passage,
            )

            unique[key] = citation

        return list(unique.values())