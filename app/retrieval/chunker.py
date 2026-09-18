from dataclasses import dataclass

from app.config import settings
from app.ingestion.pdf_loader import PageContent


@dataclass
class DocumentChunk:
    chunk_id: str
    document_name: str
    page_number: int
    text: str


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

    def chunk_pages(
        self,
        pages: list[PageContent],
    ) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        for page in pages:
            text = page.text.strip()

            if not text:
                continue

            start = 0
            chunk_index = 1

            while start < len(text):
                end = min(
                    start + self.chunk_size,
                    len(text),
                )

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunk_id = (
                        f"{page.document_name}"
                        f"_p{page.page_number}"
                        f"_c{chunk_index}"
                    )

                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_name=page.document_name,
                            page_number=page.page_number,
                            text=chunk_text,
                        )
                    )

                if end >= len(text):
                    break

                start = end - self.chunk_overlap
                chunk_index += 1

        return chunks