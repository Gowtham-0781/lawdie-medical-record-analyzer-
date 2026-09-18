from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class PageContent:
    document_name: str
    page_number: int
    text: str
    requires_ocr: bool = False


class PDFLoader:
    def __init__(self, min_text_length: int = 50):
        self.min_text_length = min_text_length

    def load(self, file_path: str | Path) -> list[PageContent]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Unsupported file type: {path.suffix}")

        pages: list[PageContent] = []

        with pymupdf.open(path) as document:
            for page_index, page in enumerate(document):
                text = page.get_text("text").strip()

                requires_ocr = len(text) < self.min_text_length

                pages.append(
                    PageContent(
                        document_name=path.name,
                        page_number=page_index + 1,
                        text=text,
                        requires_ocr=requires_ocr,
                    )
                )

        return pages