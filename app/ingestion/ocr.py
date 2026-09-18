from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

from app.ingestion.pdf_loader import PageContent


class OCRProcessor:
    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def process_page(
        self,
        file_path: str | Path,
        page_number: int,
    ) -> PageContent:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        if page_number < 1:
            raise ValueError("page_number must be 1 or greater")

        with pymupdf.open(path) as document:
            if page_number > len(document):
                raise ValueError(
                    f"Page {page_number} does not exist. "
                    f"Document has {len(document)} pages."
                )

            page = document[page_number - 1]

            zoom = self.dpi / 72
            matrix = pymupdf.Matrix(zoom, zoom)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples,
            )

            text = pytesseract.image_to_string(image).strip()

        return PageContent(
            document_name=path.name,
            page_number=page_number,
            text=text,
            requires_ocr=False,
        )