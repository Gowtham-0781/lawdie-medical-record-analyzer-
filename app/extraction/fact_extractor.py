from openai import OpenAI

from app.config import settings
from app.extraction.schemas import CaseFacts
from app.generation.prompts import (
    FACT_EXTRACTION_SYSTEM_PROMPT,
    build_fact_evidence_prompt,
)
from app.retrieval.retriever import RetrievalResult


class FactExtractor:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. "
                "Add it to the local .env file."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    @staticmethod
    def _format_evidence(
        results: list[RetrievalResult],
    ) -> str:

        evidence_blocks: list[str] = []

        for result in results:
            chunk = result.chunk

            block = (
                f"[DOCUMENT: {chunk.document_name}]\n"
                f"[PAGE: {chunk.page_number}]\n"
                f"[CHUNK: {chunk.chunk_id}]\n"
                f"{chunk.text}"
            )

            evidence_blocks.append(block)

        return "\n\n".join(evidence_blocks)

    def extract(
        self,
        results: list[RetrievalResult],
    ) -> CaseFacts:

        if not results:
            return CaseFacts()

        evidence = self._format_evidence(results)

        response = self.client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": FACT_EXTRACTION_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": build_fact_evidence_prompt(
                        evidence
                    ),
                },
            ],
            text_format=CaseFacts,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "Model did not return structured facts."
            )

        return response.output_parsed