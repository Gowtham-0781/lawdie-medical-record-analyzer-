from pathlib import Path

from app.ingestion.ocr import OCRProcessor
from app.ingestion.pdf_loader import PDFLoader, PageContent


class DocumentProcessor:
    def __init__(
        self,
        min_text_length: int = 50,
        ocr_dpi: int = 200,
    ):
        self.pdf_loader = PDFLoader(
            min_text_length=min_text_length
        )
        self.ocr_processor = OCRProcessor(dpi=ocr_dpi)

    def process(
        self,
        file_path: str | Path,
    ) -> list[PageContent]:

        path = Path(file_path)

        pages = self.pdf_loader.load(path)

        processed_pages: list[PageContent] = []

        for page in pages:

            if page.requires_ocr:
                try:
                    page = self.ocr_processor.process_page(
                        path,
                        page.page_number,
                    )

                except Exception as exc:
                    print(
                        f"OCR failed for "
                        f"{page.document_name} "
                        f"page {page.page_number}: {exc}"
                    )

            processed_pages.append(page)

        return processed_pages